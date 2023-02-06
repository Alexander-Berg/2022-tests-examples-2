package yasmsint

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/routing"
)

func checkFallbacksEqual(t *testing.T, actual, expected FallbacksList) {
	require.Equal(t, len(expected), len(actual))
	for srcname, gates := range expected {
		require.Equal(t, len(gates), len(actual[srcname]))
		for srcgate, fallbacks := range gates {
			require.Equal(t, len(fallbacks), len(actual[srcname][srcgate]))
			for idx, fallback := range fallbacks {
				require.Equal(t, fallback, actual[srcname][srcgate][idx])
			}
		}
	}
}

func TestFallbacksCollector(t *testing.T) {
	collector := newFallbacksCollector()

	collector.Append(&RawFallbackEntry{
		SrcGate: "infobip",
		SrcName: "Yandex.Go",
		DstGate: "infobipyt",
		DstName: "Yandex",
		Order:   0,
	})
	checkFallbacksEqual(t, collector.Get(), FallbacksList{
		"Yandex.Go": {
			"infobip": []*routing.FallbackEntry{
				{
					SmsC: "infobipyt",
					From: "Yandex",
				},
			},
		},
	})

	collector.Append(&RawFallbackEntry{
		SrcGate: "infobip",
		SrcName: "Yandex.Eda",
		DstGate: "infobipytuk",
		DstName: "Yandex",
		Order:   0,
	})
	collector.Append(&RawFallbackEntry{
		SrcGate: "gms",
		SrcName: "Yandex.Eda",
		DstGate: "gmsyt",
		DstName: "Yandex",
		Order:   1,
	})
	collector.Append(&RawFallbackEntry{
		SrcGate: "gms",
		SrcName: "Yandex.Eda",
		DstGate: "gmsytauth",
		DstName: "Yandex",
		Order:   0,
	})
	checkFallbacksEqual(t, collector.Get(), FallbacksList{
		"Yandex.Go": {
			"infobip": []*routing.FallbackEntry{
				{
					SmsC: "infobipyt",
					From: "Yandex",
				},
			},
		},
		"Yandex.Eda": {
			"infobip": []*routing.FallbackEntry{
				{
					SmsC: "infobipytuk",
					From: "Yandex",
				},
			},
			"gms": []*routing.FallbackEntry{
				{
					SmsC: "gmsytauth",
					From: "Yandex",
				},
				{
					SmsC: "gmsyt",
					From: "Yandex",
				},
			},
		},
	})
}
