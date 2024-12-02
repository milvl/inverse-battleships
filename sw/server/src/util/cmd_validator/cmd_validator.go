package cmd_validator

import (
	"fmt"
	"inverse-battleships-server/const/protocol"
	"unicode"
)

const (
	maxPlayerNameLength = 20
)

// IncomingMessage represents a message received from a client.
type IncomingMessage struct {
	Command string
	Parts   []string
}

// ToString returns a string representation of the message.
func (p_im *IncomingMessage) ToString() string {
	return fmt.Sprintf("Command: %s, Parts: %v", p_im.Command, p_im.Parts)
}

// GetCommand validates a client response.
func GetCommand(parts []string) (*IncomingMessage, error) {
	// sanity check
	if parts == nil {
		return nil, fmt.Errorf("parts is nil")
	}

	// check if the message is a valid handshake request
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
	return &IncomingMessage{Command: selectedCmd, Parts: parts[protocol.MinPartsCount:]}, nil
}

func validateCommand(p_im *IncomingMessage, expectedCmd string) error {
	// sanity check
	if p_im == nil {
		return fmt.Errorf("incoming message is nil")
	}
	if expectedCmd == "" {
		return fmt.Errorf("expected command is empty")
	}

	// check if the message is a valid handshake request
	if (*p_im).Command != expectedCmd {
		return fmt.Errorf("command is invalid - expected %s, got %s", expectedCmd, (*p_im).Command)
	}

	return nil
}

// ValidateHandshake validates a handshake request.
func ValidateHandshake(p_im *IncomingMessage) error {
	// sanity check
	err := validateCommand(p_im, protocol.CmdHandshakeReqv)
	if err != nil {
		return err
	}

	// check if the nickname is valid
	nickname := (*p_im).Parts[protocol.NicknameIndex]
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
func ValidatePong(p_im *IncomingMessage) error {
	// sanity check
	err := validateCommand(p_im, protocol.CmdPong)
	if err != nil {
		return err
	}

	return nil
}

// ValidateHandshakeConfirmation validates a handshake confirmation.
func ValidateHandshakeConfirmation(p_im *IncomingMessage) error {
	// sanity check
	if p_im == nil {
		return fmt.Errorf("incoming message is nil")
	}

	// check if the message is a valid handshake request
	if (*p_im).Command != protocol.CmdHandshakeAck {
		return fmt.Errorf("handshake request is invalid")
	}

	return nil
}
