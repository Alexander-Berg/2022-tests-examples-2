package api

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/resps"
	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/ytc"
)

func TestBuildPushSubscriptionResult(t *testing.T) {
	type testCase struct {
		name     string
		inRows   []ytc.PushSubscriptionRow
		outItems []resps.PushSubscriptionItem
	}
	cases := []testCase{
		{
			name:     "empty",
			inRows:   []ytc.PushSubscriptionRow{},
			outItems: []resps.PushSubscriptionItem{},
		},
		{
			name: "single hit",
			inRows: []ytc.PushSubscriptionRow{
				{AppID: "kek", DeviceID: "lol", Count: 42},
			},
			outItems: []resps.PushSubscriptionItem{
				{AppID: "kek", DeviceID: "lol", Count: 42},
			},
		},
		{
			name: "several hit from same source",
			inRows: []ytc.PushSubscriptionRow{
				{AppID: "kek", DeviceID: "lol", Count: 42},
				{AppID: "kek", DeviceID: "lol", Count: 3},
			},
			outItems: []resps.PushSubscriptionItem{
				{AppID: "kek", DeviceID: "lol", Count: 45},
			},
		},
		{
			name: "hits from several sources",
			inRows: []ytc.PushSubscriptionRow{
				{AppID: "foo", DeviceID: "lol", Count: 1},
				{AppID: "kek", DeviceID: "lol", Count: 3},
				{AppID: "kek", DeviceID: "lol", Count: 1},
				{AppID: "kek", DeviceID: "lol", Count: 4},
			},
			outItems: []resps.PushSubscriptionItem{
				{AppID: "kek", DeviceID: "lol", Count: 8},
				{AppID: "foo", DeviceID: "lol", Count: 1},
			},
		},
		{
			name: "under limit entries",
			inRows: []ytc.PushSubscriptionRow{
				{AppID: "foo", DeviceID: "lol", Count: 1},
				{AppID: "kek", DeviceID: "lol", Count: 3},
				{AppID: "lol", DeviceID: "lol", Count: 4},
			},
			outItems: []resps.PushSubscriptionItem{
				{AppID: "lol", DeviceID: "lol", Count: 4},
				{AppID: "kek", DeviceID: "lol", Count: 3},
				{AppID: "foo", DeviceID: "lol", Count: 1},
			},
		},
		{
			name: "over limit entries",
			inRows: []ytc.PushSubscriptionRow{
				{AppID: "foo", DeviceID: "lol", Count: 1},
				{AppID: "kek", DeviceID: "lol", Count: 3},
				{AppID: "bar", DeviceID: "lol", Count: 2},
				{AppID: "lol", DeviceID: "lol", Count: 4},
			},
			outItems: []resps.PushSubscriptionItem{
				{AppID: "lol", DeviceID: "lol", Count: 4},
				{AppID: "kek", DeviceID: "lol", Count: 3},
				{AppID: "bar", DeviceID: "lol", Count: 2},
			},
		},
	}

	for _, c := range cases {
		result := buildPushSubscriptionResult(c.inRows, 42, 3)

		require.NotNil(t, result, c.name)
		require.EqualValues(t, "ok", result.Status, c.name)
		require.EqualValues(t, uint64(42), result.UID, c.name)
		require.EqualValues(t, c.outItems, result.Items, c.name)
	}
}
