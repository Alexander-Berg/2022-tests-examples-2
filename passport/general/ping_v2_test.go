package handlers

import (
	"net/http"
	"testing"

	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmcache"
)

func TestPingV2(t *testing.T) {
	th := testDiagHolder{
		res: tvmcache.Diag{
			Keys: tvmcache.DiagState{
				Status: tvmcache.StatusOk,
			},
			Tickets: tvmcache.DiagState{
				Status: tvmcache.StatusOk,
			},
			TicketErrors: map[tvmcache.ServiceTicketKey]string{},
		},
	}

	handler := PingHandlerV2(&th)

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"status":"OK","error":""}
`,
		http.StatusOK,
	)

	th.res.Keys.Status = tvmcache.StatusWarning
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"status":"WARNING","error":"keys: unexpected error: please mail to tvm-dev@yandex-team.ru"}
`,
		http.StatusPartialContent,
	)

	th.res.TicketErrors[tvmcache.ServiceTicketKey{Src: 123, Dst: 456}] = "bar"
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"status":"WARNING","error":"keys: unexpected error: please mail to tvm-dev@yandex-team.ru. Missing service ticket src=123,dst=456: bar"}
`,
		http.StatusPartialContent,
	)

	th.res.Tickets.Status = tvmcache.StatusWarning
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"status":"WARNING","error":"keys: unexpected error: please mail to tvm-dev@yandex-team.ru. service tickets: unexpected error: please mail to tvm-dev@yandex-team.ru. Missing service ticket src=123,dst=456: bar"}
`,
		http.StatusPartialContent,
	)

	th.res.Tickets.LastErr = xerrors.New("tick_foo")
	th.res.Keys.LastErr = xerrors.New("keys_foo")
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"status":"WARNING","error":"keys: keys_foo. service tickets: tick_foo. Missing service ticket src=123,dst=456: bar"}
`,
		http.StatusPartialContent,
	)

	th.res.Tickets.Status = tvmcache.StatusError
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"status":"ERROR","error":"service tickets: tick_foo"}
`,
		http.StatusInternalServerError,
	)

	th.res.Keys.Status = tvmcache.StatusError
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"status":"ERROR","error":"keys: keys_foo. service tickets: tick_foo"}
`,
		http.StatusInternalServerError,
	)
}
