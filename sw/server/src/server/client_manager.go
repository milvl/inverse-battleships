package server

import (
	"fmt"
	"inverse-battleships-server/logging"
	"net"
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

// Client represents a TCP client.
type Client struct {
	conn       net.Conn
	p_nickname *string
	lastTime   time.Time
}

// Server represents a TCP server.
type ClientManager struct {
	server  *Server            // server pointer
	clients map[string]*Client // map of clients with their addresses as keys
	mutex   sync.Mutex         // mutex to lock the client manager
}

// ToNetMessage converts a list of strings to a network message.
// TODO escape special characters
func ToNetMessage(parts []string) (string, error) {
	// sanity check
	if parts == nil {
		return "", fmt.Errorf("parts is nil")
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
		server:  server,
		clients: make(map[string]*Client),
	}
}

// startServer starts the TCP server.
func (cm *ClientManager) startServer() error {
	// sanity check
	if cm.server == nil {
		return fmt.Errorf("server is nil")
	}

	cm.server.Start()
	return nil
}

// stopServer stops the TCP server.
func (cm *ClientManager) stopServer() error {
	// sanity check
	if cm.server == nil {
		return fmt.Errorf("server is nil")
	}

	cm.server.Stop()
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

func testTryHandshake(cm *ClientManager, conn net.Conn) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	// read the message
	message, err := cm.server.ReadMessage(conn)
	if err != nil {
		return fmt.Errorf("failed to read message: %w", err)
	}

	// validate the message
	expectedResp, err := ToNetMessage([]string{cmdHandshakeReqv})
	if err != nil {
		return fmt.Errorf("failed to create message: %w", err)
	}

	if message != expectedResp {
		return fmt.Errorf("invalid message: %s", message)
	}
	logging.Info(fmt.Sprintf("Client %s has sent a handshake request", conn.RemoteAddr().String()))

	// send the handshake response
	resp, err := ToNetMessage([]string{cmdHandshakeResp})
	if err != nil {
		return fmt.Errorf("failed to create message: %w", err)
	}

	err = cm.server.SendMessage(conn, resp)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}
	logging.Info(fmt.Sprintf("Client %s has received a handshake response", conn.RemoteAddr().String()))

	// wait for the handshake acknowledgment
	message, err = cm.server.ReadMessage(conn)
	if err != nil {
		return fmt.Errorf("failed to read message: %w", err)
	}

	expectedResp, err = ToNetMessage([]string{cmdHandshakeAck})
	if err != nil {
		return fmt.Errorf("failed to create message: %w", err)
	}

	if message != expectedResp {
		return fmt.Errorf("invalid message: %s", message)
	}

	logging.Info(fmt.Sprintf("Client %s has been validated", conn.RemoteAddr().String()))
	return nil
}

func testTryPong(cm *ClientManager, conn net.Conn) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	// read the message
	message, err := cm.server.ReadMessage(conn)
	if err != nil {
		return fmt.Errorf("failed to read message: %w", err)
	}

	// validate the message
	expectedResp, err := ToNetMessage([]string{cmdPing})
	if err != nil {
		return fmt.Errorf("failed to create message: %w", err)
	}

	if message != expectedResp {
		return fmt.Errorf("invalid message: %s", message)
	}
	logging.Info(fmt.Sprintf("Client %s has sent a ping", conn.RemoteAddr().String()))

	// send the pong
	resp, err := ToNetMessage([]string{cmdPong})
	if err != nil {
		return fmt.Errorf("failed to create message: %w", err)
	}

	err = cm.server.SendMessage(conn, resp)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}
	logging.Info(fmt.Sprintf("Pong has been sent to client %s", conn.RemoteAddr().String()))

	return nil
}

func testTryDisconnect(cm *ClientManager, conn net.Conn) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	// read the message
	message, err := cm.server.ReadMessage(conn)
	if err != nil {
		return fmt.Errorf("failed to read message: %w", err)
	}

	// validate the message
	expectedResp, err := ToNetMessage([]string{cmdLeave})
	if err != nil {
		return fmt.Errorf("failed to create message: %w", err)
	}

	if message != expectedResp {
		return fmt.Errorf("invalid message: %s", message)
	}
	logging.Info(fmt.Sprintf("Client %s has sent a leave request", conn.RemoteAddr().String()))

	// send the leave acknowledgment
	resp, err := ToNetMessage([]string{cmdLeaveAck})
	if err != nil {
		return fmt.Errorf("failed to create message: %w", err)
	}

	err = cm.server.SendMessage(conn, resp)
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}
	logging.Info(fmt.Sprintf("Leave acknowledgment has been sent to client %s", conn.RemoteAddr().String()))

	return nil
}

// testValidateClient validates a client by waiting for a handshake request.
func testValidateClient(cm *ClientManager, conn net.Conn) error {
	// sanity check
	if conn == nil {
		return fmt.Errorf("connection is nil")
	}

	err := testTryHandshake(cm, conn)
	if err != nil {
		return fmt.Errorf("failed to handshake: %w", err)
	}

	err = testTryPong(cm, conn)
	if err != nil {
		return fmt.Errorf("failed to pong: %w", err)
	}

	err = testTryDisconnect(cm, conn)
	if err != nil {
		return fmt.Errorf("failed to disconnect: %w", err)
	}

	return nil
}

// testHandleConnection handles a new connection. It adds the client to the client manager.
// It requires a client manager and a connection as parameters.
func testHandleConnection(cm *ClientManager, conn net.Conn) {
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

	// validate the client (wait for handshake request)
	err = testValidateClient(cm, conn)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to validate client: %v", err))
	}

	// remove the client
	cm.mutex.Lock()
	err = cm.removeClient(conn)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to remove client: %v", err))
	}
	cm.mutex.Unlock()

	// close the connection
	err = cm.server.CloseConnection(conn)
	if err != nil {
		logging.Error(fmt.Sprintf("failed to close connection: %v", err))
	}

	logging.Info(fmt.Sprintf("Client %s has disconnected", conn.RemoteAddr().String()))
}

func (cm *ClientManager) Test() {
	// start the server
	err := cm.startServer()
	if err != nil {
		logging.Error(fmt.Sprintf("failed to start server: %v", err))
		return
	}

	// to stop the server after the function ends
	defer cm.stopServer()

	// infinite loop to accept connections
	for {
		// accept new connection
		conn, err := cm.server.AcceptConnection()
		if err != nil {
			logging.Info(fmt.Sprintf("failed to accept connection: %v", err))
			continue
		}

		go testHandleConnection(cm, conn)
	}
}
