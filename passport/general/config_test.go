package tvmtypes

import (
	"errors"
	"testing"

	"a.yandex-team.ru/library/go/yandex/tvm"
)

func TestNewOptimizedConfig(t *testing.T) {
	cfg := Config{}

	cfg.Clients = make(map[string]Client)

	dsts := map[string]Dst{
		"bb_test_2": {252},
		"bb_test_3": {253},
	}

	cfg.Clients["bb_test_1"] = Client{
		Secret:    "azQnNi5BpraJplR-EFtfVA",
		SelfTvmID: 251,
		Dsts:      dsts,
	}

	dsts2 := map[string]Dst{
		"bb_test_4": {254},
	}
	cfg.Clients["bb_test_8"] = Client{
		Secret:    "6zQnNi5BpraJplR",
		SelfTvmID: 200,
		Dsts:      dsts2,
	}

	optimized := NewOptimizedConfig(&cfg)

	if client := optimized.FindClientByID(251); client == nil {
		t.Fatal(errors.New("can't find client for id in optimized config"))
	}
	if client := optimized.FindClientByID(1); client != nil {
		t.Fatal(errors.New("nothing must be found for client_id=1"))
	}
	if client := optimized.FindClientByAlias("bb_test_1"); client == nil {
		t.Fatal(errors.New("can't find client for id in optimized config"))
	}
	if client := optimized.FindClientByAlias("ololo"); client != nil {
		t.Fatal(errors.New("nothing must be found for client_id=ololo"))
	}

	if optimized.GetNumClients() != 2 {
		t.Fatal(errors.New("invalid number of clients in optimized config"))
	}

	client := optimized.FindClientByAlias("bb_test_1")
	if client == nil {
		t.Fatalf("missing client")
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_1"); err == nil {
		t.Fatalf("Should fail. id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_2"); err != nil {
		t.Fatal(err)
	} else if id != tvm.ClientID(252) || alias != "bb_test_2" {
		t.Fatalf("id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_3"); err != nil {
		t.Fatal(err)
	} else if id != tvm.ClientID(253) || alias != "bb_test_3" {
		t.Fatalf("id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_4"); err == nil {
		t.Fatalf("Should fail. id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_8"); err == nil {
		t.Fatalf("Should fail. id=%d. alias=%s", id, alias)
	}

	client = optimized.FindClientByAlias("bb_test_8")
	if client == nil {
		t.Fatalf("missing client")
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_1"); err == nil {
		t.Fatalf("Should fail. id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_2"); err == nil {
		t.Fatalf("Should fail. id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_3"); err == nil {
		t.Fatalf("Should fail. id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_4"); err != nil {
		t.Fatal(err)
	} else if id != tvm.ClientID(254) || alias != "bb_test_4" {
		t.Fatalf("id=%d. alias=%s", id, alias)
	}
	if id, alias, err := optimized.FindDstForClient(client, "bb_test_8"); err == nil {
		t.Fatalf("Should fail. id=%d. alias=%s", id, alias)
	}

	if optimized.GetBbEnv() != tvm.BlackboxProd {
		t.Fatal(errors.New("Bad env"))
	}

	cls := optimized.GetClients()
	if cls == nil {
		t.Fatalf("GetClients must return something")
	}
	if len(cls) != 2 {
		t.Fatalf("GetClients returned wrong count: %d", len(cls))
	}

	if id := cfg.Clients["bb_test_1"].SelfTvmID; cls[0].SelfTvmID != id && cls[1].SelfTvmID != id {
		t.Fatalf("GetClients return first client with secret: %d", id)
	}
	if id := cfg.Clients["bb_test_8"].SelfTvmID; cls[0].SelfTvmID != id && cls[1].SelfTvmID != id {
		t.Fatalf("GetClients return second client with secret: %d", id)
	}
}
