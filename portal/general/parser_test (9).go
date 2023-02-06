package domains

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/country"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_parser_parseHostname(t *testing.T) {
	testCases := []struct {
		name           string
		hostname       string
		expectedResult models.Domain
		expectError    bool
	}{
		{
			name:     "localhost",
			hostname: "localhost",
			expectedResult: models.Domain{
				Zone:   "ru",
				Domain: "yandex.ru",
			},
			expectError: false,
		},
		{
			name:     "short hostname (incorrect)",
			hostname: "notlocalhost",
			expectedResult: models.Domain{
				Zone:   "ru",
				Domain: "yandex.ru",
			},
			expectError: true,
		},
		{
			name:     "ya.ru",
			hostname: "ya.ru",
			expectedResult: models.Domain{
				Zone:   "ru",
				Domain: "ya.ru",
			},
			expectError: false,
		},
		{
			name:     "www.ya.ru",
			hostname: "www.ya.ru",
			expectedResult: models.Domain{
				Zone:      "ru",
				Domain:    "ya.ru",
				Subdomain: "www",
				Prefix:    "www",
			},
			expectError: false,
		},
		{
			name:     "with subzone",
			hostname: "www.yandex.com.tr",
			expectedResult: models.Domain{
				Zone:      "com.tr",
				Domain:    "yandex.com.tr",
				Subdomain: "www",
				Prefix:    "www",
			},
			expectError: false,
		},
		{
			name:     "dev instance",
			hostname: "v194d0.wdevx.yandex.ru",
			expectedResult: models.Domain{
				Zone:      "ru",
				Domain:    "yandex.ru",
				Subdomain: "v194d0.wdevx",
				Prefix:    "v194d0",
				WDevX:     "wdevx",
			},
			expectError: false,
		},
		{
			name:     "dev instance with subzone",
			hostname: "v194d0.wdevx.yandex.com.tr",
			expectedResult: models.Domain{
				Zone:      "com.tr",
				Domain:    "yandex.com.tr",
				Subdomain: "v194d0.wdevx",
				Prefix:    "v194d0",
				WDevX:     "wdevx",
			},
			expectError: false,
		},
		{
			name:     "beta instance with subzone",
			hostname: "morda-go-pr-2718706.hometest.yandex.ru",
			expectedResult: models.Domain{
				Zone:      "ru",
				Domain:    "yandex.ru",
				Subdomain: "morda-go-pr-2718706.hometest",
				Prefix:    "morda-go-pr-2718706",
				WDevX:     "hometest",
			},
			expectError: false,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			p := &parser{}
			result, err := p.parseHostname(testCase.hostname)
			if testCase.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
			assert.Equal(t, testCase.expectedResult, result)
		})
	}
}

func Test_parser_makeHostname(t *testing.T) {
	testCases := []struct {
		name           string
		host           string
		expectedResult string
	}{
		{
			name:           "default",
			host:           "www.yandex.ru",
			expectedResult: "www.yandex.ru",
		},
		{
			name:           "with port",
			host:           "localhost:8080",
			expectedResult: "localhost",
		},
		{
			name:           "with trailing dot",
			host:           "www.yandex.ru.",
			expectedResult: "www.yandex.ru",
		},
		{
			name:           "with trailing dot and port",
			host:           "www.yandex.ru.:8080",
			expectedResult: "www.yandex.ru",
		},
		{
			name:           "with trailing dot and port and some upper case",
			host:           "www.yandex.Ru.:8080",
			expectedResult: "www.yandex.ru",
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			p := &parser{}
			result := p.makeHostname(testCase.host)
			assert.Equal(t, testCase.expectedResult, result)
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	testCases := []struct {
		name           string
		host           string
		country        country.Country
		expectedResult models.Domain
	}{
		{
			name:    "usual",
			host:    "yandex.ru",
			country: country.RU,
			expectedResult: models.Domain{
				Zone:   "ru",
				Domain: "yandex.ru",
			},
		},
		{
			name:    "TR override",
			host:    "yandex.ru",
			country: country.TR,
			expectedResult: models.Domain{
				Zone:   "com.tr",
				Domain: "yandex.com.tr",
			},
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			requestGetter := NewMockrequestGetter(ctl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{
				Host: testCase.host,
			})
			appInfoGetter := NewMockappInfoGetter(ctl)
			appInfoGetter.EXPECT().GetAppInfo().Return(models.AppInfo{
				Country: testCase.country,
			})

			parser := NewParser(log3.NewLoggerStub(), requestGetter, appInfoGetter)

			result, err := parser.Parse()
			require.NoError(t, err)
			assert.Equal(t, result, testCase.expectedResult)
		})
	}
}
