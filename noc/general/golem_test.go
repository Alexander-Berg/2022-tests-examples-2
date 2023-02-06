package golem_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/golem"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/models"
)

func TestGetAllResp(t *testing.T) {
	router := http.NewServeMux()
	router.HandleFunc("/api/get_all_resp.sbml", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "text/plain")
		_, err := w.Write([]byte("example.yandex.net\tlogin1,login2\n" +
			"example.yandex.ru\t\n" +
			"example.YaNDEX-TeAM.ru\tlogin3"))
		if err != nil {
			panic(err)
		}
	})

	s := httptest.NewServer(router)
	defer s.Close()

	golem := golem.NewOnlineClient(golem.Config{
		GetAllRespURL: s.URL + "/api/get_all_resp.sbml",
	}, logging.Must(log.InfoLevel))

	resp, err := golem.GetAllResp()
	if err != nil {
		t.Fatal(err)
	}

	expectedResp := map[string][]models.TargetName{
		"example.yandex.net": {
			{Name: "login1", Type: models.TargetNameTypeLogin},
			{Name: "login2", Type: models.TargetNameTypeLogin},
		},
		"example.yandex.ru": {},
		"example.yandex-team.ru": {
			{Name: "login3", Type: models.TargetNameTypeLogin},
		},
	}
	assert.Equal(t, resp, expectedResp)
}
