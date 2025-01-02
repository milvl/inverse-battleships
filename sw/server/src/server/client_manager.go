package server

import (
	"context"
	"errors"
	"fmt"
	"inverse-battleships-server/const/custom_errors"
	"inverse-battleships-server/const/protocol"
	"inverse-battleships-server/logging"
	"inverse-battleships-server/util/cmd_validator"
	"inverse-battleships-server/util/msg_parser"
	"io"
	"net"
	"strings"
	"sync"
	"time"
)

// Client represents a TCP client.
type Client struct {
	conn     net.Conn
	nickname string
	lastTime time.Time
	isAuth   bool
	msgBuff  string
}

// Lobby represents a game lobby.
type Lobby struct {
	id            string
	player01      string
	player02      string
	state         uint8
	interruptTime time.Time
	readyCount    uint8
}

// Server represents a TCP server.
type ClientManager struct {
	pServer       *Server            // server pointer
	pendClients   map[string]*Client // map of pending clients with their addresses as keys
	authClients   map[string]*Client // map of authenticated clients with their nicknames as keys
	lobbies       map[string]*Lobby  // manage lobbies
	playerToLobby map[string]*Lobby  // map of players to their lobbies
	rwMutex       sync.RWMutex       // mutex to lock the client manager
}

// NewClientManager creates a new ClientManager.
// It requires a server pointer as a parameter.
func NewClientManager(server *Server) *ClientManager {
	return &ClientManager{
		pServer:       server,
		authClients:   make(map[string]*Client),
		lobbies:       make(map[string]*Lobby),
		playerToLobby: make(map[string]*Lobby),
		pendClients:   make(map[string]*Client),
	}
}

// getCompleteMsg checks if the message is complete.
// It returns a boolean indicating if the message is complete,
// the whole message, and additional parts of queued messages.
func getCompleteMsg(msg string) (bool, string, string) {
	isWhole := false
	wholeMsg := ""
	additional := ""

	// check if the message is complete
	if strings.Contains(msg, protocol.MsgTerminator) {
		isWhole = true

		// find the terminator index
		terminatorIndex := strings.Index(msg, protocol.MsgTerminator)
		wholeMsg = msg[:terminatorIndex+1]
		if len(msg) > terminatorIndex+1 {
			additional = msg[terminatorIndex+1:]
		}
	}

	return isWhole, wholeMsg, additional
}

// readCompleteMessage reads a message from the client.
// It returns the parsed message, the raw string message, and an error.
func (cm *ClientManager) readCompleteMessage(pClient *Client) (*cmd_validator.IncomingMessage, string, error) {
	// sanity checks
	if pClient == nil {
		return nil, "", custom_errors.ErrNilPointer
	}
	if pClient.conn == nil {
		return nil, "", custom_errors.ErrNilConn
	}

	// try to read until a whole message is received
	fullMsgDeadline := time.Now().Add(protocol.CompleteMsgTimeout)
	msg := ""
	for {
		// handle timeout
		if time.Now().After(fullMsgDeadline) {
			return nil, "", fmt.Errorf("client did not send whole message in time")
		}

		// check for any queued messages
		if pClient.msgBuff != "" {
			msg = pClient.msgBuff
			pClient.msgBuff = ""
		}

		isComplete, recv, additional := getCompleteMsg(msg)
		if isComplete {
			// buffer any additional parts
			pClient.msgBuff += additional
			msg = recv
			break
		}

		recv, err := cm.pServer.ReadMessage(pClient.conn)
		if err != nil {
			return nil, "", fmt.Errorf("failed to read message from client: %w", err)
		}
		msg += recv
		pClient.lastTime = time.Now()
	}

	// check if the message is a valid message
	parts, err := msg_parser.FromNetMessage(msg)
	if err != nil {
		return nil, "", fmt.Errorf("failed to parse message: %w", err)
	}

	// validate the message for generic format
	pCommand, err := cmd_validator.GetCommand(parts)
	if err != nil {
		return nil, "", fmt.Errorf("failed to extract valid command: %w", err)
	}

	return pCommand, msg, nil
}

// handleClientError handles client errors.
// It returns two booleans: one indicating if the error was caused by a timeout,
// and the other indicating if the error means the client should be disconnected.
func (cm *ClientManager) handleClientError(pClient *Client, err error) (bool, bool) {
	// handle i/o timeout
	var netErr net.Error
	if errors.As(err, &netErr) && netErr.Timeout() {
		return true, false
	}

	// handle EOF (graceful or abrupt disconnection)
	if errors.Is(err, io.EOF) {
		logging.Warn(fmt.Sprintf("Client %s disconnected abruptly", pClient.conn.RemoteAddr().String()))

		// some other error occurred
	} else {
		logging.Error(fmt.Sprintf("Error reading from client %s: %v", pClient.conn.RemoteAddr().String(), err))
	}
	return false, true
}

// startServer starts the TCP server.
func (cm *ClientManager) startServer() error {
	// sanity check
	if cm.pServer == nil {
		return fmt.Errorf("server is nil")
	}

	var err error = nil

	err = cm.pServer.Start()
	return err
}

// stopServer stops the TCP server.
func (cm *ClientManager) stopServer() error {
	// sanity check
	if cm.pServer == nil {
		return fmt.Errorf("server is nil")
	}

	cm.pServer.Stop()
	return nil
}

// addClient adds a new unauthenticated client to the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) addClient(conn net.Conn) (*Client, error) {
	// sanity check
	if conn == nil {
		return nil, fmt.Errorf("connection is nil")
	}

	pClient := &Client{
		conn:     conn,
		isAuth:   false,
		msgBuff:  "",
		lastTime: time.Now(),
	}

	cm.pendClients[conn.RemoteAddr().String()] = pClient
	logging.Info(fmt.Sprintf("Client %s has been added to pending", conn.RemoteAddr().String()))
	return pClient, nil
}

// authenticateClient adds a new authenticated client to the client manager.
// It returns the nickname of the client upon successful authentication.
// It returns an error if the nickname is already taken.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) authenticateClient(pClient *Client, nickname string) error {
	// sanity checks
	if pClient == nil {
		return custom_errors.ErrNilPointer
	}

	_, exists := cm.authClients[nickname]
	if exists {
		return fmt.Errorf("nickname is already taken")
	}

	// add the client to authenticated clients
	pClient.nickname = nickname
	pClient.isAuth = true
	cm.authClients[nickname] = pClient

	// remove the client from pending clients
	delete(cm.pendClients, pClient.conn.RemoteAddr().String())
	logging.Info(fmt.Sprintf("Client %s - \"%s\" has been authenticated", pClient.conn.RemoteAddr().String(), nickname))
	return nil
}

// removeClient removes a client from the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) removeClient(nickname string) error {
	// sanity check
	if nickname == "" {
		return fmt.Errorf("nickname is empty")
	}
	_, exists := cm.authClients[nickname]
	if !exists {
		return fmt.Errorf("client not found")
	}

	addr := cm.authClients[nickname].conn.RemoteAddr().String()
	delete(cm.authClients, nickname)
	logging.Info(fmt.Sprintf("Client %s - \"%s\" has been removed", addr, nickname))
	return nil
}

// removePendingClient removes a pending client from the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) removePendingClient(addr string) error {
	// sanity check
	if addr == "" {
		return fmt.Errorf("address is empty")
	}
	_, exists := cm.pendClients[addr]
	if !exists {
		return fmt.Errorf("client not found")
	}

	delete(cm.pendClients, addr)
	logging.Info(fmt.Sprintf("Client %s has been removed", addr))
	return nil
}

// getClient returns a client from the client manager.
func (cm *ClientManager) getClient(nickname string) (*Client, error) {
	// sanity check
	if nickname == "" {
		return nil, fmt.Errorf("nickname is empty")
	}

	cm.rwMutex.RLock()
	client, exists := cm.authClients[nickname]
	cm.rwMutex.RUnlock()
	if !exists {
		return nil, fmt.Errorf("client not found")
	}

	return client, nil
}

// handleDeleteLobby deletes a lobby from the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) handleDeleteLobby(lobbyID string) error {
	// sanity checks
	if lobbyID == "" {
		return fmt.Errorf("lobby ID is empty")
	}
	_, exists := cm.lobbies[lobbyID]
	if !exists {
		return fmt.Errorf("lobby not found")
	}

	if cm.lobbies[lobbyID].player01 != "" {
		pClient01, exists := cm.authClients[cm.lobbies[lobbyID].player01]
		if exists {
			logging.Debug(fmt.Sprintf("Removing player 01: %s from lobby %s", pClient01.nickname, lobbyID))
			err := cm.sendTKO(pClient01)
			if err != nil {
				logging.Error(fmt.Sprintf("failed to send TKO message to player 01: %v", err))
			}
		}

		delete(cm.playerToLobby, cm.lobbies[lobbyID].player01)
	}

	if cm.lobbies[lobbyID].player02 != "" {
		pClient02, exists := cm.authClients[cm.lobbies[lobbyID].player02]
		if exists {
			logging.Debug(fmt.Sprintf("Removing player 02: %s from lobby %s", pClient02.nickname, lobbyID))
			err := cm.sendTKO(pClient02)
			if err != nil {
				logging.Error(fmt.Sprintf("failed to send TKO message to player 02: %v", err))
			}
		}

		delete(cm.playerToLobby, cm.lobbies[lobbyID].player02)
	}

	delete(cm.lobbies, lobbyID)
	logging.Info(fmt.Sprintf("Lobby \"%s\" has been deleted", lobbyID))

	return nil
}

// sendMessage sends a message to the client.
func (cm *ClientManager) sendMessage(conn net.Conn, parts []string) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	// convert the message to correct format
	msg, err := msg_parser.ToNetMessage(parts)
	if err != nil {
		return fmt.Errorf("failed to convert message: %w", err)
	}

	// send the message
	err = cm.pServer.SendMessage(conn, msg)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	return nil
}

// sendHandshakeReply sends a handshake reply to the client.
func (cm *ClientManager) sendHandshakeReply(pClient *Client) error {
	// sanity checks
	if pClient == nil {
		return custom_errors.ErrNilPointer
	}
	if pClient.conn == nil {
		return custom_errors.ErrNilConn
	}

	// send the handshake reply
	parts := []string{protocol.CmdHandshakeResp}
	err := cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send handshake reply: %w", err)
	}

	return nil
}

// sendPing sends a ping message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendPing(pClient *Client) error {
	// send the ping message
	parts := []string{protocol.CmdPing}
	err := cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send ping message: %w", err)
	}

	return nil
}

// sendTKO sends a TKO message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendTKO(pClient *Client) error {
	// send the TKO message
	parts := []string{protocol.CmdTKO}
	err := cm.sendMessage(pClient.conn, parts)

	if err != nil {
		return fmt.Errorf("failed to send TKO message: %w", err)
	}

	return nil
}

// sendLobbies sends a list of lobbies to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendLobbies(pClient *Client, lobbies []string) error {
	// send the list of lobbies
	parts := append([]string{protocol.CmdLobbies}, lobbies...)

	err := cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send lobby list: %w", err)
	}

	return nil
}

// sendCreateLobbyAck sends a create lobby acknowledgment message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendCreateLobbyAck(pClient *Client, lobbyID string) error {
	// send the create lobby acknowledgment message
	parts := []string{protocol.CmdCreateLobbyAck, lobbyID}
	err := cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send create lobby acknowledgment message: %w", err)
	}

	return nil
}

// sendTurnMsg sends a turn message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendTurnMsg(pClient *Client, playerOnTurn string, errChan chan error) error {
	// send the turn message
	parts := []string{protocol.CmdPlayerTurn, playerOnTurn}

	err := cm.sendMessage(pClient.conn, parts)
	if err != nil {
		if errChan != nil {
			errChan <- fmt.Errorf("failed to send turn message: %w", err)
		}
		return fmt.Errorf("failed to send turn message: %w", err)
	}

	if errChan != nil {
		errChan <- nil
	}
	return nil
}

// sendPairedMsg sends a paired message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendPairedMsg(pClient *Client, opponent string) error {
	// send the paired message
	parts := []string{protocol.CmdJoinLobbyAck, opponent}

	err := cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send paired message: %w", err)
	}

	return nil
}

// handlePingCmd sends a pong message to the client.
// Expects the client to be valid.
func (cm *ClientManager) handlePingCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) error {
	// sanity check
	err := cmd_validator.ValidatePing(pCommand)
	if err != nil {
		logging.Warn(fmt.Sprintf("invalid ping message: %v", err))
		return custom_errors.ErrInvalidCommand
	}

	// send the pong message
	parts := []string{protocol.CmdPong}
	err = cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send pong message: %w", err)
	}

	return nil
}

// handleLeaveCmd sends a leave acknowledgment message to the client.
// Expects the client to be valid.
func (cm *ClientManager) handleLeaveCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) error {
	err := cmd_validator.ValidateLeave(pCommand)
	if err != nil {
		logging.Warn(fmt.Sprintf("invalid leave message: %v", err))
		return custom_errors.ErrInvalidCommand
	}

	// send the leave acknowledgment message
	parts := []string{protocol.CmdLeaveAck}
	err = cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send leave acknowledgment message: %w", err)
	}

	// if the player is in a lobby, send a TKO message to the opponent if necessary
	cm.rwMutex.RLock()
	lobby, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		cm.rwMutex.Lock()
		lobby.state = protocol.LobbyStateFail
		cm.rwMutex.Unlock()
	}

	return nil
}

// handleLobbiesCmd sends a list of lobbies to the client.
func (cm *ClientManager) handleLobbiesCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) error {
	// sanity check
	err := cmd_validator.ValidateLobbies(pCommand)
	if err != nil {
		logging.Warn(fmt.Sprintf("invalid lobbies message: %v", err))
		return custom_errors.ErrInvalidCommand
	}

	// player must be in idle state (not in a lobby)
	cm.rwMutex.RLock()
	_, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		return custom_errors.ErrPlayerNotIdle
	}

	lobbies := make([]string, 0)

	// get the list of lobbies
	cm.rwMutex.RLock()
	for _, lobby := range cm.lobbies {
		lobbies = append(lobbies, lobby.id)
	}
	cm.rwMutex.RUnlock()

	// send the list of lobbies to the client
	err = cm.sendLobbies(pClient, lobbies)
	if err != nil {
		return fmt.Errorf("failed to send lobby list: %w", err)
	}

	return nil
}

// handleCreateLobbyCmd creates a new lobby and sends the lobby ID to the client.
func (cm *ClientManager) handleCreateLobbyCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) error {
	// sanity check
	err := cmd_validator.ValidateCreateLobby(pCommand)
	if err != nil {
		logging.Warn(fmt.Sprintf("invalid create lobby message: %v", err))
		return custom_errors.ErrInvalidCommand
	}

	// player must be in idle state (not in a lobby)
	cm.rwMutex.RLock()
	_, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		return custom_errors.ErrPlayerNotIdle
	}

	// create a new lobby
	lobbyID := pClient.nickname

	// add the lobby
	cm.rwMutex.Lock()
	cm.lobbies[lobbyID] = &Lobby{
		id:         lobbyID,
		player01:   pClient.nickname,
		player02:   "",
		state:      protocol.LobbyStateCreated,
		readyCount: uint8(0),
	}

	// add the player to the lobby
	cm.playerToLobby[pClient.nickname] = cm.lobbies[lobbyID]
	cm.rwMutex.Unlock()

	// send the lobby ID to the client
	err = cm.sendCreateLobbyAck(pClient, lobbyID)
	if err != nil {
		cm.rwMutex.Lock()
		cm.lobbies[lobbyID].state = protocol.LobbyStateFail
		cm.rwMutex.Unlock()
		return fmt.Errorf("failed to send create lobby acknowledgment: %w", err)
	}

	cm.rwMutex.Lock()
	cm.lobbies[lobbyID].state = protocol.LobbyStateWaiting
	cm.rwMutex.Unlock()

	return nil
}

// handleJoinLobbyCmd attempts to connect the client to a lobby.
func (cm *ClientManager) handleJoinLobbyCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) error {
	// sanity check
	err := cmd_validator.ValidateJoinLobby(pCommand)
	if err != nil {
		logging.Warn(fmt.Sprintf("invalid join lobby message: %v", err))
		return custom_errors.ErrInvalidCommand
	}

	// player must be in idle state (not in a lobby)
	cm.rwMutex.RLock()
	_, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		return custom_errors.ErrPlayerNotIdle
	}

	// get the lobby ID
	lobbyID := pCommand.Params[protocol.LobbyIDIndex]

	// check if the lobby exists
	cm.rwMutex.RLock()
	lobby, exists := cm.lobbies[lobbyID]
	cm.rwMutex.RUnlock()
	if !exists {
		return custom_errors.ErrLobbyNotFound
	}

	// check if the lobby is full
	if lobby.player01 != "" && lobby.player02 != "" {
		return custom_errors.ErrLobbyFull
	}

	// add the player to the lobby
	cm.rwMutex.Lock()
	if lobby.player01 == "" {
		lobby.player01 = pClient.nickname
	} else {
		lobby.player02 = pClient.nickname
	}
	cm.playerToLobby[pClient.nickname] = lobby

	// NOTE: bandage fix but might cause delay for others - lobby change
	// 		 is handled in other goroutine so it needs to be synchronized (locked)
	// 		 to prevent race conditions with other clients
	err = cm.sendCreateLobbyAck(pClient, lobbyID)
	if err != nil {
		lobby.state = protocol.LobbyStateFail
		cm.rwMutex.Unlock()
		return fmt.Errorf("failed to send join lobby acknowledgment: %w", err)
	}

	// change the lobby state
	lobby.state = protocol.LobbyStatePaired
	cm.rwMutex.Unlock()

	return nil
}

// handleClientReadyCmd handles a client ready message.
func (cm *ClientManager) handleClientReadyCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) error {
	// sanity check
	err := cmd_validator.ValidateClientReady(pCommand)
	if err != nil {
		return custom_errors.ErrInvalidCommand
	}

	// player must be in a lobby
	cm.rwMutex.RLock()
	lobby, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if !exists {
		return custom_errors.ErrPlayerNotIdle
	}

	// lobby must be unready
	cm.rwMutex.RLock()
	retFlag := lobby.state != protocol.LobbyStateUnready || lobby.readyCount >= protocol.PlayerCount
	cm.rwMutex.RUnlock()
	if retFlag {
		return errors.New("lobby is not in the correct state")
	}

	// increase the ready count
	cm.rwMutex.Lock()
	lobby.readyCount++
	cm.rwMutex.Unlock()

	return nil
}

// checkAlive checks if the client is alive by sending a ping message and waiting for a pong message.
func (cm *ClientManager) checkAlive(pClient *Client) (bool, error) {
	// sanity checks
	if pClient == nil {
		return false, custom_errors.ErrNilPointer
	}
	if pClient.conn == nil {
		return false, custom_errors.ErrNilConn
	}

	// send the ping message
	err := cm.sendPing(pClient)
	if err != nil {
		return false, fmt.Errorf("failed to send ping message: %w", err)
	}

	// read the pong message
	pCommand, rawMsg, err := cm.readCompleteMessage(pClient)
	if err != nil {
		return false, fmt.Errorf("failed to read pong response: %w", err)
	}

	// check if the pong message is valid
	var tryAgain bool = false
	err = cmd_validator.ValidatePong(pCommand)
	if errors.Is(err, custom_errors.ErrInvalidCommand) {
		// if another message is received, buffer it and await the pong message
		logging.Info(fmt.Sprintf("Another message received (%s), buffering it and awaiting pong message", escapeSpecialSymbols(rawMsg)))
		tryAgain = true

	} else if err != nil {
		return false, fmt.Errorf("invalid pong message: %w", err)
	}

	// some other message managed to get through earlier so try again
	if tryAgain {
		// read the pong message
		pCommand, _, err := cm.readCompleteMessage(pClient)
		if err != nil {
			return false, fmt.Errorf("failed to read pong message: %w", err)
		}

		pClient.msgBuff += rawMsg

		// check if the pong message is valid
		err = cmd_validator.ValidatePong(pCommand)
		if err != nil {
			return false, fmt.Errorf("invalid pong message: %w", err)
		}
	}

	return true, nil
}

// validateConnection validates a new connection.
// Returns the nickname of the client upon successful validation.
func (cm *ClientManager) validateConnection(pClient *Client) (string, error) {
	// sanity checks
	if pClient == nil {
		return "", custom_errors.ErrNilPointer
	}
	if pClient.conn == nil {
		return "", custom_errors.ErrNilConn
	}

	// read the handshake message
	pValidMsg, _, err := cm.readCompleteMessage(pClient)
	if err != nil {
		return "", fmt.Errorf("failed to read handshake message: %w", err)
	}
	err = cmd_validator.ValidateHandshake(pValidMsg)
	if err != nil {
		return "", fmt.Errorf("invalid handshake message: %w", err)
	}
	nickname := pValidMsg.Params[protocol.NicknameIndex]

	// send the handshake reply
	err = cm.sendHandshakeReply(pClient)
	if err != nil {
		return "", fmt.Errorf("failed to send handshake reply: %w", err)
	}

	// await confirmation
	pValidMsg, _, err = cm.readCompleteMessage(pClient)
	if err != nil {
		return "", fmt.Errorf("failed to read confirmation message: %w", err)
	}
	err = cmd_validator.ValidateHandshakeConfirmation(pValidMsg)
	if err != nil {
		return "", fmt.Errorf("invalid confirmation message: %w", err)
	}

	// authenticate the client
	cm.rwMutex.Lock()
	err = cm.authenticateClient(pClient, nickname)
	if err != nil {
		return "", fmt.Errorf("failed to authenticate client - code error: %w", err)
	}
	cm.rwMutex.Unlock()

	return nickname, nil
}

// prepareGame prepares a game in a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) prepareGame(lobby *Lobby) error {
	// sanity checks
	if lobby == nil {
		return custom_errors.ErrNilPointer
	}
	if lobby.state != protocol.LobbyStatePaired {
		return fmt.Errorf("lobby is not in the correct state")
	}

	// get the players
	pClientPlayer01, exists := cm.authClients[lobby.player01]
	if !exists {
		logging.Error(fmt.Sprintf("Player 01: %s not found for lobby %s", lobby.player01, lobby.id))
		return custom_errors.ErrPlayerNotFound
	}
	pClientPlayer02, exists := cm.authClients[lobby.player02]
	if !exists {
		logging.Error(fmt.Sprintf("Player 02: %s not found for lobby %s", lobby.player02, lobby.id))
		return custom_errors.ErrPlayerNotFound
	}

	// send the game start message to the players
	err := cm.sendPairedMsg(pClientPlayer01, pClientPlayer02.nickname)
	if err != nil {
		return fmt.Errorf("failed to send game start message to player 01: %w", err)
	}

	err = cm.sendPairedMsg(pClientPlayer02, pClientPlayer01.nickname)
	if err != nil {
		return fmt.Errorf("failed to send game start message to player 02: %w", err)
	}

	// change the lobby state
	lobby.state = protocol.LobbyStateUnready

	return nil
}

// startGame starts a game in a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) startGame(lobby *Lobby) error {
	// sanity checks
	if lobby == nil {
		return custom_errors.ErrNilPointer
	}
	if lobby.state != protocol.LobbyStateUnready {
		return fmt.Errorf("lobby is not in the correct state")
	}

	// get the clients
	_, exists := cm.authClients[lobby.player01]
	if !exists {
		logging.Error(fmt.Sprintf("Player 01: %s not found for lobby %s", lobby.player01, lobby.id))
		lobby.state = protocol.LobbyStateFail
		return custom_errors.ErrPlayerNotFound
	}
	_, exists = cm.authClients[lobby.player02]
	if !exists {
		logging.Error(fmt.Sprintf("Player 02: %s not found for lobby %s", lobby.player02, lobby.id))
		lobby.state = protocol.LobbyStateFail
		return custom_errors.ErrPlayerNotFound
	}

	// start the game
	lobby.state = protocol.LobbyStatePlayer01Turn
	lobby.readyCount = uint8(0)

	return nil
}

// advanceGame advances a game in a lobby.
//
// WARNING: It reads a shared resource, so it should be called with a rlock.
func (cm *ClientManager) advanceGame(lobby *Lobby) error {
	// sanity checks
	if lobby == nil {
		return custom_errors.ErrNilPointer
	}
	if lobby.state != protocol.LobbyStatePlayer01Turn && lobby.state != protocol.LobbyStatePlayer02Turn {
		return fmt.Errorf("lobby is not in the correct state")
	}

	// get the players
	pClientPlayer01, exists := cm.authClients[lobby.player01]
	if !exists {
		return fmt.Errorf("player 01: %s not found for lobby %s", lobby.player01, lobby.id)
	}
	pClientPlayer02, exists := cm.authClients[lobby.player02]
	if !exists {
		return fmt.Errorf("player 02: %s not found for lobby %s", lobby.player02, lobby.id)
	}

	var playerOnTurn string
	switch lobby.state {
	case protocol.LobbyStatePlayer01Turn:
		playerOnTurn = pClientPlayer01.nickname
	case protocol.LobbyStatePlayer02Turn:
		playerOnTurn = pClientPlayer02.nickname
	default:
		return fmt.Errorf("invalid lobby state: %d", lobby.state)
	}

	// send the turn message to the players
	errChan := make(chan error, int(protocol.PlayerCount))
	go cm.sendTurnMsg(pClientPlayer01, playerOnTurn, errChan)
	go cm.sendTurnMsg(pClientPlayer02, playerOnTurn, errChan)
	var err error
	for i := 0; i < int(protocol.PlayerCount); i++ {
		err = <-errChan
		if err != nil {
			return fmt.Errorf("failed to send turn message: %w", err)
		}
	}

	return nil
}

// getLobbyStates gets the states of the lobbies and appends the lobby IDs to the corresponding slices.
//
// WARNING: It reads a shared resource, so it should be called with a rlock.
func (cm *ClientManager) getLobbyStates(lobbiesToDelete *[]string, lobbiesToPrepare *[]string, lobbiesToStart *[]string, lobbiesToAdvance *[]string) {
	for _, lobby := range cm.lobbies {
		// handle the game
		switch lobby.state {
		case protocol.LobbyStateFail:
			*lobbiesToDelete = append(*lobbiesToDelete, lobby.id)

		case protocol.LobbyStatePaired:
			*lobbiesToPrepare = append(*lobbiesToPrepare, lobby.id)

		case protocol.LobbyStateUnready:
			if lobby.readyCount == protocol.PlayerCount {
				*lobbiesToStart = append(*lobbiesToStart, lobby.id)
			}

		case protocol.LobbyStatePlayer01Turn, protocol.LobbyStatePlayer02Turn:
			*lobbiesToAdvance = append(*lobbiesToAdvance, lobby.id)
		}
	}
}

// manageLobbies handles the games.
func (cm *ClientManager) manageLobbies() error {
	var err error = nil

	var lobbiesToDelete []string
	var lobbiesToPrepare []string
	var lobbiesToStart []string
	var lobbiesToAdvance []string

	cm.rwMutex.RLock()
	cm.getLobbyStates(&lobbiesToDelete, &lobbiesToPrepare, &lobbiesToStart, &lobbiesToAdvance)
	cm.rwMutex.RUnlock()

	for _, lobbyID := range lobbiesToDelete {
		cm.rwMutex.Lock()
		err = cm.handleDeleteLobby(lobbyID)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Error(fmt.Sprintf("failed to delete lobby %s: %v", lobbyID, err))
		}
	}

	for _, lobbyID := range lobbiesToPrepare {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}
		cm.rwMutex.Lock()
		err = cm.prepareGame(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to prepare game in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}
	for _, lobbyID := range lobbiesToStart {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.Lock()
		err = cm.startGame(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to start game in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}
	for _, lobbyID := range lobbiesToAdvance {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.RLock()
		err = cm.advanceGame(lobby)
		cm.rwMutex.RUnlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to advance game in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}

	return err
}

// handleCommand handles a command from the client. It returns a boolean indicating if the client should stay connected.
// If error is not nil, the stayConnected boolean returned is not defined.
// TODO: handle these Errs
// ErrPlayerNotIdle, ErrLobbyNotFound, ErrLobbyFull, ErrInvalidCommand
func (cm *ClientManager) handleCommand(pClient *Client, pCommand *cmd_validator.IncomingMessage) (bool, error) {
	// sanity checks
	if pClient == nil {
		return false, custom_errors.ErrNilPointer
	}
	if pCommand == nil {
		return false, custom_errors.ErrNilPointer
	}

	var err error = nil
	stayConnected := true

	// handle the command
	switch pCommand.Command {
	// universal commands
	case protocol.CmdPing:
		err = cm.handlePingCmd(pClient, pCommand)
	case protocol.CmdLeave:
		logging.Info(fmt.Sprintf("Client %s - %s has requested to leave.", pClient.conn.RemoteAddr().String(), pClient.nickname))
		stayConnected = false
		err = cm.handleLeaveCmd(pClient, pCommand)

	// idle commands
	case protocol.CmdLobbies:
		err = cm.handleLobbiesCmd(pClient, pCommand)
	case protocol.CmdCreateLobby:
		err = cm.handleCreateLobbyCmd(pClient, pCommand)
	case protocol.CmdJoinLobby:
		err = cm.handleJoinLobbyCmd(pClient, pCommand)

	// in lobby commands
	case protocol.CmdClientReady:
		// TODO TADY
		err = cm.handleClientReadyCmd(pClient, pCommand)

	default:
		err = fmt.Errorf("unknown command: %s", pCommand.Command)
	}

	return stayConnected, err
}

// handleCommand handles a command from the client.
func (cm *ClientManager) handleConnection(conn net.Conn) {
	// TODO HERE
	logging.Debug(fmt.Sprintf("Handling connection from %s.", conn.RemoteAddr().String()))

	// add the client
	cm.rwMutex.Lock()
	pClient, err := cm.addClient(conn)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to add client: %v", err))
		return
	}
	cm.rwMutex.Unlock()

	// validate the connection
	nickname, err := cm.validateConnection(pClient)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to validate connection: %v", err))
		// remove the client
		cm.rwMutex.Lock()
		err = cm.removePendingClient(conn.RemoteAddr().String())
		if err != nil {
			logging.Error(fmt.Sprintf("failed to remove pending client: %v", err))
		}
		cm.rwMutex.Unlock()

		// close the connection
		err = conn.Close()
		if err != nil {
			logging.Error(fmt.Sprintf("failed to close connection: %v", err))
		}
		logging.Info(fmt.Sprintf("Client %s was disconnected", conn.RemoteAddr().String()))
		return
	}

	// TODO: handle reconnect

	// infinite loop to handle messages
	for {
		// keep alive
		if time.Since(pClient.lastTime) > protocol.KeepAliveTimeout {
			alive, err := cm.checkAlive(pClient)
			if err != nil {
				logging.Warn(fmt.Sprintf("failed to check if client is alive: %v", err))
			}
			if !alive {
				logging.Info(fmt.Sprintf("Client %s is not alive", conn.RemoteAddr().String()))
				break
			}
		}

		// read message (busy waiting is prevented by the timeout)
		pCommand, _, err := cm.readCompleteMessage(pClient)
		if err != nil {
			timeout, disconnect := cm.handleClientError(pClient, err)
			// if the client is disconnected, break the loop
			if disconnect {
				break
			}
			if timeout {
				continue
			}
		}

		stayConnected, err := cm.handleCommand(pClient, pCommand)
		if err != nil {
			logging.Error(fmt.Sprintf("failed to handle command: %v", err))
		}
		if !stayConnected {
			break
		}
	}

	// check if the client was in a lobby
	cm.rwMutex.RLock()
	lobby, exists := cm.playerToLobby[nickname]
	cm.rwMutex.RUnlock()
	if exists {
		cm.rwMutex.RLock()
		doWait := lobby.state != protocol.LobbyStateFail && lobby.state != protocol.LobbyStateWaiting
		cm.rwMutex.RUnlock()
		if doWait {
			logging.Info(fmt.Sprintf("Client abruptly disconnected from lobby %s. State changed to waiting.", lobby.id))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateWaiting
			lobby.interruptTime = time.Now()
			cm.rwMutex.Unlock()
		} else {
			cm.rwMutex.RLock()
			delLobby := lobby.state == protocol.LobbyStateWaiting
			cm.rwMutex.RUnlock()
			if delLobby {
				logging.Info(fmt.Sprintf("Client %s has abruptly disconnected from one player lobby \"%s\". Marking lobby for deletion.", nickname, lobby.id))
				cm.rwMutex.Lock()
				lobby.state = protocol.LobbyStateFail
				cm.rwMutex.Unlock()
			}
		}
	}

	// remove the client
	cm.rwMutex.Lock()
	err = cm.removeClient(nickname)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to remove client: %v", err))
	}
	cm.rwMutex.Unlock()

	// close the connection
	err = conn.Close()
	if err != nil {
		logging.Error(fmt.Sprintf("failed to close connection: %v", err))
	}
	logging.Info(fmt.Sprintf("Client %s has disconnected", conn.RemoteAddr().String()))
}

// HandleServer manages the whole server. It starts the server and accepts connections.
// It handles each connection in a separate goroutine.
// It requires a client manager as a parameter.
func (cm *ClientManager) ManageServer(ctx context.Context) error {
	err := cm.startServer()
	if err != nil {
		return fmt.Errorf("failed to start server: %w", err)
	}
	defer cm.stopServer() // to stop the server after the function ends

	// infinite loop to accept connections
	for {
		select {

		// check if the context has been cancelled (ctrl+c to stop the server)
		case <-ctx.Done():
			return nil

		// server logic
		default:
			// handle games if any
			err := cm.manageLobbies()
			if err != nil {
				return fmt.Errorf("failed to manage lobbies: %w", err)
			}

			// try to accept a new connection
			conn, err := cm.pServer.AcceptConnection()
			if err != nil {
				// if the error is timeout (will be returned explicitly)
				var nErr net.Error
				if errors.As(err, &nErr) && nErr.Timeout() {
					continue
				}

				// else error is probably unrecoverable
				return fmt.Errorf("failed to accept connection: %w", err)
			}

			// handle each connection in a separate goroutine
			go func() {
				// TODO: Uncomment
				// // safety measure to recover from panics (exceptions)
				// defer func() {
				// 	if r := recover(); r != nil {
				// 		logging.Error(fmt.Sprintf("Recovered from panic in connection handler: %v", r))
				// 	}
				// }()

				cm.handleConnection(conn) // NOTE: feasible for hundreds of clients; for thousands of clients, a worker pool would be used
			}()
		}
	}
}
