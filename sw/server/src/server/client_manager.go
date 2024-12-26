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
	id       string
	player01 string
	player02 string
	rw_mutex sync.RWMutex
}

// Server represents a TCP server.
type ClientManager struct {
	pServer       *Server            // server pointer
	pendClients   map[string]*Client // map of pending clients with their addresses as keys
	authClients   map[string]*Client // map of authenticated clients with their nicknames as keys
	lobbies       map[string]*Lobby  // manage lobbies
	playerToLobby map[string]*Lobby  // map of players to their lobbies
	mutex         sync.Mutex         // mutex to lock the client manager
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

	cm.pServer.Start()
	return nil
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
	logging.Info(fmt.Sprintf("Client %s:%s has been authenticated", pClient.conn.RemoteAddr().String(), nickname))
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
	logging.Info(fmt.Sprintf("Client %s:%s has been removed", addr, nickname))
	return nil
}

// removePendingClient removes a pending client from the client manager.
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

	client, exists := cm.authClients[nickname]
	if !exists {
		return nil, fmt.Errorf("client not found")
	}

	return client, nil
}

// readCompleteMessage reads a message from the client.
func (cm *ClientManager) readCompleteMessage(pClient *Client) (*cmd_validator.IncomingMessage, error) {
	// sanity checks
	if pClient == nil {
		return nil, custom_errors.ErrNilPointer
	}
	if pClient.conn == nil {
		return nil, custom_errors.ErrNilConn
	}

	// try to read until a whole message is received
	fullMsgDeadline := time.Now().Add(protocol.CompleteMsgTimeout)
	msg := ""
	for {
		// handle timeout
		if time.Now().After(fullMsgDeadline) {
			return nil, fmt.Errorf("client did not send whole message in time")
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
			return nil, fmt.Errorf("failed to read message from client: %w", err)
		}
		msg += recv
		pClient.lastTime = time.Now()
	}

	// check if the message is a valid message
	parts, err := msg_parser.FromNetMessage(msg)
	if err != nil {
		return nil, fmt.Errorf("failed to parse message: %w", err)
	}

	// validate the message for generic format
	pCommand, err := cmd_validator.GetCommand(parts)
	if err != nil {
		return nil, fmt.Errorf("failed to extract valid command: %w", err)
	}

	return pCommand, nil
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
	parts := []string{protocol.CmdPing}
	err := cm.sendMessage(pClient.conn, parts)
	if err != nil {
		return false, fmt.Errorf("failed to send ping message: %w", err)
	}

	// read the pong message
	p_command, err := cm.readCompleteMessage(pClient)
	if err != nil {
		return false, fmt.Errorf("failed to read pong message: %w", err)
	}

	// check if the pong message is valid
	err = cmd_validator.ValidatePong(p_command)
	if err != nil {
		return false, fmt.Errorf("invalid pong message: %w", err)
	}

	return true, nil
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
	pValidMsg, err := cm.readCompleteMessage(pClient)
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
	pValidMsg, err = cm.readCompleteMessage(pClient)
	if err != nil {
		return "", fmt.Errorf("failed to read confirmation message: %w", err)
	}
	err = cmd_validator.ValidateHandshakeConfirmation(pValidMsg)
	if err != nil {
		return "", fmt.Errorf("invalid confirmation message: %w", err)
	}

	// authenticate the client
	cm.mutex.Lock()
	err = cm.authenticateClient(pClient, nickname)
	if err != nil {
		return "", fmt.Errorf("failed to authenticate client - code error: %w", err)
	}
	cm.mutex.Unlock()

	return nickname, nil
}

func (cm *ClientManager) handleConnection(conn net.Conn) {
	// TODO HERE
	logging.Debug(fmt.Sprintf("Handling connection from %s.", conn.RemoteAddr().String()))

	// add the client
	cm.mutex.Lock()
	pClient, err := cm.addClient(conn)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to add client: %v", err))
		return
	}
	cm.mutex.Unlock()

	// validate the connection
	nickname, err := cm.validateConnection(pClient)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to validate connection: %v", err))
		// remove the client
		cm.mutex.Lock()
		err = cm.removePendingClient(conn.RemoteAddr().String())
		if err != nil {
			logging.Error(fmt.Sprintf("failed to remove pending client: %v", err))
		}
		cm.mutex.Unlock()

		// close the connection
		err = conn.Close()
		if err != nil {
			logging.Error(fmt.Sprintf("failed to close connection: %v", err))
		}
		logging.Info(fmt.Sprintf("Client %s was disconnected", conn.RemoteAddr().String()))
		return
	}

	// infinite loop to handle messages
	for {
		// keep alive
		if time.Since(pClient.lastTime) > protocol.KeepAliveTimeout {
			alive, err := cm.checkAlive(pClient)
			if err != nil {
				logging.Error(fmt.Sprintf("failed to check if client is alive: %v", err))
				break
			}
			if !alive {
				logging.Info(fmt.Sprintf("Client %s is not alive", conn.RemoteAddr().String()))
				break
			}
		}

		// read message (busy waiting is prevented by the timeout)
		pCommand, err := cm.readCompleteMessage(pClient)
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

		// PLACEHOLDER: now just print the message
		logging.Debug(fmt.Sprintf("Received message from %s: %s", conn.RemoteAddr().String(), (*pCommand).ToString()))
		if (*pCommand).Command == protocol.CmdLeave {
			err = cm.sendMessage(conn, []string{protocol.CmdLeaveAck})
			if err != nil {
				logging.Error(fmt.Sprintf("failed to send leave ack: %v", err))
			}
			break // leave the loop (end the connection)
		}
	}

	// remove the client
	cm.mutex.Lock()
	err = cm.removeClient(nickname)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to remove client: %v", err))
	}
	cm.mutex.Unlock()

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
