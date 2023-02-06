package test_test

import (
	"reflect"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

func TestRuleSplitByPorts(t *testing.T) {
	rule := models.Rule{}
	for _, p := range []string{"22", "80", "443", "8000", "8080"} {
		port, _ := models.NewPort(p) // assume that all ports are valid
		rule.Ports = append(rule.Ports, port)
	}
	result := rule.SplitByPorts(2)

	assert.Len(t, result, 3)
	assert.Equal(t, result[0].Ports, rule.Ports[0:2])
	assert.Equal(t, result[1].Ports, rule.Ports[2:4])
	assert.Equal(t, result[2].Ports, rule.Ports[4:])
}

func targetsFromStrings(targets []string) []models.RuleTarget {
	ret := make([]models.RuleTarget, len(targets))
	for i, t := range targets {
		ret[i] = models.RuleTarget{Target: models.Target{MachineName: t}}
	}
	return ret
}

func TestM4Quoting(t *testing.T) {
	tests := [...]struct {
		source      []string
		destination []string
		fmtRule     string
	}{
		{
			[]string{"%alice%"},
			[]string{"github.com"},
			"add allow ip from { %alice% } to { github.com }",
		},
		{
			[]string{"%alice%"},
			[]string{"dnl.github.com"},
			"add allow ip from { %alice% } to { `dnl.github.com' }",
		},
		{
			[]string{"%alice%"},
			[]string{"dnl12.github.com"},
			"add allow ip from { %alice% } to { dnl12.github.com }",
		},
		{
			[]string{"%alice-define%"},
			[]string{"github.com"},
			"add allow ip from { `%alice-define%' } to { github.com }",
		},
		{
			[]string{"%alice_define%", "lenrus00.yandex.ru", "len-rus00.yandex.ru"},
			[]string{"github.com", "define.yourself.com"},
			"add allow ip from { %alice_define% or lenrus00.yandex.ru or `len-rus00.yandex.ru' } to { github.com or `define.yourself.com' }",
		},
	}

	for _, test := range tests {
		rule := models.Rule{
			Protocol:     "ip",
			Sources:      targetsFromStrings(test.source),
			Destinations: targetsFromStrings(test.destination),
		}
		assert.Equal(t, test.fmtRule, rule.IpfwRule(nil))
	}
}

func TestUpdateByRequest(t *testing.T) {
	deletedAlice := modelstest.Alice
	deletedAlice.IsDeleted = true
	origSources := models.MakeRuleTargets([]models.Target{deletedAlice})
	tests := [...]struct {
		rule         models.Rule
		request      models.Request
		expectedRule models.Rule
	}{
		{
			models.Rule{
				Sources:      origSources,
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
				Protocol:     "tcp",
				Status:       "active",
				System:       models.RuleSystemPuncher,
				Ports:        []models.Port{modelstest.MustPort("1-100")},
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice, modelstest.Bob},
				Destinations: []models.Target{modelstest.CShared},
				Protocol:     "udp",
				System:       models.RuleSystemPuncher,
				Task:         "TASK-123",
				Ports:        []models.Port{modelstest.MustPort("1-200")},
			},
			models.Rule{
				Sources:      append(origSources, models.MakeRuleTargets([]models.Target{modelstest.Bob})...),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CShared}),
				Protocol:     "udp",
				Status:       "active",
				System:       models.RuleSystemPuncher,
				Tasks:        []string{"TASK-123"},
				Ports:        []models.Port{modelstest.MustPort("1-200")},
			},
		},
	}
	for _, test := range tests {
		updatedRule := test.rule
		updatedRule.UpdateByRequest(test.request)
		assert.Equal(t, updatedRule, test.expectedRule)
	}
}

func TestRule_ExtractSrcYaNets(t *testing.T) {
	port := models.Port{
		Text:  "1",
		First: 1,
		Last:  1,
	}
	r := models.Rule{
		Protocol:     "udp",
		Sources:      targetsFromStrings([]string{"_YANDEXNETS_", "_NONYANDEXNETS_"}),
		Destinations: targetsFromStrings([]string{"h"}),
		Ports:        []models.Port{port},
		System:       "static",
		Status:       "active",
	}
	e := []models.Rule{{
		Protocol:     "udp",
		Sources:      targetsFromStrings([]string{"_YANDEXNETS_"}),
		Destinations: targetsFromStrings([]string{"h"}),
		Ports:        []models.Port{port},
		System:       "static",
		Status:       "active",
	}, {
		Protocol:     "udp",
		Sources:      targetsFromStrings([]string{"_NONYANDEXNETS_"}),
		Destinations: targetsFromStrings([]string{"h"}),
		Ports:        []models.Port{port},
		System:       "static",
		Status:       "active",
	}}

	if got := r.ExtractSrcYaNets(); !reflect.DeepEqual(got, e) {
		t.Errorf("ExtractSrcYaNets() = %v, want %v", got, e)
	}

}
