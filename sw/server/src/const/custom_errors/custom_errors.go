// custom_errors package represents custom errors defined in the project.
package custom_errors

import "errors"

// ErrNilPointer is an error that occurs when a nil pointer is encountered.
var ErrNilPointer = errors.New("nil pointer error")

// ErrNilConn is an error that occurs when a nil connection is encountered.
var ErrNilConn = errors.New("nil connection error")

// ErrInvalidCommand is an error that occurs when an invalid command is encountered.
var ErrInvalidCommand = errors.New("invalid command")
