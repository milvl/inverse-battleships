// custom_errors package represents custom errors defined in the project.
package custom_errors

import "errors"

// ErrNilPointer is an error that occurs when a nil pointer is encountered.
var ErrNilPointer = errors.New("nil pointer error")

// ErrNilConn is an error that occurs when a nil connection is encountered.
var ErrNilConn = errors.New("nil connection error")

// ErrInvalidCommand is an error that occurs when an invalid command is encountered.
var ErrInvalidCommand = errors.New("invalid command")

// ErrPlayerNotIdle is an error that occurs when a player is not in idle state.
var ErrPlayerNotIdle = errors.New("player is not in idle state")

// ErrLobbyNotFound is an error that occurs when a lobby is not found.
var ErrLobbyNotFound = errors.New("lobby not found")

// ErrLobbyFull is an error that occurs when a lobby is full.
var ErrLobbyFull = errors.New("lobby is full")

// ErrPlayerNotFound is an error that occurs when a player is not found.
var ErrPlayerNotFound = errors.New("player not found")

// ErrCmdParsing is an error that occurs when a command is not parsed correctly.
var ErrCmdParseInvalParam = errors.New("error while parsing command parameters (malformed parameters)")

// ErrNotPlayerTurn is an error that occurs when it is not a player's turn but they try to make a move.
var ErrNotPlayerTurn = errors.New("not player's turn")

// ErrInvalidMove is an error that occurs when an invalid move is made.
var ErrInvalidMove = errors.New("invalid move")

// ErrSendMsg is an error that occurs when a message cannot be sent.
var ErrSendMsg = errors.New("error while sending message")
