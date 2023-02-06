package searchapp

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func TestIsStraightSchemeSupported(t *testing.T) {
	testCases := []struct {
		appInfo models.AppInfo

		expected bool
		caseName string
	}{
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.searchplugin",
				Version:  "28000000",
				Platform: "android",
			},

			expected: true,
			caseName: "fresh Android SearchApp",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.searchplugin.beta",
				Version:  "28000000",
				Platform: "android",
			},

			expected: true,
			caseName: "fresh Android SearchApp beta",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.searchplugin",
				Version:  "21050000",
				Platform: "android",
			},

			expected: true,
			caseName: "min supported Android SearchApp",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.searchplugin",
				Version:  "21000000",
				Platform: "android",
			},

			expected: false,
			caseName: "old Android SearchApp",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.searchplugin.beta",
				Version:  "21000000",
				Platform: "android",
			},

			expected: true,
			caseName: "old supported Android SearchApp Beta",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.mobile",
				Version:  "58000000",
				Platform: "iphone",
			},

			expected: false,
			caseName: "old iOS SearchApp in production",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.mobile",
				Version:  "63000000",
				Platform: "iphone",
			},

			expected: true,
			caseName: "min supported iOS SearchApp in production",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.mobile",
				Version:  "99000000",
				Platform: "iphone",
			},

			expected: true,
			caseName: "fresh iOS SearchApp in production",
		},
		{
			appInfo: models.AppInfo{
				ID:       "ru.yandex.mobile.beta",
				Version:  "58000000",
				Platform: "iphone",
			},

			expected: false,
			caseName: "old iOS SearchApp beta",
		},
	}

	mockCtrl := gomock.NewController(t)
	defer mockCtrl.Finish()

	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {

			actual := isStraightSchemeSupported(testCase.appInfo)
			if testCase.expected {
				assert.True(t, actual)
			} else {
				assert.False(t, actual)
			}
		})
	}
}
