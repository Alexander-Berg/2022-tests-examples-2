package logger

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/traffic/blockscheme/blocklist-monitoring/internal/config"
)

func TestLoggerError(t *testing.T) {
	t.Run("write error message", func(t *testing.T) {
		logger, err := NewLogger(&config.Config{
			Logger: config.LoggerParams{
				Level:  "debug",
				Format: "Console",
			}})

		require.NoError(t, err)
		logger.Errorf("test no cause exception")
	})
}
