// main.go
package main

import (
	"inverse-battleships-server/logging"
	"inverse-battleships-server/server"
	"inverse-battleships-server/utils"
)

func main() {
	logging.Info("Hello from Logger!")
	utils.PrintHello()

	p_server := server.NewServer("127.0.0.1:8080")
	p_cl_man := server.NewClientManager(p_server)

	p_cl_man.Test()

	logging.Debug("About to exit...")
	logging.Warn("Exiting...")
	logging.Critical("Exiting...")
	logging.Error("Exiting...")
	logging.Info("Program exited.")
}
