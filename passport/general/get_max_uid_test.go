package blackbox

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/blackbox/httpbb"
)

type BlackboxHTTPRsp struct {
	ExpectedMethod string          `json:"EXPECTED_METHOD"`
	ExpectedParams string          `json:"EXPECTED_PARAMS"`
	ExpectedBody   string          `json:"EXPECTED_BODY"`
	BBResponse     json.RawMessage `json:"BB_RESPONSE"`
}

func listCases(caseType string) ([]string, error) {
	return filepath.Glob(fmt.Sprintf("./testdata/%s.json", caseType))
}

func NewBlackBoxSrv(t *testing.T, rsp BlackboxHTTPRsp) *httptest.Server {
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "/blackbox", r.URL.Path)

		assert.Equal(t, rsp.ExpectedMethod, r.Method)

		expectedQuery, err := url.ParseQuery(rsp.ExpectedParams)
		if assert.NoError(t, err) {
			assert.EqualValues(t, expectedQuery, r.URL.Query())
		}

		expectedBody, err := url.ParseQuery(rsp.ExpectedBody)
		if assert.NoError(t, err) && len(expectedBody) > 0 {
			body, err := ioutil.ReadAll(r.Body)
			assert.NoError(t, err)

			actualBody, err := url.ParseQuery(string(body))
			assert.NoError(t, err)

			assert.EqualValues(t, expectedBody, actualBody)
		}

		_, _ = w.Write(rsp.BBResponse)
	}))
}

func TestClient_GetMaxUID(t *testing.T) {
	type TestCase struct {
		BlackboxHTTPRsp
		ExpectedResponse *GetMaxUIDResponse `json:"EXPECTED_RESPONSE"`
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

			response, err := bbClient.GetMaxUID(context.Background())
			require.NoError(t, err)

			require.EqualValuesf(t, tc.ExpectedResponse, response, "")
		})
	}

	cases, err := listCases("get_max_uid")
	require.NoError(t, err)
	require.NotEmpty(t, cases)

	for _, c := range cases {
		tester(c)
	}
}
