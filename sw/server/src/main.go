// main.go
package main

import (
	"context"
	"inverse-battleships-server/server"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	// to handle signals
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	p_server := server.NewServer("127.0.0.1:8080")
	p_cl_man := server.NewClientManager(p_server)

	p_cl_man.ManageServer(ctx)
}
