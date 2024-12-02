package protocol

// validCmds is a list of valid commands.
const (
	CmdHandshakeReqv = "HAND"  // 0
	CmdHandshakeResp = "SHAKE" // 1
	CmdHandshakeAck  = "DEAL"  // 2
	CmdPing          = "PING"  // 3
	CmdPong          = "PONG"  // 4
	CmdLeave         = "LEAVE" // 5
	CmdLeaveAck      = "BYE"   // 6
)

// validCmdsMap is a map of valid commands.
var validCmdsMap = map[string]int{
	CmdHandshakeReqv: 0,
	CmdHandshakeResp: 1,
	CmdHandshakeAck:  2,
	CmdPing:          3,
	CmdPong:          4,
	CmdLeave:         5,
	CmdLeaveAck:      6,
}

// IsValidCmd checks if a command is valid.
func IsValidCmd(cmd string) bool {
	_, ok := validCmdsMap[cmd]
	return ok
}

// constants for the message header and commands
const (
	MsgDelimiter    = ";"
	MsgTerminator   = "\n"
	MsgHeader       = "IBGAME"
	HeaderPartIndex = 0
	CmdPartIndex    = 1
	MinPartsCount   = 2
	NicknameIndex   = 0
)
