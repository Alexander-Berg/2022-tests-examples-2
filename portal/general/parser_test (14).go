package locales

import (
	"net/http"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/cookies"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/langdetect"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/exports"
	mocks2 "a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func parserLookupMockInit(lookup *mocks2.Lookup, geo string, acceptLang string, domain string, langCookie int,
	returnLangInfoCode string, err error) {
	mordaLangs := newMordaLangs()
	mordaContent := models.MordaContent{}
	mordaLangsValues := mordaLangs.getMordaLangsStrings(mordaContent.Value)
	defaultLang := mordaLangs.getDefaultMordaLang(mordaContent.Value)

	lookup.On("Find",
		geo, acceptLang, domain, langCookie, mordaLangsValues, defaultLang,
	).Return(langdetect.LangInfo{Code: returnLangInfoCode}, err)
}

func parserGetDefaultMordaLang() string {
	mordaLangs := newMordaLangs()
	return mordaLangs.getDefaultMordaLang(defaultMordaContent)
}

func Test_parser_Parse(t *testing.T) {
	type testCase struct {
		name string

		originRequest    *models.OriginRequest
		originRequestErr error
		acceptLanguage   string
		geo              models.Geo
		cookie           models.Cookie
		languageCookie   int
		lookupMockInit   func(lookup *mocks2.Lookup)

		want        models.Locale
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name: "Ukrainian",
			originRequest: &models.OriginRequest{
				Headers: map[string][]string{
					"Host": {"yandex.ua"},
				},
			},
			acceptLanguage: "uk",
			geo: models.Geo{
				Parents: []uint32{1, 2, 3},
			},
			cookie: models.Cookie{My: models.MyCookie{Parsed: map[uint32][]int32{
				39: {0, 1},
			}}},
			lookupMockInit: func(lookup *mocks2.Lookup) {
				parserLookupMockInit(lookup, "1,2,3", "uk", "yandex.ua", 1, "uk", nil)
			},
			want:        models.Locale{Value: "uk"},
			wantErrFunc: assert.NoError,
		},
		{
			name: "default values",
			originRequest: &models.OriginRequest{
				Headers: map[string][]string{
					"Host": {""}, // todo: возвращать ошибку
				},
			},
			originRequestErr: errors.Error("origin request error"),
			acceptLanguage:   "",
			geo: models.Geo{
				Parents: make([]uint32, 0),
			},
			cookie: models.Cookie{},
			lookupMockInit: func(lookup *mocks2.Lookup) {
				parserLookupMockInit(lookup, "", "", defaultDomain, 0, "uk", nil)
			},
			want:        models.Locale{Value: "uk"},
			wantErrFunc: assert.Error,
		},
		{
			name: "find returns error",
			originRequest: &models.OriginRequest{
				Headers: map[string][]string{
					"Host": {"yandex.ua"},
				},
			},
			acceptLanguage: "uk",
			geo: models.Geo{
				Parents: []uint32{1, 2, 3},
			},
			cookie: models.Cookie{My: models.MyCookie{Parsed: map[uint32][]int32{
				39: {0, 1},
			}}},
			lookupMockInit: func(lookup *mocks2.Lookup) {
				parserLookupMockInit(lookup, "1,2,3", "uk", "yandex.ua", 1, "uk", errors.Error("error"))
			},
			want: models.Locale{
				Value: parserGetDefaultMordaLang(),
			},
			wantErrFunc: assert.Error,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			lookupMock := &mocks2.Lookup{}
			tt.lookupMockInit(lookupMock)

			tt.originRequest.Headers.Set("Accept-Language", tt.acceptLanguage)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.originRequest, tt.originRequestErr).AnyTimes()

			cookieKeeperMock := NewMockcookieGetter(ctrl)
			cookieKeeperMock.EXPECT().GetCookie().Return(tt.cookie)

			geoKeeperMock := NewMockgeoGetter(ctrl)
			geoKeeperMock.EXPECT().GetGeo().Return(tt.geo)

			appInfoGetter := NewMockappInfoGetter(ctrl)
			appInfoGetter.EXPECT().GetAppInfo().Return(models.AppInfo{}).AnyTimes()

			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()

			mordaContentGetter := NewMockmordaContentGetter(ctrl)
			mordaContentGetter.EXPECT().GetMordaContent().Return(models.MordaContent{}).AnyTimes()

			mordaZoneGetter := NewMockmordaZoneGetter(ctrl)
			mordaZoneGetter.EXPECT().GetMordaZone().Return(models.MordaZone{}).AnyTimes()

			madmOptions := exports.Options{}

			p := NewParser(appInfoGetter, cookieKeeperMock, geoKeeperMock, lookupMock, madmOptions, mordaContentGetter,
				mordaZoneGetter, originRequestKeeperMock, requestGetter)

			actual, err := p.Parse()
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_Parse_withRealData(t *testing.T) {
	type testCase struct {
		name     string
		request  *models.OriginRequest
		remoteIP string
		want     models.Locale
	}
	cases := []testCase{
		{
			name: "Ukrainian locale",
			request: &models.OriginRequest{
				Headers: map[string][]string{
					"Accept-Language":             {"en-GB,en-US;q=0.9,en;q=0.8,uk;q=0.7"},
					"Cookie":                      {"yandexuid=8992869691619719988; yuidss=8992869691619719988; i=R0nj1lJQN9yss0hK5WTbJY9pKzqiwiEv23rqLUYWkAvnJ2CUolu0T9yLaI8IDREAu4CYPGMfILNVi9rQd51SRkU39yU=; ymex=1935079988.yrts.1619719988#1935079988.yrtsi.1619719988; is_gdpr=0; is_gdpr_b=CIL8NhC7Pw=="},
					"x-laas-answered":             {"1"},
					"x-region-is-user-choice":     {"0"},
					"x-region-city-id":            {"213"},
					"x-region-id":                 {"225"},
					"x-region-location":           {"55.753215, 37.622504, 15000, 1628842366"},
					"x-region-suspected":          {"225"},
					"x-region-suspected-city":     {"213"},
					"x-region-suspected-location": {"55.753215, 37.622504, 15000, 1628842366"},
					"host":                        {"yandex.ru"},
				},
			},
			remoteIP: "8.21.110.28",
			want: models.Locale{
				Value: "uk",
			},
		},
		{
			name: "Belorussian locale",
			request: &models.OriginRequest{
				Headers: map[string][]string{
					"Accept-Language":             {"be-BY,be;q=0.5"},
					"Cookie":                      {"mda=0; ymex=1943102643.yrts.1627742643; font_loaded=YSv1; yandexuid=7416602971627450790; L=YiteaUh3TQ9ZYkJmZW5yVWVjZnlAbEJJDCwCP10oEydVAysFFyQKXwEZ.1627742820.14683.376038.b4f40e52263ebae1abb5b7c37b511187; i=Itf44Zqm3Fr\\/AgoW5HlZGRoQ5GHbzzdA5WsW92BPpirgkMZiEHdVHdelFtyEQOa5kUg109P7+22Fo6D50n7IFxJCbH0=; Session_id=3:1628612943.5.0.1627742783310:HvyjWQ:21.1|1459878119.37.2.2:37|3:239009.756385.MaJH-mI1x3ckCgcF0VTPV1DurjE; sessionid2=3:1628612943.5.0.1627742783310:HvyjWQ:21.1|1459878119.37.2.2:37|3:239009.756385.MaJH-mI1x3ckCgcF0VTPV1DurjE; yandex_login=morokovaanastasija; yabs-frequency=\\/5\\/0000000000000000\\/Wc51ROO00014GYC0\\/; _ym_isad=2; is_gdpr=0; is_gdpr_b=CIL8NhC0PygB; yandex_gid=114316; _ym_uid=16274681468717919; _ym_d=1628833483; yp=1660354834.ygu.1#1943102820.udn.cDrQkNC90LDRgdGC0LDRgdC40Y8g0JzQvtGA0L7QutC+0LLQsA%3D%3D#1643510789.szm.1:1440x900:1440x900#1631497415.csc.1#1943102820.multib.1#1660220734.old.1; my=YwA=; _yasc=BHh4k3Kv4GskzS6o1ZmrnwxHyyUGY7SInOMO\\/E\\/qcKXXG433EOo=; gdpr=0"},
					"x-laas-answered":             {"1"},
					"x-region-is-user-choice":     {"0"},
					"x-region-city-id":            {"114316"},
					"x-region-id":                 {"114316"},
					"x-region-location":           {"58.537990, 15.046008, 15000, 1628831520"},
					"x-region-suspected":          {"114316"},
					"x-region-suspected-city":     {"114316"},
					"x-region-suspected-location": {"58.537990, 15.046008, 15000, 1628831520"},
					"host":                        {"yandex.ru"},
				},
			},
			remoteIP: "89.163.249.244",
			want: models.Locale{
				Value: "be",
			},
		},
		{
			name: "Kazakh locale",
			request: &models.OriginRequest{
				Headers: map[string][]string{
					"Accept-Language":             {"ru-RU"},
					"Cookie":                      {"is_gdpr=0; yandexuid=305446891619590534; yuidss=305446891619590534; ymex=1934950534.yrts.1619590534#1934950534.yrtsi.1619590534; mda=0; is_gdpr_b=CO2OPxDDKygC; _ym_uid=1619655121724269220; font_loaded=YSv1; my=YycCAAQA; yandex_gid=2; gdpr=0; _ym_isad=2; i=p+O93a8ge+BcB9YzHJhxX+3yYqYGYfFMdrMtk8UDS\\/kOESBeVCaEyEEZJjmCuLXeKkebMbN0AYQlM5MgoDvpVpibPkI=; _ym_d=1628802645; _ym_visorc=b; _yasc=pqtzXu9l\\/NyETayrYlYVIqN+0+PiKPholUL5xbo4iTScOuOWszz\\/BBlT; ys=wprid.1628802679590438-16785547837039583828-vla1-4279-vla-l7-balancer-prod-8080-BAL-2547; yp=1635423128.szm.1_100000023841858%3A1920x1080%3A1745x820#1631481056.csc.1#1652306285.p_sw.1620770284#1652306288.p_cl.1620770288#1653376680.mco.1#1630397648.ygu.1#1659762390.stltp.serp_bk-map_1_1628226390#1628907523.zlgn_smrt.1#1628889043.nwcst.1628804400_2_1#1629407205.mcv.0#1629407205.mct.null#1628888806.ln_tp.01#1629407482.mcl.; yabs-frequency=\\/5\\/Im0008cE5M400000\\/3LKSS9800018Gc7A3dDmb00004X28O9XGMs60000I48Z1bQmS9K00018GY3hLB1mbG0004X28FrKi72L0000I48W\\/"},
					"x-laas-answered":             {"1"},
					"x-region-is-user-choice":     {"0"},
					"x-region-city-id":            {"2"},
					"x-region-id":                 {"2"},
					"x-region-location":           {"59.938951, 30.315635, 15000, 1628803029"},
					"x-region-suspected":          {"2"},
					"x-region-suspected-city":     {"2"},
					"x-region-suspected-location": {"59.938951, 30.315635, 15000, 1628803029"},
					"host":                        {"yandex.ru"},
				},
			},
			remoteIP: "83.220.227.223",
			want: models.Locale{
				Value: "kk",
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			tt.request.Headers.Set("X-Forwarded-For-Y", tt.remoteIP)
			ctrl := gomock.NewController(t)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.request, nil).AnyTimes()

			cookieKeeper := cookies.NewKeeper(nil, log3.NewLoggerStub(), originRequestKeeperMock)

			lookup, err := langdetect.NewLookup(langdetectDataPath)
			require.NoError(t, err)

			geoKeeper := NewMockgeoGetter(ctrl)
			geoKeeper.EXPECT().GetGeo().Return(models.Geo{}).AnyTimes()

			appInfoGetter := NewMockappInfoGetter(ctrl)
			appInfoGetter.EXPECT().GetAppInfo().Return(models.AppInfo{}).AnyTimes()

			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()

			mordaContentGetter := NewMockmordaContentGetter(ctrl)
			mordaContentGetter.EXPECT().GetMordaContent().Return(models.MordaContent{}).AnyTimes()

			mordaZoneGetter := NewMockmordaZoneGetter(ctrl)
			mordaZoneGetter.EXPECT().GetMordaZone().Return(models.MordaZone{}).AnyTimes()

			madmOptions := exports.Options{}

			parser := NewParser(appInfoGetter, cookieKeeper, geoKeeper, lookup, madmOptions, mordaContentGetter,
				mordaZoneGetter, originRequestKeeperMock, requestGetter)

			actual, err := parser.Parse()
			require.NoError(t, err)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_Parse_API(t *testing.T) {
	type testCase struct {
		name         string
		mordaContent models.MordaContent
		request      models.Request
		appInfo      models.AppInfo
		want         models.Locale
	}
	cases := []testCase{
		{
			name: "AppInfo.Lang=en",
			mordaContent: models.MordaContent{
				Value: "api_widget_2",
			},
			request: models.Request{
				APIInfo: models.APIInfo{
					Name: "search",
				},
			},
			appInfo: models.AppInfo{
				Lang: "en",
			},
			want: models.Locale{
				Value: "en",
			},
		},
		{
			name: "random AppInfo.Lang",
			request: models.Request{
				APIInfo: models.APIInfo{
					Name: "search",
				},
			},
			appInfo: models.AppInfo{
				Lang: "xx",
			},
			want: models.Locale{
				Value: "ru",
			},
		},
	}
	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(&models.OriginRequest{}, nil).AnyTimes()

			cookieKeeper := cookies.NewKeeper(nil, log3.NewLoggerStub(), originRequestKeeperMock)

			lookup, err := langdetect.NewLookup(langdetectDataPath)
			require.NoError(t, err)

			geoKeeper := NewMockgeoGetter(ctrl)
			geoKeeper.EXPECT().GetGeo().Return(models.Geo{}).AnyTimes()

			appInfoGetter := NewMockappInfoGetter(ctrl)
			appInfoGetter.EXPECT().GetAppInfo().Return(tt.appInfo).AnyTimes()

			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(tt.request).AnyTimes()

			mordaContentGetter := NewMockmordaContentGetter(ctrl)
			mordaContentGetter.EXPECT().GetMordaContent().Return(tt.mordaContent).AnyTimes()

			mordaZoneGetter := NewMockmordaZoneGetter(ctrl)
			mordaZoneGetter.EXPECT().GetMordaZone().Return(models.MordaZone{}).AnyTimes()

			madmOptions := exports.Options{}

			parser := NewParser(appInfoGetter, cookieKeeper, geoKeeper, lookup, madmOptions, mordaContentGetter,
				mordaZoneGetter, originRequestKeeperMock, requestGetter)

			actual, err := parser.Parse()
			require.NoError(t, err)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_getPossibleLocales(t *testing.T) {
	type testCase struct {
		name string

		madmOptions           exports.Options
		requestMockInitFunc   func(m *MockrequestGetter)
		appInfoMockInitFunc   func(m *MockappInfoGetter)
		mordaZoneMockInitFunc func(m *MockmordaZoneGetter)

		mordaContent models.MordaContent
		want         []string
		wantErrFunc  assert.ErrorAssertionFunc
	}
	cases := []testCase{
		{
			name: "mordaContent=intercept404 and mordaZone=ru",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{},
			want:         []string{},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "mordaContent=intercept404 and mordaZone=com",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "com"})
			},

			mordaContent: models.MordaContent{Value: "intercept404"},
			want:         []string{"en", "id"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "getPossibleAPIWidget2Locales ios_widget",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:    "widget",
						Version: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"ru", "be", "kk", "tt", "uk", "en", "it", "fr", "tr"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "getPossibleAPIWidget2Locales ios_widget",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:    "widget",
						Version: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			madmOptions: exports.Options{
				Locales: exports.LocalesOptions{
					EnableUZLocale: true,
				},
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"ru", "be", "kk", "tt", "uk", "en", "it", "fr", "tr"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "getPossibleAPIWidget2Locales ios_widget",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:    "widget",
						Version: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},
			madmOptions: exports.Options{
				Locales: exports.LocalesOptions{
					EnableUZLocale:           true,
					EnableUZLocaleAPIWidgets: true,
				},
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"ru", "be", "kk", "tt", "uk", "uz", "en", "tr", "it", "fr"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "getPossibleAPISearchConfigLocales",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name: "conf",
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "9000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want: []string{"ru", "be", "kk", "tt", "uk", "uz", "tr", "bg", "cs", "da", "de", "el", "en", "es",
				"fi", "fr", "hr", "hu", "it", "lt", "nl", "no", "pl", "pt", "ro", "sk", "sl", "sv"},
			wantErrFunc: assert.NoError,
		},
		{
			name: "getPossibleAPISearchLocales comtr",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "9000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "com.tr"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"tr"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "getPossibleAPISearchLocales IsSearchOnly api_search_2_euro",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:     "search",
						Version:  2,
						RealName: "search",
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "9000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want: []string{"ru", "be", "kk", "tt", "uk", "uz", "tr", "bg", "cs", "da", "de", "el", "en", "es",
				"fi", "fr", "hr", "hu", "it", "lt", "nl", "no", "pl", "pt", "ro", "sk", "sl", "sv"},
			wantErrFunc: assert.NoError,
		},
		{
			name: "getPossibleAPISearchLocales IsSearchOnly api_search_2_euro DisabledBroLangOfEurope",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:     "search",
						Version:  2,
						RealName: "search",
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "9000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},
			madmOptions: exports.Options{
				Locales: exports.LocalesOptions{
					DisabledPPLangOfEurope: true,
				},
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"ru", "be", "kk", "tt", "uk"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "getPossibleAPISearchLocales IsYabrowser2 IsAndroid api_search_2_euro",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:        "search",
						Version:     2,
						RealName:    "yabrowser",
						RealVersion: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "1906574192",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want: []string{"ru", "be", "kk", "tt", "uk", "uz", "tr", "bg", "cs", "da", "de", "el", "en", "es",
				"fi", "fr", "hr", "hu", "it", "lt", "nl", "no", "pl", "pt", "ro", "sk", "sl", "sv"},
			wantErrFunc: assert.NoError,
		},
		{
			name: "getPossibleAPISearchLocales IsYabrowser2 IsIOS api_search_2_euro",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:        "search",
						Version:     2,
						RealName:    "yabrowser",
						RealVersion: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "1912010000",
					Platform:  "iphone",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want: []string{"ru", "be", "kk", "tt", "uk", "uz", "tr", "bg", "cs", "da", "de", "el", "en", "es",
				"fi", "fr", "hr", "hu", "it", "lt", "nl", "no", "pl", "pt", "ro", "sk", "sl", "sv"},
			wantErrFunc: assert.NoError,
		},
		{
			name: "getPossibleAPISearchLocales EnableUZLocale && EnableUZLocaleSearchapp",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "9000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},
			madmOptions: exports.Options{
				Locales: exports.LocalesOptions{
					EnableUZLocale:          true,
					EnableUZLocaleSearchapp: true,
				},
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"ru", "be", "kk", "tt", "uk", "uz", "tr"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "getPossibleAPISearchLocales EnableUZLocale && !EnableUZLocaleSearchapp",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						Name:    "search",
						Version: 2,
					},
				}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "9000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},
			madmOptions: exports.Options{
				Locales: exports.LocalesOptions{
					EnableUZLocale:          true,
					EnableUZLocaleSearchapp: false,
				},
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"ru", "be", "kk", "tt", "uk"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "uz",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "uz"})
			},
			madmOptions: exports.Options{
				Locales: exports.LocalesOptions{
					EnableUZLocale: true,
				},
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"uz", "ru"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "comtr",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "com.tr"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"tr"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "spok",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "eu"})
			},

			mordaContent: models.MordaContent{Value: "spok"},
			want:         []string{},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "len(mordaLangs) == 0",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{},
			want:         []string{},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "MordaContent = big",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "big"},
			want:         []string{"ru", "be", "kk", "tt", "uk"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "MordaContent = touch",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "touch"},
			want:         []string{"ru", "be", "kk", "tt", "uk"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "MordaContent = yaru",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "yaru"},
			want:         []string{"ru"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "MordaContent = yabrotab",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "yabrotab"},
			want:         []string{"ru", "be", "kk", "tt", "uk"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "MordaContent = com",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "com"},
			want:         []string{"en", "id"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "MordaContent = tv",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "tv"},
			want:         []string{"ru"},
			wantErrFunc:  assert.NoError,
		},
		{
			name: "MordaContent = tel",

			requestMockInitFunc: func(m *MockrequestGetter) {
				m.EXPECT().GetRequest().Return(models.Request{APIInfo: models.APIInfo{}}).Times(1)
			},
			appInfoMockInitFunc: func(m *MockappInfoGetter) {
				m.EXPECT().GetAppInfo().Return(models.AppInfo{}).Times(1)
			},
			mordaZoneMockInitFunc: func(m *MockmordaZoneGetter) {
				m.EXPECT().GetMordaZone().Return(models.MordaZone{Value: "ru"})
			},

			mordaContent: models.MordaContent{Value: "tel"},
			want:         []string{"ru"},
			wantErrFunc:  assert.NoError,
		},
	}

	mordaLangs := newMordaLangs()
	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestMock := NewMockrequestGetter(ctrl)
			tt.requestMockInitFunc(requestMock)
			appInfoMock := NewMockappInfoGetter(ctrl)
			tt.appInfoMockInitFunc(appInfoMock)
			mordaZoneMock := NewMockmordaZoneGetter(ctrl)
			tt.mordaZoneMockInitFunc(mordaZoneMock)

			p := &parser{
				appInfoGetter:   appInfoMock,
				mordaZoneGetter: mordaZoneMock,
				madmOptions:     tt.madmOptions,
				requestGetter:   requestMock,
			}
			actual, err := p.getPossibleLocales(tt.mordaContent, mordaLangs)
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_getHostname(t *testing.T) {
	type testCase struct {
		name                      string
		originRequestMockInitFunc func(m *MockoriginRequestKeeper)
		want                      string
		wantErrFunc               assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name: "origin request fails",
			originRequestMockInitFunc: func(m *MockoriginRequestKeeper) {
				m.EXPECT().GetOriginRequest().Return(nil, errors.Error("error")).Times(1)
			},
			want:        defaultDomain,
			wantErrFunc: assert.Error,
		},
		{
			name: "origin request returns host",
			originRequestMockInitFunc: func(m *MockoriginRequestKeeper) {
				m.EXPECT().GetOriginRequest().Return(&models.OriginRequest{
					Headers: map[string][]string{
						"Host": {"yandex.lv"},
					},
				}, nil).Times(1)
			},
			want:        "yandex.lv",
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			originRequestMock := NewMockoriginRequestKeeper(ctrl)
			tt.originRequestMockInitFunc(originRequestMock)

			p := &parser{originRequestKeeper: originRequestMock}

			actual, err := p.getDomain()
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_getLangCookie(t *testing.T) {
	type testCase struct {
		name    string
		cookies models.Cookie
		want    int
	}
	cases := []testCase{
		{
			name: "single value in slot",
			cookies: models.Cookie{
				My: models.MyCookie{
					Parsed: map[uint32][]int32{
						39: {77},
					},
				},
			},
			want: 0,
		},
		{
			name: "regular case",
			cookies: models.Cookie{
				My: models.MyCookie{
					Parsed: map[uint32][]int32{
						39: {33, 77},
					},
				},
			},
			want: 77,
		},
		{
			name: "no language slot in my cookie",
			cookies: models.Cookie{
				My: models.MyCookie{
					Parsed: map[uint32][]int32{
						44: {1},
					},
				},
			},
			want: 0,
		},
		{
			name: "no parsed my cookie",
			cookies: models.Cookie{
				My: models.MyCookie{
					Parsed: nil,
				},
			},
			want: 0,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			cookieGetterMock := NewMockcookieGetter(ctrl)
			cookieGetterMock.EXPECT().GetCookie().Return(tt.cookies)

			p := &parser{
				cookieGetter: cookieGetterMock,
			}
			actual := p.getLangCookie()
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_getGeoAsString(t *testing.T) {
	type testCase struct {
		name string
		geo  models.Geo
		want string
	}
	cases := []testCase{
		{
			name: "nil parents",
			geo: models.Geo{
				Parents: nil,
			},
			want: "",
		},
		{
			name: "empty parents",
			geo: models.Geo{
				Parents: make([]uint32, 0),
			},
			want: "",
		},
		{
			name: "single parent",
			geo: models.Geo{
				Parents: []uint32{20544},
			},
			want: "20544",
		},
		{
			name: "several parents",
			geo: models.Geo{
				Parents: []uint32{20544, 187},
			},
			want: "20544,187",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			geoGetterMock := NewMockgeoGetter(ctrl)
			geoGetterMock.EXPECT().GetGeo().Return(tt.geo)

			p := &parser{
				geoGetter: geoGetterMock,
			}

			got := p.getGeoAsString()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_getAcceptLanguage(t *testing.T) {
	type testCase struct {
		name             string
		originRequest    *models.OriginRequest
		originRequestErr bool
		want             string
		wantErr          bool
	}
	acceptLanguageKey := http.CanonicalHeaderKey("Accept-Language")

	cases := []testCase{
		{
			name:             "error by getting origin request",
			originRequest:    nil,
			originRequestErr: true,
			want:             "",
			wantErr:          true,
		},
		{
			name: "no Accept-language Header",
			originRequest: &models.OriginRequest{
				Headers: nil,
			},
			originRequestErr: false,
			want:             "",
			wantErr:          false,
		},
		{
			name: "empty Accept-language Header",
			originRequest: &models.OriginRequest{
				Headers: http.Header{
					acceptLanguageKey: make([]string, 0),
				},
			},
			originRequestErr: false,
			want:             "",
			wantErr:          false,
		},
		{
			name: "regular Accept-language Header",
			originRequest: &models.OriginRequest{
				Headers: http.Header{
					acceptLanguageKey: []string{"uk-UA"},
				},
			},
			originRequestErr: false,
			want:             "uk-UA",
			wantErr:          false,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			if tt.originRequestErr {
				originRequestKeeperMock.EXPECT().GetOriginRequest().Return(nil, errors.Error("some error"))
			} else {
				originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.originRequest, nil)
			}
			p := &parser{
				originRequestKeeper: originRequestKeeperMock,
			}
			actual, err := p.getAcceptLanguage()
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.want, actual)
			}
		})
	}
}
