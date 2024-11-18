package server

import (
	"fmt"
	"inverse-battleships-server/logging"
	"net"
	"time"
)

// connectionType represents the type of connection (e.g., "tcp")
const connectionType = "tcp"

// bufferSize represents the size of the buffer used to read messages
const bufferSize = 1024 // 1024 bytes == 1024 characters == 1KiB
// timeout represents the time to wait for a connection
const timeout = 10 * time.Second

// Server is the main structure that holds the TCP server's state.
type Server struct {
	Address    string        // address the server listens on (e.g., "localhost:8080")
	p_listener *net.Listener // TCP listener
}

// NewServer initializes and returns a new Server instance.
func NewServer(address string) *Server {
	return &Server{
		Address:    address,
		p_listener: nil,
	}
}

// Start launches the TCP server and begins listening for incoming connections.
func (s *Server) Start() error {
	listener, err := net.Listen(connectionType, s.Address)
	if err != nil {
		return fmt.Errorf("failed to start server: %w", err)
	}

	s.p_listener = &listener

	// fmt.Printf("Server is listening on %s\n", s.Address)
	logging.Info(fmt.Sprintf("Server is listening on %s\n", s.Address))

	return nil
}

// Stop stops the TCP server and closes the listener.
func (s *Server) Stop() error {
	// sanity check
	if s.p_listener == nil {
		return fmt.Errorf("server is not running")
	}

	err := (*s.p_listener).Close()
	if err != nil {
		return fmt.Errorf("failed to stop server: %w", err)
	}

	// fmt.Println("Server has been stopped")
	logging.Info("Server has been stopped")

	return nil
}

// AcceptConnection accepts a new connection from a client.
func (s *Server) AcceptConnection() (net.Conn, error) {
	// sanity check
	if s.p_listener == nil {
		return nil, fmt.Errorf("server is not running")
	}

	// set timeout for accepting connections
	(*s.p_listener).(*net.TCPListener).SetDeadline(time.Now().Add(timeout))

	conn, err := (*s.p_listener).Accept()
	if err != nil {
		return nil, fmt.Errorf("failed to accept connection: %w", err)
	}

	return conn, nil
}

// CloseConnection closes the connection with the client.
func (s *Server) CloseConnection(conn net.Conn) error {
	// sanity check
	if s.p_listener == nil {
		return fmt.Errorf("server is not running")
	}

	err := conn.Close()
	if err != nil {
		return fmt.Errorf("failed to close connection: %w", err)
	}

	return nil
}

// ReadMessage reads a message from the client.
func (s *Server) ReadMessage(conn net.Conn) (string, error) {
	// sanity check
	if s.p_listener == nil {
		return "", fmt.Errorf("server is not running")
	}

	// set timeout for reading messages
	conn.SetReadDeadline(time.Now().Add(timeout))

	// TODO make buffer size dynamic based on message type
	buffer := make([]byte, bufferSize)
	n, err := conn.Read(buffer)
	if err != nil {
		return "", fmt.Errorf("failed to read message: %w", err)
	}

	logging.Debug(fmt.Sprintf("Received message: \"%s\"", string(buffer[:n])))
	return string(buffer[:n]), nil
}

// SendMessage sends a message to the client.
func (s *Server) SendMessage(conn net.Conn, message string) error {
	// sanity check
	if s.p_listener == nil {
		return fmt.Errorf("server is not running")
	} else if len(message) == 0 {
		return fmt.Errorf("message is empty")
	}

	// check if message is too long
	if len(message) > bufferSize {
		return fmt.Errorf("message is too long")
	}

	_, err := conn.Write([]byte(message))
	if err != nil {
		return fmt.Errorf("failed to send message: %w", err)
	}

	logging.Debug(fmt.Sprintf("Sent message: \"%s\"", message))
	return nil
}
