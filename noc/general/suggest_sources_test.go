package actions_test

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/yandex/blackbox/httpbb"
	"a.yandex-team.ru/library/go/yandex/tvm/tvmauth"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/actions"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/front"
	"a.yandex-team.ru/noc/puncher/config"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/mock/macrosdmock"
	"a.yandex-team.ru/noc/puncher/mock/requestsdmock"
	"a.yandex-team.ru/noc/puncher/mock/rulesdmock"
	"a.yandex-team.ru/noc/puncher/mock/usersdmock"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

func TestGetSuggestSources(t *testing.T) {
	NocNetsWithFlags := modelstest.NocNets
	NocNetsWithFlags.Flags = models.TargetFlags{External: true}

	tests := []struct {
		Name                        string
		Part                        string
		Limit                       int
		SuggestSourcesReturnValue   []models.Target
		GetByMachineNameReturnValue models.Target
		FindHostsReturnValue        []string
		ExpectedTargets             []front.Target
		ExpectedErr                 error
	}{
		{
			Name:  "Empty request",
			Part:  "",
			Limit: 10,
			ExpectedTargets: []front.Target{
				{
					MachineName: "%alice%",
					Title:       models.NewLocalizedString("Alice", "Алиса"),
					Type:        models.TargetSubtypeUser,
					IsUserType:  true,
					Login:       "alice",
				},
				{
					MachineName: "@allstaff@",
					Title:       models.NewLocalizedString("@allstaff@", "@allstaff@"),
					Type:        models.TargetSubtypeManual,
					IsUserType:  true,
				},
				{
					MachineName: "any",
					Title:       models.LocalizedString{En: "Any", Ru: "Любой"},
					Type:        models.TargetSubtypeAny,
				},
			},
			ExpectedErr: nil,
		},
		{
			Name:                        "Usersd finds all",
			Part:                        "something",
			Limit:                       2,
			SuggestSourcesReturnValue:   []models.Target{modelstest.GitHubCom, modelstest.NocNets},
			GetByMachineNameReturnValue: NocNetsWithFlags,
			ExpectedTargets: []front.Target{
				{
					MachineName: "github.com",
					Title:       models.NewLocalizedString("github.com", "github.com"),
					Type:        models.TargetSubtypeHost,
				},
				{
					MachineName: "_NOCNETS_",
					Title:       models.NewLocalizedString("_NOCNETS_", "_NOCNETS_"),
					Type:        models.TargetSubtypeMacro,
					External:    true,
				},
			},
			ExpectedErr: nil,
		},
		{
			Name:                      "Duplicates are removed",
			Part:                      "github.com",
			Limit:                     3,
			SuggestSourcesReturnValue: []models.Target{modelstest.GitHubCom},
			FindHostsReturnValue:      []string{"github.com"},
			ExpectedTargets: []front.Target{
				{
					MachineName: "github.com",
					Title:       models.NewLocalizedString("github.com", "github.com"),
					Type:        models.TargetSubtypeHost,
				},
			},
			ExpectedErr: nil,
		},
	}

	logger := logging.Must(log.InfoLevel)
	requestsdClient := &requestsdmock.Client{}
	rulesdClient := &rulesdmock.Client{}
	macrosdClient := &macrosdmock.Client{}
	configService := &config.Service{}

	for _, test := range tests {
		usersdClient := &usersdmock.Client{
			SuggestSourcesReturnValue:        test.SuggestSourcesReturnValue,
			GetByMachineNameReturnValue:      test.GetByMachineNameReturnValue,
			GetUserByUIDReturnValue:          modelstest.Alice,
			GetManyByMachineNamesReturnValue: []models.Target{modelstest.Any, modelstest.AllStaff},
		}
		tvm := &tvmauth.Client{}
		bb, err := httpbb.NewIntranet()
		if err != nil {
			panic(err)
		}
		actionsService := actions.Init(
			usersdClient,
			requestsdClient,
			rulesdClient,
			macrosdClient,
			configService,
			bb,
			tvm,
			logger,
		)
		targets, err := actionsService.GetSuggestSources(&http.Request{}, test.Part, test.Limit)
		assert.Equal(t, test.ExpectedErr, err)
		assert.Equal(t, test.ExpectedTargets, targets)
	}
}
