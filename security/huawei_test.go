package parsers

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestHuawei(t *testing.T) {
	var logLine = "Feb 15 2021 04:33:56-04:00 vla-3ct13 %%01IFNET/2/linkDown_clear(l):CID=0x807a040a-alarmID=0x08520003-clearType=service_resume;The interface status changes. (ifName=25GE1/0/41, AdminStatus=UP, OperStatus=UP, Reason=Interface physical link is up, mainIfname=25GE1/0/41)"
	name := "Huawei"
	event := parseLog(logLine, Huawei, name)
	expectedTime, _ := time.Parse("Jan _2 2006 15:04:05-07:00", "Feb 15 2021 04:33:56-04:00")
	expectedData := map[string]interface{}{
		"name": name,
		ColumnsDataKey: map[string]interface{}{
			"time":        float64(expectedTime.Unix()),
			"hostname":    "vla-3ct13",
			"version":     "01",
			"module":      "IFNET",
			"brief":       "linkDown_clear",
			"info_type":   "l",
			"severity":    float64(2),
			"CID":         "0x807a040a",
			"alarmID":     "0x08520003",
			"clearType":   "service_resume",
			"message":     "The interface status changes.",
			"ifName":      "25GE1/0/41",
			"AdminStatus": "UP",
			"OperStatus":  "UP",
			"Reason":      "Interface physical link is up",
			"mainIfname":  "25GE1/0/41",
		},
	}
	require.Equal(t, expectedData, event.Data)
}
