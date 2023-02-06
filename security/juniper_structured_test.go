package parsers

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestJuniperStructured(t *testing.T) {
	var logLine = "<28>1 2021-12-06T01:40:27.849+03:00 std-cpx1 inetd 18615 - - /usr/sbin/sshd[59782]: exited, status 255"
	name := "Juniper"
	event := parseLog(logLine, JuniperStructured, name)
	expectedTime, _ := time.Parse("2006-01-02T15:04:05.000-07:00", "2021-12-06T01:40:27.849+03:00")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"app_name": "inetd",
			"hostname": "std-cpx1",
			"message":  "/usr/sbin/sshd[59782]: exited, status 255",
			"time":     float64(expectedTime.Unix()),
			"proc_id":  "18615",
			"priority": float64(28),
			"version":  float64(1),
			"facility": float64(3),
			"severity": float64(4),
		},
	}
	require.Equal(t, expectedData, event.Data)
}

func TestJuniperStructuredWithExtraData(t *testing.T) {
	var logLine = "<28>1 2021-12-06T01:39:46.441+03:00 std-cpx1 bfdd 18625 BFDD_TRAP_SHOP_STATE_DOWN [junos@2636.1.1.1.2.513 session-id=\"40\" state=\"down\" pip-interface=\"ae20.3032\" remote-peer=\"169.254.254.7\"] local discriminator: 40, new state: down, interface: ae20.3032, peer addr: 169.254.254.7"
	name := "Juniper"
	event := parseLog(logLine, JuniperStructured, name)
	expectedTime, _ := time.Parse("2006-01-02T15:04:05.000-07:00", "2021-12-06T01:39:46.441+03:00")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"app_name":      "bfdd",
			"hostname":      "std-cpx1",
			"time":          float64(expectedTime.Unix()),
			"proc_id":       "18625",
			"priority":      float64(28),
			"version":       float64(1),
			"facility":      float64(3),
			"severity":      float64(4),
			"tag":           "BFDD_TRAP_SHOP_STATE_DOWN",
			"platform":      "1.1.1.2.513",
			"message":       "local discriminator: 40, new state: down, interface: ae20.3032, peer addr: 169.254.254.7",
			"session-id":    "40",
			"state":         "down",
			"pip-interface": "ae20.3032",
			"remote-peer":   "169.254.254.7",
		},
	}
	require.Equal(t, expectedData, event.Data)
}
