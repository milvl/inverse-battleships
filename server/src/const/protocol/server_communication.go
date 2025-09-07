package protocol

import "time"

// validCmds is a list of valid commands.
const (
	CmdHandshakeReqv  = "HAND"     // 0
	CmdHandshakeResp  = "SHAKE"    // 1
	CmdHandshakeAck   = "DEAL"     // 2
	CmdPing           = "PING"     // 3
	CmdPong           = "PONG"     // 4
	CmdLeave          = "LEAVE"    // 5
	CmdLeaveAck       = "BYE"      // 6
	CmdLobbies        = "LOBBIES"  // 7
	CmdCreateLobby    = "CREATE"   // 8
	CmdJoinLobby      = "BRING_IT" // 9
	CmdCreateLobbyAck = "PAIRING"  // 10
	CmdJoinLobbyAck   = "PAIRED"   // 11
	CmdClientReady    = "READY"    // 12
	CmdPlayerTurn     = "TURN"     // 13
	CmdTKO            = "TKO"      // 14
	CmdAction         = "ACTION"   // 15
	CmdBoard          = "BOARD"    // 16
	CmdWin            = "WIN"      // 17
	CmdLose           = "LOST"     // 18
	CmdWait           = "WAIT"     // 19
	CmdWaiting        = "WAITING"  // 20
	CmdContinue       = "CONTINUE" // 21
)

// validCmdsMap is a map of valid commands.
var validCmdsMap = map[string]int{
	CmdHandshakeReqv:  0,
	CmdHandshakeResp:  1,
	CmdHandshakeAck:   2,
	CmdPing:           3,
	CmdPong:           4,
	CmdLeave:          5,
	CmdLeaveAck:       6,
	CmdLobbies:        7,
	CmdCreateLobby:    8,
	CmdJoinLobby:      9,
	CmdCreateLobbyAck: 10,
	CmdJoinLobbyAck:   11,
	CmdClientReady:    12,
	CmdPlayerTurn:     13,
	CmdTKO:            14,
	CmdAction:         15,
	CmdBoard:          16,
	CmdWin:            17,
	CmdLose:           18,
	CmdWait:           19,
	CmdWaiting:        20,
	CmdContinue:       21,
}

// lobbyStates is a list of lobby statuses.
const (
	// LobbyStateUnititialized is value used for uninitialized states.
	LobbyStateUnititialized uint8 = iota
	// LobbyStateCreated is the initial state of a lobby before adding any players.
	LobbyStateCreated
	// LobbyStateWaiting is the state of a lobby when one player is in, waiting for another.
	LobbyStateWaiting
	// LobbyStatePaired is the state of a lobby when second player joins.
	LobbyStatePaired
	// LobbyStateUnready is the state of a lobby when both players are in, but did not send ready.
	LobbyStateUnready
	// LobbyStatePlayer01Turn is the state of a lobby when player 01 should receive a turn message.
	LobbyStatePlayer01Turn
	// LobbyStatePlayer01Playing is the state of a lobby when player 01 is playing.
	LobbyStatePlayer01Playing
	// LobbyStatePlayer01Played is the state of a lobby when player 01 played and board should be sent to both players.
	LobbyStatePlayer01Played
	// LobbyStatePlayer02Turn is the state of a lobby when player 02 should receive a turn message.
	LobbyStatePlayer02Turn
	// LobbyStatePlayer02Playing is the state of a lobby when player 02 is playing.
	LobbyStatePlayer02Playing
	// LobbyStatePlayer02Played is the state of a lobby when player 02 played and board should be sent to both players.
	LobbyStatePlayer02Played
	// LobbyStateInterrupt is the state of a lobby when a player disconnects.
	LobbyStateInterrupt
	// LobbyStateInterrupted is the state of a lobby waiting for players to reconnect.
	LobbyStateInterrupted
	// LobbyStatePlayerReconnected is the state of a lobby when a player reconnects and has to receive the board and wait message.
	LobbyStatePlayerReconnected
	// LobbyStateContinue is the state of a lobby when all players are ready to continue and previous state should be restored.
	LobbyStateContinue
	// LobbyStateFinished is the state of a lobby when the game ends expectedly.
	LobbyStateFinished
	// LobbyStateFail is the state of a lobby when the game ends unexpectedly.
	LobbyStateFail
)

// IsValidCmd checks if a command is valid.
func IsValidCmd(cmd string) bool {
	_, ok := validCmdsMap[cmd]
	return ok
}

// constants for the message header and commands
const (
	MsgDelimiter          = ";"
	MsgTerminator         = "\n"
	MsgEscape             = "\\"
	MsgHeader             = "IBGAME"
	NumDelimiter          = ":"
	SeqDelimiter          = ","
	BoardSize             = 9
	BoardCellFree         = 0
	BoardCellOwner        = 1
	BoardCellPlayer01     = 1
	BoardCellPlayer02     = 2
	BoardCellBoat         = 3
	BoardCellOwnerLost    = -1
	BoardCellOpponentLost = -2
	BoardCellPlayer01Lost = -1
	BoardCellPlayer02Lost = -2
	BoardBoatsCount       = 11
	HeaderPartIndex       = 0
	CmdPartIndex          = 1
	MinPartsCount         = 2
	// indexes for the IncomingMessage params slice
	NicknameIndex = 0
	LobbyIDIndex  = 0
	PositionIndex = 0
)

// CompleteMsgTimeout is the time to wait for a valid message.
const CompleteMsgTimeout = 5 * time.Second

// KeepAliveTimeout is the time to wait for a keep-alive message.
const KeepAliveTimeout = 5 * time.Second

// PlayerReconnectTimeout is the time to wait for a player to reconnect.
const PlayerReconnectTimeout = 60 * time.Second

// PlayerCount is the number of players in a game.
const PlayerCount uint8 = 2
