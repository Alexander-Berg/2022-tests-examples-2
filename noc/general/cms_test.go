package cms_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/cms"
	"a.yandex-team.ru/noc/puncher/lib/logging"
)

func TestGetGroups(t *testing.T) {
	router := http.NewServeMux()
	router.HandleFunc("/res/cauth_export/groups.xml", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "text/xml")
		_, err := w.Write([]byte(`<?xml version='1.0' encoding='UTF-8'?>
<domain id="10" name="search">
  <group id="1770645165" name="ALL_ACTI" parent_id="">
    <host id="113314757" name="old-toxygen00.yandex.ru" />
    <host id="1378376219" name="old-toxygen00.search.yandex.net" />
    <host id="388627454" name="old-toxygen01.yandex.ru" />
    <host id="986477353" name="old-toxygen01.search.yandex.net" />
    <host id="868262252" name="oxygen-fml00.search.yandex.net" />
  </group>
  <group id="853349020" name="ALL_ACTI_GIWI_STG" parent_id="">
    <host id="1703791230" name="acti14.yandex.ru" />
    <host id="1129670725" name="acti14.search.yandex.net" />
    <host id="2076345944" name="acti15.yandex.ru" />
    <host id="1342137163" name="acti15.search.yandex.net" />
  </group>
</domain>
`))
		if err != nil {
			panic(err)
		}
	})

	s := httptest.NewServer(router)
	defer s.Close()

	c := cms.NewClient(cms.Config{
		GroupsURL: s.URL + "/res/cauth_export/groups.xml",
	}, logging.Must(log.InfoLevel))

	groups, err := c.GetGroups()
	if err != nil {
		t.Fatal(err)
	}

	expectedGroups := map[string][]string{
		"ALL_ACTI": {
			"old-toxygen00.yandex.ru",
			"old-toxygen00.search.yandex.net",
			"old-toxygen01.yandex.ru",
			"old-toxygen01.search.yandex.net",
			"oxygen-fml00.search.yandex.net",
		},
		"ALL_ACTI_GIWI_STG": {
			"acti14.yandex.ru",
			"acti14.search.yandex.net",
			"acti15.yandex.ru",
			"acti15.search.yandex.net",
		},
	}
	assert.Equal(t, groups, expectedGroups)
}
