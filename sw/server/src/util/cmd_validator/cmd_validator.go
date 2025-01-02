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
		fallthrough
	case protocol.CmdCreateLobby:
		fallthrough
	case protocol.CmdClientReady:
		if len(parts) < protocol.MinPartsCount {
			return nil, fmt.Errorf("invalid format - not enough parts")
		}

	// 2 parts needed
	case protocol.CmdHandshakeReqv:
		if len(parts) != protocol.MinPartsCount+1 {
			return nil, fmt.Errorf("invalid format - not enough parts")
		}

	// variable number of parts
	case protocol.CmdJoinLobby:
		if len(parts) > 3 {
			return nil, fmt.Errorf("invalid format - too many parts")
		}

	default:
		logging.Debug(fmt.Sprintf("Unknown command: %s", selectedCmd))
		return nil, fmt.Errorf("unknown command to parse")
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

// validateNoParams validates a message with no parameters.
func validateNoParams(pIm *IncomingMessage) error {
	// sanity check
	if pIm == nil {
		return custom_errors.ErrNilPointer
	}

	// check if there are no parameters
	if len((*pIm).Params) != 0 {
		return fmt.Errorf("message has unexpected number of parameters")
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
func ValidatePing(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdPing)
	if err != nil {
		return err
	}

	err = validateNoParams(pIm)
	if err != nil {
		return err
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

	err = validateNoParams(pIm)
	if err != nil {
		return err
	}

	return nil
}

// ValidateHandshakeConfirmation validates a handshake confirmation.
func ValidateHandshakeConfirmation(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdHandshakeAck)
	if err != nil {
		return err
	}

	err = validateNoParams(pIm)
	if err != nil {
		return err
	}

	return nil
}

// ValidateLeave validates a leave message.
func ValidateLeave(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdLeave)
	if err != nil {
		return err
	}

	err = validateNoParams(pIm)
	if err != nil {
		return err
	}

	return nil
}

// ValidateLobbies validates a lobbies message.
func ValidateLobbies(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdLobbies)
	if err != nil {
		return err
	}

	err = validateNoParams(pIm)
	if err != nil {
		return err
	}

	return nil
}

// ValidateCreateLobby validates a create lobby message.
func ValidateCreateLobby(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdCreateLobby)
	if err != nil {
		return err
	}

	err = validateNoParams(pIm)
	if err != nil {
		return err
	}

	return nil
}

// ValidateJoinLobby validates a join lobby message.
func ValidateJoinLobby(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdJoinLobby)
	if err != nil {
		return err
	}

	// check if the lobby ID is valid
	if len((*pIm).Params) != 1 {
		return fmt.Errorf("message has unexpected number of parameters")
	}

	if (*pIm).Params[protocol.LobbyIDIndex] == "" {
		return fmt.Errorf("lobby ID is empty")
	}

	return nil
}

// ValidateClientReady validates a ready message.
func ValidateClientReady(pIm *IncomingMessage) error {
	// sanity check
	err := validateCommand(pIm, protocol.CmdClientReady)
	if err != nil {
		return err
	}

	err = validateNoParams(pIm)
	if err != nil {
		return err
	}

	return nil
}
