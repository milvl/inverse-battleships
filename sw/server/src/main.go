// main.go
package main

import (
	"inverse-battleships-server/logging"
	"inverse-battleships-server/utils"
)

func main() {
	logging.Info("Hello from Logger!")
	utils.PrintHello()
	logging.Debug("About to exit...")
	logging.Warn("Exiting...")
	logging.Critical("Exiting...")
	logging.Error("Exiting...")
	logging.Info("Program exited.")
}
