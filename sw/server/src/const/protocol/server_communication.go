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
}

// lobbyStates is a list of lobby statuses.
const (
	LobbyStateCreated uint8 = iota
	LobbyStatePaired
	LobbyStateStarting
	LobbyStateUnready
	LobbyStatePlayer01Turn
	LobbyStatePlayer01Playing
	LobbyStatePlayer02Played
	LobbyStatePlayer02Turn
	LobbyStatePlayer02Playing
	LobbyStatePlayer01Played
	LobbyStateFinished
	LobbyStateWaiting
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

// PlayerCount is the number of players in a game.
const PlayerCount uint8 = 2
