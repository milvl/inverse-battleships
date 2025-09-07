// util contains utility functions that are used throughout the server.
package util

import (
	"encoding/json"
	"fmt"
	"inverse-battleships-server/const/const_file"
	"inverse-battleships-server/logging"
	"os"
)

// LoadConfig loads the configuration from a file.
func LoadConfig(path string) (*const_file.Config, error) {
	logging.Info(fmt.Sprintf("Loading configuration from %s", path))

	// open the file
	pFile, err := os.OpenFile(path, os.O_RDONLY, const_file.OpenPermissions)
	if err != nil {
		logging.Error(fmt.Sprintf("Error opening the file %s: %s", path, err))
		return nil, err
	}
	defer pFile.Close()

	// unmarshal the configuration
	var config const_file.Config
	decoder := json.NewDecoder(pFile)
	err = decoder.Decode(&config)
	if err != nil {
		logging.Error(fmt.Sprintf("Error decoding the configuration file %s: %s", path, err))
		return nil, err
	}

	logging.Info(fmt.Sprintf("Configuration loaded successfully: %v", config))

	return &config, nil
}
