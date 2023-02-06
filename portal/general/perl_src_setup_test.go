package searchapp

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	basemodels "a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/requests"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
	"a.yandex-team.ru/portal/morda-go/tests/helpers"
	"a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func canonizeHeaderNames(req *protoanswers.THttpRequest) {
	if req == nil {
		return
	}
	for _, header := range req.Headers {
		header.Name = http.CanonicalHeaderKey(header.Name)
	}
}

func TestPrepareRequests(t *testing.T) {
	testCases := []struct {
		inputReq *protoanswers.THttpRequest
		expected preparedRequests
		caseName string
	}{
		{
			inputReq: helpers.NewTHttpRequest(
				helpers.WithMethod(protoanswers.THttpRequest_Get),
				helpers.WithPath("/portal/api/search/2?some_arg=42"),
				helpers.WithScheme(protoanswers.THttpRequest_Http),
			),
			expected: preparedRequests{
				legacy: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("/portal/api/search/2?some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
				),
				perlInit: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("?original_path_prefix=%252Fportal%252Fapi%252Fsearch%252F2&some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
				),
			},
			caseName: "Regular query to API 2",
		},
		{
			inputReq: helpers.NewTHttpRequest(
				helpers.WithMethod(protoanswers.THttpRequest_Get),
				helpers.WithPath("/portal/api/search/2/weather,topnews?some_arg=42"),
				helpers.WithScheme(protoanswers.THttpRequest_Http),
			),
			expected: preparedRequests{
				legacy: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("/portal/api/search/2/weather,topnews?some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
				),
				perlInit: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("?original_path_prefix=%252Fportal%252Fapi%252Fsearch%252F2%252Fweather%252Ctopnews&some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
				),
			},
			caseName: "Regular query to API 2 with blocks list",
		},
		{
			inputReq: helpers.NewTHttpRequest(
				helpers.WithMethod(protoanswers.THttpRequest_Get),
				helpers.WithPath("/portal/api/search/1?some_arg=42"),
				helpers.WithScheme(protoanswers.THttpRequest_Http),
			),
			expected: preparedRequests{
				legacy: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("/portal/api/search/1?some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
				),
				perlInit: nil,
			},
			caseName: "Regular query to API 1",
		},
		{
			inputReq: helpers.NewTHttpRequest(
				helpers.WithMethod(protoanswers.THttpRequest_Get),
				helpers.WithPath("/portal/api/search/1?some_arg=42"),
				helpers.WithScheme(protoanswers.THttpRequest_Http),
			),
			expected: preparedRequests{
				legacy: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("/portal/api/search/1?some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
				),
				perlInit: nil,
			},
			caseName: "Regular query to API 2 with test-id",
		},
		{
			inputReq: helpers.NewTHttpRequest(
				helpers.WithMethod(protoanswers.THttpRequest_Get),
				helpers.WithPath("/portal/api/search/2?some_arg=42"),
				helpers.WithScheme(protoanswers.THttpRequest_Http),
				helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
			),
			expected: preparedRequests{
				legacy: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("/portal/api/search/2?some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
					helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
				),
				perlInit: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("?original_path_prefix=%252Fportal%252Fapi%252Fsearch%252F2&some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
					helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
				),
			},
			caseName: "Regular query to API 2 with test-id and CGI arguments",
		},
		{
			inputReq: helpers.NewTHttpRequest(
				helpers.WithMethod(protoanswers.THttpRequest_Get),
				helpers.WithPath("/portal/api/search/2?some_arg=42"),
				helpers.WithScheme(protoanswers.THttpRequest_Http),
				helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
			),
			expected: preparedRequests{
				legacy: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("/portal/api/search/2?some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
					helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
				),
				perlInit: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("?original_path_prefix=%252Fportal%252Fapi%252Fsearch%252F2&some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
					helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
				),
			},
			caseName: "Regular query to API 2 with test-id without CGI arguments",
		},
		{
			inputReq: helpers.NewTHttpRequest(
				helpers.WithMethod(protoanswers.THttpRequest_Get),
				helpers.WithPath("/portal/api/search/1?some_arg=42"),
				helpers.WithScheme(protoanswers.THttpRequest_Http),
				helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
			),
			expected: preparedRequests{
				legacy: helpers.NewTHttpRequest(
					helpers.WithMethod(protoanswers.THttpRequest_Get),
					helpers.WithPath("/portal/api/search/1?some_arg=42"),
					helpers.WithScheme(protoanswers.THttpRequest_Http),
					helpers.WithHeader("X-Yandex-ExpFlags", "123456,0,1;888999,0,1"),
				),
				perlInit: nil,
			},
			caseName: "Regular query to API 1 with test-id",
		},
	}

	perlSrcSetup := NewPerlSrcSetup(&fastjson.ArenaPool{}, nil)

	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			apiInfo := requests.NewAPIInfoParser().Parse(testCase.inputReq.Path)

			actual, err := perlSrcSetup.preparePerlRequests(testCase.inputReq, apiInfo, log3.NewLoggerStub())
			require.NoError(t, err)
			require.NotNil(t, actual)

			canonizeHeaderNames(testCase.expected.legacy)
			canonizeHeaderNames(testCase.expected.perlInit)

			canonizeHeaderNames(actual.legacy)
			canonizeHeaderNames(actual.perlInit)

			helpers.THttpRequestAssertEqual(t, testCase.expected.legacy, actual.legacy)
			helpers.THttpRequestAssertEqual(t, testCase.expected.perlInit, actual.perlInit)
		})
	}
}

type stubOptionsGetter struct {
	iosPercentage     int
	androidPercentage int
}

func newStubOptionsGetter(ios, android int) *stubOptionsGetter {
	return &stubOptionsGetter{
		iosPercentage:     ios,
		androidPercentage: android,
	}
}
func (g *stubOptionsGetter) Get() its.Options {
	return its.Options{
		ForceTopnewsNativeCard: its.PercentageByPlatform{
			IOS:     g.iosPercentage,
			Android: g.androidPercentage,
		},
	}
}

func TestForceTopnewsNativeCard(t *testing.T) {
	testCases := []struct {
		platform          string
		iosPercentage     int
		androidPercentage int
		expected          bool
		caseName          string
	}{
		{
			platform:          "android",
			iosPercentage:     0,
			androidPercentage: 0,
			expected:          false,
			caseName:          "zero percentage, request from Android",
		},
		{
			platform:          "iphone",
			iosPercentage:     0,
			androidPercentage: 0,
			expected:          false,
			caseName:          "zero percentage, request from iOS",
		},
		{
			platform:          "android",
			iosPercentage:     100,
			androidPercentage: 0,
			expected:          false,
			caseName:          "iOS enabled, request from Android",
		},
		{
			platform:          "iphone",
			iosPercentage:     0,
			androidPercentage: 100,
			expected:          false,
			caseName:          "Android enabled, request from iOS",
		},
		{
			platform:          "iphone",
			iosPercentage:     100,
			androidPercentage: 0,
			expected:          true,
			caseName:          "iOS enabled, request from iOS",
		},
		{
			platform:          "android",
			iosPercentage:     0,
			androidPercentage: 100,
			expected:          true,
			caseName:          "Android enabled, request from Android",
		},
		{
			platform:          "iphone",
			iosPercentage:     100,
			androidPercentage: 100,
			expected:          true,
			caseName:          "iOS and Android enabled, request from iOS",
		},
		{
			platform:          "android",
			iosPercentage:     100,
			androidPercentage: 100,
			expected:          true,
			caseName:          "iOS and Android enabled, request from Android",
		},
	}

	for _, testCase := range testCases {
		getter := newStubOptionsGetter(testCase.iosPercentage, testCase.androidPercentage)
		appInfo := basemodels.AppInfo{Platform: testCase.platform}
		actual := forceTopnewsNativeCard(appInfo, getter)
		assert.Equal(t, testCase.expected, actual, testCase.caseName)
	}
}

func TestIsStraightSchemeEnabled(t *testing.T) {
	type testCase struct {
		caseName string
		its.Options
		appInfo basemodels.AppInfo
	}

	testCasesEnabled := []testCase{
		{
			caseName: "android_with_flag",
			Options:  its.Options{},
			appInfo: basemodels.AppInfo{
				ID:       "ru.yandex.searchplugin",
				Version:  "22000000",
				Platform: "android",
			},
		},
		{
			caseName: "iphone_with_flag",
			Options:  its.Options{},
			appInfo: basemodels.AppInfo{
				ID:       "ru.yandex.searchplugin",
				Version:  "78000000",
				Platform: "android",
			},
		},
	}

	testCasesDisabled := []testCase{
		{
			caseName: "old_android_with_flag",
			Options:  its.Options{},
			appInfo: basemodels.AppInfo{
				ID:       "ru.yandex.searchplugin",
				Version:  "19000000",
				Platform: "android",
			},
		},
		{
			caseName: "old_iphone_with_flag",
			Options:  its.Options{},
			appInfo: basemodels.AppInfo{
				ID:       "ru.yandex.iphone",
				Version:  "58000000",
				Platform: "iphone",
			},
		},
	}

	for _, subtest := range []struct {
		cases         []testCase
		expectedValue bool
		subtestName   string
	}{
		{
			cases:         testCasesEnabled,
			expectedValue: true,
			subtestName:   "enabled",
		},
		{
			cases:         testCasesDisabled,
			expectedValue: false,
			subtestName:   "disabled",
		},
	} {
		t.Run(subtest.subtestName, func(t *testing.T) {
			for _, testCase := range subtest.cases {
				t.Run(testCase.caseName, func(t *testing.T) {
					optionsMock := new(mocks.OptionsGetter)
					optionsMock.On("Get").Return(&testCase.Options)

					perlSrcSetupObj := NewPerlSrcSetup(nil, optionsMock)
					actual := perlSrcSetupObj.isStraightSchemeEnabled(testCase.appInfo)
					assert.Equal(t, subtest.expectedValue, actual)
				})
			}
		})
	}
}
