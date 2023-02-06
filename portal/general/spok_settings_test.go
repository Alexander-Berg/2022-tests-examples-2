package spoksettings

import (
	"encoding/json"
	"fmt"
	"reflect"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"

	"a.yandex-team.ru/portal/avocado/libs/utils/madm/v2"
)

type errorTemplated interface {
	GetTemplated() (string, map[string][]interface{})
}

func Test_SpokSettings_getSpokSettings(t *testing.T) {
	type staticDataAnswer struct {
		exportItems madm.Items
		madmError   error
	}

	tests := []struct {
		name             string
		staticDataAnswer staticDataAnswer
		expectedResult   map[string]spok
		expectError      bool
		expectTextError  string
	}{
		{
			name: "simple test",
			staticDataAnswer: staticDataAnswer{
				exportItems: madm.Items{
					createItemForSpok(t, spok{
						Domain:    "az",
						CountryID: 167,
						CityID:    10253,
					}),
					createItemForSpok(t, spok{
						Domain:    "kg",
						CountryID: 207,
						CityID:    10309,
					}),
					createItemForSpok(t, spok{
						Domain:    "co.il",
						CountryID: 181,
						CityID:    131,
					}),
				},
			},
			expectedResult: map[string]spok{
				"az": {
					Domain:    "az",
					CountryID: 167,
					CityID:    10253,
				},
				"kg": {
					Domain:    "kg",
					CountryID: 207,
					CityID:    10309,
				},
				"co.il": {
					Domain:    "co.il",
					CountryID: 181,
					CityID:    131,
				},
			},
			expectError: false,
		},
		{
			name: "without value",
			staticDataAnswer: staticDataAnswer{
				exportItems: madm.Items{
					createItemForSpok(t, spok{}),
				},
			},
			expectedResult: map[string]spok{},
			expectError:    false,
		},
		{
			name: "without domain",
			staticDataAnswer: staticDataAnswer{
				exportItems: madm.Items{
					createItemForSpok(t, spok{
						CountryID: 167,
						CityID:    10253,
					}),
				},
			},
			expectedResult: map[string]spok{},
			expectError:    false,
		},
		{
			name: "zero",
			staticDataAnswer: staticDataAnswer{
				exportItems: madm.Items{},
			},
			expectedResult: map[string]spok{},
			expectError:    false,
		},
		{
			name: "error read madm export",
			staticDataAnswer: staticDataAnswer{
				exportItems: madm.Items{},
				madmError:   assert.AnError,
			},
			expectedResult:  nil,
			expectError:     true,
			expectTextError: fmt.Sprintf("can not get spokSettings from MADM: %v", assert.AnError),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			dataGetterMock := NewMockdataGetter(gomock.NewController(t))
			dataGetterMock.EXPECT().StaticDataAll(madm.SpokSettings).Return(tt.staticDataAnswer.exportItems, tt.staticDataAnswer.madmError).Times(1)

			res, err := getSpokSettings(dataGetterMock)

			assert.True(t, reflect.DeepEqual(tt.expectedResult, res), fmt.Sprintf("expected: %v\nactual: %v", tt.expectedResult, res))
			if tt.expectError {
				require.Error(t, err)
				additionalErr, ok := err.(errorTemplated)
				require.True(t, ok)
				template, _ := additionalErr.GetTemplated()

				require.Equal(t, tt.expectTextError, template)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func Test_SpokSettings_IsSpokDomain(t *testing.T) {
	tests := []struct {
		name           string
		domain         string
		spokSettings   SpokSettings
		expectedResult bool
	}{
		{
			name:           "domain exists",
			domain:         "az",
			spokSettings:   SpokSettings{items: map[string]spok{"az": {}, "kg": {}}},
			expectedResult: true,
		},
		{
			name:           "domain does not exist",
			domain:         "ru",
			spokSettings:   SpokSettings{items: map[string]spok{"az": {}, "kg": {}}},
			expectedResult: false,
		},
		{
			name:           "domain is empty str",
			domain:         "",
			spokSettings:   SpokSettings{items: map[string]spok{"az": {}, "kg": {}}},
			expectedResult: false,
		},
		{
			name:           "spokSetting is empty str",
			domain:         "by",
			spokSettings:   SpokSettings{items: map[string]spok{}},
			expectedResult: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.expectedResult, tt.spokSettings.IsSpokDomain(tt.domain))
		})
	}
}

func Test_SpokSettings_GetSpokDomains(t *testing.T) {
	tests := []struct {
		name           string
		spokSettings   SpokSettings
		expectedResult []string
	}{
		{
			name:           "spokDomains is not empty",
			spokSettings:   SpokSettings{items: map[string]spok{"az": {}, "kg": {}}},
			expectedResult: []string{"az", "kg"},
		},
		{
			name:           "spokDomains is empty",
			spokSettings:   SpokSettings{items: map[string]spok{}},
			expectedResult: []string{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.ElementsMatch(t, tt.expectedResult, tt.spokSettings.GetSpokDomains())
		})
	}
}

func Test_SpokSettings_CityIDByDomain(t *testing.T) {
	tests := []struct {
		name         string
		domain       string
		spokSettings SpokSettings
		want         uint32
	}{
		{
			name:   "success case",
			domain: "kg",
			spokSettings: SpokSettings{
				items: map[string]spok{
					"az": {CityID: 10253, Domain: "az"},
					"kg": {CityID: 10309, Domain: "kg"},
				},
			},
			want: 10309,
		},
		{
			name:   "domain doesn't exist",
			domain: "ru",
			spokSettings: SpokSettings{
				items: map[string]spok{
					"az": {CityID: 10253, Domain: "az"},
					"kg": {CityID: 10309, Domain: "kg"},
				},
			},
			want: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, tt.spokSettings.CityIDByDomain(tt.domain))
		})
	}
}

func createItemForSpok(t *testing.T, s spok) madm.Item {
	spokMarshal := struct {
		Domain    string `json:"domain"`
		CountryID uint32 `json:"country_id,string"`
		CityID    uint32 `json:"capital_city_id,string"`
	}{
		Domain:    s.Domain,
		CountryID: s.CountryID,
		CityID:    s.CityID,
	}

	b, err := json.Marshal(&spokMarshal)
	require.NoError(t, err)
	return madm.NewItem(fastjson.MustParseBytes(b))
}
