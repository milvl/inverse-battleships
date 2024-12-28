package cmd_validator

import (
	"fmt"
	"inverse-battleships-server/const/custom_errors"
	"inverse-battleships-server/const/protocol"
	"inverse-battleships-server/logging"
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

	if !protocol.IsValidCmd(selectedCmd) {
		return nil, fmt.Errorf("invalid format - unknown command")
	}

	// check for validity of the command and the number of parts associated with it
	switch selectedCmd {
	// at least 1 part needed
	case protocol.CmdHandshakeAck:
		fallthrough
	case protocol.CmdLeave:
		fallthrough
	case protocol.CmdPing:
		fallthrough
	case protocol.CmdPong:
		fallthrough
	case protocol.CmdLobbies:
		if len(parts) < protocol.MinPartsCount {
			return nil, fmt.Errorf("invalid format - not enough parts")
		}

	// at least 2 parts needed
	case protocol.CmdHandshakeReqv:
		if len(parts) < protocol.MinPartsCount+1 {
			return nil, fmt.Errorf("invalid format - not enough parts")
		}

	default:
		return nil, fmt.Errorf("logic error - should not happen")
	}

	// return only real parts (use slicing)
	return &IncomingMessage{Command: selectedCmd, Params: parts[protocol.MinPartsCount:]}, nil
}

// validateCommand validates a command.
func validateCommand(pIm *IncomingMessage, expectedCmd string) error {
	// sanity check
	if pIm == nil {
		return custom_errors.ErrNilPointer
	}
	if expectedCmd == "" {
		return fmt.Errorf("expected command is empty")
	}

	// check if the message is a valid handshake request
	if (*pIm).Command != expectedCmd {
		logging.Debug(fmt.Sprintf("Expected: %s, Got: %s", expectedCmd, (*pIm).Command))
		return custom_errors.ErrInvalidCommand
	}

	return nil
}

// ValidateHandshake validates a handshake request.
func ValidateHandshake(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdHandshakeReqv)
	if err != nil {
		return err
	}

	// check if the nickname is valid
	nickname := (*pIm).Params[protocol.NicknameIndex]
	if nickname == "" {
		return fmt.Errorf("nickname is empty")
	}
	if len(nickname) > maxPlayerNameLength {
		return fmt.Errorf("nickname is too long")
	}
	for _, char := range nickname {
		if !unicode.IsPrint(char) {
			return fmt.Errorf("nickname contains invalid characters")
		}
	}

	return nil
}

// ValidatePing validates a ping message.
func ValidatePong(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdPong)
	if err != nil {
		return err
	}

	return nil
}

// ValidateHandshakeConfirmation validates a handshake confirmation.
func ValidateHandshakeConfirmation(pIm *IncomingMessage) error {
	// sanity check
	if pIm == nil {
		return custom_errors.ErrNilPointer
	}

	// check if the message is a valid handshake request
	if (*pIm).Command != protocol.CmdHandshakeAck {
		return fmt.Errorf("handshake request is invalid")
	}

	return nil
}
