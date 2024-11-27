package server

import (
	"context"
	"fmt"
	"inverse-battleships-server/logging"
	"net"
	"strings"
	"sync"
	"time"
)

// constants for the message header and commands
const (
	msgDelimiter     = ";"
	msgTerminator    = "\n"
	msgHeader        = "IBGAME"
	cmdHandshakeReqv = "HAND"
	cmdHandshakeResp = "SHAKE"
	cmdHandshakeAck  = "DEAL"
	cmdPing          = "PING"
	cmdPong          = "PONG"
	cmdLeave         = "LEAVE"
	cmdLeaveAck      = "BYE"
)

const sleepTime = 1 * time.Millisecond

// Client represents a TCP client.
type Client struct {
	conn       net.Conn
	p_nickname *string
	lastTime   time.Time
}

// Lobby represents a game lobby.
type Lobby struct {
	id       string
	clients  []*Client
	rw_mutex sync.RWMutex
}

// Server represents a TCP server.
type ClientManager struct {
	p_server *Server            // server pointer
	clients  map[string]*Client // map of clients with their addresses as keys
	lobbies  map[string]*Lobby  // Manage lobbies
	mutex    sync.Mutex         // mutex to lock the client manager
}

// ToNetMessage converts a list of strings to a network message.
func ToNetMessage(parts []string) (string, error) {
	// sanity check
	if parts == nil {
		return "", fmt.Errorf("parts is nil")
	}

	for i, part := range parts {
		// part must not contain the terminator anywhere in the string
		if strings.Contains(part, msgTerminator) {
			return "", fmt.Errorf("part contains terminator")
		}

		// escape the delimiter if present
		if strings.Contains(part, msgDelimiter) {
			parts[i] = strings.ReplaceAll(part, msgDelimiter, "\\"+msgDelimiter)
		}
	}

	msg := ""
	msg += msgHeader
	for _, part := range parts {
		msg += msgDelimiter
		msg += part
	}
	msg += msgTerminator

	return msg, nil
}

// NewClientManager creates a new ClientManager.
// It requires a server pointer as a parameter.
func NewClientManager(server *Server) *ClientManager {
	return &ClientManager{
		p_server: server,
		clients:  make(map[string]*Client),
		lobbies:  make(map[string]*Lobby),
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
func (cm *ClientManager) addClient(conn net.Conn) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	client := &Client{
		conn:       conn,
		p_nickname: nil,
		lastTime:   time.Now(),
	}

	cm.clients[conn.RemoteAddr().String()] = client
	logging.Info(fmt.Sprintf("Client %s has been added", conn.RemoteAddr().String()))
	return nil
}

// removeClient removes a client from the client manager.
func (cm *ClientManager) removeClient(conn net.Conn) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	delete(cm.clients, conn.RemoteAddr().String())
	logging.Info(fmt.Sprintf("Client %s has been removed", conn.RemoteAddr().String()))
	return nil
}

// getClient returns a client from the client manager.
func (cm *ClientManager) getClient(conn net.Conn) (*Client, error) {
	// sanity check
	if conn == nil {
		return nil, fmt.Errorf("connection is nil")
	}

	client, exists := cm.clients[conn.RemoteAddr().String()]
	if !exists {
		return nil, fmt.Errorf("client not found")
	}

	return client, nil
}

// setNickname sets the nickname of a client.
func (cm *ClientManager) setNickname(conn net.Conn, nickname string) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	client, err := cm.getClient(conn)
	if err != nil {
		return fmt.Errorf("failed to get client: %w", err)
	}

	client.p_nickname = &nickname
	return nil
}

func (cm *ClientManager) handleConnection(conn net.Conn) {
	logging.Debug(fmt.Sprintf("Handling connection from %s", conn.RemoteAddr().String()))

	// add the client
	cm.mutex.Lock()
	err := cm.addClient(conn)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to add client: %v", err))
		return
	}
	cm.mutex.Unlock()
	logging.Info(fmt.Sprintf("Client %s has connected", conn.RemoteAddr().String()))

	// infinite loop to handle messages
	for {
		// read message
		msg, err := cm.p_server.ReadMessage(conn)
		if err != nil {
			// gracefully handle timeout
			nErr, ok := err.(net.Error)
			if ok && nErr.Timeout() {
				continue
			}

			// some other error occurred
			logging.Error(fmt.Sprintf("failed to read message: %v", err))
			break
		}

		// TODO HERE
		msg2 := msg
		msg = msg2
		// sleep to prevent busy waiting
		time.Sleep(sleepTime)
		break
	}

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

		default:
			// accept new connection
			conn, err := cm.p_server.AcceptConnection()
			if err != nil {
				// check if the error is timeout (will be returned explicitly)
				nErr, ok := err.(net.Error)
				if ok && nErr.Timeout() {
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
