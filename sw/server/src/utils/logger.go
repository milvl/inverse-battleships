// TODO rewrite

package utils

import (
	"fmt"
	"log"
	"os"
	"time"
)

// LogLevel defines different levels of logging
type LogLevel uint8

// Enum values for LogLevel
const (
	DEBUG LogLevel = iota
	INFO
	WARNING
	ERROR
	CRITICAL
)

// Mapping of colors to log levels
var colors = map[LogLevel]string{
	DEBUG:    "\033[36m", // cyan
	INFO:     "\033[37m", // white
	WARNING:  "\033[33m", // yellow
	ERROR:    "\033[31m", // red
	CRITICAL: "\033[41m", // red background
}

// Reset color code
const resetColor = "\033[0m"

// Logger struct with configurable output
type Logger struct {
	Level    LogLevel
	Output   *log.Logger
	MinLevel LogLevel
}

// NewLogger creates a new Logger instance
func NewLogger(minLevel LogLevel) *Logger {
	return &Logger{
		Level:    minLevel,
		Output:   log.New(os.Stdout, "", 0),
		MinLevel: minLevel,
	}
}

// logMessage logs a message at the given level
func (l *Logger) logMessage(level LogLevel, message string) {
	// sanity check
	if level < l.MinLevel {
		return
	}

	timestamp := time.Now().Format("15:04:05")
	colorCode := colors[level]
	logMsg := fmt.Sprintf("%s[%s] - %s%s", colorCode, timestamp, message, resetColor)
	l.Output.Println(logMsg)
}

// Debug logs a message at DEBUG level
func (l *Logger) Debug(message string) {
	l.logMessage(DEBUG, message)
}

// Info logs a message at INFO level
func (l *Logger) Info(message string) {
	l.logMessage(INFO, message)
}

// Warn logs a message at WARNING level
func (l *Logger) Warn(message string) {
	l.logMessage(WARNING, message)
}

// Error logs a message at ERROR level
func (l *Logger) Error(message string) {
	l.logMessage(ERROR, message)
}

// Critical logs a message at CRITICAL level
func (l *Logger) Critical(message string) {
	l.logMessage(CRITICAL, message)
}
