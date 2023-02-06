package mdm_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/mdm"
	"a.yandex-team.ru/noc/puncher/lib/logging"
)

const response = `
<?xml version="1.0" encoding="UTF-8"?>
<user_group>
	<id>1</id>
	<name>All users</name>
	<is_smart>true</is_smart>
	<is_notify_on_change>false</is_notify_on_change>
	<site>
		<id>-1</id>
		<name>None</name>
	</site>
	<criteria>
		<size>1</size>
		<criterion>
			<name>Username</name>
			<priority>0</priority>
			<and_or>and</and_or>
			<search_type>is not</search_type>
			<value/>
			<opening_paren>false</opening_paren>
			<closing_paren>false</closing_paren>
		</criterion>
	</criteria>
	<users>
		<size>1900</size>
		<user>
			<id>1</id>
			<username>d0uble</username>
			<full_name>Vladimir Borodin</full_name>
			<phone_number>7255</phone_number>
			<email_address>d0uble@yandex-team.ru</email_address>
		</user>
		<user>
			<id>7</id>
			<username>loschilin</username>
			<full_name>Victor Loschilin</full_name>
			<phone_number>2234</phone_number>
			<email_address>loschilin@yandex-team.ru</email_address>
		</user>
	</users>
</user_group>
`

func TestFetchUsers(t *testing.T) {
	router := http.NewServeMux()
	router.HandleFunc("/JSSResource/usergroups/id/1", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Content-Type", "text/xml;charset=UTF-8")
		_, err := w.Write([]byte(response))
		if err != nil {
			panic(err)
		}
	})

	s := httptest.NewServer(router)
	defer s.Close()

	client := mdm.NewClient(mdm.Config{
		URL: s.URL + "/JSSResource/usergroups/id/1",
	}, logging.Must(log.InfoLevel))

	logins, err := client.FetchUsers()
	if err != nil {
		t.Fatal(err)
	}

	assert.Equal(t, []string{"d0uble", "loschilin"}, logins)
}
