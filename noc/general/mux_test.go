package mur_test

import (
	"context"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/cmdb/pkg/mur"
	"a.yandex-team.ru/noc/cmdb/pkg/murchi"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestMakeChiMux(t *testing.T) {
	r := murchi.NewMux()
	r.Get("/ok", func() mur.Flow {
		return mur.NewFlow{}.NewFlow(nil).WithResult(&mur.ResultV2{
			Body: mur.BodyText(func(ctx context.Context) string {
				return "OK"
			}),
		})
	})
	r.With(func(handler http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusInternalServerError)
		})
	}).Get("/fail", func() mur.Flow {
		return mur.NewFlow{}.NewFlow(nil).WithResult(&mur.ResultV2{
			Body: mur.BodyText(func(ctx context.Context) string {
				return "OK"
			}),
		})
	})
	server := httptest.NewServer(r.IntoChiMux(fn.NopLogger))
	defer server.Close()
	client := http.DefaultClient

	response, err := client.Get(server.URL + "/ok")
	require.NoError(t, err)
	require.Equal(t, http.StatusOK, response.StatusCode)
	body, err := ioutil.ReadAll(response.Body)
	require.NoError(t, err)
	require.Equal(t, []byte("OK"), body)

	response, err = client.Get(server.URL + "/fail")
	require.NoError(t, err)
	require.Equal(t, http.StatusInternalServerError, response.StatusCode)
}
