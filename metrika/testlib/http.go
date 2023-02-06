package testlib

import (
	"a.yandex-team.ru/metrika/go/pkg/httplib"
	"github.com/go-resty/resty/v2"
	"net/http"
	"net/http/httptest"
)

func GetRestyBootstrap(handlerFunc func(w http.ResponseWriter, r *http.Request)) (srv *httptest.Server, c *resty.Client) {
	srv = httptest.NewServer(http.HandlerFunc(handlerFunc))
	c = httplib.GetRestyClient().SetHostURL(srv.URL).SetDebug(true)
	return
}
