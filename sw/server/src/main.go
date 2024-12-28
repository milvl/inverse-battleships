// main.go
package main

import (
	"context"
	"fmt"
	"inverse-battleships-server/const/exit_codes"
	"inverse-battleships-server/const/msg"
	"inverse-battleships-server/logging"
	"inverse-battleships-server/server"
	"inverse-battleships-server/util"
	"inverse-battleships-server/util/arg_parser"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	// to handle signals
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	// parse the command-line arguments
	args, err := arg_parser.ParseArgs()
	if err != nil {
		logging.Error(fmt.Sprintf("Error parsing arguments: %s", err))
		os.Exit(exit_codes.ExitFailure)
	}
	if args.Help {
		fmt.Print(msg.HelpMsg)
		os.Exit(exit_codes.ExitSuccess)
	}

	var sockAddr string
	if args.SocketAddress != "" {
		sockAddr = args.SocketAddress
	} else if args.ConfigPath != "" {
		// load the server configuration
		config, err := util.LoadConfig(args.ConfigPath)
		if err != nil {
			os.Exit(exit_codes.ExitFailure)
		}

		sockAddr = config.ServerAddress + ":" + fmt.Sprintf("%d", config.ServerPort)
	} else {
		logging.Error("No socket address or configuration file provided")
		os.Exit(exit_codes.ExitFailure)
	}

	p_server := server.NewServer(sockAddr)
	p_cl_man := server.NewClientManager(p_server)

	err = p_cl_man.ManageServer(ctx)
	if err != nil {
		logging.Error(fmt.Sprintf("Error managing server: %s", err))
		os.Exit(exit_codes.ExitFailure)
	}
}
