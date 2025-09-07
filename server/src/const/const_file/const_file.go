// const_file contains the file paths for the server
package const_file

// Config is the server configuration.
type Config struct {
	ServerAddress string `json:"server_address"` // maps to "server_address" in JSON
	ServerPort    int    `json:"server_port"`    // maps to "server_port" in JSON
}

// OpenPermissions is the permission to open a file.
const OpenPermissions = 0444
