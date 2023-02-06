package cli

import (
	"io/ioutil"
	"os"
	"strings"
	"testing"

	"a.yandex-team.ru/library/go/yandex/tvm"
	"a.yandex-team.ru/passport/infra/daemons/tvmtool/internal/tvmsrv"
)

const (
	test2Str   = "test2"
	qwerty3Str = "qwerty3"
)

func TestParseSrcDst(t *testing.T) {
	test1 := "11:test:11"
	if _, _, err := parseSrcDst(test1); err == nil {
		t.Errorf("Parsing error: %s", test1)
	}

	test2 := "11:test"
	if id, alias, err := parseSrcDst(test2); err != nil {
		t.Errorf("parsing error: %s, %s", test2, err.Error())
	} else {
		if id != 11 {
			t.Errorf("id parsing error: %d", id)
		}

		if alias != "test" {
			t.Errorf("alias parsing error: %s", alias)
		}
	}

	test3 := "test:test"
	if _, _, err := parseSrcDst(test3); err == nil {
		t.Errorf("parsing error: %s", test3)
	}
}

func TestRemoveOldConfiguration(t *testing.T) {
	cfg := tvmsrv.ConfigView{
		Clients: map[string]tvmsrv.ClientView{
			"test": {
				SelfTvmID: 22,
				Secret:    "testsecret",
				Dsts:      nil,
			},
			test2Str: {
				SelfTvmID: 33,
				Secret:    "testsecret2",
				Dsts:      nil,
			},
		},
	}

	removeOldConfiguration(&cfg, 22, "test45")
	if len(cfg.Clients) != 1 {
		t.Fatal("cfg.Clients len must be 1")
	}

	if _, ok := cfg.Clients["test"]; ok {
		t.Fatal("test app must be removed from configuration")
	}

	removeOldConfiguration(&cfg, 45, test2Str)
	if _, ok := cfg.Clients[test2Str]; ok {
		t.Fatal("test2 must be removed from configuration")
	}
}

func TestSaveLoad(t *testing.T) {
	// partial
	cfg := tvmsrv.ConfigView{
		Clients: map[string]tvmsrv.ClientView{
			"test": {
				SelfTvmID: 22,
				Secret:    "testsecret",
				Dsts:      nil,
			},
			test2Str: {
				SelfTvmID: 33,
				Secret:    "testsecret2",
				Dsts:      nil,
			},
		},
	}

	filename := "./localtmp"
	if err := saveConfiguration(&cfg, filename); err != nil {
		t.Fatal(err)
	}
	defer func() { _ = os.Remove(filename) }()

	cfg2, err := readConfiguration(filename)
	if err != nil {
		t.Fatal(err)
	}

	if cfg.Port != cfg2.Port || cfg.Port != nil {
		t.Fatalf("ports: %d, %d", cfg.Port, cfg2.Port)
	}
	if cfg.BbEnvType != cfg2.BbEnvType || cfg.BbEnvType != nil {
		t.Fatalf("BbEnvType: %d, %d", cfg.BbEnvType, cfg2.BbEnvType)
	}
	for k, v := range cfg.Clients {
		if v2, ok := cfg2.Clients[k]; !ok {
			t.Fatalf("missing: %s", k)
		} else if v.SelfTvmID != v2.SelfTvmID {
			t.Fatalf("missmatch: %d, %d", v.SelfTvmID, v2.SelfTvmID)
		} else if v.Secret != v2.Secret {
			t.Fatalf("missmatch: %s, %s", v.Secret, v2.Secret)
		}
	}

	// full
	port := uint16(18080)
	env := tvm.BlackboxEnv(3)
	cfg.Port = &port
	cfg.BbEnvType = &env
	if err := saveConfiguration(&cfg, filename); err != nil {
		t.Fatal(err)
	}
	cfg2, err = readConfiguration(filename)
	if err != nil {
		t.Fatal(err)
	}
	if *cfg.Port != *cfg2.Port || *cfg.Port != port {
		t.Fatalf("ports: %d, %d", *cfg.Port, *cfg2.Port)
	}
	if *cfg.BbEnvType != *cfg2.BbEnvType || *cfg.BbEnvType != env {
		t.Fatalf("BbEnvType: %d, %d", *cfg.BbEnvType, *cfg2.BbEnvType)
	}
	for k, v := range cfg.Clients {
		if v2, ok := cfg2.Clients[k]; !ok {
			t.Fatalf("missing: %s", k)
		} else if v.SelfTvmID != v2.SelfTvmID {
			t.Fatalf("missmatch: %d, %d", v.SelfTvmID, v2.SelfTvmID)
		} else if v.Secret != v2.Secret {
			t.Fatalf("missmatch: %s, %s", v.Secret, v2.Secret)
		}
	}

	// misc
	if cfg3, err := readConfiguration("./missing"); err != nil {
		t.Fatal(err)
	} else if le := len(cfg3.Clients); le != 0 {
		t.Fatalf("len: %d", le)
	}
	if err := ioutil.WriteFile(filename, []byte("{"), os.FileMode(fileMod)); err != nil {
		t.Fatal(err)
	}
	if _, err := readConfiguration(filename); err == nil {
		t.Fatalf("invalid json")
	}
	if err := saveConfiguration(&cfg, "/missing"); err == nil {
		t.Fatalf("no file to read")
	}
}

func TestGetSecretsInConfiguration(t *testing.T) {
	cfg := tvmsrv.ConfigView{
		Clients: map[string]tvmsrv.ClientView{
			"test": {
				SelfTvmID: 22,
				Secret:    "testsecret",
				Dsts:      nil,
			},
			test2Str: {
				SelfTvmID: 33,
				Secret:    "testsecret2",
				Dsts:      nil,
			},
		},
	}

	if err := getSecretsInConfiguration(&cfg); err != nil {
		t.Fatal(err)
	}

	cl := cfg.Clients[test2Str]
	cl.Secret = "env:KOKOKO_MISSING"
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "failed to get secret for client 33 (test2): env 'KOKOKO_MISSING' is empty or absent") {
		t.Fatal(err)
	}

	_ = os.Setenv("KOKOKO_MISSING", "qwerty")
	defer func() { _ = os.Setenv("KOKOKO_MISSING", "") }()
	if err := getSecretsInConfiguration(&cfg); err != nil {
		t.Fatal(err)
	}
	if secret := cfg.Clients[test2Str].Secret; secret != "qwerty" {
		t.Fatalf("Unexpected secret: %s", secret)
	}

	cl.Secret = "json:"
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "failed to parse structured secret value for client 33 (test2): json:") {
		t.Fatal(err)
	}

	filename := "./tmp.json"
	cl.Secret = "json:" + filename + "[kek]"
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "open ./tmp.json: no such file or directory") {
		t.Fatal(err)
	}

	_ = ioutil.WriteFile(filename, []byte("[]"), 0222)
	defer func() { _ = os.Remove(filename) }()
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "open ./tmp.json: permission denied") {
		t.Fatal(err)
	}

	_ = os.Remove(filename)
	_ = ioutil.WriteFile(filename, []byte("[]"), 0666)
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "failed to load secret from file for client 33 (test2): json map is expected in './tmp.json'") {
		t.Fatal(err)
	}

	_ = ioutil.WriteFile(filename, []byte("{}"), 0666)
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "failed to load secret from file for client 33 (test2): key 'kek' was not found in './tmp.json'") {
		t.Fatal(err)
	}

	_ = ioutil.WriteFile(filename, []byte("{\"kek\":{}}"), 0666)
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "failed to load secret from file for client 33 (test2): key 'kek' is not string in './tmp.json'") {
		t.Fatal(err)
	}

	_ = ioutil.WriteFile(filename, []byte("{\"kek\":\"\"}"), 0666)
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err == nil ||
		!strings.Contains(err.Error(), "failed to load secret from file for client 33 (test2): key 'kek' is empty in './tmp.json'") {
		t.Fatal(err)
	}

	_ = ioutil.WriteFile(filename, []byte("{\"kek\":\"qwerty3\",\"foo\":{}}"), 0666)
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err != nil {
		t.Fatal(err)
	}
	if secret := cfg.Clients[test2Str].Secret; secret != qwerty3Str {
		t.Fatalf("Unexpected secret: %s", secret)
	}

	_ = ioutil.WriteFile(filename, []byte("{\"kek\":\"qwerty3\",\"foo\":\"\"}"), 0666)
	cfg.Clients[test2Str] = cl
	if err := getSecretsInConfiguration(&cfg); err != nil {
		t.Fatal(err)
	}
	if secret := cfg.Clients[test2Str].Secret; secret != qwerty3Str {
		t.Fatalf("Unexpected secret: %s", secret)
	}
}
