package msg_parser

import (
	"fmt"
	"inverse-battleships-server/const/protocol"
	"strings"
	"unicode"
)

// ToNetMessage converts a list of strings to a network message.
// It adds the header and terminator to the message.
func ToNetMessage(parts []string) (string, error) {
	// sanity check
	if parts == nil {
		return "", fmt.Errorf("parts is nil")
	}

	for i, part := range parts {
		// part must not contain the terminator anywhere in the string
		if strings.Contains(part, protocol.MsgTerminator) {
			return "", fmt.Errorf("part contains terminator")
		}

		// escape the delimiter if present
		if strings.Contains(part, protocol.MsgDelimiter) {
			parts[i] = strings.ReplaceAll(part, protocol.MsgDelimiter, "\\"+protocol.MsgDelimiter)
		}
	}

	msg := ""
	msg += protocol.MsgHeader
	for _, part := range parts {
		msg += protocol.MsgDelimiter
		msg += part
	}
	msg += protocol.MsgTerminator

	return msg, nil
}

// FromNetMessage converts a network message to a list of strings.
func FromNetMessage(msg string) ([]string, error) {
	// sanity check
	if msg == "" {
		return nil, fmt.Errorf("message is empty")
	}

	// process the message
	var parts []string
	processedMsg := strings.Builder{}
	doEscape := false
	for _, char := range msg {
		// check for msg end
		if string(char) == protocol.MsgTerminator {
			parts = append(parts, processedMsg.String())
			break
		}

		// check for invalid character (non-printable)
		if !unicode.IsPrint(rune(char)) {
			return nil, fmt.Errorf("invalid (non-printable) character detected: %d", char)
		}

		// check for escape character
		if !doEscape && string(char) == protocol.MsgEscape {
			doEscape = true
			continue
		}

		// escaping segment
		if doEscape {
			processedMsg.WriteRune(rune(char))
			doEscape = false

			// normal segment
		} else {
			// check for terminator
			if string(char) == protocol.MsgTerminator {
				parts = append(parts, processedMsg.String())
				break

				// check for delimiter
			} else if string(char) == protocol.MsgDelimiter {
				parts = append(parts, processedMsg.String())
				processedMsg.Reset()

				// normal character
			} else {
				processedMsg.WriteRune(rune(char))
			}
		}
	}

	return parts, nil
}
