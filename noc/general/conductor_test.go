package conductor_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/conductor"
	"a.yandex-team.ru/noc/puncher/lib/logging"
)

func TestGetGroupsHosts(t *testing.T) {
	router := http.NewServeMux()
	router.HandleFunc("/api/groups_export", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "text/xml")
		_, err := w.Write([]byte(`market_front:pepelac01g.yandex.ru,pepelac02g.yandex.ru,pepelac03g.yandex.ru:devnull@yandex-team.ru
market_back:msh01ht.market.yandex.net,msh02ht.market.yandex.net:devnull@yandex-team.ru
`))
		if err != nil {
			panic(err)
		}
	})

	s := httptest.NewServer(router)
	defer s.Close()

	conductorClient := conductor.NewClient(conductor.Config{
		APIGroupsExportURL: s.URL + "/api/groups_export",
	}, logging.Must(log.InfoLevel))

	resp, err := conductorClient.GetGroupsHosts()
	if err != nil {
		t.Fatal(err)
	}

	expectedResp := map[string][]string{
		"market_front": {"pepelac01g.yandex.ru", "pepelac02g.yandex.ru", "pepelac03g.yandex.ru"},
		"market_back":  {"msh01ht.market.yandex.net", "msh02ht.market.yandex.net"},
	}

	assert.Equal(t, resp, expectedResp)
}
