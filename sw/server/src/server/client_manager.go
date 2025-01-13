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
	"math/rand"
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
	sendMu   sync.Mutex
	recvMu   sync.Mutex
}

// Lobby represents a game lobby.
type Lobby struct {
	id                  string
	player01            string
	player02            string
	state               uint8
	interruptTime       time.Time
	missingPlayer       string
	readyCount          uint8
	board               [protocol.BoardSize][protocol.BoardSize]int8
	priorInterruptState uint8
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

// boardToString converts a board to a string.
func boardToString(board [protocol.BoardSize][protocol.BoardSize]int8) string {
	var sb strings.Builder

	for i := 0; i < protocol.BoardSize; i++ {
		for j := 0; j < protocol.BoardSize; j++ {
			sb.WriteString(fmt.Sprintf("%d", board[i][j]))
			if j < protocol.BoardSize-1 {
				sb.WriteString(protocol.NumDelimiter)
			}
		}

		if i < protocol.BoardSize-1 {
			sb.WriteString("\n")
		}
	}

	return sb.String()
}

// boardToStringPlayer converts a board to a string for a player.
func boardToStringPlayer(board [protocol.BoardSize][protocol.BoardSize]int8, isPlayer01 bool) string {
	var sb strings.Builder

	for i := 0; i < protocol.BoardSize; i++ {
		for j := 0; j < protocol.BoardSize; j++ {
			cell := board[i][j]
			switch cell {
			case protocol.BoardCellBoat:
				sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellFree))

			case protocol.BoardCellPlayer01:
				if isPlayer01 {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellOwner))
				} else {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellFree))
				}

			case protocol.BoardCellPlayer02:
				if !isPlayer01 {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellOwner))
				} else {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellFree))
				}

			case protocol.BoardCellPlayer01Lost:
				if isPlayer01 {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellOwnerLost))
				} else {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellOpponentLost))
				}

			case protocol.BoardCellPlayer02Lost:
				if !isPlayer01 {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellOwnerLost))
				} else {
					sb.WriteString(fmt.Sprintf("%d", protocol.BoardCellOpponentLost))
				}

			default:
				sb.WriteString(fmt.Sprintf("%d", cell))
			}

			if j < protocol.BoardSize-1 {
				sb.WriteString(protocol.NumDelimiter)
			}
		}

		if i < protocol.BoardSize-1 {
			sb.WriteString(protocol.SeqDelimiter)
		}
	}

	return sb.String()
}

// getNighboursCount gets the count of neighbours of a cell.
func getNighboursCount(board [protocol.BoardSize][protocol.BoardSize]int8, row, col int) int {
	neighboursCount := 0
	if row > 0 && board[row-1][col] == protocol.BoardCellBoat {
		neighboursCount++
	}
	if row < protocol.BoardSize-1 && board[row+1][col] == protocol.BoardCellBoat {
		neighboursCount++
	}
	if col > 0 && board[row][col-1] == protocol.BoardCellBoat {
		neighboursCount++
	}
	if col < protocol.BoardSize-1 && board[row][col+1] == protocol.BoardCellBoat {
		neighboursCount++
	}

	return neighboursCount
}

// getInitialBoard generates a random board.
func getInitialBoard() [protocol.BoardSize][protocol.BoardSize]int8 {
	var board [protocol.BoardSize][protocol.BoardSize]int8
	retries := 0
	maxRetries := 1000
	placedFullBoats := make([][][2]int, 0)

	twoBoatsCount := rand.Intn(int(int(protocol.BoardBoatsCount/2)/2) + 1)
	for i := 0; i < twoBoatsCount; i++ {
		if retries > maxRetries {
			logging.Error(fmt.Sprintf("Failed to generate a board after %d retries", maxRetries))
			return board
		}

		row := rand.Intn(protocol.BoardSize)
		col := rand.Intn(protocol.BoardSize)
		// check if the boat is already placed
		if board[row][col] == protocol.BoardCellBoat {
			i--
			retries++
			continue
		}
		// check if neighbours are free
		possibleNeighboursCount := getNighboursCount(board, row, col)
		if possibleNeighboursCount != 0 {
			i--
			retries++
			continue
		}

		// get all possible placemets for the second part of the boat
		possiblePlacements := make([][2]int, 0)
		// left
		if col > 0 {
			possiblePlacements = append(possiblePlacements, [2]int{row, col - 1})
		}
		// right
		if col < protocol.BoardSize-1 {
			possiblePlacements = append(possiblePlacements, [2]int{row, col + 1})
		}
		// up
		if row > 0 {
			possiblePlacements = append(possiblePlacements, [2]int{row - 1, col})
		}
		// down
		if row < protocol.BoardSize-1 {
			possiblePlacements = append(possiblePlacements, [2]int{row + 1, col})
		}

		// shuffle the slice
		rand.Shuffle(len(possiblePlacements), func(i, j int) {
			possiblePlacements[i], possiblePlacements[j] = possiblePlacements[j], possiblePlacements[i]
		})

		// try to place the second part of the boat
		wasPlaced := false
		for _, placement := range possiblePlacements {
			possibleNeighboursCount := getNighboursCount(board, placement[0], placement[1])
			if possibleNeighboursCount == 0 {
				placed := make([][2]int, 0)
				board[row][col] = protocol.BoardCellBoat
				placed = append(placed, [2]int{row, col})
				board[placement[0]][placement[1]] = protocol.BoardCellBoat
				placed = append(placed, [2]int{placement[0], placement[1]})
				placedFullBoats = append(placedFullBoats, placed)
				wasPlaced = true
				break
			}
		}
		// try again with different starting position
		if !wasPlaced {
			i--
			retries++
			continue
		}
	}

	// place the rest of the boats
	for i := 0; i < protocol.BoardBoatsCount-(twoBoatsCount*2); i++ {
		if retries > maxRetries {
			logging.Error(fmt.Sprintf("Failed to generate a board after %d retries", maxRetries))
			return board
		}

		row := rand.Intn(protocol.BoardSize)
		col := rand.Intn(protocol.BoardSize)
		// check if the boat is already placed
		if board[row][col] == protocol.BoardCellBoat {
			i--
			retries++
			continue
		}
		// check if neighbours are free
		possibleNeighboursCount := getNighboursCount(board, row, col)
		if possibleNeighboursCount != 0 {
			i--
			retries++
			continue
		}

		board[row][col] = protocol.BoardCellBoat
		placed := make([][2]int, 0)
		placed = append(placed, [2]int{row, col})
		placedFullBoats = append(placedFullBoats, placed)
	}

	// place player01 boats
	randIndex := rand.Intn(len(placedFullBoats))
	player01Cells := placedFullBoats[randIndex]
	for _, cell := range player01Cells {
		board[cell[0]][cell[1]] = protocol.BoardCellPlayer01
	}
	// remove the placed boat
	placedFullBoats = append(placedFullBoats[:randIndex], placedFullBoats[randIndex+1:]...)

	// place player02 boats
	randIndex = rand.Intn(len(placedFullBoats))
	player02Cells := placedFullBoats[randIndex]
	for _, cell := range player02Cells {
		board[cell[0]][cell[1]] = protocol.BoardCellPlayer02
	}

	return board
}

// getGameStats gets the game statistics.
// It returns if the game has finished; if player01 has won; and an error if any.
// If error is returned the other two values are not defined.
func getGameStats(board [protocol.BoardSize][protocol.BoardSize]int8) (bool, bool, error) {
	player01Boats := 0
	player02Boats := 0
	freeBoatsCount := 0

	// check if the game has finished
	for i := 0; i < protocol.BoardSize; i++ {
		for j := 0; j < protocol.BoardSize; j++ {
			cell := board[i][j]
			if cell == protocol.BoardCellBoat {
				freeBoatsCount++
			}

			if cell == protocol.BoardCellPlayer01 {
				player01Boats++
			}

			if cell == protocol.BoardCellPlayer02 {
				player02Boats++
			}
		}
	}

	// check if the game has finished
	// if freeBoatsCount == 0 {
	// 	if player01Boats > player02Boats {
	// 		return true, true, nil
	// 	} else if player01Boats < player02Boats {
	// 		return true, false, nil
	// 	} else {
	// 		return true, false, errors.New("game has finished with a draw")
	// 	}
	// }
	if player01Boats == 0 && player02Boats == 0 {
		return true, false, errors.New("game has finished with a draw")
	}
	if player01Boats == 0 {
		return true, false, nil
	}
	if player02Boats == 0 {
		return true, true, nil
	}

	return false, false, nil
}

// shouldLobbyWait checks if the lobby can be switched to reconnecting state.
func shouldLobbyWait(lobby *Lobby) bool {
	doWait := true
	switch lobby.state {
	case protocol.LobbyStateFail:
		fallthrough
	case protocol.LobbyStateFinished:
		fallthrough
	case protocol.LobbyStateInterrupt:
		fallthrough
	case protocol.LobbyStateInterruptPending:
		fallthrough
	case protocol.LobbyStateInterrupted:
		doWait = false
	}

	return doWait
}

// readCompleteMessage reads a message from the client.
// It returns the parsed message, the raw string message, and an error.
// It involves socket I/O operations so it should be called with a lock.
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

// addPlayerToLobby adds a player to a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) addPlayerToLobby(nickname string, lobbyID string) error {
	// sanity check
	_, exists := cm.lobbies[lobbyID]
	if !exists {
		return fmt.Errorf("lobby not found")
	}

	// add the player to the lobby
	lobby := cm.lobbies[lobbyID]
	if lobby.player01 == "" {
		lobby.player01 = nickname
	} else if lobby.player02 == "" {
		lobby.player02 = nickname
	} else {
		return fmt.Errorf("lobby is full")
	}

	cm.playerToLobby[nickname] = lobby
	logging.Info(fmt.Sprintf("Player \"%s\" has been added to lobby \"%s\"", nickname, lobbyID))
	return nil
}

// kickPlayerFromLobby kicks a player from a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) kickPlayerFromLobby(nickname string) error {
	// sanity check
	lobby, exists := cm.playerToLobby[nickname]
	if !exists {
		logging.Critical(fmt.Sprintf("Cannot kick player \"%s\" from lobby \"%s\": player is not in a lobby", nickname, lobby.id))
		return fmt.Errorf("player is not in a lobby")
	}

	if lobby.player01 == nickname {
		lobby.player01 = ""
	} else if lobby.player02 == nickname {
		lobby.player02 = ""
	} else {
		logging.Critical(fmt.Sprintf("Cannot kick player \"%s\" from lobby \"%s\": player is not in the lobby (but was in lobbies map)", nickname, lobby.id))
		return fmt.Errorf("player is not in the lobby")
	}

	// change the lobby state
	lobby.state = protocol.LobbyStateFail

	delete(cm.playerToLobby, nickname)
	logging.Info(fmt.Sprintf("Player \"%s\" has been kicked from lobby \"%s\"", nickname, lobby.id))
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

// checkForPendingReconnect checks if a new connection is in a lobby pending reconnect state.
//
// WARNING: It reads a shared resource, so it should be called with a lock.
func (cm *ClientManager) checkForPendingReconnect(nickname string) bool {
	lobby, exists := cm.playerToLobby[nickname]
	if !exists {
		return false
	}

	isPending := false
	switch lobby.state {
	case protocol.LobbyStateInterrupt:
		fallthrough
	case protocol.LobbyStateInterruptPending:
		fallthrough
	case protocol.LobbyStateInterrupted:
		isPending = true
	}

	return isPending
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

// attemptMove attempts to make a move in a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) attemptMove(lobby *Lobby, nickname string, position []int) error {
	isPlayer01 := lobby.player01 == nickname

	targetCells := make([][2]int, 0)
	centerCell := lobby.board[position[0]][position[1]]
	switch centerCell {
	case protocol.BoardCellBoat:
		fallthrough
	case protocol.BoardCellPlayer01:
		fallthrough
	case protocol.BoardCellPlayer02:
		targetCells = append(targetCells, [2]int{position[0], position[1]})
	}

	if len(targetCells) != 0 {
		// check for neighbours
		if position[0] > 0 {
			toLeft := lobby.board[position[0]-1][position[1]]
			if toLeft == protocol.BoardCellBoat || toLeft == protocol.BoardCellPlayer01 || toLeft == protocol.BoardCellPlayer02 {
				targetCells = append(targetCells, [2]int{position[0] - 1, position[1]})
			}
		}
		if position[0] < protocol.BoardSize-1 {
			toRight := lobby.board[position[0]+1][position[1]]
			if toRight == protocol.BoardCellBoat || toRight == protocol.BoardCellPlayer01 || toRight == protocol.BoardCellPlayer02 {
				targetCells = append(targetCells, [2]int{position[0] + 1, position[1]})
			}
		}
		if position[1] > 0 {
			toUp := lobby.board[position[0]][position[1]-1]
			if toUp == protocol.BoardCellBoat || toUp == protocol.BoardCellPlayer01 || toUp == protocol.BoardCellPlayer02 {
				targetCells = append(targetCells, [2]int{position[0], position[1] - 1})
			}
		}
		if position[1] < protocol.BoardSize-1 {
			toDown := lobby.board[position[0]][position[1]+1]
			if toDown == protocol.BoardCellBoat || toDown == protocol.BoardCellPlayer01 || toDown == protocol.BoardCellPlayer02 {
				targetCells = append(targetCells, [2]int{position[0], position[1] + 1})
			}
		}
	}

	for _, targetCell := range targetCells {
		targetCellVal := lobby.board[targetCell[0]][targetCell[1]]
		switch targetCellVal {
		case protocol.BoardCellBoat:
			if isPlayer01 {
				lobby.board[targetCell[0]][targetCell[1]] = protocol.BoardCellPlayer01
			} else {
				lobby.board[targetCell[0]][targetCell[1]] = protocol.BoardCellPlayer02
			}

		case protocol.BoardCellPlayer01:
			if isPlayer01 {
				logging.Warn(fmt.Sprintf("Player \"%s\" tried to make a move on their own ship", nickname))
				return custom_errors.ErrInvalidMove
			}
			lobby.board[targetCell[0]][targetCell[1]] = protocol.BoardCellPlayer01Lost

		case protocol.BoardCellPlayer02:
			if !isPlayer01 {
				logging.Warn(fmt.Sprintf("Player \"%s\" tried to make a move on their own ship", nickname))
				return custom_errors.ErrInvalidMove
			}
			lobby.board[targetCell[0]][targetCell[1]] = protocol.BoardCellPlayer02Lost

		case protocol.BoardCellPlayer01Lost, protocol.BoardCellPlayer02Lost:
			logging.Warn(fmt.Sprintf("Player \"%s\" tried to make a move on a sank ship", nickname))
			return custom_errors.ErrInvalidMove
		}
	}

	logging.Debug(fmt.Sprintf("Player \"%s\" made a move in lobby \"%s\"", nickname, lobby.id))

	// update the lobby state
	if isPlayer01 {
		lobby.state = protocol.LobbyStatePlayer01Played
	} else {
		lobby.state = protocol.LobbyStatePlayer02Played
	}

	return nil
}

// sendMessage sends a message to the client.
// It involves socket I/O operations so it should be called with a lock.
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
		logging.Error(fmt.Sprintf("Failed to send message: %v", err))
		return custom_errors.ErrSendMsg
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
	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
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
	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
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
	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
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

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		return fmt.Errorf("failed to send lobby list: %w", err)
	}

	return nil
}

// sendLobbyAck sends a create lobby acknowledgment message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendLobbyAck(pClient *Client, lobbyID string) error {
	// send the create lobby acknowledgment message
	parts := []string{protocol.CmdCreateLobbyAck, lobbyID}

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
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

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
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

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		return fmt.Errorf("failed to send paired message: %w", err)
	}

	return nil
}

// sendBoard sends a board to the client.
func (cm *ClientManager) sendBoard(pClient *Client, board string, errChan chan error) error {
	// send the board
	parts := []string{protocol.CmdBoard, board}

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		if errChan != nil {
			errChan <- fmt.Errorf("failed to send board: %w", err)
		}
		return fmt.Errorf("failed to send board: %w", err)
	}

	if errChan != nil {
		errChan <- nil
	}
	return nil
}

// sendGameEndMsg sends a game end message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendGameEndMsg(pClient *Client, isWinner bool, errChan chan error) error {
	// send the game end message
	var parts []string
	if isWinner {
		parts = []string{protocol.CmdWin}
	} else {
		parts = []string{protocol.CmdLose}
	}

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		if errChan != nil {
			errChan <- fmt.Errorf("failed to send game end message: %w", err)
		}
		return fmt.Errorf("failed to send game end message: %w", err)
	}

	if errChan != nil {
		errChan <- nil
	}
	return nil
}

// sendWaitMsg sends a wait message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendWaitMsg(pClient *Client, errChan chan error) error {
	// send the wait message
	parts := []string{protocol.CmdWait}

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		if errChan != nil {
			errChan <- fmt.Errorf("failed to send wait message: %w", err)
		}
		return fmt.Errorf("failed to send wait message: %w", err)
	}

	if errChan != nil {
		errChan <- nil
	}
	return nil
}

// sendContinueMsg sends a continue message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendContinueMsg(pClient *Client, lobbyID string, opponent string, playerOnTurn string, board string, errChan chan error) error {
	// send the continue message
	parts := []string{protocol.CmdContinue, lobbyID, opponent, playerOnTurn, board}

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		if errChan != nil {
			errChan <- fmt.Errorf("failed to send continue message: %w", err)
		}
		return fmt.Errorf("failed to send continue message: %w", err)
	}

	if errChan != nil {
		errChan <- nil
	}
	return nil
}

// handlePingCmd sends a pong message to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handlePingCmd(pClient *Client) (bool, error) {
	// send the pong message
	parts := []string{protocol.CmdPong}

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		return false, fmt.Errorf("failed to send pong message: %w", err)
	}

	return true, nil
}

// handleLeaveCmd sends a leave acknowledgment message to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleLeaveCmd(pClient *Client) (bool, error) {
	// send the leave acknowledgment message
	parts := []string{protocol.CmdLeaveAck}

	pClient.sendMu.Lock()
	err := cm.sendMessage(pClient.conn, parts)
	pClient.sendMu.Unlock()
	if err != nil {
		return false, fmt.Errorf("failed to send leave acknowledgment message: %w", err)
	}

	// if the player is in a lobby, send a TKO message to the opponent if necessary
	cm.rwMutex.RLock()
	_, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		cm.rwMutex.Lock()
		cm.kickPlayerFromLobby(pClient.nickname)
		cm.rwMutex.Unlock()
	}

	return false, nil
}

// handleLobbiesCmd sends a list of lobbies to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleLobbiesCmd(pClient *Client) (bool, error) {
	// player must be in idle state (not in a lobby)
	cm.rwMutex.RLock()
	_, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		cm.rwMutex.Lock()
		cm.kickPlayerFromLobby(pClient.nickname)
		cm.rwMutex.Unlock()
		return false, custom_errors.ErrPlayerNotIdle
	}

	lobbies := make([]string, 0)

	// get the list of lobbies
	cm.rwMutex.RLock()
	for _, lobby := range cm.lobbies {
		if lobby.state == protocol.LobbyStateWaiting {
			lobbies = append(lobbies, lobby.id)
		}
	}
	cm.rwMutex.RUnlock()

	// send the list of lobbies to the client
	err := cm.sendLobbies(pClient, lobbies)
	if err != nil {
		return false, fmt.Errorf("failed to send lobby list: %w", err)
	}

	return true, nil
}

// handleCreateLobbyCmd creates a new lobby and sends the lobby ID to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleCreateLobbyCmd(pClient *Client) (bool, error) {
	// player must be in idle state (not in a lobby)
	cm.rwMutex.RLock()
	_, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		cm.rwMutex.Lock()
		cm.kickPlayerFromLobby(pClient.nickname)
		cm.rwMutex.Unlock()
		return false, custom_errors.ErrPlayerNotIdle
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
	err := cm.sendLobbyAck(pClient, lobbyID)
	if err != nil {
		cm.rwMutex.Lock()
		cm.lobbies[lobbyID].state = protocol.LobbyStateFail
		cm.rwMutex.Unlock()
		return false, fmt.Errorf("failed to send create lobby acknowledgment: %w", err)
	}

	cm.rwMutex.Lock()
	cm.lobbies[lobbyID].state = protocol.LobbyStateWaiting
	cm.rwMutex.Unlock()

	return true, nil
}

// handleJoinLobbyCmd attempts to connect the client to a lobby.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleJoinLobbyCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) (bool, error) {
	// sanity check
	lobbyID, err := cmd_validator.ParseJoinLobbyCmd(pCommand)
	if err != nil {
		logging.Warn(fmt.Sprintf("invalid join lobby message: %v", err))
		return false, custom_errors.ErrInvalidCommand
	}

	// player must be in idle state (not in a lobby)
	cm.rwMutex.RLock()
	_, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if exists {
		cm.rwMutex.Lock()
		cm.kickPlayerFromLobby(pClient.nickname)
		cm.rwMutex.Unlock()
		return false, custom_errors.ErrPlayerNotIdle
	}

	// check if the lobby exists
	cm.rwMutex.RLock()
	lobby, exists := cm.lobbies[lobbyID]
	cm.rwMutex.RUnlock()
	if !exists {
		return false, custom_errors.ErrLobbyNotFound
	}

	// check if the lobby is full
	if lobby.player01 != "" && lobby.player02 != "" {
		return true, custom_errors.ErrLobbyFull
	}

	// check if the lobby is in the correct state
	cm.rwMutex.RLock()
	failed := lobby.state != protocol.LobbyStateWaiting
	cm.rwMutex.RUnlock()
	if failed {
		return true, errors.New("lobby is not in the correct state")
	}

	// add the player to the lobby
	cm.rwMutex.Lock()
	err = cm.addPlayerToLobby(pClient.nickname, lobbyID)
	if err != nil {
		cm.rwMutex.Unlock()
		return false, fmt.Errorf("failed to add player to lobby: %w", err)
	}

	// NOTE: bandage fix but might cause delay for others - lobby change
	// 		 is handled in other goroutine so it needs to be synchronized (locked)
	// 		 to prevent race conditions with other clients
	err = cm.sendLobbyAck(pClient, lobbyID)
	if err != nil {
		cm.kickPlayerFromLobby(pClient.nickname)
		cm.rwMutex.Unlock()
		return false, fmt.Errorf("failed to send join lobby acknowledgment: %w", err)
	}

	// change the lobby state
	lobby.state = protocol.LobbyStatePaired
	cm.rwMutex.Unlock()

	return true, nil
}

// handleClientReadyCmd handles a client ready message.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleClientReadyCmd(pClient *Client) (bool, error) {
	// player must be in a lobby
	cm.rwMutex.RLock()
	lobby, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if !exists {
		return false, custom_errors.ErrPlayerNotIdle
	}

	// lobby must be unready
	cm.rwMutex.RLock()
	retFlag := lobby.state != protocol.LobbyStateUnready || lobby.readyCount >= protocol.PlayerCount
	cm.rwMutex.RUnlock()
	if retFlag {
		return false, errors.New("lobby is not in the correct state")
	}

	// increase the ready count
	cm.rwMutex.Lock()
	lobby.readyCount++
	cm.rwMutex.Unlock()

	return true, nil
}

// handleActionCmd handles an action message.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleActionCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) (bool, error) {
	// player must be in a lobby
	cm.rwMutex.RLock()
	lobby, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if !exists {
		return false, custom_errors.ErrPlayerNotIdle
	}

	// figure out if its the player's turn
	playerNick := pClient.nickname
	cm.rwMutex.RLock()
	switch lobby.state {
	case protocol.LobbyStatePlayer01Playing:
		if playerNick != lobby.player01 {
			return true, custom_errors.ErrNotPlayerTurn
		}
	case protocol.LobbyStatePlayer02Playing:
		if playerNick != lobby.player02 {
			return true, custom_errors.ErrNotPlayerTurn
		}
	case protocol.LobbyStateInterrupt:
		logging.Warn(fmt.Sprintf("Player \"%s\" tried to make a move in an interrupted lobby", playerNick))
		return true, nil
	default:
		logging.Critical(fmt.Sprintf("Lobby \"%s\" is in an invalid state: %d", lobby.id, lobby.state))
		cm.rwMutex.RUnlock()
		cm.rwMutex.Lock()
		cm.kickPlayerFromLobby(playerNick)
		cm.rwMutex.Unlock()

		return false, errors.New("lobby is not in the correct state")
	}
	cm.rwMutex.RUnlock()

	// parse the action message
	position, err := cmd_validator.ParseActionCmd(pCommand)
	if err != nil {
		logging.Warn(fmt.Sprintf("invalid action message: %v", err))
		cm.rwMutex.Lock()
		cm.kickPlayerFromLobby(playerNick)
		cm.rwMutex.Unlock()
		return false, custom_errors.ErrInvalidCommand
	}

	// attempt to make a move
	cm.rwMutex.Lock()
	err = cm.attemptMove(lobby, pClient.nickname, position)
	cm.rwMutex.Unlock()
	if err != nil {
		cm.rwMutex.Lock()
		cm.kickPlayerFromLobby(playerNick)
		cm.rwMutex.Unlock()
		return false, fmt.Errorf("failed to make a move: %w", err)
	}

	return true, nil
}

// handleWaitingCmd handles a waiting message.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleWaitingCmd(pClient *Client) (bool, error) {
	// player must be in a lobby
	cm.rwMutex.RLock()
	lobby, exists := cm.playerToLobby[pClient.nickname]
	cm.rwMutex.RUnlock()
	if !exists {
		return false, custom_errors.ErrLobbyNotFound
	}

	// lobby must be in the correct state
	cm.rwMutex.RLock()
	retFlag := lobby.state != protocol.LobbyStateInterruptPending
	cm.rwMutex.RUnlock()
	if retFlag {
		return false, errors.New("lobby is not in the correct state")
	}

	// change the lobby state
	cm.rwMutex.Lock()
	lobby.state = protocol.LobbyStateInterrupted
	cm.rwMutex.Unlock()

	return true, nil
}

// checkAlive checks if the client is alive by sending a ping message and waiting for a pong message.
// Returns true if the client is alive, false otherwise. Returns an error if any.
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
	pClient.recvMu.Lock()
	pCommand, rawMsg, err := cm.readCompleteMessage(pClient)
	pClient.recvMu.Unlock()
	if err != nil {
		return false, fmt.Errorf("failed to read pong response: %w", err)
	}

	// check if the pong message is valid
	var tryAgain bool = false
	if pCommand.Command != protocol.CmdPong {
		// if another message is received, buffer it and await the pong message
		logging.Info(fmt.Sprintf("Another message received (%s), buffering it and awaiting pong message", escapeSpecialSymbols(rawMsg)))
		tryAgain = true
	}

	// some other message managed to get through earlier so try again
	if tryAgain {
		// read the pong message
		pClient.recvMu.Lock()
		pCommand, _, err := cm.readCompleteMessage(pClient)
		pClient.recvMu.Unlock()
		if err != nil {
			return false, fmt.Errorf("failed to read pong message: %w", err)
		}

		pClient.msgBuff += rawMsg

		// check if the pong message is valid
		if pCommand.Command != protocol.CmdPong {
			return false, fmt.Errorf("invalid pong message: %s", pCommand.ToString())
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
	pClient.recvMu.Lock()
	pValidMsg, _, err := cm.readCompleteMessage(pClient)
	pClient.recvMu.Unlock()
	if err != nil {
		return "", fmt.Errorf("failed to read handshake message: %w", err)
	}
	nickname, err := cmd_validator.ParseHandshakeCmd(pValidMsg)
	if err != nil {
		return "", fmt.Errorf("invalid handshake message: %w", err)
	}

	// check if the nickname is already taken
	cm.rwMutex.RLock()
	_, exists := cm.authClients[nickname]
	cm.rwMutex.RUnlock()
	if exists {
		return "", fmt.Errorf("nickname is already taken")
	}

	// send the handshake reply
	err = cm.sendHandshakeReply(pClient)
	if err != nil {
		return "", fmt.Errorf("failed to send handshake reply: %w", err)
	}

	// await confirmation
	pClient.recvMu.Lock()
	pValidMsg, _, err = cm.readCompleteMessage(pClient)
	pClient.recvMu.Unlock()
	if err != nil {
		return "", fmt.Errorf("failed to read confirmation message: %w", err)
	}
	if pValidMsg.Command != protocol.CmdHandshakeAck {
		return "", fmt.Errorf("invalid confirmation message: %s", pValidMsg.ToString())
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

// getMissingPlayerNickname returns the nickname of the missing player in a lobby.
// Expects the lobby to be valid.
//
// WARNING: It reads a shared resource, so it should be called with a rlock.
func (cm *ClientManager) getMissingPlayerNickname(lobby *Lobby) string {
	var missingPlayerNickname string = ""
	_, exists := cm.authClients[lobby.player01]
	if !exists {
		missingPlayerNickname = lobby.player01
	}

	_, exists = cm.authClients[lobby.player02]
	if !exists {
		if missingPlayerNickname != "" {
			logging.Error(fmt.Sprintf("There is a discrepancy in lobby \"%s\": both players are missing", lobby.id))
		}
		missingPlayerNickname = lobby.player02
	}

	return missingPlayerNickname
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

	// initialize the board
	lobby.board = getInitialBoard()
	logging.Debug(fmt.Sprintf("Initial board for lobby %s:\n%s", lobby.id, boardToString(lobby.board)))

	// start the game
	lobby.state = protocol.LobbyStatePlayer02Played
	lobby.readyCount = uint8(0)

	return nil
}

func (cm *ClientManager) informMoves(lobby *Lobby) error {
	// sanity checks
	if lobby == nil {
		return custom_errors.ErrNilPointer
	}
	if lobby.state != protocol.LobbyStatePlayer01Played && lobby.state != protocol.LobbyStatePlayer02Played {
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

	player01Board := boardToStringPlayer(lobby.board, true)
	player02Board := boardToStringPlayer(lobby.board, false)

	// send the move message to the players
	errChan := make(chan error, int(protocol.PlayerCount))
	go cm.sendBoard(pClientPlayer01, player01Board, errChan)
	go cm.sendBoard(pClientPlayer02, player02Board, errChan)
	var err error
	for i := 0; i < int(protocol.PlayerCount); i++ {
		err = <-errChan
		if err != nil {
			return fmt.Errorf("failed to send move message: %w", err)
		}
	}

	// change the lobby state
	if lobby.state == protocol.LobbyStatePlayer01Played {
		lobby.state = protocol.LobbyStatePlayer02Turn
	} else {
		lobby.state = protocol.LobbyStatePlayer01Turn
	}

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

	// prepare sync channel for errors
	errChan := make(chan error, int(protocol.PlayerCount))

	// check if the game is hasFinished
	hasFinished, isPlayer01Winner, err := getGameStats(lobby.board)
	if err != nil {
		return fmt.Errorf("failed to get game stats: %w", err)
	}

	if hasFinished {
		// send the game over message to the players
		go cm.sendGameEndMsg(pClientPlayer01, isPlayer01Winner, errChan)
		go cm.sendGameEndMsg(pClientPlayer02, !isPlayer01Winner, errChan)
		for i := 0; i < int(protocol.PlayerCount); i++ {
			err = <-errChan
			if err != nil {
				return fmt.Errorf("failed to send game over message: %w", err)
			}
		}

		// change the lobby state
		lobby.state = protocol.LobbyStateFinished

	} else {
		// send the turn message to the players
		go cm.sendTurnMsg(pClientPlayer01, playerOnTurn, errChan)
		go cm.sendTurnMsg(pClientPlayer02, playerOnTurn, errChan)
		for i := 0; i < int(protocol.PlayerCount); i++ {
			err = <-errChan
			if err != nil {
				return fmt.Errorf("failed to send turn message: %w", err)
			}
		}

		// change the lobby state
		if lobby.state == protocol.LobbyStatePlayer01Turn {
			lobby.state = protocol.LobbyStatePlayer01Playing
		} else {
			lobby.state = protocol.LobbyStatePlayer02Playing
		}
	}

	return nil
}

// pauseLobby pauses a lobby and sends wait messages to the players.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) pauseLobby(lobby *Lobby) error {
	// sanity checks
	if lobby == nil {
		return custom_errors.ErrNilPointer
	}
	if lobby.state != protocol.LobbyStateInterrupt {
		return fmt.Errorf("lobby is not in the correct state")
	}

	// send the other plater wait msg
	pClientPlayer01, p01Exists := cm.authClients[lobby.player01]
	pClientPlayer02, p02Exists := cm.authClients[lobby.player02]
	if lobby.player01 != lobby.missingPlayer {
		if !p01Exists {
			lobby.state = protocol.LobbyStateFail
			return fmt.Errorf("player 01: %s not found for lobby %s", lobby.player01, lobby.id)
		}
		err := cm.sendWaitMsg(pClientPlayer01, nil)
		if err != nil {
			lobby.state = protocol.LobbyStateFail
			return fmt.Errorf("failed to send wait message to player 01: %w", err)
		}
	} else if lobby.player02 != lobby.missingPlayer {
		if !p02Exists {
			lobby.state = protocol.LobbyStateFail
			return fmt.Errorf("player 02: %s not found for lobby %s", lobby.player02, lobby.id)
		}
		err := cm.sendWaitMsg(pClientPlayer02, nil)
		if err != nil {
			lobby.state = protocol.LobbyStateFail
			return fmt.Errorf("failed to send wait message to player 02: %w", err)
		}
	} else {
		lobby.state = protocol.LobbyStateFail
		return fmt.Errorf("missing player not found in lobby %s", lobby.id)
	}

	// change the lobby state
	lobby.state = protocol.LobbyStateInterruptPending
	return nil
}

// handleLobbyInterrupted handles a lobby in the waiting state.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) handleLobbyInterrupted(lobby *Lobby) error {
	// sanity checks
	if lobby == nil {
		return custom_errors.ErrNilPointer
	}
	if lobby.state != protocol.LobbyStateInterrupted {
		return fmt.Errorf("lobby is not in the correct state")
	}

	// check how long the lobby has been waiting
	if time.Since(lobby.interruptTime) > protocol.PlayerReconnectTimeout {
		// get the missing player nickname
		missingPlayerNickname := cm.getMissingPlayerNickname(lobby)
		cm.kickPlayerFromLobby(missingPlayerNickname)
		lobby.state = protocol.LobbyStateFail
	}

	return nil
}

// handleLobbyContinue handles a lobby in the waiting state.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) handleLobbyContinue(lobby *Lobby) error {
	// sanity checks
	if lobby == nil {
		return custom_errors.ErrNilPointer
	}
	if lobby.state != protocol.LobbyStateContinue {
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

	// get the last player on turn
	var playerOnTurn string
	var isPlayer01OnTurn bool
	switch lobby.priorInterruptState {
	case protocol.LobbyStatePlayer01Turn:
		fallthrough
	case protocol.LobbyStatePlayer01Played:
		fallthrough
	case protocol.LobbyStatePlayer01Playing:
		playerOnTurn = pClientPlayer01.nickname
		isPlayer01OnTurn = true
	case protocol.LobbyStatePlayer02Turn:
		fallthrough
	case protocol.LobbyStatePlayer02Played:
		fallthrough
	case protocol.LobbyStatePlayer02Playing:
		playerOnTurn = pClientPlayer02.nickname
		isPlayer01OnTurn = false
	default:
		lobby.state = protocol.LobbyStateFail
		return fmt.Errorf("invalid prior interrupt state: %d", lobby.priorInterruptState)
	}

	player01Board := boardToStringPlayer(lobby.board, true)
	player02Board := boardToStringPlayer(lobby.board, false)

	// send the game start message to the players
	errChan := make(chan error, int(protocol.PlayerCount))
	go cm.sendContinueMsg(pClientPlayer01, lobby.id, lobby.player02, playerOnTurn, player01Board, errChan)
	go cm.sendContinueMsg(pClientPlayer02, lobby.id, lobby.player01, playerOnTurn, player02Board, errChan)
	var err error
	for i := 0; i < int(protocol.PlayerCount); i++ {
		err = <-errChan
		if err != nil {
			lobby.state = protocol.LobbyStateFail
			return fmt.Errorf("failed to send continue message: %w", err)
		}
	}

	// change the lobby state
	if isPlayer01OnTurn {
		lobby.state = protocol.LobbyStatePlayer01Turn
	} else {
		lobby.state = protocol.LobbyStatePlayer02Turn
	}

	return nil
}

// getLobbyStates gets the states of the lobbies and appends the lobby IDs to the corresponding slices.
//
// WARNING: It reads a shared resource, so it should be called with a rlock.
func (cm *ClientManager) getLobbyStates(
	lobbiesToDelete *[]string,
	lobbiesToPrepare *[]string,
	lobbiesToStart *[]string,
	lobbiesToFeedbackPlayers *[]string,
	lobbiesToAdvance *[]string,
	lobbiesToInterrupt *[]string,
	lobbiesInterrupted *[]string,
	lobbiesToContinue *[]string) {

	for _, lobby := range cm.lobbies {
		// handle the game
		switch lobby.state {
		case protocol.LobbyStateFail:
			fallthrough
		case protocol.LobbyStateFinished:
			*lobbiesToDelete = append(*lobbiesToDelete, lobby.id)

		case protocol.LobbyStatePaired:
			*lobbiesToPrepare = append(*lobbiesToPrepare, lobby.id)

		case protocol.LobbyStateUnready:
			if lobby.readyCount == protocol.PlayerCount {
				*lobbiesToStart = append(*lobbiesToStart, lobby.id)
			}

		case protocol.LobbyStatePlayer01Played, protocol.LobbyStatePlayer02Played:
			*lobbiesToFeedbackPlayers = append(*lobbiesToFeedbackPlayers, lobby.id)

		case protocol.LobbyStatePlayer01Turn, protocol.LobbyStatePlayer02Turn:
			*lobbiesToAdvance = append(*lobbiesToAdvance, lobby.id)

		case protocol.LobbyStateInterrupt:
			*lobbiesToInterrupt = append(*lobbiesToInterrupt, lobby.id)

		case protocol.LobbyStateInterrupted:
			*lobbiesInterrupted = append(*lobbiesInterrupted, lobby.id)

		case protocol.LobbyStateContinue:
			*lobbiesToContinue = append(*lobbiesToContinue, lobby.id)
		}
	}
}

// manageLobbiesToDelete handles the lobbies that need to be deleted.
func (cm *ClientManager) manageLobbiesToDelete(lobbiesToDelete []string) {
	for _, lobbyID := range lobbiesToDelete {
		cm.rwMutex.Lock()
		err := cm.handleDeleteLobby(lobbyID)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Error(fmt.Sprintf("failed to delete lobby %s: %v", lobbyID, err))
		}
	}
}

// manageLobbiesToPrepare handles the lobbies that need to be prepared.
func (cm *ClientManager) manageLobbiesToPrepare(lobbiesToPrepare []string) {
	for _, lobbyID := range lobbiesToPrepare {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}
		cm.rwMutex.Lock()
		err := cm.prepareGame(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to prepare game in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}
}

// manageLobbiesToStart handles the lobbies that need to be started.
func (cm *ClientManager) manageLobbiesToStart(lobbiesToStart []string) {
	for _, lobbyID := range lobbiesToStart {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.Lock()
		err := cm.startGame(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to start game in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}
}

// manageLobbiesToFeedback handles the lobbies that need to inform the players about the moves.
func (cm *ClientManager) manageLobbiesToFeedback(lobbiesToFeedbackPlayers []string) {
	for _, lobbyID := range lobbiesToFeedbackPlayers {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.Lock()
		err := cm.informMoves(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to inform players in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}
}

// manageLobbiesToAdvance handles the lobbies to advance.
func (cm *ClientManager) manageLobbiesToAdvance(lobbiesToAdvance []string) {
	for _, lobbyID := range lobbiesToAdvance {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.Lock()
		err := cm.advanceGame(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to advance game in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}
}

// manageLobbiesToInterrupt handles the lobbies to interrupt.
func (cm *ClientManager) manageLobbiesToInterrupt(lobbiesToInterrupt []string) {
	for _, lobbyID := range lobbiesToInterrupt {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.Lock()
		err := cm.pauseLobby(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to pause lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
		}
	}
}

// manageLobbiesInterrupted handles the interrupted lobbies.
func (cm *ClientManager) manageLobbiesInterrupted(lobbiesReconnecting []string) {
	for _, lobbyID := range lobbiesReconnecting {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.Lock()
		err := cm.handleLobbyInterrupted(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to handle wait in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
			continue
		}
	}
}

// manageLobbiesToContinue handles the lobbies that need to continue.
func (cm *ClientManager) manageLobbiesToContinue(lobbiesToContinue []string) {
	for _, lobbyID := range lobbiesToContinue {
		cm.rwMutex.RLock()
		lobby, exists := cm.lobbies[lobbyID]
		cm.rwMutex.RUnlock()
		if !exists {
			logging.Error(fmt.Sprintf("Lobby %s not found", lobbyID))
			continue
		}

		cm.rwMutex.Lock()
		err := cm.handleLobbyContinue(lobby)
		cm.rwMutex.Unlock()
		if err != nil {
			logging.Warn(fmt.Sprintf("failed to handle continue in lobby %s: %v", lobbyID, err))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
			continue
		}
	}
}

// manageLobbies handles the games.
func (cm *ClientManager) manageLobbies() {
	var lobbiesToDelete []string
	var lobbiesToPrepare []string
	var lobbiesToStart []string
	var lobbiesToFeedbackPlayers []string
	var lobbiesToAdvance []string
	var lobbiesToInterrupt []string
	var lobbiesInterrupted []string
	var lobbiesToContinue []string

	cm.rwMutex.RLock()
	cm.getLobbyStates(
		&lobbiesToDelete,
		&lobbiesToPrepare,
		&lobbiesToStart,
		&lobbiesToFeedbackPlayers,
		&lobbiesToAdvance,
		&lobbiesToInterrupt,
		&lobbiesInterrupted,
		&lobbiesToContinue)
	cm.rwMutex.RUnlock()

	cm.manageLobbiesToDelete(lobbiesToDelete)
	cm.manageLobbiesToPrepare(lobbiesToPrepare)
	cm.manageLobbiesToStart(lobbiesToStart)
	cm.manageLobbiesToFeedback(lobbiesToFeedbackPlayers)
	cm.manageLobbiesToAdvance(lobbiesToAdvance)
	cm.manageLobbiesToInterrupt(lobbiesToInterrupt)
	cm.manageLobbiesInterrupted(lobbiesInterrupted)
	cm.manageLobbiesToContinue(lobbiesToContinue)
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
	var stayConnected bool = true

	// handle the command
	switch pCommand.Command {

	// universal commands
	case protocol.CmdPing:
		stayConnected, err = cm.handlePingCmd(pClient)

	case protocol.CmdLeave:
		logging.Info(fmt.Sprintf("Client %s - %s has requested to leave.", pClient.conn.RemoteAddr().String(), pClient.nickname))
		stayConnected, err = cm.handleLeaveCmd(pClient)

	// idle commands
	case protocol.CmdLobbies:
		stayConnected, err = cm.handleLobbiesCmd(pClient)

	case protocol.CmdCreateLobby:
		stayConnected, err = cm.handleCreateLobbyCmd(pClient)

	case protocol.CmdJoinLobby:
		stayConnected, err = cm.handleJoinLobbyCmd(pClient, pCommand)

	// in lobby commands
	case protocol.CmdClientReady:
		stayConnected, err = cm.handleClientReadyCmd(pClient)

	// game session commands
	case protocol.CmdAction:
		stayConnected, err = cm.handleActionCmd(pClient, pCommand)

	case protocol.CmdWaiting:
		stayConnected, err = cm.handleWaitingCmd(pClient)

	default:
		err = fmt.Errorf("unknown command: %s", pCommand.Command)
		stayConnected = false
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

	cm.rwMutex.RLock()
	isPendingReconnect := cm.checkForPendingReconnect(nickname)
	cm.rwMutex.RUnlock()
	if isPendingReconnect {
		logging.Info(fmt.Sprintf("Client %s has reconnected", nickname))
		isValidState := false
		reconnectFail := false
		var pLobby *Lobby = nil
		var exists bool = false

		// wait for valid state
		for {
			if isValidState {
				break
			}

			cm.rwMutex.RLock()
			pLobby, exists = cm.playerToLobby[nickname]
			cm.rwMutex.RUnlock()
			if !exists {
				logging.Error(fmt.Sprintf("Lobby not found for player %s", nickname))
				reconnectFail = true
				break
			}

			cm.rwMutex.RLock()
			isValidState = pLobby.state == protocol.LobbyStateInterrupted
			cm.rwMutex.RUnlock()
		}

		// reconnect
		if !reconnectFail {
			cm.rwMutex.Lock()
			pLobby.missingPlayer = ""
			pLobby.state = protocol.LobbyStateContinue
			cm.rwMutex.Unlock()
		}
	}

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
		pClient.recvMu.Lock()
		pCommand, _, err := cm.readCompleteMessage(pClient)
		pClient.recvMu.Unlock()
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
		doWait := shouldLobbyWait(lobby)
		cm.rwMutex.RUnlock()
		if doWait {
			logging.Info(fmt.Sprintf("Client abruptly disconnected from lobby %s. State changed to interrupt.", lobby.id))
			cm.rwMutex.Lock()
			lobby.priorInterruptState = lobby.state
			lobby.state = protocol.LobbyStateInterrupt
			lobby.missingPlayer = nickname
			lobby.interruptTime = time.Now()
			cm.rwMutex.Unlock()
		} else {
			logging.Info(fmt.Sprintf("Client %s has abruptly disconnected from one player lobby \"%s\". Marking lobby for deletion.", nickname, lobby.id))
			cm.rwMutex.Lock()
			lobby.state = protocol.LobbyStateFail
			cm.rwMutex.Unlock()
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
			cm.manageLobbies()

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
