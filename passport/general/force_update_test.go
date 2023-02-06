package handlers

import (
	"errors"
	"net/http"
	"testing"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/errs"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

type testForceUpdater struct {
	err error
}

func (h *testForceUpdater) ForceUpdate(config *tvmtypes.OptimizedConfig, client *http.Client) error {
	return h.err
}

func TestForceUpdate(t *testing.T) {
	tu := testForceUpdater{}
	handler := ForceUpdateHandler(&tu, nil, nil)

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`OK`,
		http.StatusOK)

	tu.err = errors.New("foo")
	httpclientmock.TestCaseErr(t, handler,
		httpclientmock.MakeRequest("", nil),
		&errs.Temporary{Message: `foo`},
	)
}
