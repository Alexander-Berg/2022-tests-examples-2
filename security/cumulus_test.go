package parsers

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestCumulus(t *testing.T) {
	var logLine = "2021-01-27T15:55:17.479480+02:00 netlab-myt-1 watchfrr[20984]: bgpd state -> up : connect succeeded"
	name := "Cumulus"
	event := parseLog(logLine, Cumulus, name)
	expectedTime, _ := time.Parse("2006-01-02T15:04:05.000000-07:00", "2021-01-27T15:55:17.479480+02:00")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"process":  "watchfrr",
			"proc_id":  "20984",
			"time":     float64(expectedTime.Unix()),
			"hostname": "netlab-myt-1",
			"message":  "bgpd state -> up : connect succeeded",
		},
	}
	require.Equal(t, expectedData, event.Data)
}
