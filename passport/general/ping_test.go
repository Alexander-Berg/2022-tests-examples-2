package handlers

import (
	"errors"
	"net/http"
	"testing"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmcache"
)

type testDiagHolder struct {
	res tvmcache.Diag
}

func (h *testDiagHolder) GetDiag() tvmcache.Diag {
	return h.res
}

func TestPing(t *testing.T) {
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

	handler := PingHandler(&th)

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		"OK",
		http.StatusOK,
	)

	th.res.Keys.Status = tvmcache.StatusWarning
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		"keys: unexpected error: please mail to tvm-dev@yandex-team.ru",
		http.StatusPartialContent,
	)

	th.res.TicketErrors[tvmcache.ServiceTicketKey{Src: 123, Dst: 456}] = "bar"
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		"keys: unexpected error: please mail to tvm-dev@yandex-team.ru\nMissing service ticket src=123,dst=456: bar",
		http.StatusPartialContent,
	)

	th.res.Tickets.Status = tvmcache.StatusWarning
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		"keys: unexpected error: please mail to tvm-dev@yandex-team.ru\nservice tickets: unexpected error: please mail to tvm-dev@yandex-team.ru\nMissing service ticket src=123,dst=456: bar",
		http.StatusPartialContent,
	)

	th.res.Tickets.LastErr = errors.New("tick_foo")
	th.res.Keys.LastErr = errors.New("keys_foo")
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		"keys: keys_foo\nservice tickets: tick_foo\nMissing service ticket src=123,dst=456: bar",
		http.StatusPartialContent,
	)

	th.res.Tickets.Status = tvmcache.StatusError
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		"service tickets: tick_foo",
		http.StatusInternalServerError,
	)

	th.res.Keys.Status = tvmcache.StatusError
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		"keys: keys_foo\nservice tickets: tick_foo",
		http.StatusInternalServerError,
	)
}
