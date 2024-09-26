package logging

import (
	"fmt"
	"log"
	"os"
	"path"
	"runtime"
	"sync"
	"time"
)

// LogLevel defines different levels of logging
type LogLevel uint8

// Enum values for LogLevel
const (
	DEBUG    LogLevel = 1 << iota // 1 << 0 == 1
	INFO                          // 1 << 1 == 2
	WARNING                       // 1 << 2 == 4
	ERROR                         // 1 << 3 == 8
	CRITICAL                      // 1 << 4 == 16
)

// Default allowed log levels
const defaultAllowedLevels = DEBUG | INFO | WARNING | ERROR | CRITICAL

// Default time format
const defaultTimeFormat = "15:04:05.000000"

// Default trace call
const defaultDoTraceCall = true

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

// Mapping of log levels to string
var logLevelStrings = map[LogLevel]string{
	DEBUG:    "DEBUG",
	INFO:     "INFO",
	WARNING:  "WARNING",
	ERROR:    "ERROR",
	CRITICAL: "CRITICAL",
}

// Logger struct with configurable output
type Logger struct {
	enabledLevels LogLevel
	timeFormat    string
	doTraceCall   bool
	Output        *log.Logger
}

// Global logger instance
var (
	globalLogger *Logger
	once         sync.Once
	defaultOut   = os.Stdout
)

// NewDefaultLogger creates a new logger instance with default configuration.
func NewDefaultLogger() *Logger {
	return NewLogger(defaultAllowedLevels, defaultTimeFormat, defaultDoTraceCall, defaultOut)
}

// NewLogger creates a new logger instance with the given configuration.
// Argument enabledLevels is a bitmask of LogLevel values.
// Example usage: "DEBUG" returns a logger that logs messages at the DEBUG level.
// Example usage: "DEBUG | INFO | WARNING" returns a logger that logs messages at the DEBUG, INFO, and WARNING levels.
// If timeFormat is empty, no timestamp will be added.
func NewLogger(enabledLevels LogLevel, timeFormat string, doTraceCall bool, stream *os.File) *Logger {
	if stream == nil {
		stream = defaultOut // use default output if none is specified
	}

	return &Logger{
		enabledLevels: enabledLevels,
		timeFormat:    timeFormat,
		doTraceCall:   doTraceCall,
		Output:        log.New(stream, "", 0),
	}
}

// Global logger instance
func getGlobalLogger() *Logger {
	once.Do(func() {
		globalLogger = NewLogger(defaultAllowedLevels, defaultTimeFormat, defaultDoTraceCall, defaultOut)
	})

	return globalLogger
}

// Tells if the given level is allowed
func isAllowed(enabledLevels LogLevel, level LogLevel) bool {
	return (enabledLevels & level) != 0
}

// Colorizes a message with the given color
func colorize(color string, message string) string {
	return fmt.Sprintf("%s%s%s", color, message, resetColor)
}

// logMessage logs a message at the given level
func (l *Logger) logMessage(level LogLevel, message string) {
	if !isAllowed(l.enabledLevels, level) {
		return
	}

	numOfFramesTillCaller := 2

	// format: <timestamp> [<level>] [<file>:<line>] - <message>
	// example: 01:23:45:678 [INFO] (main.go:12) - Hello from Logger!
	levelString := logLevelStrings[level]
	timestamp := ""
	caller := ""

	// add timestamp if timeFormat is set
	if l.timeFormat != "" {
		timestamp = time.Now().Format(l.timeFormat)
	}

	// add caller if doTraceCall is set
	if l.doTraceCall {
		_, file, line, ok := runtime.Caller(numOfFramesTillCaller)
		if !ok {
			file = "???"
			line = 0
		}

		// extract only the file name
		file = path.Base(file)
		caller = fmt.Sprintf("(%s:%d)", file, line)
	}

	message = fmt.Sprintf("%s [%s] %s - %s", timestamp, levelString, caller, message)

	// colorize message if color is available
	if color, ok := colors[level]; ok {
		message = colorize(color, message)
	}

	l.Output.Println(message)
}

// Logs a message at the DEBUG level
func (l *Logger) Debug(message string) {
	l.logMessage(DEBUG, message)
}

// Logs a message at the INFO level
func (l *Logger) Info(message string) {
	l.logMessage(INFO, message)
}

// Logs a message at the WARNING level
func (l *Logger) Warn(message string) {
	l.logMessage(WARNING, message)
}

// Logs a message at the ERROR level
func (l *Logger) Error(message string) {
	l.logMessage(ERROR, message)
}

// Logs a message at the CRITICAL level
func (l *Logger) Critical(message string) {
	l.logMessage(CRITICAL, message)
}

// Logs a message at the CRITICAL level
func Debug(message string) {
	getGlobalLogger().logMessage(DEBUG, message)
}

// Logs a message at the INFO level
func Info(message string) {
	getGlobalLogger().logMessage(INFO, message)
}

// Logs a message at the WARNING level
func Warn(message string) {
	getGlobalLogger().logMessage(WARNING, message)
}

// Logs a message at the ERROR level
func Error(message string) {
	getGlobalLogger().logMessage(ERROR, message)
}

// Logs a message at the CRITICAL level
func Critical(message string) {
	getGlobalLogger().logMessage(CRITICAL, message)
}
