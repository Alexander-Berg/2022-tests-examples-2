package core

import (
	"errors"
	"fmt"
	"os"
	"testing"

	"github.com/sirupsen/logrus"

	"a.yandex-team.ru/noc/traffic/dns/junk/d2/events"

	"a.yandex-team.ru/noc/traffic/dns/junk/dns2-api/cmd/config"
)

const (
	TEST_CONFIG_FILE = "/home/slayer/arcadia/noc/traffic/dns/junk/dns2-api/legacy/dns2-api.yaml"
)

func GetSyncManager(t *testing.T) (*SyncManager, error) {
	var err error

	var g config.CmdGlobal
	g = config.CmdGlobal{Opts: &config.ConfYaml{}}
	*g.Opts, err = config.LoadConf(TEST_CONFIG_FILE)

	g.Log = logrus.New()
	g.Log.Formatter = &logrus.TextFormatter{
		TimestampFormat: "2006/01/02 - 15:04:05.000",
		FullTimestamp:   true,
	}
	level, _ := logrus.ParseLevel("debug")
	g.Log.Level = level
	g.Log.Out = os.Stdout

	g.CreateSingletons()

	g.Events = events.CreateEvents("/usr/bin/dns2-api", g.Log, nil,
		g.Opts.Dns2Api.Dns2ApiSocket)

	var core *Core
	if core, err = CreateCore(&g); err != nil {
		t.Error("core create failed", fmt.Sprintf(", err:'%s'", err))
	}

	var api *Api
	if api, err = core.CreateIntegrationCache(true, nil); err != nil {
		t.Error("api create failed", fmt.Sprintf(", err:'%s'", err))
	}

	api.core = core
	core.httpapi = api

	var SyncManager *SyncManager
	if SyncManager, err = CreateSyncManager(&g, api); err != nil {
		t.Error("sync manager create failed", fmt.Sprintf(", err:'%s'", err))
	}

	return SyncManager, err
}

// Main view resolve function implementing
// view api call function method
func TestViewResolve(t *testing.T) {

	var err error

	var SyncManager *SyncManager
	if SyncManager, err = GetSyncManager(t); err != nil {
		t.Error("sync manager create failed", fmt.Sprintf(", err:'%s'", err))
	}

	// We have here a cache of nodes ns3+ns4, as json file,
	// fetched from dns core masters, could be used as cache
	// /tmp/dns2-api-cluster-nodes-dynamic-ns3+ns4+others.json
	var output []byte
	if output, err = SyncManager.ViewResolve(); err != nil {
		t.Error("error view resolve", fmt.Sprintf(", err:'%s'", err))
	}

	l := len(output)
	if l == 0 {
		err = errors.New(fmt.Sprintf("view resolve content data length %d", l))
		t.Error("error view resolve", fmt.Sprintf(", err:'%s'", err))
	}
}

// Resoving fqdn in parallel threads till at least
// one node returns successfull resolve
func TestParallelResolve(t *testing.T) {

	var err error

	// disabling at least now
	return

	type TTestsTestParallelResolve struct {
		fqdn string
	}

	var TestsTestParallelResolve = []TTestsTestParallelResolve{
		{"tv.yandex.ua"},
		{"mail.yandex.ua"},
		{"push.yandex.ua"},
		{"market.yandex.ua"},
	}

	// possible values are DNS2_SERVER_PORT
	// resolving via SUBNET CLIENT NETWORK and
	// direct resolve via 53
	port := DNS2_SERVER_PORT

	var SyncManager *SyncManager
	if SyncManager, err = GetSyncManager(t); err != nil {
		t.Error("sync manager create failed", fmt.Sprintf(", err:'%s'", err))
	}

	class := "dynamic"
	var nodes []string
	if nodes, err = SyncManager.GetClusterNodes(class); err != nil {
		t.Error(fmt.Sprintf("error getting cluster nodes, class:'%s', err:'%s'", class, err))
	}

	l := len(nodes)
	if l == 0 {
		err = errors.New(fmt.Sprintf("zero nodes count returned %d", l))
		t.Error("error parallel resolve", fmt.Sprintf(", err:'%s'", err))
	}

	for _, pair := range TestsTestParallelResolve {
		fqdn := pair.fqdn
		var answer []string
		var ttl uint32
		if answer, ttl, err = SyncManager.ParallelResolve(nodes,
			fqdn, port); err != nil {
			t.Error(fmt.Sprintf("error resolving fqdn:'%s', class:'%s', err:'%s'",
				fqdn, class, err))
		}
		l = len(answer)
		if l == 0 {
			err = errors.New(fmt.Sprintf("fqdn:'%s' resolve content data zero length:'%d'", fqdn, l))
			t.Error("error fqdn resolve", fmt.Sprintf(", err:'%s'", err))
		}

		if ttl == 0 {
			err = errors.New(fmt.Sprintf("fqdn:'%s' resolve has incorrect ttl:'%d'", fqdn, ttl))
			t.Error("error fqdn resolve", fmt.Sprintf(", err:'%s'", err))
		}
	}
}
