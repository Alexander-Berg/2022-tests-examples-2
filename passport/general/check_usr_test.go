package handlers

import (
	"errors"
	"net/http"
	"testing"

	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmcontext"
)

const (
	teamProdEnvTag = "prodyateam"
	teamTestEnvTag = "testyateam"
	prodEnvTag     = "prod"
	testEnvTag     = "test"
	stressEnvTag   = "stress"
)

func TestGetEnvWithOverride(t *testing.T) {
	tst := func(def, expected tvm.BlackboxEnv, override string) {
		if env, err := getEnv(def, override); err != nil {
			t.Fatal(err)
		} else if env != expected {
			t.Fatalf("%s\ngetEnv returned incorrect env: %d. expected: %d", whereAmI(), env, expected)
		}
	}
	tstErr := func(def tvm.BlackboxEnv, override string) {
		if env, err := getEnv(def, override); err == nil {
			t.Fatalf("%s\ngetEnv should fail: overriden_env=%s. default=%s. get=%s", whereAmI(), override, def, env)
		}
	}

	tst(tvm.BlackboxProd, tvm.BlackboxProd, prodEnvTag)
	tst(tvm.BlackboxProd, tvm.BlackboxProdYateam, teamProdEnvTag)
	tstErr(tvm.BlackboxProd, testEnvTag)
	tstErr(tvm.BlackboxProd, teamTestEnvTag)
	tstErr(tvm.BlackboxProd, stressEnvTag)

	tst(tvm.BlackboxProdYateam, tvm.BlackboxProd, prodEnvTag)
	tst(tvm.BlackboxProdYateam, tvm.BlackboxProdYateam, teamProdEnvTag)
	tstErr(tvm.BlackboxProdYateam, testEnvTag)
	tstErr(tvm.BlackboxProdYateam, teamTestEnvTag)
	tstErr(tvm.BlackboxProdYateam, stressEnvTag)

	tst(tvm.BlackboxTest, tvm.BlackboxProd, prodEnvTag)
	tst(tvm.BlackboxTest, tvm.BlackboxProdYateam, teamProdEnvTag)
	tst(tvm.BlackboxTest, tvm.BlackboxTest, testEnvTag)
	tst(tvm.BlackboxTest, tvm.BlackboxTestYateam, teamTestEnvTag)
	tst(tvm.BlackboxTest, tvm.BlackboxStress, stressEnvTag)

	tstErr(tvm.BlackboxTestYateam, prodEnvTag)
	tstErr(tvm.BlackboxTestYateam, teamProdEnvTag)
	tst(tvm.BlackboxTestYateam, tvm.BlackboxTest, testEnvTag)
	tst(tvm.BlackboxTestYateam, tvm.BlackboxTestYateam, teamTestEnvTag)
	tstErr(tvm.BlackboxTestYateam, stressEnvTag)

	tstErr(tvm.BlackboxStress, prodEnvTag)
	tstErr(tvm.BlackboxStress, teamProdEnvTag)
	tstErr(tvm.BlackboxStress, testEnvTag)
	tstErr(tvm.BlackboxStress, teamTestEnvTag)
	tst(tvm.BlackboxStress, tvm.BlackboxStress, stressEnvTag)
}

func TestGetEnvWithNoOverride(t *testing.T) {
	tst := func(p tvm.BlackboxEnv) {
		if env, err := getEnv(p, ""); err != nil {
			t.Fatal(err)
		} else if env != p {
			t.Fatalf("getEnv returned incorrect env: %d. expected: %d", env, p)
		}
	}
	tst(tvm.BlackboxProd)
	tst(tvm.BlackboxProdYateam)
	tst(tvm.BlackboxTest)
	tst(tvm.BlackboxTestYateam)
	tst(tvm.BlackboxStress)
}

type testCheckUsr struct {
	res *tvmcontext.UserContext
	err error
}

func (t *testCheckUsr) GetUserContext() (*tvmcontext.UserContext, error) {
	return t.res, t.err
}

func TestCheckUserTicketHandler(t *testing.T) {
	uc, err := tvmcontext.NewUserContext(getTestKeys(getKeys()), tvm.BlackboxTestYateam)
	if err != nil {
		t.Fatal(err)
	}
	tcu := testCheckUsr{
		err: errors.New("foooo"),
	}

	handler := GetCheckUsrHandler(&tcu)

	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.InvalidParam{Message: "ticket was not found in X-Ya-User-Ticket header"},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-User-Ticket": "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:KJ"}),
		&errs.Temporary{Message: `foooo`},
	)

	tcu.err = nil
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-User-Ticket": "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:KJ"}),
		&errs.Temporary{Message: `internal error: missing usrctx`},
	)

	tcu.res = uc
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-User-Ticket": "kek"}),
		&errs.Forbidden{
			Message:       "invalid ticket format",
			LoggingString: "kek",
		},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-User-Ticket": "3:serv:CBAQ__________9_IgcIyYp6EN8B:zxc"}),
		&errs.Forbidden{
			Message:       "wrong ticket type, user-ticket is expected",
			LoggingString: "3:serv:CBAQ__________9_IgcIyYp6EN8B:",
		},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("override_env=stress", map[string]string{"X-Ya-User-Ticket": "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:KJ"}),
		&errs.InvalidParam{Message: `can't switch env from TestYateam to the requested stress`},
	)
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-User-Ticket": "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:KJ"}),
		&errs.Forbidden{
			Message:       "user ticket is accepted from wrong blackbox enviroment. Env expected=TestYateam, got=Test",
			DebugString:   "ticket_type=user;expiration_time=9223372036854775807;scope=bb:sess1,bb:sess2;default_uid=456;uid=456,123;env=Test;",
			LoggingString: "3:user:CA0Q__________9_GiQKAwjIAwoCCHsQyAMaCGJiOnNlc3MxGghiYjpzZXNzMiASKAE:",
		},
	)
	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", map[string]string{"X-Ya-User-Ticket": "3:user:CA4Q__________9_GhYKAgh7EHsaBmJiOmtlayDShdjMBCgD:Jc2RRaCw9h5iriNWLc3klj4ehM2PU9x8IYDoi7q1I-BFZVsx8Pi7EucmdypWqF4tmNc0BX_AK5mh50LU8ViQh7aikP6h7BnkDTVLaJLw2aJscBaauegJ_E4UjsTwP6Tpx-I1CK3BSA8Pvbk8sYBQQ9IPf2xJ_-CqX4SdghWNfp0"}),
		`{"default_uid":123,"uids":[123],"scopes":["bb:kek"],"debug_string":"ticket_type=user;expiration_time=9223372036854775807;scope=bb:kek;default_uid=123;uid=123;env=TestYateam;","logging_string":"3:user:CA4Q__________9_GhYKAgh7EHsaBmJiOmtlayDShdjMBCgD:"}
`,
		http.StatusOK)
}
