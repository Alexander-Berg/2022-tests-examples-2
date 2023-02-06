package decoder

import (
	"testing"
	"time"

	"a.yandex-team.ru/noc/snmptrapper/internal/snmp"
)

var testTime = time.Date(1988, time.June, 17, 1, 1, 1, 2, time.UTC)

func TestMacHuaweiCE6870(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("hwMacTrapPortCfgAlarm", 0, map[string]interface{}{
		"hwCfgFdbVlanId.1c:1b:0d:bc:a5:ed.333.-": "333",
		"ifDescr.18":                             "10GE1/0/14",
		"hwMacTrapMacInfo.0":                     "MAC learning",
		"hwCfgFdbMac.1c:1b:0d:bc:a5:ed.333.-":    "1c:1b:0d:bc:a5:ed",
	})
	exp := `{"fqdn":"host","ip":"127.0.0.1","timestamp":582512461,"mac_address":"1c:1b:0d:bc:a5:ed","ifname":"10GE1/0/14","ifindex":18,"action":"learning","uptime":0}`
	assertConfRes(t, oidMap, exp, Mac{})
}

func TestMacHuawei5700(t *testing.T) {
	oidMap := snmp.NewResolvedOidMapWithData("hwMacTrapAlarm", 0, map[string]interface{}{
		"hwMacTrapMacInfo.0": "1.12.1.999.00:09:f5:20:8e:74",
	})
	exp := `{"timestamp":582512461,"fqdn":"host","ip":"127.0.0.1","mac_address":"00:09:f5:20:8e:74","ifindex":12,"action":"learning","uptime":0}`
	assertConfRes(t, oidMap, exp, Mac{})
}
