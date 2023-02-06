package knifeunittest

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmcache"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmtypes"
)

func TestFactoryFail(t *testing.T) {
	cfg := &tvmtypes.Config{
		BbEnvType: 3,
		Clients: map[string]tvmtypes.Client{
			"me": {
				Secret:    "ololo",
				SelfTvmID: 42,
				Dsts: map[string]tvmtypes.Dst{
					"he": {ID: 100501},
				},
			},
		},
	}
	ocfg := tvmtypes.NewOptimizedConfig(cfg)

	_, err := NewUnittestState(ocfg, "")
	if err == nil {
		t.Fatalf("Expecting error because of secret")
	}

	c := cfg.Clients["me"]
	c.Secret = "fake_secret"
	cfg.Clients["me"] = c
	ocfg = tvmtypes.NewOptimizedConfig(cfg)
	_, err = NewUnittestState(ocfg, "")
	if err != nil {
		t.Fatal(err)
	}

	c = cfg.Clients["me"]
	c.Secret = ""
	cfg.Clients["me"] = c
	ocfg = tvmtypes.NewOptimizedConfig(cfg)
	_, err = NewUnittestState(ocfg, "")
	require.NoError(t, err)

	c.IdmSlug = "unconfigured_slug"
	cfg.Clients["me"] = c
	_, err = NewUnittestState(tvmtypes.NewOptimizedConfig(cfg), "")
	require.EqualError(t, err, "dir with roles for unittest mode is not configured")
}

func TestFactoryOk(t *testing.T) {
	cfg := &tvmtypes.Config{
		BbEnvType: 3,
		Clients: map[string]tvmtypes.Client{
			"me": {
				Secret:    "fake_secret",
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

	if us.Update(nil, nil) != nil {
		t.Fatalf("Update should do nothing")
	}
	if us.ForceUpdate(nil, nil) != nil {
		t.Fatalf("Update should do nothing")
	}
}

func TestFactoryDiag(t *testing.T) {
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

	d := us.GetDiag()
	if len(d.TicketErrors) > 0 {
		t.Fatalf("TicketErrors must be empty")
	}

	if d.Tickets.Status != tvmcache.StatusOk {
		t.Fatalf("Wrong status: %d", d.Tickets.Status)
	}
	if time.Now().Unix()-d.Tickets.LastUpdate.Unix() > 5 || time.Now().Unix()-d.Tickets.LastUpdate.Unix() < -5 {
		t.Fatalf("Public keys has strange birthtime")
	}
	if d.Tickets.LastErr != nil {
		t.Fatal(d.Tickets.LastErr)
	}

	if d.Keys.Status != tvmcache.StatusOk {
		t.Fatalf("Wrong status: %d", d.Keys.Status)
	}
	if time.Now().Unix()-d.Keys.LastUpdate.Unix() > 5 || time.Now().Unix()-d.Keys.LastUpdate.Unix() < -5 {
		t.Fatalf("Public keys has strange birthtime")
	}
	if d.Keys.LastErr != nil {
		t.Fatal(d.Keys.LastErr)
	}
}
