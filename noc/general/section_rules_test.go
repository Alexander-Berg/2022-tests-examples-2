package app

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

func TestSectionRules(t *testing.T) {
	rules := make(sectionRules)
	rules.AddRule(
		models.Rule{
			Comment: "My comment1",
			Tasks:   []string{"AA-1"},
			System:  models.RuleSystemBigPuncher,
		},
		"add allow tcp from any to any",
		"file1",
		true,
	)
	rules.AddRule(
		models.Rule{
			Comment: "My comment2",
			Tasks:   []string{"AA-2"},
			System:  models.RuleSystemRacktables,
		},
		"add allow tcp from any to any",
		"file1",
		true,
	)
	rules.AddRule(
		models.Rule{Comment: "My comment1", Tasks: []string{"AA-3"}},
		"add allow tcp from any to any",
		"file2",
		true,
	)
	rules.AddRule(
		models.Rule{Comment: "My comment1", Tasks: []string{"AA-4"}},
		"add allow tcp from {_YANDEXNETS_} to any",
		"file1",
		true,
	)

	rules.AddRule(
		models.Rule{Comment: "My comment1", Tasks: []string{"AA-5"}},
		"add allow tcp from any to any",
		"file3",
		false,
	)
	rules.AddRule(
		models.Rule{Comment: "My comment1", Tasks: []string{"AA-6"}},
		"add allow tcp from any to any",
		"file3",
		false,
	)

	sources := models.MakeRuleTargets([]models.Target{modelstest.NocNets})
	rules.AddRule(
		models.Rule{
			Comment:  "My comment1",
			Tasks:    []string{"AA-7"},
			Sources:  sources,
			Ports:    []models.Port{{First: 80, Last: 80, Text: "80"}},
			Protocol: "tcp",
		},
		"-A _CURRENTTABLE_ -p tcp --source { _NOCNETS_ } --dport 80 -j ACCEPT",
		"slb/file1",
		false,
	)
	rules.AddRule(
		models.Rule{
			Comment:  "My comment1",
			Tasks:    []string{"AA-8"},
			Sources:  sources,
			Ports:    []models.Port{{First: 443, Last: 443, Text: "443"}},
			Protocol: "tcp",
		},
		"-A _CURRENTTABLE_ -p tcp --source { _NOCNETS_ } --dport 443 -j ACCEPT",
		"slb/file1",
		false,
	)
	rules.AddRule(
		models.Rule{
			Comment: "My comment1",
			Tasks:   []string{"AA-9"},
			Sources: sources,
			Ports: []models.Port{
				{First: 80, Last: 80, Text: "80"},
				{First: 400, Last: 500, Text: "400-500"},
			},
			Protocol: "tcp",
		},
		"-A _CURRENTTABLE_ -m multiport -p tcp --source { _NOCNETS_ } --dports 80,400:500 -j ACCEPT",
		"slb/file1",
		false,
	)
	rules.AddRule(
		models.Rule{
			Comment:  "My comment1",
			Tasks:    []string{"AA-10"},
			Sources:  models.MakeRuleTargets([]models.Target{modelstest.TestNets}),
			Ports:    []models.Port{{First: 80, Last: 80, Text: "80"}},
			Protocol: "tcp",
		},
		"-A _CURRENTTABLE_ -p tcp --source { _TESTNETS_ } --dport 80 -j ACCEPT",
		"slb/file1",
		false,
	)

	location, err := time.LoadLocation("Europe/Moscow")
	assert.NoError(t, err)
	rules.MergeSLBPorts("slb/", location)

	expected := []sectionRuleText{
		{
			Text:     "# My comment1; AA-4\nadd allow tcp from {_YANDEXNETS_} to any\n\n",
			FilePath: "file1",
		},
		{
			Text:     "# My comment1; AA-1\n# My comment2; AA-2\nadd allow tcp from any to any\n\n",
			FilePath: "file1",
		},
		{
			Text:     "# My comment1; AA-3\nadd allow tcp from any to any\n\n",
			FilePath: "file2",
		},
		{
			Text:     "# AA-5\n# AA-6\nadd allow tcp from any to any\n\n",
			FilePath: "file3",
		},
		{
			Text:     "# AA-8\n# AA-7\n# AA-9\n-A _CURRENTTABLE_ -m multiport -p tcp --source { _NOCNETS_ } --dports 80,400:500 -j ACCEPT\n\n",
			FilePath: "slb/file1",
		},
		{
			Text:     "# AA-10\n-A _CURRENTTABLE_ -p tcp --source { _TESTNETS_ } --dport 80 -j ACCEPT\n\n",
			FilePath: "slb/file1",
		},
	}
	assert.Equal(t, expected, rules.IterRules())
}
