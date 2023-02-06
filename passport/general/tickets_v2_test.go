package handlers

import (
	"net/http"
	"testing"
	"time"

	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
)

func TestGetTicketV2(t *testing.T) {
	tgt := testGetTickets{
		tick:  "mega_ticket",
		er:    "mega_error",
		err:   xerrors.New("foooo"),
		btime: time.Unix(10050700, 0),
	}

	handler := GetTicketHandlerV2(setupComplexHandler().cfg, &tgt)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.InvalidParam{Message: "missing parameter 'self'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("self=lol&dsts=ololo", nil),
		&errs.InvalidParam{Message: "couldn't find client in config by alias: 'lol'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("self=kokoko&dsts=ololo", nil),
		&errs.InvalidParam{Message: `foooo`},
	)

	tgt.err = nil
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("self=kokoko&dsts=ololo2,ololo,252", nil),
		&errs.InvalidParam{Message: "can't find in config destination tvmid for src = kokoko, dstparam = 252"},
	)
	resp := httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("self=kokoko&dsts=ololo2,ololo", nil),
		`{"ololo":{"ticket":"mega_ticket","tvm_id":252,"error":"mega_error"},"ololo2":{"ticket":"mega_ticket","tvm_id":252,"error":"mega_error"}}
`,
		http.StatusOK)
	if bt := resp.Header.Get("X-Ya-TvmTool-Data-Birthtime"); bt != "10050700" {
		t.Fatalf("birthtime: %s", bt)
	}

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("self=kekeke&dsts=foo,foo2,ololo2,ololo3", nil),
		`{"foo":{"ticket":"mega_ticket","tvm_id":257,"error":"mega_error"},"foo2":{"ticket":"mega_ticket","tvm_id":258,"error":"mega_error"},"ololo2":{"ticket":"mega_ticket","tvm_id":252,"error":"mega_error"},"ololo3":{"ticket":"mega_ticket","tvm_id":111,"error":"mega_error"}}
`,
		http.StatusOK)

	tgt.er = ""
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("self=kekeke&dsts=foo,ololo", nil),
		&errs.InvalidParam{Message: `can't find in config destination tvmid for src = kekeke, dstparam = ololo`},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("self=100500&dsts=foo,foo2", nil),
		&errs.InvalidParam{Message: `couldn't find client in config by alias: '100500'`},
	)
}
