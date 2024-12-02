package server

import (
	"context"
	"errors"
	"fmt"
	"inverse-battleships-server/const/protocol"
	"inverse-battleships-server/logging"
	"inverse-battleships-server/util/cmd_validator"
	"inverse-battleships-server/util/msg_parser"
	"io"
	"net"
	"sync"
	"time"
)

// Client represents a TCP client.
type Client struct {
	conn     net.Conn
	nickname string
	lastTime time.Time
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
	p_server      *Server            // server pointer
	clients       map[string]*Client // map of clients with their addresses as keys
	lobbies       map[string]*Lobby  // manage lobbies
	playerToLobby map[string]*Lobby  // map of players to their lobbies
	mutex         sync.Mutex         // mutex to lock the client manager
}

// NewClientManager creates a new ClientManager.
// It requires a server pointer as a parameter.
func NewClientManager(server *Server) *ClientManager {
	return &ClientManager{
		p_server:      server,
		clients:       make(map[string]*Client),
		lobbies:       make(map[string]*Lobby),
		playerToLobby: make(map[string]*Lobby),
	}
}

// startServer starts the TCP server.
func (cm *ClientManager) startServer() error {
	// sanity check
	if cm.p_server == nil {
		return fmt.Errorf("server is nil")
	}

	cm.p_server.Start()
	return nil
}

// stopServer stops the TCP server.
func (cm *ClientManager) stopServer() error {
	// sanity check
	if cm.p_server == nil {
		return fmt.Errorf("server is nil")
	}

	cm.p_server.Stop()
	return nil
}

// addClient adds a new client to the client manager.
func (cm *ClientManager) addClient(conn net.Conn, nickname string) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	client := &Client{
		conn:     conn,
		lastTime: time.Now(),
	}

	cm.clients[nickname] = client
	logging.Info(fmt.Sprintf("Client %s:%s has been added", conn.RemoteAddr().String(), nickname))
	return nil
}

// removeClient removes a client from the client manager.
func (cm *ClientManager) removeClient(nickname string) error {
	// sanity check
	if nickname == "" {
		return fmt.Errorf("nickname is empty")
	}
	_, exists := cm.clients[nickname]
	if !exists {
		return fmt.Errorf("client not found")
	}

	addr := cm.clients[nickname].conn.RemoteAddr().String()
	delete(cm.clients, nickname)
	logging.Info(fmt.Sprintf("Client %s:%s has been removed", addr, nickname))
	return nil
}

// getClient returns a client from the client manager.
func (cm *ClientManager) getClient(nickname string) (*Client, error) {
	// sanity check
	if nickname == "" {
		return nil, fmt.Errorf("nickname is empty")
	}

	client, exists := cm.clients[nickname]
	if !exists {
		return nil, fmt.Errorf("client not found")
	}

	return client, nil
}

// readValidMessage reads a message from the client.
func (cm *ClientManager) readValidMessage(conn net.Conn) (*cmd_validator.IncomingMessage, error) {
	// sanity check
	if conn == nil {
		return nil, fmt.Errorf("connection is nil")
	}

	// read the message
	msg, err := cm.p_server.ReadMessage(conn)
	if err != nil {
		return nil, fmt.Errorf("failed to read message from client: %w", err)
	}

	// check if the message is a valid message
	parts, err := msg_parser.FromNetMessage(msg)
	if err != nil {
		return nil, fmt.Errorf("failed to parse message: %w", err)
	}

	// validate the message for generic format
	p_command, err := cmd_validator.GetCommand(parts)
	if err != nil {
		return nil, fmt.Errorf("failed to extract valid command: %w", err)
	}

	return p_command, nil
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
	err = cm.p_server.SendMessage(conn, msg)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	return nil
}

// checkAlive checks if the client is alive by sending a ping message and waiting for a pong message.
func (cm *ClientManager) checkAlive(conn net.Conn) (bool, error) {
	// sanity check
	if conn == nil {
		return false, fmt.Errorf("connection is nil")
	}

	// send the ping message
	parts := []string{protocol.CmdPing}
	err := cm.sendMessage(conn, parts)
	if err != nil {
		return false, fmt.Errorf("failed to send ping message: %w", err)
	}

	// read the pong message
	p_command, err := cm.readValidMessage(conn)
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
func (cm *ClientManager) sendHandshakeReply(conn net.Conn) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	// send the handshake reply
	parts := []string{protocol.CmdHandshakeResp}
	err := cm.sendMessage(conn, parts)
	if err != nil {
		return fmt.Errorf("failed to send handshake reply: %w", err)
	}

	return nil
}

// validateConnection validates a new connection.
// Returns the nickname of the client upon successful validation.
func (cm *ClientManager) validateConnection(conn net.Conn) (string, error) {
	// sanity check
	if conn == nil {
		return "", fmt.Errorf("connection is nil")
	}

	// read the handshake message
	p_command, err := cm.readValidMessage(conn)
	if err != nil {
		return "", fmt.Errorf("failed to read handshake message: %w", err)
	}
	err = cmd_validator.ValidateHandshake(p_command)
	if err != nil {
		return "", fmt.Errorf("invalid handshake message: %w", err)
	}

	nickname := p_command.Parts[protocol.NicknameIndex]

	err = cm.sendHandshakeReply(conn)
	if err != nil {
		return "", fmt.Errorf("failed to send handshake reply: %w", err)
	}

	// await confirmation
	p_command, err = cm.readValidMessage(conn)
	if err != nil {
		return "", fmt.Errorf("failed to read confirmation message: %w", err)
	}
	err = cmd_validator.ValidateHandshakeConfirmation(p_command)
	if err != nil {
		return "", fmt.Errorf("invalid confirmation message: %w", err)
	}

	return nickname, nil
}

func (cm *ClientManager) handleConnection(conn net.Conn) {
	// TODO HERE
	logging.Debug(fmt.Sprintf("Handling connection from %s", conn.RemoteAddr().String()))

	// validate the connection
	nickname, err := cm.validateConnection(conn)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to validate connection: %v", err))
		return
	}

	// add the client
	cm.mutex.Lock()
	err = cm.addClient(conn, nickname)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to add client: %v", err))
		return
	}
	cm.mutex.Unlock()
	logging.Info(fmt.Sprintf("Client %s has connected", conn.RemoteAddr().String()))

	// infinite loop to handle messages
	for {
		// read message (busy waiting is prevented by the timeout)
		p_command, err := cm.readValidMessage(conn)
		if err != nil {
			// TODO decompose handling
			// handle timeout or disconnection
			var netErr net.Error
			if errors.As(err, &netErr) && netErr.Timeout() {
				logging.Debug(fmt.Sprintf("Timeout for client %s, pinging...", conn.RemoteAddr().String()))
				isAlive, err := cm.checkAlive(conn)
				if err != nil {
					logging.Error(fmt.Sprintf("failed to check if client is alive: %v", err))
					break
				}
				if !isAlive {
					logging.Warn(fmt.Sprintf("Client %s is not alive, disconnecting...", conn.RemoteAddr().String()))
					break
				}

				// client is alive, continue
				logging.Debug(fmt.Sprintf("Client %s is alive", conn.RemoteAddr().String()))
				continue
			}

			// handle EOF (graceful or abrupt disconnection)
			if errors.Is(err, io.EOF) {
				logging.Warn(fmt.Sprintf("Client %s disconnected abruptly", conn.RemoteAddr().String()))

				// some other error occurred
			} else {
				logging.Error(fmt.Sprintf("Error reading from client %s: %v", conn.RemoteAddr().String(), err))
			}
			break
		}

		// PLACEHOLDER: now just print the message
		logging.Debug(fmt.Sprintf("Received message from %s: %s", conn.RemoteAddr().String(), (*p_command).ToString()))
		if (*p_command).Command == protocol.CmdLeave {
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
			conn, err := cm.p_server.AcceptConnection()
			if err != nil {
				// check if the error is timeout (will be returned explicitly)
				var nErr net.Error
				if errors.As(err, &nErr) && nErr.Timeout() {
					continue
				}

				// error is probably unrecoverable
				return fmt.Errorf("failed to accept connection: %w", err)
			}

			// handle each connection in a separate goroutine
			go func() {
				// safety measure to recover from panics (exceptions)
				defer func() {
					if r := recover(); r != nil {
						logging.Error(fmt.Sprintf("Recovered from panic in connection handler: %v", r))
					}
				}()

				cm.handleConnection(conn) // NOTE: feasible for hundreds of clients; for thousands of clients, a worker pool would be used
			}()
		}
	}
}
