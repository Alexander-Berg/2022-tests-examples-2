package parsers

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/osquery/osquery-sender/syslogparsing/formats"
)

func TestJuniperStandard(t *testing.T) {
	var logLine = "Jan  6 08:45:01 std-b1 newsyslog[68743]: logfile turned over due to size>1024K"
	name := "Juniper"
	event := parseLog(logLine, JuniperStandard, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Jan  6 08:45:01")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":     float64(expectedTime.Unix()),
			"hostname": "std-b1",
			"process":  "newsyslog",
			"proc_id":  "68743",
			"message":  "logfile turned over due to size>1024K",
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestJuniperStandardWithTag(t *testing.T) {
	var logLine = "Feb 25 08:45:49  std-b1 rpd[13130]: BGP_CONNECT_FAILED: bgp_connect_start: connect 192.168.243.2 (External AS 65402): Operation not permitted"
	name := "Juniper"
	event := parseLog(logLine, JuniperStandard, name)
	expectedTime, _ := formats.ParseStandardFormatDate("Feb 25 08:45:49")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":     float64(expectedTime.Unix()),
			"hostname": "std-b1",
			"process":  "rpd",
			"proc_id":  "13130",
			"tag":      "BGP_CONNECT_FAILED",
			"message":  "bgp_connect_start: connect 192.168.243.2 (External AS 65402): Operation not permitted",
		},
	}
	require.Equal(t, expectedData, event.Data)
}
