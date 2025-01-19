# Server files:

## File: server\src\main.go

### Functions/Methods

```go
func main()
```

## File: server\src\logging\logging.go

### Functions/Methods

```go
// NewLogger creates a new logger instance with the given configuration.
// Argument enabledLevels is a bitmask of LogLevel values.
// Example usage: "DEBUG" returns a logger that logs messages at the DEBUG level.
// Example usage: "DEBUG | INFO | WARNING" returns a logger that logs messages at the DEBUG, INFO, and WARNING levels.
// If timeFormat is empty, no timestamp will be added.
func NewLogger(enabledLevels LogLevel, timeFormat string, doTraceCall bool, stream *os.File) *Logger
```

```go
// NewDefaultLogger creates a new logger instance with default configuration.
func NewDefaultLogger() *Logger
```

```go
// getGlobalLogger returns the global logger instance
func getGlobalLogger() *Logger
```

```go
// isAllowed checks if the given level is allowed
func isAllowed(enabledLevels LogLevel, level LogLevel) bool
```

```go
// colorize colorizes a message with the given color
func colorize(color string, message string) string
```

```go
// logMessage logs a message at the given level
func (l *Logger) logMessage(level LogLevel, message string)
```

```go
func (l *Logger) Debug(message string)
```

```go
// Info logs a message at the INFO level for the given logger
func (l *Logger) Info(message string)
```

```go
// Warn logs a message at the WARNING level for the given logger
func (l *Logger) Warn(message string)
```

```go
// Error logs a message at the ERROR level for the given logger
func (l *Logger) Error(message string)
```

```go
// Critical logs a message at the CRITICAL level for the given logger
func (l *Logger) Critical(message string)
```

```go
// Debug logs a message at the CRITICAL level
func Debug(message string)
```

```go
// Info logs a message at the INFO level
func Info(message string)
```

```go
// Warn logs a message at the WARNING level
func Warn(message string)
```

```go
// Error logs a message at the ERROR level
func Error(message string)
```

```go
// Critical logs a message at the CRITICAL level
func Critical(message string)
```

## File: server\src\server\client_manager.go

### Functions/Methods

```go
// NewClientManager creates a new ClientManager.
// It requires a server pointer as a parameter.
func NewClientManager(server *Server) *ClientManager
```

```go
// getCompleteMsg checks if the message is complete.
// It returns a boolean indicating if the message is complete,
// the whole message, and additional parts of queued messages.
func getCompleteMsg(msg string) (bool, string, string)
```

```go
// boardToString converts a board to a string.
func boardToString(board [protocol.BoardSize][protocol.BoardSize]int8) string
```

```go
// boardToStringPlayer converts a board to a string for a player.
func boardToStringPlayer(board [protocol.BoardSize][protocol.BoardSize]int8, isPlayer01 bool) string
```

```go
// getNighboursCount gets the count of neighbours of a cell.
func getNighboursCount(board [protocol.BoardSize][protocol.BoardSize]int8, row, col int) int
```

```go
// getInitialBoard generates a random board.
func getInitialBoard() [protocol.BoardSize][protocol.BoardSize]int8
```

```go
// getGameStats gets the game statistics.
// It returns if the game has finished; if player01 has won; and an error if any.
// If error is returned the other two values are not defined.
func getGameStats(board [protocol.BoardSize][protocol.BoardSize]int8) (bool, bool, error)
```

```go
// shouldLobbyWait checks if the lobby can be switched to reconnecting state.
func shouldLobbyWait(lobby *Lobby) bool
```

```go
// areAllPlayersConnected checks if all players are connected in a lobby.
func areAllPlayersConnected(pLobby *Lobby) bool
```

```go
// readCompleteMessage reads a message from the client.
// It returns the parsed message, the raw string message, and an error.
// It involves socket I/O operations so it should be called with a lock.
func (cm *ClientManager) readCompleteMessage(pClient *Client) (*cmd_validator.IncomingMessage, string, error)
```

```go
// handleClientError handles client errors.
// It returns two booleans: one indicating if the error was caused by a timeout,
// and the other indicating if the error means the client should be disconnected.
func (cm *ClientManager) handleClientError(pClient *Client, err error) (bool, bool)
```

```go
// startServer starts the TCP server.
func (cm *ClientManager) startServer() error
```

```go
// stopServer stops the TCP server.
func (cm *ClientManager) stopServer() error
```

```go
// addClient adds a new unauthenticated client to the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) addClient(conn net.Conn) (*Client, error)
```

```go
// authenticateClient adds a new authenticated client to the client manager.
// It returns the nickname of the client upon successful authentication.
// It returns an error if the nickname is already taken.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) authenticateClient(pClient *Client, nickname string) error
```

```go
// removeClient removes a client from the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) removeClient(nickname string) error
```

```go
// addPlayerToLobby adds a player to a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) addPlayerToLobby(nickname string, lobbyID string) error
```

```go
// kickPlayerFromLobby kicks a player from a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) kickPlayerFromLobby(nickname string) error
```

```go
// removePendingClient removes a pending client from the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) removePendingClient(addr string) error
```

```go
// getClient returns a client from the client manager.
func (cm *ClientManager) getClient(nickname string) (*Client, error)
```

```go
// checkForPendingReconnect checks if a new connection is in a lobby pending reconnect state.
//
// WARNING: It reads a shared resource, so it should be called with a lock.
func (cm *ClientManager) checkForPendingReconnect(nickname string) bool
```

```go
// handleDeleteLobby deletes a lobby from the client manager.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) handleDeleteLobby(lobbyID string) error
```

```go
// attemptMove attempts to make a move in a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) attemptMove(lobby *Lobby, nickname string, position []int) error
```

```go
// sendMessage sends a message to the client.
// It involves socket I/O operations so it should be called with a lock.
func (cm *ClientManager) sendMessage(conn net.Conn, parts []string) error
```

```go
// sendHandshakeReply sends a handshake reply to the client.
func (cm *ClientManager) sendHandshakeReply(pClient *Client) error
```

```go
// sendPing sends a ping message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendPing(pClient *Client) error
```

```go
// sendTKO sends a TKO message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendTKO(pClient *Client) error
```

```go
// sendLobbies sends a list of lobbies to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendLobbies(pClient *Client, lobbies []string) error
```

```go
// sendLobbyAck sends a create lobby acknowledgment message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendLobbyAck(pClient *Client, lobbyID string) error
```

```go
// sendTurnMsg sends a turn message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendTurnMsg(pClient *Client, playerOnTurn string, errChan chan error) error
```

```go
// sendPairedMsg sends a paired message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendPairedMsg(pClient *Client, opponent string) error
```

```go
// sendBoard sends a board to the client.
func (cm *ClientManager) sendBoard(pClient *Client, board string, errChan chan error) error
```

```go
// sendGameEndMsg sends a game end message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendGameEndMsg(pClient *Client, isWinner bool, errChan chan error) error
```

```go
// sendWaitMsg sends a wait message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendWaitMsg(pClient *Client, errChan chan error) error
```

```go
// sendContinueMsg sends a continue message to the client.
// Expects the client to be valid.
func (cm *ClientManager) sendContinueMsg(pClient *Client, lobbyID string, opponent string, playerOnTurn string, board string, errChan chan error) error
```

```go
// handlePingCmd sends a pong message to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handlePingCmd(pClient *Client) (bool, error)
```

```go
// handleLeaveCmd sends a leave acknowledgment message to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleLeaveCmd(pClient *Client) (bool, error)
```

```go
// handleLobbiesCmd sends a list of lobbies to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleLobbiesCmd(pClient *Client) (bool, error)
```

```go
// handleCreateLobbyCmd creates a new lobby and sends the lobby ID to the client.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleCreateLobbyCmd(pClient *Client) (bool, error)
```

```go
// handleJoinLobbyCmd attempts to connect the client to a lobby.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleJoinLobbyCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) (bool, error)
```

```go
// handleClientReadyCmd handles a client ready message.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleClientReadyCmd(pClient *Client) (bool, error)
```

```go
// handleActionCmd handles an action message.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleActionCmd(pClient *Client, pCommand *cmd_validator.IncomingMessage) (bool, error)
```

```go
// handleWaitingCmd handles a waiting message.
// Expects the client to be valid.
// Returns if the connection should continue and an error if any.
func (cm *ClientManager) handleWaitingCmd(pClient *Client) (bool, error)
```

```go
// checkAlive checks if the client is alive by sending a ping message and waiting for a pong message.
// Returns true if the client is alive, false otherwise. Returns an error if any.
func (cm *ClientManager) checkAlive(pClient *Client) (bool, error)
```

```go
// validateConnection validates a new connection.
// Returns the nickname of the client upon successful validation.
func (cm *ClientManager) validateConnection(pClient *Client) (string, error)
```

```go
// getMissingPlayerNickname returns the nickname of the missing player in a lobby.
// Expects the lobby to be valid.
//
// WARNING: It reads a shared resource, so it should be called with a rlock.
func (cm *ClientManager) getMissingPlayerNickname(lobby *Lobby) string
```

```go
// prepareGame prepares a game in a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) prepareGame(lobby *Lobby) error
```

```go
// startGame starts a game in a lobby.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) startGame(lobby *Lobby) error
```

```go
func (cm *ClientManager) informMoves(lobby *Lobby) error
```

```go
// advanceGame advances a game in a lobby.
//
// WARNING: It reads a shared resource, so it should be called with a rlock.
func (cm *ClientManager) advanceGame(lobby *Lobby) error
```

```go
// interruptLobby pauses a lobby and sends wait messages to the players.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) interruptLobby(pLobby *Lobby) error
```

```go
// handleLobbyInterrupted handles a lobby in the waiting state.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) handleLobbyInterrupted(lobby *Lobby) error
```

```go
// handleLobbyPlayerReconnect handles a lobby in the waiting state.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) handleLobbyPlayerReconnect(lobby *Lobby) error
```

```go
// handleLobbyContinue handles a lobby in the waiting state.
//
// WARNING: It manipulates a shared resource, so it should be called with a lock.
func (cm *ClientManager) handleLobbyContinue(pLobby *Lobby) error
```

```go
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
    lobbiesWithPlayerReconnect *[]string,
    lobbiesToContinue *[]string)
```

```go
// manageLobbiesToDelete handles the lobbies that need to be deleted.
func (cm *ClientManager) manageLobbiesToDelete(lobbiesToDelete []string)
```

```go
// manageLobbiesToPrepare handles the lobbies that need to be prepared.
func (cm *ClientManager) manageLobbiesToPrepare(lobbiesToPrepare []string)
```

```go
// manageLobbiesToStart handles the lobbies that need to be started.
func (cm *ClientManager) manageLobbiesToStart(lobbiesToStart []string)
```

```go
// manageLobbiesToFeedback handles the lobbies that need to inform the players about the moves.
func (cm *ClientManager) manageLobbiesToFeedback(lobbiesToFeedbackPlayers []string)
```

```go
// manageLobbiesToAdvance handles the lobbies to advance.
func (cm *ClientManager) manageLobbiesToAdvance(lobbiesToAdvance []string)
```

```go
// manageLobbiesToInterrupt handles the lobbies to interrupt.
func (cm *ClientManager) manageLobbiesToInterrupt(lobbiesToInterrupt []string)
```

```go
// manageLobbiesInterrupted handles the interrupted lobbies.
func (cm *ClientManager) manageLobbiesInterrupted(lobbiesReconnecting []string)
```

```go
// manageLobbiesWithPlayerReconnect handles the lobbies with player reconnected.
func (cm *ClientManager) manageLobbiesWithPlayerReconnect(lobbiesWithPlayerReconnect []string)
```

```go
// manageLobbiesToContinue handles the lobbies that need to continue.
func (cm *ClientManager) manageLobbiesToContinue(lobbiesToContinue []string)
```

```go
// manageLobbies handles the games.
func (cm *ClientManager) manageLobbies()
```

```go
// handleCommand handles a command from the client. It returns a boolean indicating if the client should stay connected.
// If error is not nil, the stayConnected boolean returned is not defined.
func (cm *ClientManager) handleCommand(pClient *Client, pCommand *cmd_validator.IncomingMessage) (bool, error)
```

```go
// reconnectPlayer reconnects a player to a lobby.
func (cm *ClientManager) reconnectPlayer(nickname string)
```

```go
func (cm *ClientManager) handleConnection(conn net.Conn)
```

```go
func (cm *ClientManager) ManageServer(ctx context.Context) error
```

## File: server\src\server\connection_manager.go

### Functions/Methods

```go
// escapeSpecialSymbols escapes special symbols in a string.
func escapeSpecialSymbols(input string) string
```

```go
// NewServer initializes and returns a new Server instance.
func NewServer(address string) *Server
```

```go
// Start launches the TCP server and begins listening for incoming connections.
func (s *Server) Start() error
```

```go
// Stop stops the TCP server and closes the listener.
func (s *Server) Stop() error
```

```go
// AcceptConnection accepts a new connection from a client.
func (s *Server) AcceptConnection() (net.Conn, error)
```

```go
// CloseConnection closes the connection with the client.
func (s *Server) CloseConnection(conn net.Conn) error
```

```go
// ReadMessage reads a message from the client.
func (s *Server) ReadMessage(conn net.Conn) (string, error)
```

```go
// SendMessage sends a message to the client.
func (s *Server) SendMessage(conn net.Conn, message string) error
```

## File: server\src\util\util.go

### Functions/Methods

```go
// LoadConfig loads the configuration from a file.
func LoadConfig(path string) (*const_file.Config, error)
```

## File: server\src\const\protocol\server_communication.go

### Functions/Methods

```go
// IsValidCmd checks if a command is valid.
func IsValidCmd(cmd string) bool
```

## File: server\src\util\arg_parser\arg_parser.go

### Functions/Methods

```go
// isFlag checks if an argument is a flag
func isFlag(arg string) bool
```

```go
// ParseArgs parses command-line arguments
func ParseArgs() (*Arguments, error)
```

## File: server\src\util\cmd_validator\cmd_validator.go

### Functions/Methods

```go
// ToString returns a string representation of the message.
func (p_im *IncomingMessage) ToString() string
```

```go
// GetCommand validates a client response.
func GetCommand(parts []string) (*IncomingMessage, error)
```

```go
// ParseHandshakeCmd parses a handshake command. It returns the nickname or an error.
func ParseHandshakeCmd(pIm *IncomingMessage) (string, error)
```

```go
// ParseJoinLobbyCmd parses a join lobby command. It returns the lobby ID or an error.
func ParseJoinLobbyCmd(pIm *IncomingMessage) (string, error)
```

```go
// ParseActionCmd parses an action command.
func ParseActionCmd(pIm *IncomingMessage) ([]int, error)
```

## File: server\src\util\msg_parser\msg_parser.go

### Functions/Methods

```go
// ToNetMessage converts a list of strings to a network message.
// It adds the header and terminator to the message.
func ToNetMessage(parts []string) (string, error)
```

```go
// FromNetMessage converts a network message to a list of strings.
func FromNetMessage(msg string) ([]string, error)
```

