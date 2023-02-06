package tvmcache

import (
	_ "embed"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/httpclientmock"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

//go:embed gotest/secret
var secret string

func TestCache(t *testing.T) {
	keysResponse, err := ioutil.ReadFile(getFilePath("test_keys_response.txt"))
	require.NoError(t, err)

	ticketResponse, err := ioutil.ReadFile(getFilePath("test_ticket_response.txt"))
	require.NoError(t, err)

	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodPost && strings.Contains(req.URL.Path, "ticket") {
					return ticketResponse, http.StatusOK, nil
				}
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return keysResponse, http.StatusOK, nil
				}

				return nil, http.StatusOK, nil
			},
		},
	}

	cfg := tvmtypes.Config{
		Backends: tvmtypes.BackendsConfig{
			TvmURL:    &url.URL{Scheme: "http", Host: "localhost:1"},
			TiroleURL: &url.URL{Scheme: "http", Host: "localhost:2"},
		},
	}

	cfg.Clients = make(map[string]tvmtypes.Client)

	dsts := map[string]tvmtypes.Dst{
		"bb_test_2": {ID: 252},
		"bb_test_3": {ID: 253},
		"missing":   {ID: 100500},
	}

	cfg.Clients["bb_test_1"] = tvmtypes.Client{
		Secret:    secret,
		SelfTvmID: 251,
		Dsts:      dsts,
	}
	optimized := tvmtypes.NewOptimizedConfig(&cfg)

	cache, err := NewCache(optimized.GetBbEnv(), "")
	require.NoError(t, err)
	require.NoError(t, cache.Update(optimized, client))

	keys, _, err := cache.GetKeys()
	require.NoError(t, err)
	fmt.Println("Keys: ", len(keys))

	tick, er, err := cache.GetTicket(251, 252)
	require.NoError(t, err)
	require.Contains(t, tick, "3:serv:CBAQ__________9_IgYI-wEQ_AE:")
	require.EqualValues(t, "", er)

	tick, er, err = cache.GetTicket(251, 253)
	require.NoError(t, err)
	require.Contains(t, tick, "3:serv:CBAQ__________9_IgYI-wEQ_QE:")
	require.EqualValues(t, "", er)

	_, _, err = cache.GetTicket(251, 254)
	require.Error(t, err)

	_, er, err = cache.GetTicket(251, 100500)
	require.NoError(t, err)
	require.EqualValues(t, "no such client_id", er)

	d := cache.GetDiag()
	require.EqualValues(t, StatusOk, d.Keys.Status)
	require.EqualValues(t, StatusOk, d.Tickets.Status)

	// Nothing to do
	require.NoError(t, cache.Update(optimized, client))
	// Ignore timings
	require.NoError(t, cache.ForceUpdate(optimized, client))

	client = &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodPost && strings.Contains(req.URL.Path, "ticket") {
					return ticketResponse, http.StatusOK, nil
				}
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return []byte("1:qwe"), http.StatusOK, nil
				}
				return nil, http.StatusOK, nil
			},
		},
	}
	cache, err = NewCache(optimized.GetBbEnv(), "")
	require.NoError(t, err)
	err = cache.Update(optimized, client)
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to check tickets after fetching")

	cache, err = NewCache(optimized.GetBbEnv(), "")
	require.NoError(t, err)

	require.EqualError(t,
		cache.ForceUpdate(optimized, client),
		"invalid protobuf in keys",
	)

	client = &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodPost && strings.Contains(req.URL.Path, "ticket") {
					return []byte("{}"), http.StatusOK, nil
				}
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return []byte("1:qwerty"), http.StatusOK, nil
				}
				return nil, http.StatusOK, nil
			},
		},
	}
	cache, err = NewCache(optimized.GetBbEnv(), "")
	require.NoError(t, err)
	require.Error(t, cache.Update(optimized, client))

	cache, err = NewCache(optimized.GetBbEnv(), "")
	require.NoError(t, err)
	require.Error(t, cache.ForceUpdate(optimized, client))

	client = &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodPost && strings.Contains(req.URL.Path, "ticket") {
					return []byte("{}"), http.StatusOK, nil
				}
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return keysResponse, http.StatusOK, nil
				}
				return nil, http.StatusOK, nil
			},
		},
	}
	cache, err = NewCache(optimized.GetBbEnv(), "")
	require.NoError(t, err)
	require.Error(t, cache.Update(optimized, client))
}

func TestCacheOnlyKeys(t *testing.T) {
	keysResponse, err := ioutil.ReadFile(getFilePath("test_keys_response.txt"))
	require.NoError(t, err)

	client := &http.Client{
		Transport: httpclientmock.TestRoundTripper{
			AnswerFunc: func(req *http.Request) ([]byte, int, error) {
				if req.Method == http.MethodGet && strings.Contains(req.URL.Path, "keys") {
					return keysResponse, http.StatusOK, nil
				}
				return nil, http.StatusNotFound, nil
			},
		},
	}
	cfg := tvmtypes.Config{
		Backends: tvmtypes.BackendsConfig{
			TvmURL: &url.URL{Scheme: "http", Host: "localhost:1"},
		},
		Clients: map[string]tvmtypes.Client{
			"bb_test_1": {
				Secret:    secret,
				SelfTvmID: 251,
				Dsts:      nil,
			},
		},
	}

	optimized := tvmtypes.NewOptimizedConfig(&cfg)

	cache, err := NewCache(optimized.GetBbEnv(), "")
	require.NoError(t, err)

	require.NoError(t, cache.Update(optimized, client))

	d := cache.GetDiag()
	require.EqualValues(t, StatusOk, d.Keys.Status)
	require.EqualValues(t, StatusOk, d.Tickets.Status)
}
