package handlers

import (
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"runtime"
	"testing"
	"time"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

func getKeys() string {
	return yatest.SourcePath("passport/infra/daemons/tvmtool/internal/tvmcontext/gotest/test_keys.txt")
}

func setupSimpleHandler() TicketHandler {
	config := tvmtypes.Config{
		BbEnvType: tvm.BlackboxTestYateam,
		Clients: map[string]tvmtypes.Client{
			"kokoko": {
				SelfTvmID: tvm.ClientID(111),
				Dsts: map[string]tvmtypes.Dst{
					"ololo": {
						ID: tvm.ClientID(252),
					},
				},
			},
		},
	}
	cfg := tvmtypes.NewOptimizedConfig(&config)
	return NewTicketHandler(cfg)
}

func createComplexConfig() *tvmtypes.OptimizedConfig {
	return createComplexConfigWithEnv(tvm.BlackboxTestYateam)
}

func createComplexConfigWithEnv(env tvm.BlackboxEnv) *tvmtypes.OptimizedConfig {
	config := tvmtypes.Config{
		BbEnvType: env,
		Clients: map[string]tvmtypes.Client{
			"kokoko": {
				Alias:     "kokoko",
				SelfTvmID: tvm.ClientID(111),
				Dsts: map[string]tvmtypes.Dst{
					"ololo": {
						ID: tvm.ClientID(252),
					},
					"ololo2": {
						ID: tvm.ClientID(252),
					},
				},
				IdmSlug: "some_slug",
			},
			"kekeke": {
				Alias:     "kekeke",
				SelfTvmID: tvm.ClientID(112),
				Dsts: map[string]tvmtypes.Dst{
					"foo": {
						ID: tvm.ClientID(257),
					},
					"foo2": {
						ID: tvm.ClientID(258),
					},
					"ololo3": {
						ID: tvm.ClientID(111),
					},
					"ololo2": {
						ID: tvm.ClientID(252),
					},
				},
			},
			"kekeke2": {
				Alias:     "kekeke2",
				SelfTvmID: tvm.ClientID(112),
				Dsts:      map[string]tvmtypes.Dst{},
				IdmSlug:   "some_other_slug",
			},
		},
	}
	return tvmtypes.NewOptimizedConfig(&config)
}

func setupComplexHandler() TicketHandler {
	return NewTicketHandler(createComplexConfig())
}

func getTestKeys(filename string) string {
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}
	return string(data)
}

func whereAmI() string {
	function, file, line, _ := runtime.Caller(2)
	return fmt.Sprintf("File: %s:%d\nFunction: %s", file, line, runtime.FuncForPC(function).Name())
}

type testGetTickets struct {
	tick  string
	er    string
	err   error
	btime time.Time
}

func (t *testGetTickets) GetTicketUpdateTime() time.Time {
	return t.btime
}
func (t *testGetTickets) GetTicket(src tvm.ClientID, dst tvm.ClientID) (tvmtypes.Ticket, string, error) {
	return tvmtypes.Ticket(t.tick), t.er, t.err
}

func TestGetServiceTicketSimple(t *testing.T) {
	tktHandler := setupSimpleHandler()

	tgt := testGetTickets{
		tick:  "mega_ticket",
		er:    "mega_error",
		err:   errors.New("foooo"),
		btime: time.Unix(10050705, 0),
	}

	handler := tktHandler.GetTicketHandler(&tgt)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.InvalidParam{Message: "missing parameter 'dsts'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dsts=ololo", map[string]string{}),
		&errs.InvalidParam{Message: "foooo"},
	)

	tgt.err = nil
	resp := httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("dsts=ololo", map[string]string{}),
		`{"ololo":{"ticket":"mega_ticket","tvm_id":252,"error":"mega_error"}}
`,
		http.StatusOK)
	if bt := resp.Header.Get("X-Ya-TvmTool-Data-Birthtime"); bt != "10050705" {
		t.Fatalf("birthtime: %s", bt)
	}

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dsts=fsh", map[string]string{}),
		&errs.InvalidParam{Message: `can't find in config destination tvmid for src = 111, dstparam = fsh (strconv)`},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dsts=253", map[string]string{}),
		&errs.InvalidParam{Message: `can't find in config destination tvmid for src = 111, dstparam = 253 (by number)`},
	)

	tgt.er = ""
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("src=kokoko&dsts=ololo", map[string]string{}),
		`{"ololo":{"ticket":"mega_ticket","tvm_id":252}}
`,
		http.StatusOK)
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("src=kekeke&dsts=ololo", map[string]string{}),
		`{"ololo":{"ticket":"mega_ticket","tvm_id":252}}
`,
		http.StatusOK)

	tgt.er = "mega_error"
	tgt.tick = ""
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("src=111&dsts=252", map[string]string{}),
		`{"ololo":{"tvm_id":252,"error":"mega_error"}}
`,
		http.StatusOK)
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("src=100500&dsts=252", map[string]string{}),
		`{"ololo":{"tvm_id":252,"error":"mega_error"}}
`,
		http.StatusOK)
}

func TestGetServiceTicketComplex(t *testing.T) {
	tktHandler := setupComplexHandler()

	tgt := testGetTickets{
		tick:  "mega_ticket",
		er:    "mega_error",
		err:   errors.New("foooo"),
		btime: time.Unix(10050700, 0),
	}

	handler := tktHandler.GetTicketHandler(&tgt)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.InvalidParam{Message: "missing parameter 'src'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("src=kokoko&dsts=ololo", map[string]string{}),
		&errs.InvalidParam{Message: `foooo`},
	)

	tgt.err = nil
	resp := httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("src=kokoko&dsts=ololo2,ololo,252", map[string]string{}),
		`{"ololo":{"ticket":"mega_ticket","tvm_id":252,"error":"mega_error"},"ololo2":{"ticket":"mega_ticket","tvm_id":252,"error":"mega_error"}}
`,
		http.StatusOK)
	if bt := resp.Header.Get("X-Ya-TvmTool-Data-Birthtime"); bt != "10050700" {
		t.Fatalf("birthtime: %s", bt)
	}

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("src=kekeke&dsts=foo,foo2,ololo2,ololo3", map[string]string{}),
		`{"foo":{"ticket":"mega_ticket","tvm_id":257,"error":"mega_error"},"foo2":{"ticket":"mega_ticket","tvm_id":258,"error":"mega_error"},"ololo2":{"ticket":"mega_ticket","tvm_id":252,"error":"mega_error"},"ololo3":{"ticket":"mega_ticket","tvm_id":111,"error":"mega_error"}}
`,
		http.StatusOK)
	// TODO: PASSP-24859
	// httpclientmock.TestCase(t, handler,
	// 	httpclientmock.MakeRequest("src=112&dsts=foo,foo2", map[string]string{}),
	// 	`{"foo":{"ticket":"mega_ticket","tvm_id":257,"error":"mega_error"},"foo2":{"ticket":"mega_ticket","tvm_id":258,"error":"mega_error"}}`,
	// 	http.StatusOK)

	tgt.er = ""
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("src=kekeke&dsts=foo,ololo", map[string]string{}),
		&errs.InvalidParam{Message: `can't find in config destination tvmid for src = 112, dstparam = ololo (strconv)`},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("src=100500&dsts=foo,foo2", map[string]string{}),
		&errs.InvalidParam{Message: `couldn't find in config client by either src or alias for param = 100500`},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("src=bar&dsts=foo,foo2", map[string]string{}),
		&errs.InvalidParam{Message: `'src' parameter incorrect`},
	)
}
