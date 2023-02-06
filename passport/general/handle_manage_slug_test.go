package tiroleinternal

import (
	"io/ioutil"
	"net/http"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tirole_internal/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tirole_internal/internal/reqs"
)

type testRespWriter struct {
}

func (t *testRespWriter) Header() http.Header {
	return map[string][]string{}
}

func (t *testRespWriter) Write([]byte) (int, error) {
	return 0, nil
}

func (t *testRespWriter) WriteHeader(statusCode int) {
}

func TestParseManageSlugRequest(t *testing.T) {
	CTJson := http.Header{
		echo.HeaderContentType: []string{echo.MIMEApplicationJSONCharsetUTF8},
	}

	cases := []struct {
		Headers http.Header
		Body    string
		Err     string
		Req     reqs.ManageSlug
	}{
		{
			Err: "Only JSON allowed as request, got Content-Type: ''",
		},
		{
			Headers: CTJson,
			Body:    "[",
			Err:     "Bad JSON body:",
		},
		{
			Headers: CTJson,
			Body:    `{"tvmid":42}`,
			Err:     "Bad JSON body:",
		},
		{
			Headers: CTJson,
			Body:    `{"tvmid":[]}`,
			Err:     "'system_slug' cannot be empty",
		},
		{
			Headers: CTJson,
			Body:    `{"system_slug":"foo","tvmid":[0,1,3,4]}`,
			Err:     "Tvmid cannot be 0",
		},
		{
			Headers: CTJson,
			Body:    `{"system_slug":"foo","tvmid":[]}`,
			Req: reqs.ManageSlug{
				SystemSlug: "foo",
				Tvmid:      []tvm.ClientID{},
			},
		},
		{
			Headers: CTJson,
			Body:    `{"system_slug":"foo","tvmid":[3,2,1]}`,
			Req: reqs.ManageSlug{
				SystemSlug: "foo",
				Tvmid:      []tvm.ClientID{3, 2, 1},
			},
		},
	}

	for idx, c := range cases {
		e := echo.New()
		req := &http.Request{
			Header:        c.Headers,
			Body:          ioutil.NopCloser(strings.NewReader(c.Body)),
			ContentLength: int64(len(c.Body)),
		}
		wr := &testRespWriter{}
		ctx := e.NewContext(req, wr)

		r, err := ParseManageSlugRequest(ctx)
		if c.Err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, c.Req, *r, idx)
		} else {
			require.Error(t, err, idx)
			require.Contains(t, err.Error(), c.Err, idx)
			_, ok := err.(*errs.InvalidRequestError)
			require.True(t, ok)
			require.Nil(t, r, idx)
		}
	}
}
