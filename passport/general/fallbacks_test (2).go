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
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/routing"
	"a.yandex-team.ru/passport/shared/golibs/utils"
)

func fakeGetFallbacksHandler(t *testing.T) httpmock.Responder {
	fallbacksPages := map[uint64]GetFallbackResponse{
		0: {
			Fallbacks: []*RawFallbackEntry{
				{
					SrcGate: "infobip",
					SrcName: "Yandex.Go",
					DstGate: "infobipyt",
					DstName: "Yandex",
					Order:   0,
				},
				{
					SrcGate: "gms",
					SrcName: "Yandex.Eda",
					DstGate: "gmsyt",
					DstName: "Yandex",
					Order:   2,
				},
			},
			NextURL: "/1/service/fallbacks?min=36&limit=2",
		},
		36: {
			Fallbacks: []*RawFallbackEntry{
				{
					SrcGate: "gms",
					SrcName: "Yandex.Eda",
					DstGate: "gmsytauth",
					DstName: "Yandex",
					Order:   0,
				},
				{
					SrcGate: "infobip",
					SrcName: "Yandex.Eda",
					DstGate: "infobipytuk",
					DstName: "Yandex",
					Order:   0,
				},
			},
			NextURL: "/1/service/fallbacks?min=129&limit=2",
		},
		129: {
			Fallbacks: []*RawFallbackEntry{
				{
					SrcGate: "gms",
					SrcName: "Yandex.Eda",
					DstGate: "mfms",
					DstName: "Yandex",
					Order:   1,
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

		page, exists := fallbacksPages[min]
		require.True(t, exists, "got unexpected 'min' value")

		body, err := json.Marshal(page)
		require.NoError(t, err)

		return &http.Response{
			StatusCode: 200,
			Body:       io.NopCloser(bytes.NewReader(body)),
		}, nil
	}
}

func TestReloadFallbacks(t *testing.T) {
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
		FallbacksLimitPerRequest: 2,
	}, tvmMock, logs)

	tvmMock.EXPECT().GetServiceTicketForAlias(context.Background(), gomock.Eq("yasms_internal")).Return("ticket", nil).AnyTimes()

	httpmock.ActivateNonDefault(fetcher.client.httpClient.GetClient())
	defer httpmock.DeactivateAndReset()

	httpmock.RegisterResponder("GET", "http://localhost:8201/1/service/fallbacks", fakeGetFallbacksHandler(t))

	require.NoError(t, fetcher.ReloadFallbacks(context.Background()))

	fallbacks := fetcher.Fallbacks("Yandex.Go", "infobip")
	require.Equal(t, 1, len(fallbacks))
	require.Equal(t, routing.FallbackEntry{SmsC: "infobipyt", From: "Yandex"}, *fallbacks[0])

	fallbacks = fetcher.Fallbacks("Yandex.Eda", "infobip")
	require.Equal(t, 1, len(fallbacks))
	require.Equal(t, routing.FallbackEntry{SmsC: "infobipytuk", From: "Yandex"}, *fallbacks[0])

	fallbacks = fetcher.Fallbacks("Yandex.Eda", "gms")
	require.Equal(t, 3, len(fallbacks))
	require.Equal(t, routing.FallbackEntry{SmsC: "gmsytauth", From: "Yandex"}, *fallbacks[0])
	require.Equal(t, routing.FallbackEntry{SmsC: "mfms", From: "Yandex"}, *fallbacks[1])
	require.Equal(t, routing.FallbackEntry{SmsC: "gmsyt", From: "Yandex"}, *fallbacks[2])

	require.Nil(t, fetcher.Fallbacks("Yandex", "infobip"))
	require.Nil(t, fetcher.Fallbacks("Yandex.Go", "gms"))
	require.Nil(t, fetcher.Fallbacks("Yandex.Eda", "mfms"))
}
