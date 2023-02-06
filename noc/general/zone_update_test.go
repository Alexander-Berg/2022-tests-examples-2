package cmd

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"a.yandex-team.ru/noc/traffic/dns/dns-client2/internal/config"
	zoneupdate "a.yandex-team.ru/noc/traffic/dns/dns-client2/pkg/zone_update"
)

func TestZoneUpdateCmd(t *testing.T) {
	tests := []struct {
		name       string
		expression []string
		expert     bool
		add        bool
		remove     bool
	}{
		{
			name:       "delete AAAA and PTR in one request",
			expression: []string{"delete dukeartem02t.tt.yandex.net. 2a02:6b8:c0e:125:0:433f:1235:1235"},
		},
		{
			name:       "add AAAA in easy mode",
			expression: []string{"add-aaaa dukeartem02t.tt.yandex.net. 2a02:6b8:c0e:125:0:433f:1235:1235"},
		},
		{
			name:       "add AAAA in expert mode",
			expression: []string{"dukeartem02t.tt.yandex.net. 600 IN AAAA 2a02:6b8:c0e:125:0:433f:1235:1235"},
			expert:     true,
			add:        true,
		},
		{
			name:       "delete AAAA in expert mode",
			expression: []string{"dukeartem02t.tt.yandex.net. 600 IN AAAA 2a02:6b8:c0e:125:0:433f:1235:1235"},
			expert:     true,
			remove:     true,
		},
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		//TODO когда будет новое api, надо реализовать, что оно хотя бы парсится как json объект
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("hello"))
	}))

	ctx = config.GetContextKey()
	ctx.CFG.Auth = zoneupdate.MockInitAuth("MockToken", "MockHeader")
	ctx.CFG.MonkeyDNSAPIURL = server.URL
	ctx.Vars.APIURLService = server.URL
	ctx.Vars.Debug = false
	initialZoneUpdate(ctx)

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			expressions = tt.expression
			expert = tt.expert
			add = tt.add
			remove = tt.remove

			err := zoneUpdateCmd.Execute()
			if err != nil {
				fmt.Println(err)
				return
			}
		})
	}
}
