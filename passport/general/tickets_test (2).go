package knifeunittest

import (
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/crypto"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

func TestTime(t *testing.T) {
	cfg := &tvmtypes.Config{
		BbEnvType: 3,
		Clients: map[string]tvmtypes.Client{
			"me": {
				Secret:    unittestSecret,
				SelfTvmID: 42,
				Dsts: map[string]tvmtypes.Dst{
					"he": {ID: 100501},
				},
			},
		},
	}
	ocfg := tvmtypes.NewOptimizedConfig(cfg)

	us, err := NewUnittestState(ocfg, "")
	if err != nil {
		t.Fatal(err)
	}

	require.True(t, time.Now().Before(us.GetTicketUpdateTime().Add(time.Duration(5)*time.Second)))
	require.True(t, time.Now().After(us.GetTicketUpdateTime().Add(time.Duration(-5)*time.Second)))
}

func TestCheckSrcDst(t *testing.T) {
	cfg := &tvmtypes.Config{
		BbEnvType: 3,
		Clients: map[string]tvmtypes.Client{
			"me": {
				Secret:    unittestSecret,
				SelfTvmID: 42,
				Dsts: map[string]tvmtypes.Dst{
					"he": {ID: 100501},
				},
			},
		},
	}
	ocfg := tvmtypes.NewOptimizedConfig(cfg)

	res := checkSrcDst(ocfg, 42, 100501)
	if len(res) > 0 {
		t.Fatalf("Unexpected error: %s", res)
	}

	res = checkSrcDst(ocfg, 43, 100501)
	if res != "Src 43 was not configured" {
		t.Fatalf("Unexpected error: %s", res)
	}

	res = checkSrcDst(ocfg, 42, 100500)
	if res != "Dst 100500 was not configured for src 42" {
		t.Fatalf("Unexpected error: %s", res)
	}
}

func TestNewTicket(t *testing.T) {
	priv, err := crypto.RWPrivateKeyFromString(crypto.TvmKnifePrivateKey)
	if err != nil {
		t.Fatal(err)
	}

	res, err := newServiceTicket(priv, 42, 100500)
	if err != nil {
		t.Fatal(err)
	}

	if !strings.HasPrefix(res, "3:serv:C") {
		t.Fatalf("Unexpected error: %s", res)
	}
}

func TestGetTicket(t *testing.T) {
	cfg := &tvmtypes.Config{
		BbEnvType: 3,
		Clients: map[string]tvmtypes.Client{
			"me": {
				Secret:    unittestSecret,
				SelfTvmID: 42,
				Dsts: map[string]tvmtypes.Dst{
					"he": {ID: 100501},
				},
			},
		},
	}
	ocfg := tvmtypes.NewOptimizedConfig(cfg)

	us, err := NewUnittestState(ocfg, "")
	if err != nil {
		t.Fatal(err)
	}

	if tick, er, err := us.GetTicket(42, 100501); err != nil || len(er) != 0 || len(tick) == 0 {
		t.Fatalf("GetTicket: %s, %s, %s", tick, er, err)
	}
	if tick, er, err := us.GetTicket(40, 100501); err != nil || len(er) == 0 || len(tick) != 0 {
		t.Fatalf("GetTicket: %s, %s, %s", tick, er, err)
	}
}
