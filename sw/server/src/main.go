// main.go
package main

import (
	"inverse-battleships-server/utils"
)

func main() {
	p_logger := utils.NewLogger(utils.INFO)
	p_logger.Info("Hello from Logger!")
	utils.PrintHello()
	p_logger.Debug("About to exit...")
	p_logger.Warn("Exiting...")
	p_logger.Critical("Exiting...")
	p_logger.Error("Exiting...")
	p_logger.Info("Program exited.")
}
