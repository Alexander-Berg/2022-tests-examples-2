package policy_test

import (
	"reflect"
	"testing"
	"time"

	"a.yandex-team.ru/noc/puncher/cmd/puncher-daemon/policy"
	"a.yandex-team.ru/noc/puncher/models"
	"a.yandex-team.ru/noc/puncher/models/modelstest"
)

var (
	dateOneWeekLater    time.Time
	dateThreeMonthLater time.Time
	dateSixMonthLater   time.Time
)

func init() {
	now := time.Now().Truncate(time.Second)
	dateOneWeekLater = now.AddDate(0, 0, 7)
	dateThreeMonthLater = now.AddDate(0, 3, 0)
	dateSixMonthLater = now.AddDate(0, 6, 0)
}

func TestNoUntilForGroup(t *testing.T) {
	httpErr := policy.ValidateUntil(nil, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt},
		Until:   nil,
	})
	if httpErr != nil {
		t.Errorf("got %v, want nil", httpErr)
	}
}

func TestLongUntilForGroup(t *testing.T) {
	httpErr := policy.ValidateUntil(nil, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt},
		Until:   &dateThreeMonthLater,
	})
	if httpErr != nil {
		t.Errorf("got %v, want nil", httpErr)
	}
}

func TestNoUntilForUser(t *testing.T) {
	httpErr := policy.ValidateUntil(nil, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt, modelstest.Alice},
		Until:   nil,
	})
	if !reflect.DeepEqual(httpErr, policy.ErrLongDurationForRuleWithLogin) {
		t.Errorf("got %v, want %v", httpErr, policy.ErrLongDurationForRuleWithLogin)
	}
}

func TestShortUntilForUser(t *testing.T) {
	httpErr := policy.ValidateUntil(nil, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt, modelstest.Alice},
		Until:   &dateOneWeekLater,
	})
	if httpErr != nil {
		t.Errorf("got %v, want nil", httpErr)
	}
}

func TestNoopRequest(t *testing.T) {
	httpErr := policy.ValidateUntil(&models.Rule{
		Sources: models.MakeRuleTargets([]models.Target{modelstest.DptYandexMnt, modelstest.Alice}),
		Until:   &dateThreeMonthLater,
	}, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt, modelstest.Alice},
		Until:   &dateThreeMonthLater,
	})
	if httpErr != nil {
		t.Errorf("got %v, want nil", httpErr)
	}
}

func TestAddGroupToExistingRule(t *testing.T) {
	httpErr := policy.ValidateUntil(&models.Rule{
		Sources: models.MakeRuleTargets([]models.Target{modelstest.Alice}),
		Until:   &dateThreeMonthLater,
	}, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt, modelstest.Alice},
		Until:   &dateThreeMonthLater,
	})
	if httpErr != nil {
		t.Errorf("got %v, want nil", httpErr)
	}
}

func TestAddUserToExistingRule(t *testing.T) {
	httpErr := policy.ValidateUntil(&models.Rule{
		Sources: models.MakeRuleTargets([]models.Target{modelstest.Alice, modelstest.DptYandexMnt}),
		Until:   &dateThreeMonthLater,
	}, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt, modelstest.Bob, modelstest.Alice},
		Until:   &dateThreeMonthLater,
	})
	if !reflect.DeepEqual(httpErr, policy.ErrLongDurationForRuleWithLogin) {
		t.Errorf("got %v, want %v", httpErr, policy.ErrLongDurationForRuleWithLogin)
	}
}

func TestChangeLongUntilForUser(t *testing.T) {
	httpErr := policy.ValidateUntil(&models.Rule{
		Sources: models.MakeRuleTargets([]models.Target{modelstest.Alice}),
		Until:   &dateSixMonthLater,
	}, models.Request{
		Sources: []models.Target{modelstest.Alice},
		Until:   &dateThreeMonthLater,
	})
	if !reflect.DeepEqual(httpErr, policy.ErrChangeDurationForRuleWithLogin) {
		t.Errorf("got %v, want %v", httpErr, policy.ErrChangeDurationForRuleWithLogin)
	}
}

func TestDropUntilForGroup(t *testing.T) {
	httpErr := policy.ValidateUntil(&models.Rule{
		Sources: models.MakeRuleTargets([]models.Target{modelstest.DptYandexMnt}),
		Until:   &dateThreeMonthLater,
	}, models.Request{
		Sources: []models.Target{modelstest.DptYandexMnt},
		Until:   nil,
	})
	if httpErr != nil {
		t.Errorf("got %v, want nil", httpErr)
	}
}

func TestDropUntilForUser(t *testing.T) {
	httpErr := policy.ValidateUntil(&models.Rule{
		Sources: models.MakeRuleTargets([]models.Target{modelstest.Alice}),
		Until:   &dateThreeMonthLater,
	}, models.Request{
		Sources: []models.Target{modelstest.Alice},
		Until:   nil,
	})
	if !reflect.DeepEqual(httpErr, policy.ErrChangeDurationForRuleWithLogin) {
		t.Errorf("got %v, want %v", httpErr, policy.ErrChangeDurationForRuleWithLogin)
	}
}
