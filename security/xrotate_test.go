package xlog_test

import (
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/security/libs/go/xlog"
)

func TestXRotateSink(t *testing.T) {
	testLogFilename := "test.log"
	testDir := "testLogrotate"

	// use test dir in default temp files location
	tempDir, err := os.MkdirTemp("", testDir)
	require.NoError(t, err)

	testLogPath := filepath.Join(tempDir, testLogFilename)

	defer func() {
		_ = os.RemoveAll(tempDir)
	}() // clean up

	err = xlog.RegisterXRotateSink(xlog.WithXRotateMaxSize(1024))
	require.NoError(t, err)

	cfg := zap.JSONConfig(log.DebugLevel)
	cfg.OutputPaths = []string{
		xlog.LogURL(testLogPath),
	}
	logger, err := zap.New(cfg)
	require.NoError(t, err, "failed to create logger")

	_, err = os.Stat(testLogPath)
	require.NoError(t, err, "expected logger to create file: %v", err)

	// test write to file
	logger.Debug(strings.Repeat("A", 1024))
	logger.Debug("test_A")

	requireLineCount(t, testLogPath, 1)
	requireContains(t, testLogPath, "test_A")
	requireLineCount(t, testLogPath+".old", 1)
	requireContains(t, testLogPath+".old", strings.Repeat("A", 1024))

	logger.Debug("test_B")
	requireLineCount(t, testLogPath, 2)
	requireContains(t, testLogPath, "test_B")
	requireLineCount(t, testLogPath+".old", 1)

	logger.Debug(strings.Repeat("C", 1024))
	logger.Debug("test_C")
	requireLineCount(t, testLogPath, 1)
	requireContains(t, testLogPath, "test_C")
	requireLineCount(t, testLogPath+".old", 3)
	requireContains(t, testLogPath+".old", strings.Repeat("C", 1024))
}

func requireLineCount(t *testing.T, path string, lines int) {
	file, err := os.OpenFile(path, os.O_RDONLY, 0)
	require.NoError(t, err, "failed to open log file for reading")
	defer func() { _ = file.Close() }()
	dataRead, err := io.ReadAll(file)
	require.NoError(t, err, "failed to read log file")
	require.Equal(t, lines, strings.Count(string(dataRead), "\n"))
}

func requireContains(t *testing.T, path string, substr string) {
	file, err := os.OpenFile(path, os.O_RDONLY, 0)
	require.NoError(t, err, "failed to open log file for reading")
	defer func() { _ = file.Close() }()
	dataRead, err := io.ReadAll(file)
	require.NoError(t, err, "failed to read log file")
	require.Contains(t, string(dataRead), substr)
}
