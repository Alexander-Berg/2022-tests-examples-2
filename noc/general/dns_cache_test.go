package internal

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
)

type testLookupData struct {
	cbCount int
	dns     map[string]string
}

func (m *testLookupData) testLookup(ip string) (string, error) {
	m.cbCount += 1
	if res, ok := m.dns[ip]; ok {
		return res, nil
	} else {
		return "", fmt.Errorf("unable to reolve %v", ip)
	}
}

func TestDNSCache(t *testing.T) {
	as := assert.New(t)
	logger := zap.Must(zap.StandardConfig("console", log.DebugLevel)) // TODO: use fake logger
	var baseTS int64 = 1600000000
	now = func() time.Time { return time.Unix(baseTS, 0) }
	ttl = time.Second * 100
	testCb := testLookupData{
		dns: map[string]string{"127.0.0.1": "localhost"},
	}
	cache := newDNSCache(testCb.testLookup, logger)
	assertResolver(t, cache, "127.0.0.1", "localhost")
	now = func() time.Time { return time.Unix(baseTS+1, 0) }
	res, err := cache.Lookup("127.0.0.1")
	// prev res received from cache
	as.NoError(err)
	as.Equal(res, "localhost")
	as.Equal(testCb.cbCount, 1)
	// update record in dns
	testCb.dns["127.0.0.1"] = "nonlocalhost"
	now = func() time.Time { return time.Unix(baseTS+int64(minUpdateTTL.Seconds())+1, 0) }
	err = cache.updateCache()
	as.NoError(err)
	as.Equal(testCb.cbCount, 2)
	assertResolver(t, cache, "127.0.0.1", "nonlocalhost")
}

func assertResolver(t *testing.T, cache *dnsCache, ip string, expected string) {
	res, err := cache.Lookup(ip)
	assert.NoError(t, err)
	assert.Equal(t, res, expected)
}
