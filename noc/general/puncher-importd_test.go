package main

import (
	"context"
	"net/http"
	"os"
	"reflect"
	"testing"

	statsd "github.com/smira/go-statsd"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/go/startrek"
	"a.yandex-team.ru/noc/puncher/client/macrosd"
	"a.yandex-team.ru/noc/puncher/client/requestsd"
	"a.yandex-team.ru/noc/puncher/client/rulesd"
	"a.yandex-team.ru/noc/puncher/client/usersd"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/lib/metrics"
	"a.yandex-team.ru/noc/puncher/lib/mongodb"
	"a.yandex-team.ru/noc/puncher/mock/configmock"
	"a.yandex-team.ru/noc/puncher/mock/macrosdmock"
	"a.yandex-team.ru/noc/puncher/mock/requestsdmock"
	"a.yandex-team.ru/noc/puncher/mock/rulesdmock"
	"a.yandex-team.ru/noc/puncher/mock/usersdmock"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

var app *App

func NewTestApp() *App {
	a := &App{}

	configService := configmock.NewTestConfig()
	a.config = configService.ImportDaemon
	a.ctx = context.Background()
	a.statsdClient = metrics.NewStatsdClient()
	a.logger = logging.Must(configService.Logging.Level)

	a.session = mongodb.MustNew(configService.MongoDB, a.logger)
	a.usersdClient = usersd.NewCachedClient(a.config.UsersDaemonURL)
	a.rulesdClient = rulesd.NewClient(a.config.RulesDaemonURL)
	a.requestsdClient = requestsd.NewClient(a.config.RequestsDaemonURL)
	a.macrosdClient = macrosd.NewClient(a.config.MacrosDaemonURL)

	a.taskUpdateRulesTargets = metrics.NewTaskMonitor(
		"update rules targets",
		[]statsd.Tag{statsd.StringTag("role", "imported"), statsd.StringTag("task", "update_rules_targets")},
	)
	a.taskUpdateRequestsTargets = metrics.NewTaskMonitor(
		"update requests targets",
		[]statsd.Tag{statsd.StringTag("role", "imported"), statsd.StringTag("task", "update_requests_targets")},
	)
	stConfig := configService.StarTrek
	a.stClient = &startrek.Client{
		APIV2URL: stConfig.APIV2URL,
		APIToken: stConfig.Token,
		Client: http.Client{
			Timeout: stConfig.Timeout.Duration,
		},
		UserAgent: "Puncher",
	}
	return a
}

func run(m *testing.M) int {
	usersdServer := usersdmock.NewServer()
	requestsdServer := requestsdmock.NewServer()
	rulesdServer := rulesdmock.NewServer()
	macrosdmock.NewServer()

	app = NewTestApp()
	app.usersdClient = usersd.NewCachedClient(usersdServer.URL)
	app.rulesdClient = rulesd.NewClient(rulesdServer.URL)
	app.requestsdClient = requestsd.NewClient(requestsdServer.URL)

	return m.Run()
}

func TestMain(m *testing.M) {
	os.Exit(run(m))
}

func TestSectionChange(t *testing.T) {
	tests := []struct {
		Name             string
		OriginSections   []string
		NewSections      []string
		ExpectedSections []string
		MustNewRequest   bool
		Target           *models.Target
	}{
		{
			Name:             "add new section",
			OriginSections:   []string{},
			NewSections:      []string{"NEW"},
			ExpectedSections: []string{},
			MustNewRequest:   true,
			Target:           &modelstest.MntNets,
		},
		{
			Name:             "remove section",
			OriginSections:   []string{"ONE", "TWO"},
			NewSections:      []string{"ONE"},
			ExpectedSections: []string{"ONE", "TWO"},
			MustNewRequest:   true,
			Target:           &modelstest.TestNets,
		},
		{
			Name:             "change section 1",
			OriginSections:   []string{"ONE", "TWO"},
			NewSections:      []string{"ONE", "THREE"},
			ExpectedSections: []string{"ONE", "TWO"},
			MustNewRequest:   true,
			Target:           &modelstest.NocNets,
		},
	}

	for _, test := range tests {
		test.Target.Sections = test.OriginSections

		originalTarget := models.RuleTarget{
			Target:    *test.Target,
			DeletedAt: nil,
		}

		// create rule with original target
		testRule := models.Rule{
			Sources: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
			Status:  "active",
		}
		testRule.Destinations = append(testRule.Destinations, originalTarget)
		testRule.System = models.RuleSystemBigPuncher

		originalRule, err := app.rulesdClient.CreateRule(testRule)
		assert.NoError(t, err)

		// change original target
		test.Target.Sections = test.NewSections
		var so []models.SectionOwners
		for _, s := range test.NewSections {
			so = append(so, models.SectionOwners{Name: s})
		}
		app.macrosdClient = &macrosdmock.Client{
			ResponsiblesResult: so,
		}

		// update targets in rules
		err = app.UpdateRulesTargets()
		assert.NoError(t, err)

		// check if rules have updated targets
		newRule, err := app.rulesdClient.FindRuleByID(originalRule.ID)
		assert.NoError(t, err)

		for _, dst := range newRule.Destinations {
			if dst.MachineName == originalTarget.MachineName {
				assert.Equal(t, dst.Sections, test.ExpectedSections)
			}
		}

		// check if new requests are created
		_, requests, _, err := app.requestsdClient.GetRequestsPage(
			models.RequestsBaseQuery{RulesIDs: []models.ID{originalRule.ID}},
			models.RequestsCursor{},
			100)

		assert.NoError(t, err)

		if test.MustNewRequest && len(requests) == 0 {
			t.Errorf("Test '%s' failed: no new requests", test.Name)
		} else if !test.MustNewRequest && len(requests) > 0 {
			t.Errorf("Test '%s' failed: new requests created", test.Name)
		}
	}
}

func TestUpdateTargetDoesNotWriteEmptyResponsibles(t *testing.T) {
	tests := []struct {
		OrigResps  []string
		NewResps   []string
		SavedResps []string
	}{
		{
			OrigResps:  []string{"Alice"},
			NewResps:   []string{"Bob"},
			SavedResps: []string{"Bob"},
		},
		{
			OrigResps:  []string{"Alice"},
			NewResps:   []string{},
			SavedResps: []string{"Alice"},
		},
	}

	for _, test := range tests {
		origTarget := models.RuleTarget{
			Target:    modelstest.NocNets,
			DeletedAt: nil,
		}
		origTarget.Responsibles = test.OrigResps
		newTarget := modelstest.NocNets
		newTarget.Responsibles = test.NewResps
		app.usersdClient = &usersdmock.Client{GetByExternalIDReturnValue: newTarget}

		savedTarget, err := app.updateTarget(origTarget, false)
		if err != nil {
			t.Errorf("updateTarget %s", err)
		}

		if !reflect.DeepEqual(savedTarget.Responsibles, test.SavedResps) {
			t.Errorf("Invalid responsibles: expected %s, got %s", test.SavedResps, origTarget.Responsibles)
		}
	}

}
