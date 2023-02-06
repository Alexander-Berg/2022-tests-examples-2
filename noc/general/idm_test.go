package idm_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/idm"
	"a.yandex-team.ru/noc/puncher/lib/logging"
)

func TestGetSystems(t *testing.T) {
	router := http.NewServeMux()
	router.HandleFunc("/firewall/rules/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "application/json")
		_, err := w.Write([]byte(`[
  {
    "macros": [
      {
        "content": {
          "users": ["user"],
          "groups": [123]
        },
        "macro": "my_macro",
        "description": {
          "ru": "macro description (ru)",
          "en": "macro description (en)"
        },
        "path": "/"
      }
    ],
    "name": {
      "ru": "system name (ru)",
      "en": "system name (en)"
    },
    "slug": "my_system"
  }
]
`))
		if err != nil {
			panic(err)
		}
	})

	s := httptest.NewServer(router)
	defer s.Close()

	c, err := idm.NewClient(idm.Config{
		APIURL: s.URL + "/firewall/rules/",
	}, logging.Must(log.InfoLevel))
	if err != nil {
		t.Fatal(err)
	}

	resp, err := c.GetSystems()
	if err != nil {
		t.Fatal(err)
	}

	expectedResp := []idm.System{
		{
			Slug: "my_system",
			Name: struct{ Ru, En string }{
				Ru: "system name (ru)",
				En: "system name (en)",
			},
			Macros: []idm.Macro{
				{
					Path: "/",
					Description: struct{ Ru, En string }{
						Ru: "macro description (ru)",
						En: "macro description (en)",
					},
					Macro: "my_macro",
					Content: struct {
						Users  []string
						Groups []int
					}{Users: []string{"user"}, Groups: []int{123}},
				},
			},
		},
	}
	assert.Equal(t, resp, expectedResp)
}
