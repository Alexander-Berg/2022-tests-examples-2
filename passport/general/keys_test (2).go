package keys

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"io"
	"net/http"
	"os"
	"path"
	"strings"
	"testing"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/ssh"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/internal/cache"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/internal/utils"
	shared_utils "a.yandex-team.ru/passport/shared/golibs/utils"
)

var publicKeysResponse = `ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBP8w+sr7XJuSXHQ9OAOj0eRfv4fQi/qFnW185Ae5fkKX9VhtmkM7LpfIy7NeOOthxS9wUJmfEcAGUrSH5Pry/ZU=
ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEJARUiEOnhTZ1d9A9fPIAN7NNOOUantJ5jvr0zjRCc2Qf7RFJUOvT9NaTUIilhkfDviLJj4mp07QWK23pz8OXE= insecure_20211011
ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBJnF1UG50PejZLaFFAWTMOL7e4xy44Z/mDJyF6RTsQsIxFN2oC9E4cwOTKSf2Ko/jemdnDOWu+j8X6f4y2KTV5M=
ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEhN1c1fB+DiAH/hFpOV4oUSyBUZ/KkIa1VpHOzRx54YBQMi+7cMBFdqYMSQO4zQAsQk1uix76/XLz90G1WEGuI= secure_20211011`

var publicKeys = []string{
	"AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBP8w+sr7XJuSXHQ9OAOj0eRfv4fQi/qFnW185Ae5fkKX9VhtmkM7LpfIy7NeOOthxS9wUJmfEcAGUrSH5Pry/ZU=",
	"AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEJARUiEOnhTZ1d9A9fPIAN7NNOOUantJ5jvr0zjRCc2Qf7RFJUOvT9NaTUIilhkfDviLJj4mp07QWK23pz8OXE=",
	"AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBJnF1UG50PejZLaFFAWTMOL7e4xy44Z/mDJyF6RTsQsIxFN2oC9E4cwOTKSf2Ko/jemdnDOWu+j8X6f4y2KTV5M=",
	"AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEhN1c1fB+DiAH/hFpOV4oUSyBUZ/KkIa1VpHOzRx54YBQMi+7cMBFdqYMSQO4zQAsQk1uix76/XLz90G1WEGuI=",
}
var timeZero = time.Date(1, 1, 1, 0, 0, 0, 0, time.UTC)

func newSkottyPKResponder() httpmock.Responder {
	return func(*http.Request) (*http.Response, error) {
		return &http.Response{
			StatusCode: 200,
			Body:       io.NopCloser(strings.NewReader(publicKeysResponse)),
		}, nil
	}
}

func newSkottyFetcherConfig() SkottyFetcherConfig {
	return SkottyFetcherConfig{
		SkottyURL:             "https://skotty.sec.yandex-team.ru",
		CacheDir:              yatest.OutputPath(""),
		KeysUpdatePeriod:      &shared_utils.Duration{Duration: time.Minute},
		JugglerKeyAgeWarn:     &shared_utils.Duration{Duration: 2 * time.Minute},
		JugglerKeyAgeCritical: &shared_utils.Duration{Duration: 3 * time.Minute},
	}
}

func withMockSkottyFetcher(config SkottyFetcherConfig, f func(fetcher *SkottyFetcher)) {
	client := resty.New().SetBaseURL(config.SkottyURL)
	cm, _ := cache.NewManager(path.Join(config.CacheDir, publicKeysFile))
	fetcher := &SkottyFetcher{
		keysHolder:             Holder{},
		client:                 client,
		cache:                  cm,
		jugglerWarnTimeout:     config.JugglerKeyAgeWarn.Duration,
		jugglerCriticalTimeout: config.JugglerKeyAgeCritical.Duration,
	}
	httpmock.ActivateNonDefault(client.GetClient())
	defer httpmock.DeactivateAndReset()
	httpmock.RegisterResponder("GET", "https://skotty.sec.yandex-team.ru/api/v1/ca/pub/ssh", newSkottyPKResponder())
	f(fetcher)
}

func TestSkottyFetcher_InitWithAPI(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(publicKeysFile))
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		require.NoError(t, fetcher.Init())
	})
}

func TestSkottyFetcher_InitWithCache(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(publicKeysFile))
	config := newSkottyFetcherConfig()
	config.SkottyURL = "asdf"
	withMockSkottyFetcher(config, func(fetcher *SkottyFetcher) {
		keys, err := ParsePublicKeys(io.NopCloser(strings.NewReader(publicKeysResponse)))
		require.NoError(t, err)
		fetcher.keysHolder.Update(keys)
		require.NoError(t, fetcher.WriteCache())
		fetcher.keysHolder = Holder{}
		require.NoError(t, err)
		require.NoError(t, fetcher.Init())
	})
}

func TestSkottyFetcher_FetchKeysFromAPI(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(publicKeysFile))
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		keys, ts := fetcher.keysHolder.GetKeys()
		require.Equal(t, 0, len(keys))
		require.Truef(t, ts.Equal(timeZero), "%s", ts)
		now := time.Now()
		require.NoError(t, fetcher.UpdateKeys(fetcher.FetchKeysFromAPI))
		keys, ts = fetcher.keysHolder.GetKeys()
		require.Equal(t, len(publicKeys), len(keys))
		for i, key := range keys {
			require.Equal(t, publicKeys[i], base64.StdEncoding.EncodeToString(key.Marshal()))
		}
		require.Truef(t, ts.Equal(now) || ts.After(now), "%s != %s", now, ts)
	})
}

func TestSkottyFetcher_FetchKeysFromCache(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(publicKeysFile))
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		keys, ts := fetcher.keysHolder.GetKeys()
		require.Equal(t, 0, len(keys))
		require.Truef(t, ts.Equal(timeZero), "%s", ts)
		now := time.Now()
		c := PublicKeyCache{
			Timestamp: now,
			Keys:      [][]byte{},
		}
		for _, key := range publicKeys {
			rawKey, err := base64.StdEncoding.DecodeString(key)
			require.NoError(t, err)
			c.Keys = append(c.Keys, rawKey)
		}
		data, _ := json.Marshal(c)
		require.NoError(t, os.WriteFile(yatest.OutputPath(publicKeysFile), data, os.ModePerm))
		require.NoError(t, fetcher.UpdateKeys(fetcher.FetchKeysFromCache))
		keys, ts = fetcher.keysHolder.GetKeys()
		require.Equal(t, len(publicKeys), len(keys))
		for i, key := range keys {
			require.Equal(t, publicKeys[i], base64.StdEncoding.EncodeToString(key.Marshal()))
		}
		require.Truef(t, ts.Equal(now), "%s != %s", now, ts)
	})
}

func TestSkottyFetcher_ParsePublicKeys(t *testing.T) {
	keys, err := ParsePublicKeys(io.NopCloser(strings.NewReader(publicKeysResponse)))
	require.NoError(t, err)
	require.Equal(t, len(publicKeys), len(keys))
	for i, key := range keys {
		require.Equal(t, publicKeys[i], base64.StdEncoding.EncodeToString(key.Marshal()))
	}
}

func TestSkottyFetcher_CheckPublicKey(t *testing.T) {
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		require.NoError(t, fetcher.Init())
		keys, err := ParsePublicKeys(io.NopCloser(strings.NewReader(publicKeysResponse)))
		require.NoError(t, err)
		for _, key := range keys {
			require.NoError(t, fetcher.CheckPublicKey(key))
		}
		pk, err := ecdsa.GenerateKey(elliptic.P384(), rand.Reader)
		require.NoError(t, err)
		key, err := ssh.NewPublicKey(&pk.PublicKey)
		require.NoError(t, err)
		require.Error(t, fetcher.CheckPublicKey(key))
	})
}
