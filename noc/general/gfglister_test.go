package gfglister

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/require"
	zzap "go.uber.org/zap"
	"go.uber.org/zap/zaptest/observer"
	"golang.org/x/sync/errgroup"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/gfglister/pkg/api"
	"a.yandex-team.ru/noc/go/metrics"
	"a.yandex-team.ru/noc/topka/pkg/topka/cluster"
)

var wayback = time.Date(2022, time.June, 7, 13, 40, 9, 0, time.UTC)
var metConf = metrics.Config{
	Pull: &metrics.Pull{Enabled: true},
	Push: nil,
}

func makeTestLogger() (log.Logger, *observer.ObservedLogs) {
	zlcore, logged := observer.New(zzap.DebugLevel)
	logger := zap.NewWithCore(zlcore)
	return logger, logged
}

func makeRequest(t *testing.T, e *echo.Echo, handler echo.HandlerFunc, reqData string) {
	as := require.New(t)
	rec := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/", strings.NewReader(reqData))
	req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
	c := e.NewContext(req, rec)
	as.NoError(handler(c))
	as.Equal(http.StatusOK, rec.Code)
	resp := api.Response{}
	err := json.Unmarshal(rec.Body.Bytes(), &resp)
	as.NoError(err)
	as.Equal(resp.Response, "OK")
	as.Equal(resp.Code, 200)
}

type fakeINVAPI struct {
	hosts []string
}

func (f fakeINVAPI) Update(ctx context.Context) (err error) {
	return nil
}

func (f fakeINVAPI) Check(hostname string) (found bool, err error) {
	return true, err
}

func (f fakeINVAPI) List() []string {
	return f.hosts
}

type fakeZK struct {
}

func (m fakeZK) IsMaster() bool {
	return true
}

func (m fakeZK) Master() string {
	return ""
}

func (m fakeZK) Run(ctx context.Context, ch chan<- cluster.ElectionEvent) error {
	<-ctx.Done()
	return ctx.Err()
}

type testConfigGetter struct {
	log log.Logger
}

func newTestConfigGetter(log log.Logger) *testConfigGetter {
	return &testConfigGetter{log: log}
}

func (m testConfigGetter) Get(ctx context.Context, hostname string) (map[string][]byte, error) {
	return map[string][]byte{oneConfPath: []byte(hostname + "_config")}, nil
}

type testConfigSaver struct {
	log     log.Logger
	configs []configRes
}

func newtestConfigSaver(log log.Logger) *testConfigSaver {
	return &testConfigSaver{log: log}
}

func (m *testConfigSaver) Save(ctx context.Context, config configRes) (bool, error) {
	m.configs = append(m.configs, config)
	return false, nil
}

func (m *testConfigSaver) Periodical(ctx context.Context) error {
	return nil
}

func TestCfgNoSyslog(t *testing.T) {
	now = func() time.Time {
		return wayback
	}
	host := "vla-47d8.yndx.net"
	reqData := `{
		  "data": {
			"fqdn": "` + host + `",
			"ip": "2a02:6b8:0:c011:0:210:c:9f",
			"timestamp": ` + strconv.FormatInt(wayback.Unix()+1, 10) + `,
			"committer": "olo"
		  },
		  "format": "post_fn_config",
		  "uuid": "b2f51ade-7935-4d6c-afa6-94d9718169bd",
		  "hostname": "vla-snmptrap1.net.yandex.net"
		}`
	as := require.New(t)
	logger, _ := makeTestLogger()
	confSaver := newtestConfigSaver(logger)
	invapi := fakeINVAPI{hosts: []string{"vla-47d8.yndx.net"}}
	met, err := metrics.New(&metConf, logger.WithName("metrics"))
	as.NoError(err)
	app, err := MakeApp(logger, NewDefaultConf(), newTestConfigGetter(logger), confSaver, fakeZK{}, invapi, met)
	as.NoError(err)
	e := echo.New()
	_, err = app.runFilterResolve(context.Background())
	as.NoError(err)
	makeRequest(t, e, app.handleWebHookRequest, reqData)
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(float64(commentMaxDuration)*1.5))
	defer cancel()
	wg, wCtx := errgroup.WithContext(ctx)
	wg.Go(func() error {
		return app.Run(wCtx)
	})
	err = wg.Wait()
	as.Error(err)
	as.Len(confSaver.configs, 1)
	conf := confSaver.configs[0]
	as.Equal(configRes{
		hostname:   host,
		config:     hostConf{oneConfPath: []byte(host + "_config")},
		additional: "originated by confChangeSourceTrap\nfrom snmptrap committer olo",
	}, conf)
}

func TestCfgSyslog(t *testing.T) {
	now = func() time.Time {
		return wayback
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	host := "vla-47d8.yndx.net"
	reqData := `{
		"data": {
			"fromhost-ip": "64:ff9b::ac18:72e1",
			"fromhost": "64:ff9b::ac18:72e1",
			"timegenerated": "` + wayback.Format(time.RFC3339) + `",
			"timestamp": "2022-06-19T16:39:13+03:00",
			"host": "` + host + `",
			"severity": 6,
			"facility": 23,
			"syslog-tag": "%%01CONFIGURATION/6/hwcfgmaneventlog(t):",
			"source": "%%01CONFIGURATION",
			"msg": "CID=0x80cb000c-OID=1.3.6.1.4.1.2011.6.10.2.1;Configuration file was changed. (LogIndex=1, SrcCmd=1, SrcData=2, DestData=4, TerUser=\"racktables\", SrcAddr=77.88.1.117, ConfigChangeId=1331, LogTime=518127131, CfgBaselineTime=\"2019-07-31 12:02:27\")"
		},
		"uuid": "d3d30d44-65ff-4f30-a048-30f17683ec6b",
		"name": "config",
		"format": "syslog",
		"hostname": "sas-metridatag1.net.yandex.net"
	}
`
	reqDataTrap := `{
		  "data": {
			"fqdn": "` + host + `",
			"ip": "2a02:6b8:0:c011:0:210:c:9f",
			"timestamp": ` + strconv.FormatInt(wayback.Unix()+1, 10) + `,
			"committer": ""
		  },
		  "format": "post_fn_config",
		  "uuid": "b2f51ade-7935-4d6c-afa6-94d9718169bd",
		  "hostname": "vla-snmptrap1.net.yandex.net"
		}`
	as := require.New(t)
	logger, _ := makeTestLogger()
	confSaver := newtestConfigSaver(logger)
	invapi := fakeINVAPI{hosts: []string{"vla-47d8.yndx.net"}}
	met, err := metrics.New(&metConf, logger.WithName("metrics"))
	as.NoError(err)
	app, err := MakeApp(logger, NewDefaultConf(), newTestConfigGetter(logger), confSaver, fakeZK{}, invapi, met)
	as.NoError(err)
	e := echo.New()
	_, err = app.runFilterResolve(ctx)
	as.NoError(err)
	makeRequest(t, e, app.handleWebHookRequest, reqData)
	makeRequest(t, e, app.handleWebHookRequest, reqDataTrap)
	ctx, cancel = context.WithTimeout(ctx, time.Duration(float64(commentMaxDuration)*1.5))
	defer cancel()
	wg, wCtx := errgroup.WithContext(ctx)
	wg.Go(func() error {
		return app.Run(wCtx)
	})
	err = wg.Wait()
	as.Error(err)
	as.Len(confSaver.configs, 1)
	conf := confSaver.configs[0]
	as.Equal(configRes{
		hostname:   host,
		config:     hostConf{oneConfPath: []byte(host + "_config")},
		additional: "originated by confChangeSourceSyslog\nfrom syslog info: %%01CONFIGURATION/6/hwcfgmaneventlog(t):CID=0x80cb000c-OID=1.3.6.1.4.1.2011.6.10.2.1;Configuration file was changed. (LogIndex=1, SrcCmd=1, SrcData=2, DestData=4, TerUser=\"racktables\", SrcAddr=77.88.1.117, ConfigChangeId=1331, LogTime=518127131, CfgBaselineTime=\"2019-07-31 12:02:27\")\nfrom snmptrap",
	}, conf)
}
