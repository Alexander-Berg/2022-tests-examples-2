package handlers

import (
	"errors"
	"net/http"
	"testing"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmcontext"
)

type testCheckSrv struct {
	res *tvmcontext.ServiceContext
	err error
}

func (t *testCheckSrv) GetServiceContext() (*tvmcontext.ServiceContext, error) {
	return t.res, t.err
}

func TestCheckServiceTicketHandler(t *testing.T) {
	tktHandler := setupComplexHandler()

	sc, err := tvmcontext.NewServiceContext(getTestKeys(getKeys()))
	if err != nil {
		t.Fatal(err)
	}
	tcs := testCheckSrv{
		err: errors.New("foooo"),
	}

	handler := tktHandler.GetCheckSrvTicketHandler(&tcs)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.InvalidParam{Message: "missing parameter 'dst'"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{}),
		&errs.InvalidParam{Message: `ticket was not found in X-Ya-Service-Ticket header`},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgcIyYp6EN8B:TyM3QK1A5vMYqt507iKFKp1I1dZO0hdUSogBOloxnehCJ5vZ1-1e_zaxt2kxL9WX9BJQ5Sxcb5PNG_dCELrG22UojArBmllf4iKyoggp9q2MVDwi-DjbEmdofejeN9fCGhqLwdnnhUtkCwW8beF3QWOemLyC1yyRf0k5uPhfOwA"}),
		&errs.Temporary{Message: `foooo`},
	)

	tcs.err = nil
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgcIyYp6EN8B:TyM3QK1A5vMYqt507iKFKp1I1dZO0hdUSogBOloxnehCJ5vZ1-1e_zaxt2kxL9WX9BJQ5Sxcb5PNG_dCELrG22UojArBmllf4iKyoggp9q2MVDwi-DjbEmdofejeN9fCGhqLwdnnhUtkCwW8beF3QWOemLyC1yyRf0k5uPhfOwA"}),
		&errs.Temporary{Message: `internal error: missing srvctx`},
	)

	tcs.res = sc
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "kek"}),
		&errs.Forbidden{
			Message:       "invalid ticket format",
			LoggingString: "kek",
		},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "kek"}),
		&errs.Forbidden{
			Message:       `invalid ticket format`,
			LoggingString: "kek",
		},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:KJ"}),
		&errs.Forbidden{
			Message:       "wrong ticket type, service-ticket is expected",
			LoggingString: "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:",
		},
	)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgcIyYp6EN8B:TyM3QK1A5vMYqt507iKFKp1I1dZO0hdUSogBOloxnehCJ5vZ1"}),
		&errs.Forbidden{
			Message:       "invalid base64 in signature",
			DebugString:   "ticket_type=service;expiration_time=9223372036854775807;src=2000201;dst=223;scope=;",
			LoggingString: "3:serv:CBAQ__________9_IgcIyYp6EN8B:",
		},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgcIyYp6EN8B:TyM3QK1A5vMYqt507iKFKp1I1dZO0hdUSogBOloxnehCJ5vZ1-1e_zaxt2kxL9WX9BJQ5Sxcb5PNG_dCELrG22UojArBmllf4iKyoggp9q2MVDwi-DjbEmdofejeN9fCGhqLwdnnhUtkCwW8beF3QWOemLyC1yyRf0k5uPhfOwA"}),
		&errs.Forbidden{
			Message:       "Wrong ticket dst, expected 111, got 223",
			DebugString:   "ticket_type=service;expiration_time=9223372036854775807;src=2000201;dst=223;scope=;",
			LoggingString: "3:serv:CBAQ__________9_IgcIyYp6EN8B:",
		},
	)

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgYIlJEGEG8:MCMr5s6x_v8Bef2SgqouWp1fNQJ5WHoNFAeXYzbfbjYnpjRCp04Hth0pIr1agJ7-NlVEY-HfXl-U82782k9sGeg_VfFxc3N0Yq_1r1kPvYojC3xWFE8j8HCj_9QyX4oiqJJ4_sgCNXbRXJ2GFzWmpjKWwuQezVA9wKeen_vgsVA"}),
		`{"src":100500,"dst":111,"scopes":null,"debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=100500;dst=111;scope=;","logging_string":"3:serv:CBAQ__________9_IgYIlJEGEG8:","issuer_uid":null}
`,
		http.StatusOK)
}

func TestCheckServiceTicketSimple(t *testing.T) {
	tktHandler := setupSimpleHandler()

	sc, err := tvmcontext.NewServiceContext(getTestKeys(getKeys()))
	if err != nil {
		t.Fatal(err)
	}
	tcs := testCheckSrv{
		res: sc,
	}

	handler := tktHandler.GetCheckSrvTicketHandler(&tcs)

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("dst=kokoko", map[string]string{"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgYIlJEGEG8:MCMr5s6x_v8Bef2SgqouWp1fNQJ5WHoNFAeXYzbfbjYnpjRCp04Hth0pIr1agJ7-NlVEY-HfXl-U82782k9sGeg_VfFxc3N0Yq_1r1kPvYojC3xWFE8j8HCj_9QyX4oiqJJ4_sgCNXbRXJ2GFzWmpjKWwuQezVA9wKeen_vgsVA"}),
		`{"src":100500,"dst":111,"scopes":null,"debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=100500;dst=111;scope=;","logging_string":"3:serv:CBAQ__________9_IgYIlJEGEG8:","issuer_uid":null}
`,
		http.StatusOK)
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-Service-Ticket": "3:serv:CBAQ__________9_IgYIlJEGEG8:MCMr5s6x_v8Bef2SgqouWp1fNQJ5WHoNFAeXYzbfbjYnpjRCp04Hth0pIr1agJ7-NlVEY-HfXl-U82782k9sGeg_VfFxc3N0Yq_1r1kPvYojC3xWFE8j8HCj_9QyX4oiqJJ4_sgCNXbRXJ2GFzWmpjKWwuQezVA9wKeen_vgsVA"}),
		`{"src":100500,"dst":111,"scopes":null,"debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=100500;dst=111;scope=;","logging_string":"3:serv:CBAQ__________9_IgYIlJEGEG8:","issuer_uid":null}
`,
		http.StatusOK)
}
