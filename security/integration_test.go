package integration_test

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/csp-report/integration"
	"a.yandex-team.ru/security/csp-report/internal/app"
	"a.yandex-team.ru/security/csp-report/internal/config"
)

var (
	defaultCfg = &config.Config{
		LogLevel: log.InfoString,
		App: config.AppConfig{
			ReadTimeout:        4 * time.Second,
			WriteTimeout:       3 * time.Second,
			IdleTimeout:        1 * time.Second,
			ShutdownTimeout:    1 * time.Minute,
			ReportWriteTimeout: 500 * time.Millisecond,
			MaxBodySize:        5 << 10,
		},
		Logbroker: config.LogbrokerConfig{
			QueueSize:       1024,
			ShutdownTimeout: 1 * time.Minute,
		},
	}
)

func getAllReports(t *testing.T, e *integration.LbEnv, count int) (messages [][]byte) {
	readerPath, err := yatest.BinaryPath("security/csp-report/integration/reader/reader")
	require.NoError(t, err)

	cmd := exec.Command(
		readerPath,
		"--endpoint", e.Endpoint,
		"--port", strconv.Itoa(e.Port),
		"--consumer", e.Consumer,
		"--topic", e.Topic,
		"--max-msgs", strconv.Itoa(count),
	)

	var stdout bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = os.Stderr

	err = cmd.Run()
	require.NoError(t, err)

	err = json.Unmarshal(stdout.Bytes(), &messages)
	require.NoError(t, err)
	return
}

func TestSmoke(t *testing.T) {
	l, err := zap.New(zap.ConsoleConfig(log.DebugLevel))
	require.NoError(t, err)

	cfg := *defaultCfg

	// configure app
	cfg.App.Addr, err = integration.GetFreeAddr()
	require.NoError(t, err)

	// configure lb writer
	lbEnv, stop := integration.NewLbEnv(t)
	defer stop()

	dbPath, err := ioutil.TempDir("", "csp_report_smoke")
	require.NoError(t, err)

	cfg.Logbroker.Endpoint = fmt.Sprintf("%s:%d", lbEnv.Endpoint, lbEnv.Port)
	cfg.Logbroker.Topic = lbEnv.Topic
	cfg.Logbroker.DBPath = dbPath
	cfg.Logbroker.Writers = 1

	instance, err := app.New(&cfg, app.WithLogger(l))
	require.NoError(t, err)

	go func() {
		l.Info("starting application", log.String("addr", cfg.App.Addr))
		err := instance.Start()
		if err != nil && err != http.ErrServerClosed {
			require.NoError(t, err)
		} else {
			l.Info("server stopped")
		}
	}()

	// wait while server starts
	httpc := resty.New().SetBaseURL("http://" + cfg.App.Addr)
	for i := 0; i < 100; i++ {
		_, err := httpc.R().Get("/ping")
		if err == nil {
			break
		}
		l.Info("server not starts, wait", log.Error(err))
		time.Sleep(100 * time.Millisecond)
	}

	cases := []struct {
		uri         string
		content     []byte
		origin      string
		addr        string
		userAgent   string
		contentType string
		formatted   string
		scheduled   bool
	}{
		{
			uri:         "/csp?small-json",
			contentType: "application/json",
			content:     []byte(`{"lol":"kek"}`),
			addr:        "127.0.0.1",
			origin:      "http://small-json",
			userAgent:   "small-json",
			scheduled:   true,
			formatted: `tskv
tskv_format=csp-log
addr=127.0.0.1
path=/csp?small-json
user-agent=small-json
origin=http://small-json
content={"lol":"kek"}
`,
		},
		{
			uri:         "/csp?small-csp-report",
			contentType: "application/csp-report",
			content:     []byte(`{"lol": 1, "kek": 2,"cheburek": 3}`),
			addr:        "127.0.0.2",
			origin:      "http://small-csp-report",
			userAgent:   "small-csp-report",
			scheduled:   true,
			formatted: `tskv
tskv_format=csp-log
addr=127.0.0.2
path=/csp?small-csp-report
user-agent=small-csp-report
origin=http://small-csp-report
content={"lol": 1, "kek": 2,"cheburek": 3}
`,
		},
		{
			uri:         "/csp?small-some-shit",
			contentType: "application/x-www-form-urlencoded",
			content:     []byte(`lala=blabla`),
			addr:        "127.0.0.3",
			origin:      "http://small-some-shit",
			userAgent:   "small-some-shit",
			scheduled:   true,
			formatted: `tskv
tskv_format=csp-log
addr=127.0.0.3
path=/csp?small-some-shit
user-agent=small-some-shit
origin=http://small-some-shit
content=lala\=blabla
`,
		},
		{
			uri:         "/csp?broken-body-json",
			contentType: "application/json",
			content:     []byte(`lala`),
			addr:        "127.0.0.4",
			origin:      "http://small",
			scheduled:   false,
		},
		{
			uri:         "/csp?broken-body-csp-report",
			contentType: "application/csp-report",
			content:     []byte(`blabla`),
			addr:        "127.0.0.5",
			origin:      "http://small",
			scheduled:   false,
		},
		{
			uri:         "/csp?broken-body-too-big",
			contentType: "application/csp-report",
			content:     make([]byte, 1024<<10),
			addr:        "127.0.0.6",
			origin:      "http://small",
			scheduled:   false,
		},
	}

	for _, cs := range cases {
		t.Run("send/"+cs.uri, func(t *testing.T) {
			rsp, err := httpc.R().
				SetHeader("Content-Type", cs.contentType).
				SetHeader("X-Forwarded-For-Y", cs.addr).
				SetHeader("User-Agent", cs.userAgent).
				SetHeader("Origin", cs.origin).
				SetBody(cs.content).
				Post(cs.uri)

			require.NoError(t, err)
			require.Equal(t, 200, rsp.StatusCode())
			require.Equal(t, "*", rsp.Header().Get("Access-Control-Allow-Origin"))
		})
	}

	defer func() {
		err = instance.Shutdown(context.Background())
		require.NoError(t, err)
	}()

	expectedCount := 0
	for _, cs := range cases {
		if cs.scheduled {
			expectedCount++
		}
	}

	reports := getAllReports(t, lbEnv, expectedCount)
	for _, cs := range cases {
		if !cs.scheduled {
			continue
		}

		t.Run("search/"+cs.uri, func(t *testing.T) {
			expectedReport := strings.ReplaceAll(cs.formatted, "\n", "\t")
			expectedReportBytes := []byte(expectedReport)
			found := false
			for _, report := range reports {
				if bytes.HasPrefix(report, expectedReportBytes) {
					found = true
					break
				}
			}

			require.True(t, found, "report not found: %s", expectedReport)
		})
	}
}
