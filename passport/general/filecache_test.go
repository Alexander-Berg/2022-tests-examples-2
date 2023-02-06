package tvmcache

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

func getFilePath(file string) string {
	return yatest.SourcePath("passport/infra/daemons/tvmtool/internal/tvmcache/gotest/" + file)
}

func TestSaveLoadKeysCache(t *testing.T) {
	wd, err := os.Getwd()
	require.NoError(t, err)

	filename := getCacheFileName(wd, keysCacheFileName)
	require.EqualValues(t, filename, fmt.Sprintf("%s/.tvm-keys.cache", wd))

	keys, err := ioutil.ReadFile(getFilePath("test_keys_response.txt"))
	require.NoError(t, err)

	savedTimestamp := uint64(time.Now().Unix())
	require.NoError(t, writeCacheFile(filename, savedTimestamp, keys))

	defer func() { _ = os.Remove(filename) }()

	keysCache, tmpstamp, err := readCacheFile(filename)
	require.NoError(t, err)

	require.EqualValues(t, savedTimestamp, tmpstamp)
	require.EqualValues(t, keysCache, keys)
}

func TestLoadCache(t *testing.T) {
	_, _, err := readCacheFile("filename")
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to read file:")

	_, _, err = readCacheFile(getFilePath("test_small_file.txt"))
	require.EqualError(t, err, "file is too small")

	_, _, err = readCacheFile(getFilePath("test_corrupted_file.txt"))
	require.EqualError(t, err, "invalid cache data hash value")
}

func TestTicketsCache(t *testing.T) {
	wd, err := os.Getwd()
	require.NoError(t, err)

	cache, err := NewCache(tvm.BlackboxTest, wd)
	require.NoError(t, err)
	filename := getCacheFileName(wd, ticketsCacheFileName)

	testTickets := map[ServiceTicketKey]tvmtypes.Ticket{
		{111, 252}:     "dummy_ticket_data_1",
		{111, 253}:     "dummy_ticket_data_2",
		{222, 333}:     "dummy_ticket_data_3",
		{222, 444}:     "dummy_ticket_data_4",
		{31337, 31338}: "leet_ticket_data",
	}

	savedTimestamp := uint64(time.Now().Unix())
	require.NoError(t, saveTicketsCache(filename, testTickets, savedTimestamp))

	defer func() { _ = os.Remove(filename) }()

	_, _, err = tryReadTicketsCache("filename")
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to read file:")

	_, _, err = tryReadTicketsCache(getFilePath("test_invalid_json.txt"))
	require.EqualError(t, err, "failed to parse json in cache")

	loadedTickets, tmstamp, err := tryReadTicketsCache(filename)
	require.NoError(t, err)
	require.EqualValues(t, tmstamp, savedTimestamp)

	for src, item := range loadedTickets {
		for dst, ticket := range item {
			originalTicket, ok := testTickets[ServiceTicketKey{src, dst}]
			require.True(t, ok, dst)
			require.EqualValues(t, ticket, originalTicket)
		}
	}

	for k := range testTickets {
		require.True(t, checkHasSrcDst(loadedTickets, k.Src, k.Dst))
	}
	require.False(t, checkHasSrcDst(loadedTickets, 42, 100500))
	require.False(t, checkHasSrcDst(loadedTickets, 111, 100500))

	cache.ticketCache.setTicketsForClient(
		&tvmtypes.Client{
			SelfTvmID: 111,
			Dsts: map[string]tvmtypes.Dst{
				"alias": {ID: 252},
			},
		},
		tvmtypes.TicketsInfo{
			Tickets: map[tvm.ClientID]tvmtypes.Ticket{
				252: "some ticket",
			},
		},
	)

	require.NoError(t, checkCacheDirectory("/"))
}

func TestTicketsCache_CheckCacheDirectory(t *testing.T) {
	require.NoError(t, checkCacheDirectory("/"))

	require.EqualError(t,
		checkCacheDirectory(getFilePath("test_invalid_json.txt")),
		"this is not a directory",
	)

	err := checkCacheDirectory("/ololo")
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to stat disk cache dir:")
}

func TestTicketsCacheDiag(t *testing.T) {
	cache, err := NewCache(tvm.BlackboxTest, "")
	require.NoError(t, err)
	require.NoError(t, cache.ticketCache.state.lastError)
	require.NoError(t, cache.keysCache.state.lastError)

	err1 := errors.New("my darling 1")
	cache.keysCache.setLastError(err1)
	require.NoError(t, cache.ticketCache.state.lastError)
	require.EqualError(t, cache.keysCache.state.lastError, err1.Error())

	err2 := errors.New("my darling 2")
	cache.ticketCache.setLastError(err2)
	require.EqualError(t, cache.ticketCache.state.lastError, err2.Error())
	require.EqualError(t, cache.keysCache.state.lastError, err1.Error())

	cache.ticketCache.setLastUpdated(time.Unix(10, 0))
	require.EqualValues(t, time.Unix(10, 0), cache.ticketCache.state.lastUpdated)

	require.EqualValues(t, StatusOk, cache.ticketCache.state.GetDiag(209, 100).Status)
	require.EqualValues(t, StatusWarning, cache.ticketCache.state.GetDiag(210, 100).Status)
	require.EqualValues(t, StatusWarning, cache.ticketCache.state.GetDiag(409, 100).Status)
	require.EqualValues(t, StatusError, cache.ticketCache.state.GetDiag(410, 100).Status)
}

type KeysGetter struct {
	res string
	err error
}

func (k *KeysGetter) GetKeys() (string, error) {
	return k.res, k.err
}

type TicketsGetter struct {
	res tvmtypes.TicketsInfo
	err error
}

func (t *TicketsGetter) GetTickets(secret string, src tvm.ClientID, dsts []tvmtypes.Dst) (tvmtypes.TicketsInfo, error) {
	return t.res, t.err
}

func TestCacheUpdateAndGet(t *testing.T) {
	// Empty cache
	cache, err := NewCache(tvm.BlackboxTest, "./")
	require.NoError(t, err)
	_, _, err = cache.GetKeys()
	require.EqualError(t, err, "tvm keys are empty")
	_, err = cache.GetServiceContext()
	require.EqualError(t, err, "service context update fail")
	_, err = cache.GetUserContext()
	require.EqualError(t, err, "user context update fail")
	require.EqualValues(t, time.Time{}, cache.GetTicketUpdateTime())

	// Initing
	config := tvmtypes.Config{
		BbEnvType: tvm.BlackboxTestYateam,
		Clients: map[string]tvmtypes.Client{
			"kokoko": {
				SelfTvmID: tvm.ClientID(111),
				Dsts: map[string]tvmtypes.Dst{
					"ololo": {
						ID: tvm.ClientID(252),
					},
				},
			},
		},
	}
	cfg := tvmtypes.NewOptimizedConfig(&config)

	require.NoError(t, checkCacheDirectory("./"))
	require.Error(t, cache.FetchFromDisk(cfg))

	// Processing keys
	tvmTestKeys, err := ioutil.ReadFile(getFilePath("test_keys_response.txt"))
	require.NoError(t, err)
	require.NoError(t, writeCacheFile("./"+keysCacheFileName, uint64(time.Now().Unix())-100000, tvmTestKeys))
	defer func() { _ = os.Remove("./" + keysCacheFileName) }()

	err = cache.FetchFromDisk(cfg)
	require.Error(t, err)
	require.Contains(t, err.Error(), "keys cache is too old, online updated is required")
	require.Contains(t, err.Error(), "failed to read file:")

	require.NoError(t, writeCacheFile("./"+keysCacheFileName, uint64(time.Now().Unix()), []byte("qwe1231321312qweqweqweqweqweqwqweqw")))
	err = cache.FetchFromDisk(cfg)
	require.Error(t, err)
	require.Contains(t, err.Error(), "invalid keys format")
	require.Contains(t, err.Error(), "failed to read file:")

	keyTime := time.Now()
	require.NoError(t, writeCacheFile("./"+keysCacheFileName, uint64(keyTime.Unix()), tvmTestKeys))
	require.Error(t, cache.FetchFromDisk(cfg))

	// Processing tickets
	testTickets := map[ServiceTicketKey]tvmtypes.Ticket{
		{111, 253}:     "dummy_ticket_data_2",
		{222, 333}:     "dummy_ticket_data_3",
		{222, 444}:     "dummy_ticket_data_4",
		{31337, 31338}: "leet_ticket_data",
	}
	require.NoError(t, saveTicketsCache("./"+ticketsCacheFileName, testTickets, uint64(time.Now().Unix())-100000))
	defer func() { _ = os.Remove("./" + ticketsCacheFileName) }()
	require.EqualError(t,
		cache.FetchFromDisk(cfg),
		"tickets cache is too old, online update is required",
	)

	require.NoError(t, saveTicketsCache("./"+ticketsCacheFileName, testTickets, uint64(time.Now().Unix())))
	require.EqualError(t,
		cache.FetchFromDisk(cfg),
		"cache and configuration mismatch",
	)

	testTickets[ServiceTicketKey{111, 252}] = "dummy_ticket_data_1"
	ticketsTime := time.Now()
	require.NoError(t, saveTicketsCache("./"+ticketsCacheFileName, testTickets, uint64(ticketsTime.Unix())))
	require.NoError(t, cache.FetchFromDisk(cfg))

	// Check cache
	v, tim, err := cache.GetKeys()
	require.NoError(t, err)
	require.EqualValues(t, string(tvmTestKeys), v)
	require.EqualValues(t, time.Unix(keyTime.Unix(), 0), tim)

	s, err := cache.GetServiceContext()
	require.NoError(t, err)
	require.NotNil(t, s)

	u, err := cache.GetUserContext()
	require.NoError(t, err)
	require.NotNil(t, u)

	require.EqualValues(t, time.Unix(ticketsTime.Unix(), 0), cache.GetTicketUpdateTime())

	// Internal set keys
	require.NoError(t, checkCacheDirectory("/"))
	kg := KeysGetter{
		res: string(tvmTestKeys),
	}
	require.NoError(t, cache.keysCache.Update(&kg))
	terr := errors.New("kek")
	kg.err = terr
	require.EqualError(t, cache.keysCache.Update(&kg), terr.Error())

	srvctx, err := cache.GetServiceContext()
	require.NoError(t, err)

	// Internal set tickets
	tg := TicketsGetter{
		res: tvmtypes.TicketsInfo{
			Tickets: map[tvm.ClientID]tvmtypes.Ticket{
				tvm.ClientID(253): "3:serv:CBAQ__________9_IgUIbxD9AQ:JfWruGnK-7-hg29Kin5hu4GsQ792k2uxxjGoaoC-kjQFIL2Gj-GBbbI_6C7fmir0_PrP2S6ONSeO4ChfN6MdZhzWT3g7000u5_A537YbKlrF5NU8T87ZSXltWqtlT7vdgpbq_nVWcf7HbggpwZ3btFIBWOWnchswfN4vMsE8IAY",
			},
			Errors: map[tvm.ClientID]string{},
		},
	}
	require.NoError(t, cache.ticketCache.updateImpl(&tg, srvctx, cfg.FindClientByAlias("kokoko")))
	delete(tg.res.Tickets, 253)
	require.Error(t, cache.ticketCache.updateImpl(&tg, srvctx, cfg.FindClientByAlias("kokoko")))
	tg.err = terr
	require.EqualError(t, cache.ticketCache.updateImpl(&tg, srvctx, cfg.FindClientByAlias("kokoko")), terr.Error())
}
