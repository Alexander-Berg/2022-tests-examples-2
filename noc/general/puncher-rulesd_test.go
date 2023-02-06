package main

import (
	"fmt"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/rulesd"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-rulesd/storage"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/lib/mongodb"
	"a.yandex-team.ru/noc/puncher/mock/configmock"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

var testServer *httptest.Server
var rulesdClient rulesd.Client
var app *App

func NewTestApp() *App {
	a := &App{}

	configService := configmock.NewTestConfig()
	a.logger = logging.Must(configService.Logging.Level)

	a.config = configService.RulesDaemon
	a.session = mongodb.MustNew(configService.MongoDB, a.logger)

	rulesStorage, err := storage.New(a.session, a.logger)
	if err != nil {
		a.logger.Fatal("Unable to initialize rules storage", log.Error(err))
	}
	a.storage = rulesStorage
	return a
}

func run(m *testing.M) int {
	app = NewTestApp()
	defer app.Close()

	testServer = httptest.NewServer(app.httpHandler())
	defer testServer.Close()

	rulesdClient = rulesd.NewClient(testServer.URL)

	return m.Run()
}

func TestMain(m *testing.M) {
	os.Exit(run(m))
}

func TestCreateNewRule(t *testing.T) {
	port, err := models.NewPort("22")
	assert.NoError(t, err)

	rule := models.Rule{
		ID:           models.ID{},
		Sources:      models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
		Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts}),
		Protocol:     "tcp",
		Ports:        []models.Port{port},
		Locations:    []string{"vpn"},
		Until:        nil,
		Status:       "active",
		Tasks:        []string{"TEST-1"},
		Added:        time.Now(),
		Updated:      time.Now(),
	}

	rule, err = rulesdClient.CreateRule(rule)
	assert.NoError(t, err)

	rule, err = rulesdClient.FindRuleByID(rule.ID)
	assert.NoError(t, err)
}

func TestUpdateRule(t *testing.T) {
	port, err := models.NewPort("22")
	assert.NoError(t, err)

	originalRule := models.Rule{
		ID:           models.ID{},
		Sources:      models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
		Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts}),
		Protocol:     "tcp",
		Ports:        []models.Port{port},
		Locations:    []string{"vpn"},
		Until:        nil,
		Status:       "active",
		Tasks:        []string{"TEST-1"},
		Added:        time.Now(),
		Updated:      time.Now(),
	}

	originalRule, err = rulesdClient.CreateRule(originalRule)
	assert.NoError(t, err)

	//	Update original rule
	originalRule.Sources = models.MakeRuleTargets([]models.Target{modelstest.CAnotherAliceHosts})
	_, err = rulesdClient.UpdateRule(originalRule)
	assert.NoError(t, err)

	updatedRule, err := rulesdClient.FindRuleByID(originalRule.ID)
	assert.NoError(t, err)

	assert.Equal(t, updatedRule.Sources[0].MachineName, modelstest.CAnotherAliceHosts.MachineName)
	assert.Equal(t, updatedRule.ID, originalRule.ID)
}

func TestDeleteRule(t *testing.T) {
	port, err := models.NewPort("22")
	assert.NoError(t, err)

	rule := models.Rule{
		ID:           models.ID{},
		Sources:      models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
		Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts}),
		Protocol:     "tcp",
		Ports:        []models.Port{port},
		Locations:    []string{"vpn"},
		Until:        nil,
		Status:       "active",
		Tasks:        []string{"TEST-1"},
		Added:        time.Now(),
		Updated:      time.Now(),
	}

	rule, err = rulesdClient.CreateRule(rule)
	assert.NoError(t, err)

	_, err = rulesdClient.ObsoleteRule(rule.ID, "TEST TASK")
	assert.NoError(t, err)

	deletedRule, err := rulesdClient.FindRuleByID(rule.ID)
	assert.NoError(t, err)
	assert.Equal(t, deletedRule.Status, "obsolete")
}

func TestAddTaskToRule(t *testing.T) {
	port, err := models.NewPort("22")
	assert.NoError(t, err)

	rule := models.Rule{
		ID:           models.ID{},
		Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice}),
		Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
		Protocol:     "tcp",
		Ports:        []models.Port{port},
		Locations:    []string{"vpn"},
		Until:        nil,
		Status:       "active",
		Tasks:        []string{"TEST-1"},
		Added:        time.Now(),
		Updated:      time.Now(),
	}

	rule, err = app.storage.InsertRule(rule)
	assert.NoError(t, err)
	assert.Equal(t, rule.Tasks, []string{"TEST-1"})

	rule, err = app.storage.AddTaskToRule(rule, "TEST-2")
	assert.NoError(t, err)
	assert.Equal(t, rule.Tasks, []string{"TEST-1", "TEST-2"})

	rule = app.storage.MustAddTaskToRule(rule, "TEST-3")
	assert.Equal(t, rule.Tasks, []string{"TEST-1", "TEST-2", "TEST-3"})

	rule, err = app.storage.FindRuleByID(&rule.ID)
	assert.NoError(t, err)
	assert.Equal(t, rule.Tasks, []string{"TEST-1", "TEST-2", "TEST-3"})
}

func TestGetAllRules(t *testing.T) {
	port, err := models.NewPort("22")
	assert.NoError(t, err)

	rule := models.Rule{
		ID:           models.ID{},
		Sources:      models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
		Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts}),
		Protocol:     "tcp",
		Ports:        []models.Port{port},
		Locations:    []string{"vpn"},
		Until:        nil,
		Status:       "active",
		Tasks:        []string{"TEST-1"},
		Added:        time.Now(),
		Updated:      time.Now(),
	}

	rule, err = rulesdClient.CreateRule(rule)
	assert.NoError(t, err)
	fmt.Println("Rule ID ", rule.ID.Hex())
	rules, err := rulesdClient.GetAllRules()
	assert.NoError(t, err)
	findRule := false
	for _, r := range rules {
		if r.ID == rule.ID {
			findRule = true
		}
	}
	assert.True(t, findRule)
}
