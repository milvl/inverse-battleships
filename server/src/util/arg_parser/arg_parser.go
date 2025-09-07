// are_parser is for parsing command line arguments
package arg_parser

import (
	"fmt"
	"os"
	"strings"
)

// Arguments struct to hold parsed arguments
type Arguments struct {
	Help          bool
	SocketAddress string
	ConfigPath    string
}

// isFlag checks if an argument is a flag
func isFlag(arg string) bool {
	return strings.HasPrefix(arg, "-")
}

// ParseArgs parses command-line arguments
func ParseArgs() (*Arguments, error) {
	if len(os.Args) == 1 {
		return &Arguments{Help: true}, nil
	}

	args := os.Args[1:] // skip the program name
	parsed := Arguments{
		Help:          false,
		SocketAddress: "",
		ConfigPath:    "",
	}

	// check for help flag
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "-h", "--help":
			parsed.Help = true
			return &parsed, nil
		}
	}

	// handle other flags
	switch args[0] {
	case "-a", "--socket_address":
		if 1 < len(args) && !isFlag(args[1]) {
			parsed.SocketAddress = args[1]
			return &parsed, nil
		} else {
			return nil, fmt.Errorf("-a/--socket_address requires a value")
		}

	case "-c", "--cfg_path":
		if 1 < len(args) && !isFlag(args[1]) {
			parsed.ConfigPath = args[1]
			return &parsed, nil
		} else {
			return nil, fmt.Errorf("-c/--cfg_path requires a value")
		}

	default:
		return nil, fmt.Errorf("unknown argument: %s", args[0])
	}
}
