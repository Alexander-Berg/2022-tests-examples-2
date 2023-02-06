package httplib

import (
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// copy paste from a.yandex-team.ru/metrika/go/pkg/testlib to avoid import cycle
func getBootstrap(handlerFunc func(w http.ResponseWriter, r *http.Request)) (srv *httptest.Server, c *resty.Client) {
	srv = httptest.NewServer(http.HandlerFunc(handlerFunc))
	c = GetRestyClient().SetHostURL(srv.URL).SetDebug(true)
	return
}

func TestRetry(t *testing.T) {
	calls := new(int32)
	var srv *httptest.Server
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt32(calls, 1)
		srv.CloseClientConnections()
	}
	srv, client := getBootstrap(handlerFunc)
	defer srv.Close()

	_, err := client.R().Get("/test_url")

	require.Error(t, err)
	assert.Equal(t, int32(3), atomic.LoadInt32(calls))
}

func TestRetryFinalSuccess(t *testing.T) {
	calls := new(int32)
	var srv *httptest.Server
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt32(calls, 1)
		if atomic.LoadInt32(calls) == int32(1) {
			srv.CloseClientConnections()
		} else {
			_, _ = w.Write([]byte(`this is a config`))
		}
	}
	srv, client := getBootstrap(handlerFunc)
	defer srv.Close()

	rsp, err := client.R().Get("/test_url")

	require.NoError(t, err)
	assert.Equal(t, int32(2), atomic.LoadInt32(calls))
	assert.Equal(t, "this is a config", rsp.String())
}

func TestNoRetryClientErrors(t *testing.T) {
	calls := new(int32)
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt32(calls, 1)
		w.WriteHeader(http.StatusBadRequest)
		_, _ = w.Write([]byte(`this is a config`))
	}
	srv, client := getBootstrap(handlerFunc)
	defer srv.Close()

	rsp, err := client.R().Get("/test_url")

	require.NoError(t, err)
	assert.Equal(t, int32(1), atomic.LoadInt32(calls))
	assert.Equal(t, http.StatusBadRequest, rsp.StatusCode())
	assert.Equal(t, "this is a config", rsp.String())
}

func TestRetryServerErrors(t *testing.T) {
	calls := new(int32)
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		atomic.AddInt32(calls, 1)
		w.WriteHeader(http.StatusInternalServerError)
		_, _ = w.Write([]byte(`it is a real fail`))
	}
	srv, client := getBootstrap(handlerFunc)
	defer srv.Close()

	rsp, err := client.R().Get("/test_url")

	require.NoError(t, err)
	assert.Equal(t, int32(3), atomic.LoadInt32(calls))
	assert.Equal(t, http.StatusInternalServerError, rsp.StatusCode())
	assert.Equal(t, "it is a real fail", rsp.String())
}
