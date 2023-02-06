package handlers

import (
	"errors"
	"net/http"
	"testing"
	"time"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
)

type testKeysHolder struct {
	res string
	t   time.Time
	err error
}

func (h *testKeysHolder) GetKeys() (string, time.Time, error) {
	return h.res, h.t, h.err
}

func TestKeys(t *testing.T) {
	th := testKeysHolder{
		res: "kek",
		t:   time.Unix(10050706, 0),
	}
	handler := KeysHandler(&th)

	resp := httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`kek`,
		http.StatusOK)
	if bt := resp.Header.Get("X-Ya-TvmTool-Data-Birthtime"); bt != "10050706" {
		t.Fatalf("birthtime: %s", bt)
	}

	th.err = errors.New("foo")
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.Temporary{Message: `foo`},
	)
}
