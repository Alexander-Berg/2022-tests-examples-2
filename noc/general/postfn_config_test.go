package decoder

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/snmptrapper/internal"
	"a.yandex-team.ru/noc/snmptrapper/internal/snmp"
)

func assertConfRes(t *testing.T, oidMap snmp.ResolvedOidMap, exp string, fn internal.PostFN) {
	as := require.New(t)
	f := internal.NewSNMPTrapFormatter("host", "127.0.0.1", testTime, oidMap)
	newf, err := fn.Run(f)
	as.NoError(err)
	if len(exp) == 0 {
		as.Len(newf, 0)
	} else {
		as.Len(newf, 1)
		jsonOut, err := newf[0].MarshalJSON()
		as.NoError(err)
		as.JSONEq(exp, string(jsonOut))
	}
}

func TestConfigHuawei5700(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("hwCfgManEventlog", 0, map[string]interface{}{
		"hwCfgLogSrcCmd.20":  "1",
		"hwCfgLogSrcData.20": "2",
		"hwCfgLogDesData.20": "4",
	})
	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigHuaweiCE6800(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("hwCfgChgNotify", 0, map[string]interface{}{
		"hwCurrentCfgChgSeqID.0":      "790",
		"hwCfgChgSeqIDReveralCount.0": "0",
		"hwCfgChgTableMaxItem.0":      "10000",
		"hwCfgBaselineTime.0":         "2020-05-30 21:58:14",
	})
	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigNexus(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("ccmCLIRunningConfigChanged", 0, map[string]interface{}{
		"ccmHistoryRunningLastChanged.0":   "1630709040",
		"ccmHistoryEventTerminalType.3853": "terminal",
	})

	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigLinuxCommitAPI(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("linuxCommitAPI", 0, map[string]interface{}{
		"yandexConfigUser.3853": "root",
		"yandexConfigCounter":   "280",
	})

	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"root","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigCiscoNotAConfig(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("ciscoConfigManEvent", 0, map[string]interface{}{
		"ccmHistoryEventEntry.12799":             "1",
		"ccmHistoryEventConfigSource.12799":      "running",
		"ccmHistoryEventConfigDestination.12799": "commandSource",
	})
	exp := ``
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigCisco(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("ciscoConfigManEvent", 0, map[string]interface{}{
		"ccmHistoryEventEntry.12799":             "1",
		"ccmHistoryEventConfigSource.12799":      "running",
		"ccmHistoryEventConfigDestination.12799": "startup",
	})

	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigLinuxArista(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("aristaConfigManEvent", 0, map[string]interface{}{
		"aristaCmdHistoryEventCommandSource.27":         "commandLine",
		"aristaCmdHistoryEventConfigSource.27":          "running",
		"aristaCmdHistoryEventConfigDestination.27":     "startup",
		"aristaCmdHistoryEventConfigSourceURLScheme.27": "",
		"aristaCmdHistoryEventConfigDestURLScheme.27":   "",
	})

	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigLinuxJuniper(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("jnxCmCfgChange", 0, map[string]interface{}{
		"jnxCmCfgChgEventSource.79": "cli",
		"jnxCmCfgChgEventUser.79":   "root",
		"jnxCmCfgChgEventLog.79":    "",
		"jnxCmCfgChgEventTime.79":   "293656436",
		"jnxCmCfgChgEventDate.79":   "2022-06-15T14:01:23 +0300",
	})

	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"root","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}

func TestConfigLinuxNokia(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("ssiSaveConfigSucceeded", 0, map[string]interface{}{})

	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"committer":"","uptime":0}`
	assertConfRes(t, oidMap, exp, Config{})
}
