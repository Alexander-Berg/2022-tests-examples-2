package krl

import (
	"bytes"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/md5"
	"crypto/rand"
	_ "embed"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"testing"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/jarcoal/httpmock"
	"github.com/stretchr/testify/require"
	"github.com/stripe/krl"
	"golang.org/x/crypto/ssh"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/internal/cache"
	"a.yandex-team.ru/passport/infra/daemons/tvmcert/internal/utils"
	shared_utils "a.yandex-team.ru/passport/shared/golibs/utils"
)

//go:embed gotest/all.zst
var zstdKRL []byte
var zstdKRLEtag = "76ad74241b562578da09542a2de1227b"

var timeZero = time.Date(1, 1, 1, 0, 0, 0, 0, time.UTC)

func TestParseKRL(t *testing.T) {
	fmt.Println(zstdKRL)
}

func newSkottyKRLResponder() httpmock.Responder {
	return func(*http.Request) (*http.Response, error) {
		checkSum := md5.Sum(zstdKRL)
		return &http.Response{
			StatusCode: 200,
			Header: map[string][]string{
				"Etag": {hex.EncodeToString(checkSum[:])},
			},
			Body: io.NopCloser(bytes.NewReader(zstdKRL)),
		}, nil
	}
}

func noChangesSkottyKRLResponder() httpmock.Responder {
	return func(*http.Request) (*http.Response, error) {
		checkSum := md5.Sum(zstdKRL)
		return &http.Response{
			StatusCode: 304,
			Header: map[string][]string{
				"Etag": {hex.EncodeToString(checkSum[:])},
			},
			Body: nil,
		}, nil
	}
}

func newSkottyFetcherConfig() SkottyFetcherConfig {
	return SkottyFetcherConfig{
		SkottyURL:          "https://skotty.sec.yandex-team.ru",
		CacheDir:           yatest.OutputPath(""),
		UpdatePeriod:       &shared_utils.Duration{Duration: time.Minute},
		JugglerAgeWarn:     &shared_utils.Duration{Duration: 2 * time.Minute},
		JugglerAgeCritical: &shared_utils.Duration{Duration: 3 * time.Minute},
	}
}

type MockScottyFetcherMode int

const (
	NewValueDoUpdate MockScottyFetcherMode = iota
	OldValueNoUpdate
)

func withMockSkottyFetcherCommon(config SkottyFetcherConfig, f func(fetcher *SkottyFetcher), mode MockScottyFetcherMode) {
	client := resty.New().SetBaseURL(config.SkottyURL)
	cm, _ := cache.NewManager(path.Join(config.CacheDir, CacheFile))
	fetcher := &SkottyFetcher{
		holder:                 Holder{},
		client:                 client,
		cache:                  cm,
		jugglerWarnTimeout:     config.JugglerAgeWarn.Duration,
		jugglerCriticalTimeout: config.JugglerAgeCritical.Duration,
	}
	httpmock.ActivateNonDefault(client.GetClient())
	defer httpmock.DeactivateAndReset()
	if mode == NewValueDoUpdate {
		httpmock.RegisterResponder("GET", "https://skotty.sec.yandex-team.ru/api/v1/ca/krl/all.zst", newSkottyKRLResponder())
	} else {
		httpmock.RegisterResponder("GET", "https://skotty.sec.yandex-team.ru/api/v1/ca/krl/all.zst", noChangesSkottyKRLResponder())
	}
	f(fetcher)
}

func withMockSkottyFetcher(config SkottyFetcherConfig, f func(fetcher *SkottyFetcher)) {
	withMockSkottyFetcherCommon(config, f, NewValueDoUpdate)
}

func withMockSkottyFetcherNoUpdates(config SkottyFetcherConfig, f func(fetcher *SkottyFetcher)) {
	withMockSkottyFetcherCommon(config, f, OldValueNoUpdate)
}

func TestSkottyFetcher_InitWithAPI(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(CacheFile))
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		require.NoError(t, fetcher.Init())
	})
}

func TestSkottyFetcher_InitWithAPINoUpdates(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(CacheFile))
	withMockSkottyFetcherNoUpdates(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		err := fetcher.Update(fetcher.FetchFromAPI)
		require.EqualError(t, err, "got 'not modified' from api with empty Etag")
		err = fetcher.Init()
		require.Error(t, err)
	})
}

func TestSkottyFetcher_InitWithCache(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(CacheFile))
	config := newSkottyFetcherConfig()
	config.SkottyURL = "asdf"
	withMockSkottyFetcher(config, func(fetcher *SkottyFetcher) {
		k, err := ParseKRL(zstdKRL)
		require.NoError(t, err)
		fetcher.holder.Update(k, zstdKRLEtag)
		require.NoError(t, fetcher.WriteCache())
		fetcher.holder = Holder{}
		require.NoError(t, err)
		require.NoError(t, fetcher.Init())
		require.Equal(t, zstdKRLEtag, fetcher.holder.Etag)
		require.Equal(t, k, fetcher.holder.KRL)
	})
}

func TestSkottyFetcher_FetchKeysFromAPI(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(CacheFile))
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		k, ts, etag := fetcher.holder.GetKRL()
		require.Nil(t, k)
		require.Truef(t, ts.Equal(timeZero), "%s", ts)
		require.Equal(t, "", etag)
		now := time.Now()
		require.NoError(t, fetcher.Update(fetcher.FetchFromAPI))
		k, ts, etag = fetcher.holder.GetKRL()
		expectedKRL, _ := ParseKRL(zstdKRL)
		require.Equal(t, expectedKRL, k)
		require.Truef(t, ts.Equal(now) || ts.After(now), "%s != %s", now, ts)
		require.Equal(t, zstdKRLEtag, etag)
	})
}

func TestSkottyFetcher_FetchKeysFromAPINoUpdate(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(CacheFile))
	withMockSkottyFetcherNoUpdates(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		plainKRL, _ := base64.StdEncoding.DecodeString(`U1NIS1JMCgAAAAABAAAAAAAABNIAAAAAVoLDtwAAAAAAAAAAAAAAAAAAAAABAAAA3QAAAJcAAAAHc3NoLXJzYQAAAAMBAAEAAACBAKooUHhyxYmMyVQZ1RP0KktwX6CiEsXIaE1SA3XYjFyw0pzttXLLqbB0deluNjUR57D7WF7po8xY20EavDzW58JtfQQqLOhCvXr0BSJ5hoC58aVP21mKgKFwFTmVyOPmPUEa9dQ2/fK5Z1wuS7PMI1oD5/GVU4aqUhG6kZ7PtBN3AAAAACAAAAAQAAAAAAAAACoAAAAAAAARdSEAAAAQAAAAAAAAH0AAAAAAAAAnECIAAAAPAAAAAAAAZXIAAAADFVVV`)
		prevKRL, err := krl.ParseKRL(plainKRL)
		if err != nil {
			t.Fatal(err)
		}
		prevEtag := "12345"
		prevTS := time.Date(2001, 1, 1, 0, 0, 0, 0, time.UTC)
		fetcher.holder.UpdateWithTimestamp(prevKRL, prevTS, prevEtag)
		k, ts, etag := fetcher.holder.GetKRL()
		require.Equal(t, prevKRL, k)
		require.Equal(t, prevTS, ts)
		require.Equal(t, prevEtag, etag)
		now := time.Now()
		require.NoError(t, fetcher.Update(fetcher.FetchFromAPI))
		// only timestamp should be updated
		k, ts, etag = fetcher.holder.GetKRL()
		require.Equal(t, prevKRL, k)
		require.Truef(t, ts.Equal(now) || ts.After(now), "%s != %s", now, ts)
		require.Equal(t, prevEtag, etag)
	})
}

func TestSkottyFetcher_FetchKeysFromCache(t *testing.T) {
	defer utils.SkipYaTest(t)
	_ = os.Remove(yatest.OutputPath(CacheFile))
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		k, ts, etag := fetcher.holder.GetKRL()
		require.Nil(t, k)
		require.Truef(t, ts.Equal(timeZero), "%s", ts)
		require.Equal(t, "", etag)
		now := time.Now()
		c := Cache{
			Timestamp: now,
			Etag:      zstdKRLEtag,
		}

		expectedKRL, err := ParseKRL(zstdKRL)
		require.NoError(t, err)
		c.KRL, err = expectedKRL.Marshal(rand.Reader)
		require.NoError(t, err)

		data, _ := json.Marshal(c)
		require.NoError(t, os.WriteFile(yatest.OutputPath(CacheFile), data, os.ModePerm))
		require.NoError(t, fetcher.Update(fetcher.FetchFromCache))
		k, ts, etag = fetcher.holder.GetKRL()

		require.Equal(t, expectedKRL, k)
		require.Truef(t, ts.Equal(now), "%s != %s", now, ts)
		require.Equal(t, zstdKRLEtag, etag)
	})
}

func TestSkottyFetcher_CheckCertificate(t *testing.T) {
	withMockSkottyFetcher(newSkottyFetcherConfig(), func(fetcher *SkottyFetcher) {
		privateKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
		require.NoError(t, err)
		publicKey, err := ssh.NewPublicKey(privateKey.Public())
		require.NoError(t, err)
		ca, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
		require.NoError(t, err)
		caSigner, err := ssh.NewSignerFromKey(ca)
		require.NoError(t, err)

		cert1 := &ssh.Certificate{
			Key:             publicKey,
			Serial:          10,
			CertType:        ssh.UserCert,
			KeyId:           "10",
			ValidPrincipals: []string{"user1", "user2"},
			ValidAfter:      0,
			ValidBefore:     ssh.CertTimeInfinity,
			Permissions:     ssh.Permissions{},
		}
		require.NoError(t, cert1.SignCert(rand.Reader, caSigner))

		cert2 := &ssh.Certificate{
			Key:             publicKey,
			Serial:          100,
			CertType:        ssh.UserCert,
			KeyId:           "100",
			ValidPrincipals: []string{"user1", "user2"},
			ValidAfter:      0,
			ValidBefore:     ssh.CertTimeInfinity,
			Permissions:     ssh.Permissions{},
		}
		require.NoError(t, cert2.SignCert(rand.Reader, caSigner))

		k := krl.KRL{
			GeneratedDate: uint64(time.Now().Unix()),
			Version:       1,
			Sections: []krl.KRLSection{
				&krl.KRLCertificateSection{
					CA: caSigner.PublicKey(),
					Sections: []krl.KRLCertificateSubsection{
						&krl.KRLCertificateKeyID{"10", "11"},
					},
				},
			},
		}

		require.NoError(t, fetcher.Update(func() (*krl.KRL, time.Time, string, error) {
			return &k, time.Now(), "", nil
		}))

		require.Error(t, fetcher.CheckCertificate(cert1))
		require.NoError(t, fetcher.CheckCertificate(cert2))
	})
}
