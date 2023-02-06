package policy_test

import (
	"reflect"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/client/macrosd"
	"a.yandex-team.ru/noc/puncher/client/usersd"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/errors"
	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/policy"
	"a.yandex-team.ru/noc/puncher/mock/macrosdmock"
	"a.yandex-team.ru/noc/puncher/mock/usersdmock"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

func TestIsReduction(t *testing.T) {
	tests := []struct {
		Name    string
		Rule    models.Rule
		Request models.Request
		Result  bool
	}{
		{
			"ports: 80,443 -> 443",
			models.Rule{
				Ports: []models.Port{modelstest.MustPort("80"), modelstest.MustPort("443")},
			},
			models.Request{
				Ports: []models.Port{modelstest.MustPort("443")},
			},
			true,
		},
		{
			"ports: 443 -> 80,443",
			models.Rule{
				Ports: []models.Port{modelstest.MustPort("443")},
			},
			models.Request{
				Ports: []models.Port{modelstest.MustPort("80"), modelstest.MustPort("443")},
			},
			false,
		},
		{
			"sources: %alice% -> %alice%,%bob%",
			models.Rule{
				Sources: models.MakeRuleTargets([]models.Target{modelstest.Alice}),
			},
			models.Request{
				Sources: []models.Target{modelstest.Alice, modelstest.Bob},
			},
			false,
		},
		{
			"destinations: CAliceHosts -> CAliceHosts,CShared",
			models.Rule{
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
			},
			models.Request{
				Destinations: []models.Target{modelstest.CAliceHosts, modelstest.CShared},
			},
			false,
		},
	}

	for _, test := range tests {
		result := policy.IsReduction(&test.Rule, test.Request)
		if result != test.Result {
			t.Errorf("%s - got %v, want %v", test.Name, result, test.Result)
		}
	}
}

func TestGetRemovedTargets(t *testing.T) {
	tests := []struct {
		Name    string
		Rule    models.Rule
		Request models.Request
		Result  []models.Target
	}{
		{
			"sources: %alice% -> %alice%,%bob%",
			models.Rule{
				Sources: models.MakeRuleTargets([]models.Target{modelstest.Alice}),
			},
			models.Request{
				Sources: []models.Target{modelstest.Alice, modelstest.Bob},
			},
			[]models.Target{},
		},
		{
			"sources: %alice%,%bob% -> %alice%",
			models.Rule{
				Sources: models.MakeRuleTargets([]models.Target{modelstest.Alice, modelstest.Bob}),
			},
			models.Request{
				Sources: []models.Target{modelstest.Alice},
			},
			[]models.Target{modelstest.Bob},
		},
		{
			"sources: %alice%,%bob% -> %alice%; destinations: %alice%,%bob% -> %bob%",
			models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Alice, modelstest.Bob}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.Alice, modelstest.Bob}),
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.Bob},
			},
			[]models.Target{modelstest.Bob, modelstest.Alice},
		},
	}

	for _, test := range tests {
		result := policy.GetRemovedTargets(&test.Rule, test.Request)
		if !reflect.DeepEqual(result, test.Result) {
			t.Errorf("%s - got %v, want %v", test.Name, result, test.Result)
		}
	}
}

func TestCanCreateRequest(t *testing.T) {
	usersdServer := usersdmock.NewServer()
	defer usersdServer.Close()

	macrosdServer := macrosdmock.NewServer()
	defer macrosdServer.Close()

	usersdClient := usersd.NewClient(usersdServer.URL)
	macrosdClient := macrosd.NewClient(macrosdServer.URL)

	ruleFakeID := models.NewID()

	tests := []struct {
		Name       string
		User       models.Target
		Capability models.Capability
		Rule       *models.Rule
		Request    models.Request
		Status     models.RequestStatus
		UserRole   models.UserRole
		Err        errors.HTTPError
	}{
		{
			"owner can create requests with confirmed status",
			modelstest.Alice,
			models.Capability{},
			nil, models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusConfirmed, models.UserRoleAdmin, nil,
		},
		{
			"other users can create requests with new status",
			modelstest.Bob, models.Capability{},
			nil, models.Request{
				Sources:      []models.Target{modelstest.Bob},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusNew, models.UserRoleAuthor, nil,
		},
		{
			"mix destinations with different owners",
			modelstest.Bob, models.Capability{},
			nil, models.Request{
				Sources:      []models.Target{modelstest.Bob},
				Destinations: []models.Target{modelstest.CAliceHosts, modelstest.CShared},
			},
			models.RequestStatusNew, models.UserRoleAuthor, nil,
		},
		{
			"do not allow to create request from @dpt_yandex@",
			modelstest.Eve, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.DptYandex},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Type:         models.RequestTypeCreate,
			},
			"", "", errors.NewBadRequestError("use @allstaff@ instead of @dpt_yandex@ (DOSTUP-47304)"),
		},
		{
			"allow to delete rules from @dpt_yandex@",
			modelstest.Alice, models.Capability{AdminUser: true},
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.DptYandex}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
			},
			models.Request{
				RuleID:       &ruleFakeID,
				Type:         models.RequestTypeDelete,
				Sources:      []models.Target{modelstest.DptYandex},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusApproved, models.UserRoleAdmin, nil,
		},
		{
			"do not allow to create request from backbone to fastbone",
			modelstest.Eve, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.CAliceHosts, modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.FastboneNets},
				Type:         models.RequestTypeCreate,
			},
			"", "", errors.NewInternalError("There are destinations from Fastbone, but sources are in Backbone. Destinations in Fastbone: [_FB_NETS_]"),
		},
		{
			"do not allow to create request from fastbone to backbone",
			modelstest.Eve, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.FastboneNets},
				Destinations: []models.Target{modelstest.CAliceHosts, modelstest.CBobHosts},
				Type:         models.RequestTypeCreate,
			},
			"", "", errors.NewInternalError("There are sources from Fastbone, but destinations are in Backbone. Sources in Fastbone: [_FB_NETS_]"),
		},
		{
			"do not allow to create request with mixed targets fb/bb in sources",
			modelstest.Eve, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.FastboneNets, modelstest.CAliceHosts},
				Destinations: []models.Target{modelstest.FastboneNets2},
				Type:         models.RequestTypeCreate,
			},
			"", "", errors.NewInternalError("Mixed sources from fastbone and backbone. Fastbone sources: [_FB_NETS_]"),
		},
		{
			"do not allow to create request with mixed targets fb/bb in destinations",
			modelstest.Eve, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.FastboneNets},
				Destinations: []models.Target{modelstest.FastboneNets2, modelstest.CAliceHosts},
				Type:         models.RequestTypeCreate,
			},
			"", "", errors.NewInternalError("Mixed destinations from fastbone and backbone. Fastbone destinations: [_FB_2_NETS_]"),
		},
		{
			"allow to create request from fastbone to fastbone",
			modelstest.Eve, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.FastboneNets},
				Destinations: []models.Target{modelstest.FastboneNets2},
				Type:         models.RequestTypeCreate,
			},
			models.RequestStatusNew, models.UserRoleAuthor, nil,
		},
		{
			"reduction is auto-approved if made by the owner of one of removed targets from sources",
			modelstest.Alice, models.Capability{},
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Bob, modelstest.CAliceHosts}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts}),
			}, models.Request{
				Sources:      []models.Target{modelstest.Bob},
				Destinations: []models.Target{modelstest.CBobHosts},
				Type:         models.RequestTypeUpdate,
			},
			models.RequestStatusApproved, models.UserRoleAdmin, nil,
		},
		{
			"reduction is auto-approved if made by the owner of one of removed targets from destinations",
			modelstest.Alice, models.Capability{},
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Bob}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts, modelstest.CAliceHosts}),
			}, models.Request{
				Sources:      []models.Target{modelstest.Bob},
				Destinations: []models.Target{modelstest.CBobHosts},
				Type:         models.RequestTypeUpdate,
			},
			models.RequestStatusApproved, models.UserRoleAdmin, nil,
		},
		{
			"can not create request if rule is not changed",
			modelstest.Alice, models.Capability{},
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.CBobHosts, modelstest.CAliceHosts}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts}),
			}, models.Request{
				Sources:      []models.Target{modelstest.CBobHosts, modelstest.CAliceHosts},
				Destinations: []models.Target{modelstest.CBobHosts},
				Type:         models.RequestTypeUpdate,
			},
			"", "", errors.NewInternalError("Invalid request: nothing changed in the rule"),
		},
		{
			"anyone must be able to create a request for static rules",
			modelstest.Alice, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.CAliceHosts},
				Destinations: []models.Target{modelstest.CBobHosts},
			},
			models.RequestStatusNew, models.UserRoleAuthor, nil,
		},
		{
			"responsible must be able to create a static rule without SIB approve",
			modelstest.Alice, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.CAliceHosts},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusApproved, models.UserRoleAdmin, nil,
		},
		{
			"responsible must be able to delete a rule without SIB approve",
			modelstest.Alice, models.Capability{},
			nil,
			models.Request{
				Type:         models.RequestTypeDelete,
				Sources:      []models.Target{modelstest.Bob},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusApproved, models.UserRoleAdmin, nil,
		},
		{
			"responsible must be able to reduce a rule without SIB approve",
			modelstest.Alice, models.Capability{},
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.Bob, modelstest.Alice}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CAliceHosts}),
			},
			models.Request{
				Sources:      []models.Target{modelstest.Alice},
				Destinations: []models.Target{modelstest.CAliceHosts},
				Type:         models.RequestTypeUpdate,
			},
			models.RequestStatusApproved, models.UserRoleAdmin, nil,
		},
		{
			"do not allow to create request if static rule has sources from ForbiddenSources",
			modelstest.Bob, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.UsersNets},
				Destinations: []models.Target{modelstest.CBobHosts},
			},
			"", "", errors.NewInternalError("Can not create static rule from _DYNAMICACCESSNETS_ (in _DYNAMICACCESSNETS_), not supported by first-hop firewall"),
		},
		{
			"do not allow to create request if static rule has destinations to ForbiddenDestinations",
			modelstest.Bob, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.UsersNets},
			},
			"", "", errors.NewInternalError("Can not create static rule to _DYNAMICACCESSNETS_ (in _DYNAMICACCESSNETS_), not supported by first-hop firewall (PUNCHER-807)"),
		},
		{
			"if static rule has sources from RestrictedSources request must be approved SIB",
			modelstest.Bob, models.Capability{},
			nil,
			models.Request{
				Sources:      []models.Target{modelstest.GuestsNets},
				Destinations: []models.Target{modelstest.CBobHosts},
				Type:         models.RequestTypeUpdate,
			},
			models.RequestStatusConfirmed, models.UserRoleAdmin, nil,
		},
		{
			"if destination has responsibles but not common allow to create delete request",
			modelstest.Bob, models.Capability{},
			&models.Rule{
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.GuestsNets}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts, modelstest.CAliceHosts}),
			},
			models.Request{
				Type:         models.RequestTypeDelete,
				Sources:      []models.Target{modelstest.GuestsNets},
				Destinations: []models.Target{modelstest.CBobHosts, modelstest.CAliceHosts},
			},
			models.RequestStatusConfirmed, models.UserRoleAuthor, nil,
		},
		{
			// Add for PUNCHER-538
			"Not common allow to create change request",
			modelstest.Bob, models.Capability{},
			&models.Rule{
				ID:           ruleFakeID,
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.GuestsNets}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts, modelstest.CAliceHosts}),
			},
			models.Request{
				RuleID:       &ruleFakeID,
				Type:         models.RequestTypeDelete,
				Sources:      []models.Target{modelstest.GuestsNets},
				Destinations: []models.Target{modelstest.CBobHosts, modelstest.CAliceHosts},
			},
			"", "", errors.NewInternalError("You can not create request. Access denied."),
		},
		{
			// Add for PUNCHER-538
			"Allow to create change request for user's source",
			modelstest.Bob, models.Capability{},
			&models.Rule{
				ID:      ruleFakeID,
				Sources: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts}),
			},
			models.Request{
				RuleID:       &ruleFakeID,
				Type:         models.RequestTypeDelete,
				Sources:      []models.Target{modelstest.CBobHosts},
				Destinations: []models.Target{modelstest.CAliceHosts},
			},
			models.RequestStatusNew, models.UserRoleAuthor, nil,
		},
		{
			// Add for PUNCHER-538
			"Not common allow to create change request, but adminUser can create it",
			modelstest.Eve, models.Capability{AdminUser: true},
			&models.Rule{
				ID:           ruleFakeID,
				Sources:      models.MakeRuleTargets([]models.Target{modelstest.GuestsNets}),
				Destinations: models.MakeRuleTargets([]models.Target{modelstest.CBobHosts, modelstest.CAliceHosts}),
			},
			models.Request{
				RuleID:       &ruleFakeID,
				Type:         models.RequestTypeDelete,
				Sources:      []models.Target{modelstest.GuestsNets},
				Destinations: []models.Target{modelstest.CBobHosts, modelstest.CAliceHosts},
			},
			models.RequestStatusConfirmed, models.UserRoleAuthor, nil,
		},
		{
			"_HBF_EXCLUDE_* is forbidden in source",
			modelstest.Bob, models.Capability{},
			nil,
			models.Request{
				Type:         models.RequestTypeCreate,
				Sources:      []models.Target{modelstest.HbfExludeMacro},
				Destinations: []models.Target{modelstest.CBobHosts, modelstest.CAliceHosts},
			},
			"", "", errors.NewBadRequestError("macro _HBF_EXCLUDE_CLOUD_ is not suitable entity for source"),
		},
	}

	for _, test := range tests {
		status, userRole, err := policy.CanCreateRequest(usersdClient, macrosdClient, test.User, test.Capability, test.Rule, test.Request, false)
		if status != test.Status {
			t.Errorf("%s - status: got %q, want %q", test.Name, status, test.Status)
		}
		if userRole != test.UserRole {
			t.Errorf("%s - user role: got %q, want %q", test.Name, userRole, test.UserRole)
		}
		assert.Equal(t, test.Err, err)
	}
}
