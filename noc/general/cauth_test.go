package cauth_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/cauth"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/lib/timemachine"
	"a.yandex-team.ru/noc/puncher/models"
)

func TestGetRules(t *testing.T) {
	router := http.NewServeMux()
	router.HandleFunc("/puncher/rules", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "text/xml")
		_, err := w.Write([]byte(`{
  "rules": [
    {
      "dst": {
        "object": {
          "fqdn": "bus-receiver01g.tst.maps.yandex.ru",
          "id": 138342
        },
        "type": "server"
      },
      "src": {
        "object": {
          "login": "dprokoptsev",
          "uid": 20590
        },
        "type": "user"
      },
      "id": 22431
    },
    {
      "dst": {
        "object": {
          "source": "conductor",
          "name": "mail-backup-storage",
          "id": 33541
        },
        "type": "group"
      },
      "src": {
        "object": {
          "staff_id": 380,
          "name": "dpt_yandex_mnt_person_mailservice_service",
          "gid": 20378
        },
        "type": "dpt"
      },
      "id": 22470
    }
  ]
}
`))
		if err != nil {
			panic(err)
		}
	})

	s := httptest.NewServer(router)
	defer s.Close()

	// TODO: remove hack
	timemachine.EnableTestFS()
	cauthClient, err := cauth.NewClient(cauth.Config{
		PuncherRulesURL: s.URL + "/puncher/rules",
	}, logging.Must(log.InfoLevel))
	if err != nil {
		t.Fatal(err)
	}

	rules, err := cauthClient.GetRules()
	if err != nil {
		t.Fatal(err)
	}

	expectedRules := []models.RawCAuthRule{
		{
			Source: models.RawCAuthSource{
				Type: "user",
				Name: "dprokoptsev",
			},
			Destination: models.RawCAuthDestination{
				Type: "server",
				Name: "bus-receiver01g.tst.maps.yandex.ru",
			},
		},
		{
			Source: models.RawCAuthSource{
				Type:    "dpt",
				Name:    "dpt_yandex_mnt_person_mailservice_service",
				StaffID: 380,
			},
			Destination: models.RawCAuthDestination{
				Type: "conductor",
				Name: "mail-backup-storage",
			},
		},
	}
	assert.Equal(t, rules, expectedRules)
}
