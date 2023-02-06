package yasmsint

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"path"
	"strconv"
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	mock_tvm "a.yandex-team.ru/library/go/yandex/tvm/mocks"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/logs"
	"a.yandex-team.ru/passport/shared/golibs/utils"
)

func fakeGetGatesHandler(t *testing.T) httpmock.Responder {
	gatesPages := map[uint64]GetGatesResponse{
		0: {
			Gates: []*RawGateEntry{
				{
					ID:   "32",
					SmsC: "gms",
					From: "Yandex",
				},
				{
					ID:   "36",
					SmsC: "taxiauth",
					From: "Yandex.Eda",
				},
			},
			NextURL: "/1/service/gates?min=36&limit=2",
		},
		36: {
			Gates: []*RawGateEntry{
				{
					ID:   "39",
					SmsC: "infobip",
					From: "YandexTrack",
				},
			},
			NextURL: "",
		},
	}

	return func(req *http.Request) (*http.Response, error) {
		require.True(t, req.URL.Query().Has("min"))
		require.True(t, req.URL.Query().Has("limit"))

		limit, err := strconv.ParseUint(req.URL.Query().Get("limit"), 10, 64)
		require.NoError(t, err, "'limit' must be uint")
		require.Equal(t, uint64(2), limit)

		min, err := strconv.ParseUint(req.URL.Query().Get("min"), 10, 64)
		require.NoError(t, err, "'min' must be uint")

		page, exists := gatesPages[min]
		require.True(t, exists, "got unexpected 'min' value")

		body, err := json.Marshal(page)
		require.NoError(t, err)

		return &http.Response{
			StatusCode: 200,
			Body:       io.NopCloser(bytes.NewReader(body)),
		}, nil
	}
}

func TestReloadGates(t *testing.T) {
	logs := logs.NewLogs(&logs.Config{
		Common:   path.Join(yatest.OutputPath("logs"), "general.log"),
		Graphite: path.Join(yatest.OutputPath("logs"), "graphite.log"),
	})
	_ = logs.ReOpen()

	tvmMock := mock_tvm.NewMockClient(gomock.NewController(t))
	fetcher := NewYasmsInternalFetcher(&FetcherConfig{
		Client: &ClientConfig{
			Host:           "http://localhost",
			Port:           8201,
			RequestTimeout: utils.Duration{Duration: 500 * time.Millisecond},
		},
		GatesLimitPerRequest: 2,
	}, tvmMock, logs)

	tvmMock.EXPECT().GetServiceTicketForAlias(context.Background(), gomock.Eq("yasms_internal")).Return("ticket", nil).AnyTimes()

	httpmock.ActivateNonDefault(fetcher.client.httpClient.GetClient())
	defer httpmock.DeactivateAndReset()

	httpmock.RegisterResponder("GET", "http://localhost:8201/1/service/gates", fakeGetGatesHandler(t))

	require.NoError(t, fetcher.ReloadGates(context.Background()))

	gate := fetcher.GateEntry(32)
	require.NotNil(t, gate)
	require.Equal(t, uint64(32), gate.ID)
	require.Equal(t, "gms", gate.SmsC)
	require.Equal(t, "Yandex", gate.From)

	gate = fetcher.GateEntry(36)
	require.NotNil(t, gate)
	require.Equal(t, uint64(36), gate.ID)
	require.Equal(t, "taxiauth", gate.SmsC)
	require.Equal(t, "Yandex.Eda", gate.From)

	gate = fetcher.GateEntry(39)
	require.NotNil(t, gate)
	require.Equal(t, uint64(39), gate.ID)
	require.Equal(t, "infobip", gate.SmsC)
	require.Equal(t, "YandexTrack", gate.From)

	require.Nil(t, fetcher.GateEntry(0))
	require.Nil(t, fetcher.GateEntry(15))
	require.Nil(t, fetcher.GateEntry(35))
	require.Nil(t, fetcher.GateEntry(40))
}
