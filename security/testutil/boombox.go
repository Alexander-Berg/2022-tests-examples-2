package testutil

import (
	"net/http/httptest"

	"a.yandex-team.ru/security/libs/go/boombox/httpreplay"
)

// TODO
func StartSumDB(proxy bool) (*httptest.Server, error) {
	opts := []httpreplay.Option{
		httpreplay.WithLogger(Logger),
		httpreplay.WithNamespace("sumdb"),
	}
	if proxy {
		opts = append(opts, httpreplay.WithProxyMode("http://sumdb.golang.org"))
	}

	r, err := httpreplay.NewReplay(KirbyTape(), opts...)
	if err != nil {
		return nil, err
	}

	return httptest.NewServer(r), nil
}

func StartGoProxy(proxy bool) (*httpreplay.Replay, error) {
	opts := []httpreplay.Option{
		httpreplay.WithLogger(Logger),
		httpreplay.WithNamespace("goproxy"),
	}
	if proxy {
		opts = append(opts, httpreplay.WithProxyMode("http://kirby.sec.yandex.net"))
	}

	r, err := httpreplay.NewReplay(KirbyTape(), opts...)
	if err != nil {
		return nil, err
	}

	return r, nil
}
