package uaasproxy

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestModifyFlags(t *testing.T) {
	experiments := []Experiment{
		{
			Handler: "PASSPORT",
			TestID:  182998,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"show-subscriptions", "to-be-removed"},
				},
			},
		},
		{
			Handler: "PASSPORT",
			TestID:  176965,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"domik-challenge-exp"},
				},
			},
		},
	}
	toAdd := []string{"to-be-added-1", "to-be-added-2"}
	toRemove := []string{"to-be-removed"}
	actual := modifyFlags(experiments, toAdd, toRemove)
	assert.Equal(t, 3, len(actual)) // всё лишнее уберётся из-за неожиданной структуры данных
	assert.Equal(t, []string{"show-subscriptions"}, actual[0].Context.Passport.Flags)
	assert.Equal(t, []string{"domik-challenge-exp"}, actual[1].Context.Passport.Flags)
	assert.Equal(t, []string{"to-be-added-1", "to-be-added-2"}, actual[2].Context.Passport.Flags)
}

func TestRemoveOnly(t *testing.T) {
	experiments := []Experiment{
		{
			Handler: "PASSPORT",
			TestID:  182998,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"show-subscriptions", "to-be-removed"},
				},
			},
		},
	}
	toAdd := []string{}
	toRemove := []string{"to-be-removed"}
	actual := modifyFlags(experiments, toAdd, toRemove)
	assert.Equal(t, 1, len(actual))
	assert.Equal(t, []string{"show-subscriptions"}, actual[0].Context.Passport.Flags)
}

func TestMatchParameters(t *testing.T) {
	inputExpression := RewriteExperimentsExpression{
		MatchKeyValue: map[string]string{
			"k1": "v1",
			"k2": "v2",
		},
	}
	inputParams := map[string]string{
		"k1": "v1",
		"k2": "v2",
		"k3": "v3",
	}
	assert.True(t, matchParameters(inputExpression, inputParams))

	inputExpression = RewriteExperimentsExpression{
		MatchKeyValue: map[string]string{
			"k1": "v1",
			"k2": "v2",
		},
	}
	inputParams = map[string]string{
		"k1": "v1",
	}

	assert.False(t, matchParameters(inputExpression, inputParams))
}

func TestUniqueAppIDs(t *testing.T) {
	// Тест проверяет, что в конфиге сейчас один app_id встречается один раз
	// Чтобы не запутаться
	InitRewriteConfig()
	assert.Greater(t, len(RewriteConfig), 0)

	seenAppIDs := map[string]string{}

	for _, expression := range RewriteConfig {
		for expectedKey, appID := range expression.MatchKeyValue {
			if expectedKey != "app_id" {
				continue
			}
			_, exists := seenAppIDs[appID]
			if exists {
				assert.Fail(t, fmt.Sprintf("app_id %+v is not unique", appID))
			} else {
				seenAppIDs[appID] = ""
			}
		}
	}
	assert.Greater(t, len(seenAppIDs), 0)
}

var testRules = []struct {
	request       map[string]string
	flagsToAdd    []string
	flagsToRemove []string
}{
	{
		map[string]string{
			"app_id": "ru.yandex.taxi",
		},
		[]string{"turn_neophonish_reg_on=1", "native_to_browser_exp=0"},
		[]string{},
	},
	{
		map[string]string{
			"app_id": "ru.yandex.vezet",
		},
		[]string{"new_design_on=0", "native_to_browser_exp=0", "turn_mailing_accept_on=0"},
		[]string{},
	},
	{
		map[string]string{
			"app_id": "ru.yandex.uber",
		},
		[]string{"native_to_browser_exp=0", "turn_mailing_accept_on=0"},
		[]string{},
	},
	{
		map[string]string{
			"app_id": "unit-tests",
		},
		[]string{},
		[]string{},
	},
	{
		map[string]string{
			"am_version": "unit-tests",
		},
		[]string{},
		[]string{},
	},
	{
		map[string]string{
			"app_id":     "unit-tests",
			"am_version": "unit-tests",
		},
		[]string{"hello-unit-tests"},
		[]string{},
	},
}

func TestRules(t *testing.T) {
	// Тест проверяет, что все заказанные правила переписывания работают как надо
	// ...чтобы не продергивать курлом
	InitRewriteConfig()
	assert.Greater(t, len(RewriteConfig), 0)

	for _, tt := range testRules {
		t.Run(
			tt.request["app_id"],
			func(t *testing.T) {
				experiments := []Experiment{
					{
						Handler: "PASSPORT",
						TestID:  182998,
						Context: UaasContext{
							Passport: UaasFlags{
								Flags: tt.flagsToRemove,
							},
						},
					},
				}
				rewrittenExperiments := rewriteExperiments(experiments, RewriteConfig, tt.request)
				if len(tt.flagsToAdd) > 0 {
					// старый эксперимент остался + новый добавился
					assert.Equal(t, 2, len(rewrittenExperiments))
					// новый флаг добавляется как новый эксперимент с test-id -1
					assert.Equal(t, -1, rewrittenExperiments[1].TestID)
					assert.Equal(t, tt.flagsToAdd, rewrittenExperiments[1].Context.Passport.Flags)
				} else {
					assert.Equal(t, 1, len(rewrittenExperiments))
				}
				// в этом тесте все флаги старого эксперимента должны удалиться,
				// потому что они изначально параметризуются flagsToRemove
				assert.Equal(t, 0, len(rewrittenExperiments[0].Context.Passport.Flags))
			},
		)
	}
}

func BenchmarkRewriteOnlyByAppID(b *testing.B) {
	InitRewriteConfig()
	experiments := []Experiment{
		{
			Handler: "PASSPORT",
			TestID:  182998,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"test"},
				},
			},
		},
	}
	request := map[string]string{
		"app_id": "ru.yandex.taxi",
	}
	config := []RewriteExperimentsExpression{
		{
			MatchKeyValue: map[string]string{
				"app_id": "ru.yandex.taxi",
			},
			FlagsToAdd: []string{"hello-unit-tests"},
		},
	}

	for n := 0; n < b.N; n++ {
		rewriteExperiments(experiments, config, request)
	}
}

func BenchmarkRewriteByManyParams(b *testing.B) {
	InitRewriteConfig()
	experiments := []Experiment{
		{
			Handler: "PASSPORT",
			TestID:  182998,
			Context: UaasContext{
				Passport: UaasFlags{
					Flags: []string{"test"},
				},
			},
		},
	}
	request := map[string]string{
		"app_id":     "unit-tests",
		"am_version": "unit-tests",
	}
	config := []RewriteExperimentsExpression{
		{
			MatchKeyValue: map[string]string{
				"app_id":     "unit-tests",
				"am_version": "unit-tests",
			},
			FlagsToAdd: []string{"hello-unit-tests"},
		},
	}

	for n := 0; n < b.N; n++ {
		rewriteExperiments(experiments, config, request)
	}
}
