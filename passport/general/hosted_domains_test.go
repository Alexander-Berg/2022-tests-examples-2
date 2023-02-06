package blackbox

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/blackbox/httpbb"
)

func TestClient_HostedDomains(t *testing.T) {
	type TestCase struct {
		BlackboxHTTPRsp
		ExpectedResponse *HostedDomainsResponse `json:"EXPECTED_RESPONSE"`
	}

	tester := func(casePath string) {
		t.Run(filepath.Base(casePath), func(t *testing.T) {
			t.Parallel()

			rawCase, err := os.Open(casePath)
			require.NoError(t, err)
			defer func() { _ = rawCase.Close() }()

			dec := json.NewDecoder(rawCase)
			dec.DisallowUnknownFields()

			var tc TestCase
			err = dec.Decode(&tc)
			require.NoError(t, err)

			srv := NewBlackBoxSrv(t, tc.BlackboxHTTPRsp)
			defer srv.Close()

			bbClient, err := NewBlackBoxClient(httpbb.Environment{
				BlackboxHost: srv.URL,
			})
			require.NoError(t, err)

			response, err := bbClient.HostedDomains(context.Background(), 123)
			require.NoError(t, err)

			require.EqualValuesf(t, tc.ExpectedResponse, response, "")
		})
	}

	cases, err := listCases("hosted_domains")
	require.NoError(t, err)
	require.NotEmpty(t, cases)

	for _, c := range cases {
		tester(c)
	}
}
