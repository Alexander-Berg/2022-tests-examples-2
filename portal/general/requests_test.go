package topnews

import (
	"testing"

	"github.com/golang/protobuf/proto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"

	"a.yandex-team.ru/portal/avocado/libs/products/perlinit"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
	"a.yandex-team.ru/portal/avocado/proto/topnews"
)

func TestNewTopnewsRequestProtoSearchapp(t *testing.T) {
	testCases := []struct {
		name                    string
		perlInitJSONResponse    []byte
		abflags                 models.ABFlags
		expectedProto           *topnews.TRequest
		options                 exports.Options
		isStraightSchemeEnabled bool
	}{
		{
			name: "all fields",
			perlInitJSONResponse: []byte(`{
				"topnews" : {
                    "is_tourist_tab" : 1,
                    "is_disclaimer" : 1,
					"ordered_rubrics": [
						"politics",
						"society",
						"business",
						"world",
						"sport",
						"incident",
						"culture",
						"computers",
						"science",
						"auto",
						"index"
					],
					"url" : "https://data.news.yandex.ru/api/v3/tops_export?client=morda"
				},
				"scale_factor" : 1,
				"locale" : "ru",
				"experiments" : "exp1,exp2",
				"flags" : "flag1,flag2",
				"home_region" : 10758,
				"is_palette": 1
			}`),
			abflags: models.ABFlags{
				Flags: map[string]string{
					"geohelper_extra_stories":       "1",
					"news_degradation":              "1",
					"topnews_extended_from_avocado": "1",
					"topnews_extended":              "1",
					"oficcomment_open":              "1",
				},
			},
			expectedProto: &topnews.TRequest{
				Common: &topnews.TCommon{
					Locale: "ru",
					OrderedRubrics: []string{
						"politics",
						"society",
						"business",
						"world",
						"sport",
						"incident",
						"culture",
						"computers",
						"science",
						"auto",
						"index",
					},
					ScaleFactor:                   1.0,
					Url:                           "https://data.news.yandex.ru/api/v3/tops_export?client=morda",
					HomeRegion:                    10758,
					IsDegradation:                 true,
					IsTouristTab:                  true,
					IsTopnewsUnifiedCard:          true,
					IsExtraStories:                true,
					IsDisclaimer:                  true,
					IsTopnewsOfficialCommentsLink: true,
					IsOfficialCommentOpen:         true,
				},
				Data: &topnews.TRequest_SearchApp{
					SearchApp: &topnews.TSearchAppData{
						Experiments: "exp1,exp2",
						Flags:       "flag1,flag2",
						IsPalette:   true,
					},
				},
			},
			options:                 exports.Options{},
			isStraightSchemeEnabled: true,
		},
		{
			name: "some missing fields",
			perlInitJSONResponse: []byte(`{
				"topnews" : {
					"url" : "https://data.news.yandex.ru/api/v3/tops_export?client=morda"
				},
				"scale_factor" : 1
			}`),
			abflags: models.ABFlags{},
			expectedProto: &topnews.TRequest{
				Common: &topnews.TCommon{
					Locale:         "",
					OrderedRubrics: []string{},
					ScaleFactor:    1.0,
					Url:            "https://data.news.yandex.ru/api/v3/tops_export?client=morda",
					IsDegradation:  false,
				},
				Data: &topnews.TRequest_SearchApp{SearchApp: &topnews.TSearchAppData{}},
			},
			options:                 exports.Options{},
			isStraightSchemeEnabled: false,
		},
		{
			name: "extended, hiding hot stories",
			perlInitJSONResponse: []byte(`{
				"topnews" : {
					"url" : "https://data.news.yandex.ru/api/v3/tops_export?client=morda"
				},
				"scale_factor" : 1.5
			}`),
			abflags: models.ABFlags{
				Flags: map[string]string{
					"topnews_extended_from_avocado": "1",
					"topnews_extended":              "1",
				},
			},
			expectedProto: &topnews.TRequest{
				Common: &topnews.TCommon{
					OrderedRubrics:                []string{},
					ScaleFactor:                   1.5,
					Url:                           "https://data.news.yandex.ru/api/v3/tops_export?client=morda",
					IsTopnewsUnifiedCard:          true,
					IsTopnewsOfficialCommentsLink: true,
				},
				Data: &topnews.TRequest_SearchApp{
					SearchApp: &topnews.TSearchAppData{
						IsHotStoriesDisabled: true,
					},
				},
			},
			options: exports.Options{
				Topnews: exports.TopnewsOptions{
					DisableTopnewsExtendedHotStories: true,
				},
			},
			isStraightSchemeEnabled: true,
		},
		{
			name: "with ab flag topnews_official_comments_link set",
			perlInitJSONResponse: []byte(`{
				"topnews" : {
					"url" : "https://data.news.yandex.ru/api/v3/tops_export?client=morda"
				},
				"scale_factor" : 1.5
			}`),
			abflags: models.ABFlags{},
			expectedProto: &topnews.TRequest{
				Common: &topnews.TCommon{
					ScaleFactor:                   1.5,
					Url:                           "https://data.news.yandex.ru/api/v3/tops_export?client=morda",
					IsTopnewsOfficialCommentsLink: true,
				},
				Data: &topnews.TRequest_SearchApp{
					SearchApp: &topnews.TSearchAppData{},
				},
			},
			options:                 exports.Options{},
			isStraightSchemeEnabled: true,
		},
		{
			name: "with disable_news_disclaimer_api flag set",
			perlInitJSONResponse: []byte(`{
				"topnews" : {
					"url" : "https://data.news.yandex.ru/api/v3/tops_export?client=morda",
                    "is_disclaimer" : 1
				},
				"scale_factor" : 1.5
			}`),
			abflags: models.ABFlags{},
			expectedProto: &topnews.TRequest{
				Common: &topnews.TCommon{
					ScaleFactor:                   1.5,
					Url:                           "https://data.news.yandex.ru/api/v3/tops_export?client=morda",
					IsDisclaimer:                  true,
					IsTopnewsOfficialCommentsLink: true,
				},
				Data: &topnews.TRequest_SearchApp{SearchApp: &topnews.TSearchAppData{}},
			},
			options:                 exports.Options{},
			isStraightSchemeEnabled: true,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			baseCtx := &mocks.Base{}
			baseCtx.On("GetMadmOptions").Return(testCase.options).Once()
			baseCtx.On("GetFlags").Return(testCase.abflags)
			perlInitData, err := fastjson.ParseBytes(testCase.perlInitJSONResponse)
			require.NoError(t, err)

			actualProto := NewTopnewsRequestProtoSearchapp(baseCtx, &perlinit.PerlInitResponseWrapper{JSON: perlInitData}, testCase.isStraightSchemeEnabled)
			assert.True(t, proto.Equal(testCase.expectedProto, actualProto), "check TTopnewsRequests for equality. Test: "+testCase.name)
		})
	}
}

func TestNewTopnewsSpecialProto(t *testing.T) {
	testCases := []struct {
		name            string
		specialJSON     []byte
		expectedSpecial *topnews.TSpecial
	}{
		{
			name: "all fields",
			specialJSON: []byte(`{
				"alias" : "some alias",
				"name" : "some name",
				"counter" : "covid19",
				"href" : "url",
				"title" : "title",
				"window" : "1"
			}`),
			expectedSpecial: &topnews.TSpecial{
				Name:    "some name",
				Alias:   "some alias",
				Counter: "covid19",
				Href:    "url",
				Title:   "title",
				Window:  "1",
			},
		},
		{
			name: "some missing fields",
			specialJSON: []byte(`{
				"alias" : "some alias",
				"counter" : "covid19",
				"window" : "1"
			}`),
			expectedSpecial: &topnews.TSpecial{
				Alias:   "some alias",
				Counter: "covid19",
				Window:  "1",
			},
		},
		{
			name:            "empty",
			specialJSON:     []byte(`{}`),
			expectedSpecial: &topnews.TSpecial{},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			specialJSON, err := fastjson.ParseBytes(testCase.specialJSON)
			assert.NoError(t, err, "failed to parse special JSON")
			specialWrapper := &perlinit.PerlInitResponseWrapper{JSON: specialJSON}

			special := NewTopnewsSpecialProto(specialWrapper)
			assert.True(t, proto.Equal(testCase.expectedSpecial, special), "Check TTopnewsSpecial for equality, test: "+testCase.name)
		})
	}
}

func TestNewTopnewsSettingsProto(t *testing.T) {
	testCases := []struct {
		name             string
		settingsJSON     []byte
		expectedSettings *topnews.TSettings
	}{
		{
			name: "all fields",
			settingsJSON: []byte(`{
				"globtop" : "213",
				"reg_tab" : "1",
				"world_tab" : "1",
				"theme_tabs" : "tab1,tab2",
				"tab_default" : "tab",
				"disabled_globtop" : "1",
				"save_tab" : "tab"
			}`),
			expectedSettings: &topnews.TSettings{
				Globtop:         213,
				RegTab:          true,
				WorldTab:        true,
				ThemeTabs:       []string{"tab1", "tab2"},
				WorldTabOld:     "1",
				ThemeTabsOld:    "tab1,tab2",
				TabDefault:      "tab",
				DisabledGlobtop: true,
				SaveTab:         "tab",
			},
		},
		{
			name: "some missing fields",
			settingsJSON: []byte(`{
				"reg_tab" : "1",
				"world_tab" : "1",
				"disabled_globtop" : "1",
				"save_tab" : "tab"
			}`),
			expectedSettings: &topnews.TSettings{
				RegTab:          true,
				WorldTabOld:     "1",
				WorldTab:        true,
				DisabledGlobtop: true,
				SaveTab:         "tab",
			},
		},
		{
			name:             "empty",
			settingsJSON:     []byte(`{}`),
			expectedSettings: &topnews.TSettings{},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			settingsJSON, err := fastjson.ParseBytes(testCase.settingsJSON)
			assert.NoError(t, err, "failed to parse settings JSON")
			settingsWrapper := &perlinit.PerlInitResponseWrapper{JSON: settingsJSON}

			settings := NewTopnewsSettingsProto(settingsWrapper)
			assert.True(t, proto.Equal(testCase.expectedSettings, settings), "Check TTopnewsSettings for equality, test: "+testCase.name)
		})
	}
}

func TestNewTopnewsRequestProtoWeb(t *testing.T) {
	testCases := []struct {
		name                 string
		perlInitJSONResponse []byte
		abflags              models.ABFlags
		expectedRequest      *topnews.TRequest
	}{
		{
			name: "all fields",
			perlInitJSONResponse: []byte(`{
   				"local_day" : 31,
   				"local_hour" : 12,
   				"local_min" : 41,
   				"local_mon" : 1,
   				"local_wday" : 1,
   				"local_year" : 2022,
   				"locale" : "ru",
   				"morda_zone" : "ru",
   				"scale_factor" : 1.5,
				"home_region" : 10758,
   				"topnews" : {
                   "jsmda_url" : "url",
   				   "data_url" : "http://data.news.yandex.ru/api/v3/",
   				   "is_disclaimer" : 1,
   				   "is_tourist_tab" : 1,
   				   "ordered_rubrics" : [
   				      "politics",
   				      "society"
   				   ],
   				   "personal_url" : "https://news.yandex.ru/api/v2/",
   				   "settings" : {
   				      "content" : "all",
   				      "domain" : "all",
   				      "geo" : "225",
   				      "globtop" : "225",
   				      "reg_tab" : "1"
   				   },
   				   "special" : {
						"alias" : "some alias",
						"counter" : "covid19"
					},
   				   "url" : "http://data.news.yandex.ru/api/v3/"
   				}
			}`),
			abflags: models.ABFlags{
				Flags: map[string]string{
					"topnews_extra":                 "1",
					"news_degradation":              "1",
					"topnews_extended_from_avocado": "1",
					"topnews_extended":              "1",
					"oficcomment_open":              "1",
				},
			},
			expectedRequest: &topnews.TRequest{
				Common: &topnews.TCommon{
					Locale:                "ru",
					IsDisclaimer:          true,
					ScaleFactor:           1.5,
					HomeRegion:            10758,
					IsDegradation:         true,
					IsTopnewsUnifiedCard:  true,
					IsExtraStories:        true,
					OrderedRubrics:        []string{"politics", "society"},
					PersonalUrl:           "https://news.yandex.ru/api/v2/",
					Url:                   "http://data.news.yandex.ru/api/v3/",
					IsTouristTab:          true,
					IsOfficialCommentOpen: true,
					Settings: &topnews.TSettings{
						Globtop: 225,
						RegTab:  true,
					},
					SpecialTab: &topnews.TSpecial{
						Alias:   "some alias",
						Counter: "covid19",
					},
					MordaZone:                     "ru",
					IsTopnewsOfficialCommentsLink: true,
				},
				Data: &topnews.TRequest_Web{
					Web: &topnews.TWebData{
						LocalDay:  31,
						LocalMon:  1,
						LocalWday: 1,
						LocalHour: 12,
						LocalMin:  41,
						LocalYear: 2022,
						JsmdaUrl:  "url",
						DataUrl:   "http://data.news.yandex.ru/api/v3/",
					},
				},
			},
		},
		{
			name: "some missing fields",
			perlInitJSONResponse: []byte(`{
   				"topnews" : {
   				   "data_url" : "http://data.news.yandex.ru/api/v3/",
   				   "is_disclaimer" : 1,
   				   "is_tourist_tab" : 1,
   				   "ordered_rubrics" : [
   				      "politics",
   				      "society"
   				   ],
   				   "personal_url" : "https://news.yandex.ru/api/v2/",
   				   "url" : "http://data.news.yandex.ru/api/v3/"
   				}
			}`),
			abflags: models.ABFlags{},
			expectedRequest: &topnews.TRequest{
				Common: &topnews.TCommon{
					OrderedRubrics:                []string{"politics", "society"},
					PersonalUrl:                   "https://news.yandex.ru/api/v2/",
					Url:                           "http://data.news.yandex.ru/api/v3/",
					IsDisclaimer:                  true,
					IsTouristTab:                  true,
					IsTopnewsOfficialCommentsLink: true,
				},
				Data: &topnews.TRequest_Web{
					Web: &topnews.TWebData{
						DataUrl: "http://data.news.yandex.ru/api/v3/",
					},
				},
			},
		},
		{
			name:                 "empty",
			perlInitJSONResponse: []byte(`{}`),
			abflags:              models.ABFlags{},
			expectedRequest: &topnews.TRequest{
				Common: &topnews.TCommon{
					IsTopnewsOfficialCommentsLink: true,
				},
				Data: &topnews.TRequest_Web{Web: &topnews.TWebData{}},
			},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			baseCtx := &mocks.Base{}
			baseCtx.On("GetFlags").Return(testCase.abflags)

			perlInitData, err := fastjson.ParseBytes(testCase.perlInitJSONResponse)
			assert.NoError(t, err, "failed to parse perl init response")
			perlInitWrapper := &perlinit.PerlInitResponseWrapper{JSON: perlInitData}

			request := NewTopnewsRequestProtoWeb(baseCtx, perlInitWrapper)
			assert.True(t, proto.Equal(testCase.expectedRequest, request), "Check TTopnewsRequestWeb for equality, test: "+testCase.name)
		})
	}
}
