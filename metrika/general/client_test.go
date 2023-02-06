package bishop

import (
	"a.yandex-team.ru/library/go/core/xerrors"
	"a.yandex-team.ru/metrika/go/pkg/testlib"
	"fmt"
	"net/http"
	"testing"

	"github.com/go-resty/resty/v2"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestGetConfig(t *testing.T) {
	program := "my_program"
	environment := "my_env"
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(
			t,
			fmt.Sprintf("/api/v2/config/%s/%s", program, environment),
			r.URL.Path,
		)

		assert.Equal(t, "OAuth asd", r.Header.Get("Authorization"))
		_, _ = w.Write([]byte(`this is a config`))
	}

	srv, httpClient := testlib.GetRestyBootstrap(handlerFunc)
	defer srv.Close()
	client := NewClientWithResty("asd", httpClient)

	rsp, err := client.GetConfig(program, environment)

	require.NoError(t, err)
	assert.IsType(t, &resty.Response{}, rsp)
}

func TestClientErrors(t *testing.T) {
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadRequest)
	}
	srv, httpClient := testlib.GetRestyBootstrap(handlerFunc)
	defer srv.Close()
	client := NewClientWithResty("asd", httpClient)

	rsp, err := client.GetConfig("qwe", "asd")

	require.Error(t, err)
	assert.True(t, xerrors.Is(err, bishopError))
	assert.Equal(t, http.StatusBadRequest, rsp.StatusCode())
}

func TestServerErrors(t *testing.T) {
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	}
	srv, httpClient := testlib.GetRestyBootstrap(handlerFunc)
	defer srv.Close()
	client := NewClientWithResty("asd", httpClient)

	rsp, err := client.GetConfig("qwe", "asd")

	require.Error(t, err)
	assert.True(t, xerrors.Is(err, internalError))
	assert.Equal(t, http.StatusInternalServerError, rsp.StatusCode())
}

func TestNoConfig(t *testing.T) {
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNotFound)
	}
	srv, httpClient := testlib.GetRestyBootstrap(handlerFunc)
	defer srv.Close()
	client := NewClientWithResty("asd", httpClient)

	rsp, err := client.GetConfig("qwe", "asd")

	require.Error(t, err)
	assert.Equal(t, configNotFound, err)
	assert.Equal(t, http.StatusNotFound, rsp.StatusCode())
}
