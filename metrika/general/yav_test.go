package yav

import (
	"a.yandex-team.ru/library/go/yandex/yav"
	"a.yandex-team.ru/library/go/yandex/yav/httpyav"
	"a.yandex-team.ru/metrika/go/pkg/testlib"
	"encoding/json"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func createVersion() yav.Version {
	return yav.Version{
		CreatedAt:    yav.Timestamp{Time: time.Now()},
		CreatedBy:    123,
		CreatorLogin: "qwerty",
		SecretName:   "secret",
		SecretUUID:   "sec-123",
		Values: []yav.Value{
			{
				Key:   "key1",
				Value: "sec1",
			},
			{
				Key:   "key2",
				Value: "sec2",
			},
		},
		VersionUUID: "ver-123",
	}
}

func TestGetSecret(t *testing.T) {
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		rsp := new(yav.GetVersionResponse)
		rsp.Status = yav.StatusOK
		rsp.Version = createVersion()
		body, _ := json.Marshal(rsp)

		_, _ = w.Write(body)
	}
	srv, httpClient := testlib.GetRestyBootstrap(handlerFunc)
	defer srv.Close()

	client, err := NewClientWithToken("")
	require.NoError(t, err)
	client.yavClient, err = httpyav.NewClientWithResty(httpClient)
	require.NoError(t, err)

	secret, err := client.GetSecret("sec-123", "key2")
	require.NoError(t, err)
	assert.Equal(t, "sec2", secret)
}

func TestKeyNotFound(t *testing.T) {
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		rsp := new(yav.GetVersionResponse)
		rsp.Status = yav.StatusOK
		rsp.Version = createVersion()
		body, _ := json.Marshal(rsp)

		_, _ = w.Write(body)
	}
	srv, httpClient := testlib.GetRestyBootstrap(handlerFunc)
	defer srv.Close()

	client, err := NewClientWithToken("")
	require.NoError(t, err)
	client.yavClient, err = httpyav.NewClientWithResty(httpClient)
	require.NoError(t, err)

	secret, err := client.GetSecret("sec-123", "key3")
	require.Error(t, err)
	assert.Equal(t, err, keyNotFound)
	assert.Equal(t, "", secret)
}

func TestAccessError(t *testing.T) {
	handlerFunc := func(w http.ResponseWriter, r *http.Request) {
		rsp := new(yav.GetVersionResponse)
		rsp.Status = yav.StatusError
		rsp.Code = yav.ErrAccess.Error()
		body, _ := json.Marshal(rsp)

		_, _ = w.Write(body)
	}
	srv, httpClient := testlib.GetRestyBootstrap(handlerFunc)
	defer srv.Close()

	client, err := NewClientWithToken("")
	require.NoError(t, err)
	client.yavClient, err = httpyav.NewClientWithResty(httpClient)
	require.NoError(t, err)

	secret, err := client.GetSecret("sec-123", "key1")
	require.Error(t, err)
	assert.Equal(t, err, yav.ErrAccess)
	assert.Equal(t, "", secret)
}
