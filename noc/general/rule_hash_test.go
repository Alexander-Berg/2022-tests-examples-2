package importers_test

import (
	"testing"

	"a.yandex-team.ru/noc/puncher/cmd/puncher-rules-cauth/importers"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

func TestRuleHash(t *testing.T) {
	var ports []models.Port
	for _, p := range []string{"22", "80", "443"} {
		port, err := models.NewPort(p)
		if err != nil {
			t.Fatal(err)
		}
		ports = append(ports, port)
	}

	rule := models.Rule{
		Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
		Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
		Protocol:     "tcp",
		Ports:        ports,
		Locations:    []string{"office", "vpn"},
		Status:       "active",
		Comment:      "",
	}

	// $ printf "%s" '{"Sources":[{"Type":"user","ExternalID":"1"}],"Destinations":[{"Type":"macro","ExternalID":"2"}],"Protocol":"tcp","Ports":["22","80","443"],"Locations":["office","vpn"],"Status":"active","Comment":""}' | shasum -a 256
	// 862a95182a5bba70ad8d88190c143cf125fe65f134c06c493d2bd314b67601e2

	hash, err := importers.RuleHash(rule)
	if err != nil {
		t.Fatal(err)
	}
	expectedHash := "862a95182a5bba70ad8d88190c143cf125fe65f134c06c493d2bd314b67601e2"
	if hash != expectedHash {
		t.Fatalf("got %q, want %q", hash, expectedHash)
	}
}
