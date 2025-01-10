package cmd_validator

import (
	"fmt"
	"inverse-battleships-server/const/custom_errors"
	"inverse-battleships-server/const/protocol"
	"inverse-battleships-server/logging"
	"strconv"
	"strings"
	"unicode"
)

const (
	maxPlayerNameLength = 20
)

// IncomingMessage represents a message received from a client.
type IncomingMessage struct {
	Command string
	Params  []string
}

// ToString returns a string representation of the message.
func (p_im *IncomingMessage) ToString() string {
	return fmt.Sprintf("Command: %s, Params: %v", p_im.Command, p_im.Params)
}

// GetCommand validates a client response.
func GetCommand(parts []string) (*IncomingMessage, error) {
	// sanity check
	if parts == nil {
		return nil, fmt.Errorf("parts is nil")
	}

	// check if the message is a valid response
	if len(parts) < protocol.MinPartsCount {
		return nil, fmt.Errorf("invalid format - not enough parts")
	}
	if parts[protocol.HeaderPartIndex] != protocol.MsgHeader {
		return nil, fmt.Errorf("invalid format - wrong header")
	}

	selectedCmd := parts[protocol.CmdPartIndex]
	params := parts[protocol.MinPartsCount:]
	cmd := IncomingMessage{Command: selectedCmd, Params: params}

	if !protocol.IsValidCmd(cmd.Command) {
		return nil, fmt.Errorf("invalid format - unknown command")
	}

	// check for validity of the command and the number of parts associated with it
	switch cmd.Command {
	// 1 part commands
	case protocol.CmdHandshakeAck:
		fallthrough
	case protocol.CmdLeave:
		fallthrough
	case protocol.CmdPing:
		fallthrough
	case protocol.CmdPong:
		fallthrough
	case protocol.CmdLobbies:
		fallthrough
	case protocol.CmdCreateLobby:
		fallthrough
	case protocol.CmdClientReady:
		if len(parts) != protocol.MinPartsCount {
			return nil, fmt.Errorf("invalid format - not enough parts")
		}
		return &cmd, nil

	// 2 parts commands
	case protocol.CmdHandshakeReqv:
		fallthrough
	case protocol.CmdJoinLobby:
		fallthrough
	case protocol.CmdAction:
		if len(parts) != protocol.MinPartsCount+1 {
			return nil, fmt.Errorf("invalid format - not enough parts")
		}

	default:
		logging.Debug(fmt.Sprintf("Unknown command: %s", selectedCmd))
		return nil, fmt.Errorf("unknown command to parse")
	}

	return &cmd, nil
}

// ParseHandshakeCmd parses a handshake command. It returns the nickname or an error.
func ParseHandshakeCmd(pIm *IncomingMessage) (string, error) {
	// check if the nickname is valid
	nickname := (*pIm).Params[protocol.NicknameIndex]
	if nickname == "" {
		logging.Warn("Error parsing handshake: empty nickname")
		return "", custom_errors.ErrCmdParseInvalParam
	}
	if len(nickname) > maxPlayerNameLength {
		logging.Warn("Error parsing handshake: nickname too long")
		return "", custom_errors.ErrCmdParseInvalParam
	}
	for _, char := range nickname {
		if !unicode.IsPrint(char) {
			logging.Warn(fmt.Sprintf("Error parsing handshake - invalid character in nickname: %c", char))
			return "", custom_errors.ErrCmdParseInvalParam
		}
	}

	return nickname, nil
}

// ParseJoinLobbyCmd parses a join lobby command. It returns the lobby ID or an error.
func ParseJoinLobbyCmd(pIm *IncomingMessage) (string, error) {
	if (*pIm).Params[protocol.LobbyIDIndex] == "" {
		logging.Warn("Error parsing join lobby: empty lobby ID")
		return "", custom_errors.ErrCmdParseInvalParam
	}

	return (*pIm).Params[protocol.LobbyIDIndex], nil
}

// ParseActionCmd parses an action command.
func ParseActionCmd(pIm *IncomingMessage) ([]int, error) {
	if (*pIm).Params[protocol.PositionIndex] == "" {
		logging.Warn("Error parsing action position: empty position")
		return nil, custom_errors.ErrCmdParseInvalParam
	}

	// parse the position
	position := strings.Split((*pIm).Params[protocol.PositionIndex], protocol.NumDelimiter)

	nums := make([]int, 2)
	for i, num := range position {
		n, err := strconv.Atoi(num)
		if err != nil {
			logging.Warn(fmt.Sprintf("Error parsing action position: %s", err))
			return nil, custom_errors.ErrCmdParseInvalParam
		}
		nums[i] = n
	}

	// check if the position is valid
	if nums[0] < 0 || nums[0] >= protocol.BoardSize || nums[1] < 0 || nums[1] >= protocol.BoardSize {
		logging.Warn(fmt.Sprintf("Error parsing action position: invalid position: %v", nums))
		return nil, custom_errors.ErrCmdParseInvalParam
	}

	return nums, nil
}
