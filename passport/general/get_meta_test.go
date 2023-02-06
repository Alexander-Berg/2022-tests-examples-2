package handlers

import (
	"net/http"
	"testing"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
)

func TestMeta(t *testing.T) {
	tktHandler := setupSimpleHandler()
	handler := GetMetaHandler(tktHandler.cfg)

	httpclientmock.TestCase(t, handler,
		httpclientmock.MakeRequest("", nil),
		`{"bb_env":"TestYaTeam","tenants":[{"self":{"alias":"kokoko","client_id":111},"dsts":[{"alias":"ololo","client_id":252}]}]}
`,
		http.StatusOK)
}
