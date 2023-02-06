package loggers

import (
	"context"
	"fmt"
	"io/ioutil"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/passport/shared/golibs/logger"
)

func TestQuote(t *testing.T) {
	logPath := yatest.OutputPath("tskv_test.log")
	_ = os.Remove(logPath)

	log, err := NewTskvLog(logger.Config{
		FilePath: logPath,
	})
	require.NoError(t, err)

	contextLog := log.WithContext(context.Background())

	ts := time.Unix(1647439939, 0)
	tsStr := ts.Local().Format("2006-01-02T15:04:05")
	contextLog.LogAction(ts, "provider", ActionDelete, GateEntity, "113", map[string]string{"some": "field"})

	content, err := ioutil.ReadFile(logPath)
	require.NoError(t, err)

	lines := strings.Split(string(content), "\n")
	require.NotEqual(t, len(lines), 0)
	if lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}
	require.Equal(t, 1, len(lines))

	require.Equal(t, lines[0], fmt.Sprintf("tskv\ttskv_format=action\tdate=%s\tunixtime=1647439939\tuser=-\tprovider=provider\taction=delete\tentity=gate\tid=113\tsome=field", tsStr))
}
