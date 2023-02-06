package yabs

import (
	"net/http"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/library/go/yandex/uatraits"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
)

func createHTTPHeaderFromMap(headers map[string][]string) http.Header {
	h := make(http.Header)
	for k, values := range headers {
		for _, v := range values {
			h.Add(k, v)
		}
	}
	return h
}

func createHTTPHeaderFromProtoanswers(headers []*protoanswers.THeader) http.Header {
	h := make(http.Header)
	for _, header := range headers {
		h.Add(header.GetName(), header.GetValue())
	}
	return h
}

func TestRequestBuilder_buildFullPath(t *testing.T) {
	tests := []struct {
		name string
		arg  Request
		want string
	}{
		{
			name: "no CGI arg",
			arg: Request{
				Host:    "yabs.yandex.ru",
				Path:    "/page/123456",
				CGIArgs: nil,
			},
			want: "/page/123456",
		},
		{
			name: "with CGI arg",
			arg: Request{
				Host: "yabs.yandex.ru",
				Path: "/page/123456",
				CGIArgs: map[string]string{
					"fruit": "apple",
				},
			},
			want: "/page/123456?fruit=apple",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := requestBuilder{}
			got := b.buildFullPath(tt.arg)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestRequestBuilder_prepareHeaders(t *testing.T) {
	tests := []struct {
		name    string
		headers map[string][]string
		ip      string
		want    map[string][]string
	}{
		{
			name: "common query",
			headers: map[string][]string{
				"Cookie":     {"yandexuid=123", "ys=abc"},
				"User-Agent": {"SomeBrowser 15.11"},
			},
			ip: "8.8.8.8",
			want: map[string][]string{
				"Cookie":     {"yandexuid=123", "ys=abc"},
				"User-Agent": {"SomeBrowser 15.11"},
				"X-Real-IP":  {"8.8.8.8"},
			},
		},
		{
			name: "no user-agent",
			headers: map[string][]string{
				"Cookie": {"yandexuid=123", "ys=abc"},
			},
			ip: "8.8.8.8",
			want: map[string][]string{
				"Cookie":     {"yandexuid=123", "ys=abc"},
				"User-Agent": {"Unknown user agent"},
				"X-Real-IP":  {"8.8.8.8"},
			},
		},
		{
			name: "clean up unwanted headers",
			headers: map[string][]string{
				"Accept":            {"*/*"},
				"Authorization":     {"oauth=xxx"},
				"Connection":        {"keep-alive"},
				"Content-Length":    {"100500"},
				"Host":              {"yandex.ru"},
				"Transfer-Encoding": {"chunked"},
				"User-Agent":        {"SomeBrowser 15.11"},
				"X-Real-Ip":         {"15.11.19.92"},
				"X-Ya-User-Ticket":  {"some-user-ticket"},
			},
			ip: "8.8.8.8",
			want: map[string][]string{
				"User-Agent": {"SomeBrowser 15.11"},
				"X-Real-Ip":  {"8.8.8.8"},
			},
		},
		{
			name: "clean up accept- headers",
			headers: map[string][]string{
				"Accept":          {"*/*"},
				"Accept-Language": {"ru-RU"},
				"Accept-Encoding": {"gzip"},
				"User-Agent":      {"SomeBrowser 15.11"},
			},
			ip: "8.8.8.8",
			want: map[string][]string{
				"Accept-Language": {"ru-RU"},
				"User-Agent":      {"SomeBrowser 15.11"},
				"X-Real-Ip":       {"8.8.8.8"},
			},
		},
		{
			name: "referer header",
			headers: map[string][]string{
				"Referer":    {"https://yandex.ru/beta"},
				"User-Agent": {"SomeBrowser 15.11"},
			},
			ip: "8.8.8.8",
			want: map[string][]string{
				"User-Agent":       {"SomeBrowser 15.11"},
				"X-Real-Ip":        {"8.8.8.8"},
				"X-YaBS-ReReferer": {"https://yandex.ru/beta"},
			},
		},
		{
			name: "different cases",
			headers: map[string][]string{
				"referer":     {"https://yandex.ru/beta"},
				"user-AGENT":  {"SomeBrowser 15.11"},
				"SOME-HEADER": {"1"},
			},
			ip: "8.8.8.8",
			want: map[string][]string{
				"User-Agent":       {"SomeBrowser 15.11"},
				"X-Real-Ip":        {"8.8.8.8"},
				"X-YaBS-ReReferer": {"https://yandex.ru/beta"},
				"Some-Header":      {"1"},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)

			componentsGetterMock.EXPECT().GetRequest().Return(models.Request{
				IP: tt.ip,
			})
			componentsGetterMock.EXPECT().GetOriginRequest().Return(&models.OriginRequest{
				Headers: createHTTPHeaderFromMap(tt.headers),
			}, nil)

			builder := requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			actual := builder.prepareHeaders()
			actualHeaders := createHTTPHeaderFromProtoanswers(actual)
			wantHeaders := createHTTPHeaderFromMap(tt.want)

			assert.Equal(t, wantHeaders, actualHeaders)
		})
	}
}

// TODO: дополнить тестами позднее
func TestRequestBuilder_getPageKey(t *testing.T) {
	type testCase struct {
		name          string
		initMocksFunc func(*MockcomponentsGetter)
		expected      string
	}

	cases := []testCase{
		{
			name: "desktop",
			initMocksFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetMordaContent().Return(models.MordaContent{
					Value: "big",
				}).AnyTimes()
				getter.EXPECT().GetDevice().Return(models.Device{}).AnyTimes()
				getter.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()
			},
			expected: "_default",
		},
		{
			name: "touch",
			initMocksFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetMordaContent().Return(models.MordaContent{
					Value: "touch",
				}).AnyTimes()
				getter.EXPECT().GetDevice().Return(models.Device{}).AnyTimes()
				getter.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()
			},
			expected: "touch",
		},
		{
			name: "search app",
			initMocksFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetMordaContent().Return(models.MordaContent{}).AnyTimes()
				getter.EXPECT().GetDevice().Return(models.Device{}).AnyTimes()
				getter.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						RealName: "search",
					},
				}).AnyTimes()
			},
			expected: "api_search_2_only",
		},
		{
			name: "yabrowser",
			initMocksFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetMordaContent().Return(models.MordaContent{}).AnyTimes()
				getter.EXPECT().GetDevice().Return(models.Device{}).AnyTimes()
				getter.EXPECT().GetRequest().Return(models.Request{
					APIInfo: models.APIInfo{
						RealName:    "yabrowser",
						RealVersion: 2,
					},
				}).AnyTimes()
			},
			expected: "api_yabrowser_2",
		},
		{
			name: "tv",
			initMocksFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetMordaContent().Return(models.MordaContent{
					Value: "tv",
				}).AnyTimes()
				getter.EXPECT().GetDevice().Return(models.Device{}).AnyTimes()
				getter.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()
			},
			expected: "tv",
		},
		{
			name: "desktop from tablet",
			initMocksFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetMordaContent().Return(models.MordaContent{
					Value: "big",
				}).AnyTimes()
				getter.EXPECT().GetDevice().Return(models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{
							"isTablet": "true",
						},
					},
				}).AnyTimes()
				getter.EXPECT().GetRequest().Return(models.Request{}).AnyTimes()
			},
			expected: "big_isTablet",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			tt.initMocksFunc(componentsGetterMock)
			b := requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			actual := b.getPageKey()
			assert.Equal(t, tt.expected, actual, "check page key")
		})
	}
}

func TestRequestBuilder_getPageNumberByKey(t *testing.T) {
	type testCase struct {
		name         string
		arg          string
		mockInitFunc func(getter *MockgeoSettingsGetter)
		expected     int
	}

	cases := []testCase{
		{
			name: "no settings",
			arg:  "touch",
			mockInitFunc: func(getter *MockgeoSettingsGetter) {
				getter.EXPECT().Get().Return(nil, errors.Error("no data")).Times(1)
			},
			expected: TouchPage,
		},
		{
			name: "no page value in settings",
			arg:  "touch",
			mockInitFunc: func(getter *MockgeoSettingsGetter) {
				getter.EXPECT().Get().Return(&geoSettings{
					Page: common.NewOptionalRaw[int](nil),
				}, errors.Error("no data")).Times(1)
			},
			expected: TouchPage,
		},
		{
			name: "page overriden by settings",
			arg:  "touch",
			mockInitFunc: func(getter *MockgeoSettingsGetter) {
				getter.EXPECT().Get().Return(&geoSettings{
					Page: common.NewOptional(123456),
				}, nil).Times(1)
			},
			expected: 123456,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			settingsGetterMock := NewMockgeoSettingsGetter(ctrl)
			tt.mockInitFunc(settingsGetterMock)
			b := &requestBuilder{
				geoSettingsGetter: settingsGetterMock,
			}
			actual := b.getPageNumberByKey(tt.arg)
			assert.Equal(t, tt.expected, actual, "check page number")
		})
	}
}

func TestRequestBuilder_getCLID(t *testing.T) {
	type testCase struct {
		name         string
		initMockFunc func(*MockcomponentsGetter)
		want         string
	}

	cases := []testCase{
		{
			name: "no clid",
			initMockFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetClid().Return(models.Clid{
					Client: "",
				})
			},
			want: "0",
		},
		{
			name: "non-empty clid",
			initMockFunc: func(getter *MockcomponentsGetter) {
				getter.EXPECT().GetClid().Return(models.Clid{
					Client: "123",
				})
			},
			want: "123",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			tt.initMockFunc(componentsGetterMock)
			builder := requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			actual := builder.getCLID()
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestRequestBuilder_getDeviceClass(t *testing.T) {
	type testCase struct {
		name   string
		traits uatraits.Traits
		want   string
	}

	cases := []testCase{
		{
			name: "empty os family",
			traits: map[string]string{
				"OSFamily": "",
			},
			want: "",
		},
		{
			name: "iOS",
			traits: map[string]string{
				"OSFamily": "ios",
			},
			want: "iphoneos",
		},
		{
			name: "Android",
			traits: map[string]string{
				"OSFamily": "AndrOiD",
			},
			want: "android",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetDevice().Return(models.Device{
				BrowserDesc: &models.BrowserDesc{Traits: tt.traits},
			})
			builder := requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			actual := builder.getDeviceClass()
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestRequestBuilder_getEnabledFeatures(t *testing.T) {
	type testCase struct {
		name string
		req  models.Request
		want string
	}

	cases := []testCase{
		{
			name: "desktop",
			req:  models.Request{},
			want: "",
		},
		{
			name: "search app without any features",
			req: models.Request{
				APIInfo: models.APIInfo{
					RealName: "api",
					Version:  2,
				},
				SearchAppFeatures: make([]models.SearchAppFeature, 0),
			},
			want: "",
		},
		{
			name: "search app with enabled features",
			req: models.Request{
				APIInfo: models.APIInfo{
					Name:    "search",
					Version: 2,
				},
				SearchAppFeatures: models.SearchAppFeatures{
					{
						Name:    "darktheme",
						Enabled: true,
					},
					{
						Name:    "keyboard",
						Enabled: false,
					},
					{
						Name:    "alice",
						Enabled: true,
					},
				},
			},
			want: "alice\ndarktheme",
		},
		{
			name: "search app with enabled features with same name",
			req: models.Request{
				APIInfo: models.APIInfo{
					Name:    "search",
					Version: 2,
				},
				SearchAppFeatures: models.SearchAppFeatures{
					{
						Name:    "widget",
						Enabled: true,
						Parameters: map[string]string{
							"type": "4x1",
						},
					},
					{
						Name:    "darktheme",
						Enabled: true,
					},
					{
						Name:    "keyboard",
						Enabled: false,
					},
					{
						Name:    "alice",
						Enabled: true,
					},
					{
						Name:    "widget",
						Enabled: false,
						Parameters: map[string]string{
							"type": "2x1",
						},
					},
				},
			},
			want: "alice\ndarktheme\nwidget",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetRequest().Return(tt.req)
			builder := requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			actual := builder.getEnabledFeatures()
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestRequestBuilder_getLang(t *testing.T) {

}

func TestRequestBuilder_getMobilMail(t *testing.T) {
	type authArgs struct {
		auth    models.Auth
		authErr error
	}

	type testCase struct {
		name string
		authArgs
		want string
	}

	cases := []testCase{
		{
			name: "auth err",
			authArgs: authArgs{
				auth:    models.Auth{},
				authErr: errors.Error("auth error"),
			},
			want: "",
		},
		{
			name: "empty value without uid",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						models.MobileMailSid: "",
					},
					UID: "",
				},
				authErr: nil,
			},
			want: "",
		},
		{
			name: "empty value",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						models.MobileMailSid: "",
					},
					UID: "test1234567890",
				},
				authErr: nil,
			},
			want: "0",
		},
		{
			name: "zero value without uid",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						models.MobileMailSid: "0",
					},
					UID: "",
				},
				authErr: nil,
			},
			want: "",
		},
		{
			name: "zero value",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						models.MobileMailSid: "0",
					},
					UID: "test1234567890",
				},
				authErr: nil,
			},
			want: "0",
		},
		{
			name: "non-zero value without uid",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						models.MobileMailSid: "1",
					},
					UID: "",
				},
				authErr: nil,
			},
			want: "",
		},
		{
			name: "non-zero value",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						models.MobileMailSid: "1",
					},
					UID: "test1234567890",
				},
				authErr: nil,
			},
			want: "1",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetAuthOrErr().Return(tt.auth, tt.authErr)
			b := &requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			assert.Equal(t, tt.want, b.getMobilmail())
		})
	}
}

func TestRequestBuilder_getOptions(t *testing.T) {

}

func TestRequestBuilder_getSIDs(t *testing.T) {
	type authArgs struct {
		auth    models.Auth
		authErr error
	}

	type testCase struct {
		name string
		authArgs
		want string
	}

	cases := []testCase{
		{
			name: "auth err",
			authArgs: authArgs{
				auth:    models.Auth{},
				authErr: errors.Error("auth error"),
			},
			want: "",
		},
		{
			name: "no sids",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{},
				},
				authErr: nil,
			},
			want: "",
		},
		{
			name: "single sid",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						"123": "value_123",
					},
				},
				authErr: nil,
			},
			want: "123",
		},
		{
			name: "several sids",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						"124":    "value_124",
						"123":    "value_123",
						"151192": "value_151192",
						"11":     "value_11",
						"1":      "value_1",
					},
				},
				authErr: nil,
			},
			want: "1\n11\n123\n124\n151192",
		},
		{
			name: "not integer sids",
			authArgs: authArgs{
				auth: models.Auth{
					Sids: map[string]string{
						"124":             "value_124",
						"11":              "value_11",
						"non_integer_sid": "some_value",
					},
				},
				authErr: nil,
			},
			want: "11\n124",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetAuthOrErr().Return(tt.auth, tt.authErr)
			b := &requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			assert.Equal(t, tt.want, b.getSIDs())
		})
	}
}

func TestRequestBuilder_getIsTablet(t *testing.T) {
	type testCase struct {
		name   string
		traits uatraits.Traits
		want   string
	}

	cases := []testCase{
		{
			name:   "no info about tablet",
			traits: make(map[string]string),
			want:   "0",
		},
		{
			name: "not a tablet",
			traits: map[string]string{
				"isTablet": "false",
			},
			want: "0",
		},
		{
			name: "tablet",
			traits: map[string]string{
				"isTablet": "true",
			},
			want: "1",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetDevice().Return(models.Device{
				BrowserDesc: &models.BrowserDesc{Traits: tt.traits},
			})
			builder := requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			actual := builder.getIsTablet()
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestRequestBuilder_getNewYandexUID(t *testing.T) {
	type testCase struct {
		name    string
		cookies models.YaCookies
		want    string
	}

	cases := []testCase{
		{
			name: "not generated",
			cookies: models.YaCookies{
				YandexUID:            "1234567890123456789",
				IsYandexUIDGenerated: false,
			},
			want: "",
		},
		{
			name: "generated",
			cookies: models.YaCookies{
				YandexUID:            "1234567890123456789",
				IsYandexUIDGenerated: true,
			},
			want: "1234567890123456789",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetYaCookies().Return(tt.cookies)
			b := &requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			assert.Equal(t, tt.want, b.getNewYandexUID())
		})
	}
}

func TestRequestBuilder_getTestIDs(t *testing.T) {
	type testCase struct {
		name    string
		testIDs common.IntSet
		want    string
	}

	cases := []testCase{
		{
			name:    "no test id",
			testIDs: common.NewIntSet(),
			want:    "",
		},
		{
			name:    "single test id",
			testIDs: common.NewIntSet(15111992),
			want:    "15111992",
		},
		{
			name: "several test ids",
			testIDs: common.NewIntSet(
				2128506, 15111992, 3141592, 777777),
			want: "777777\n2128506\n3141592\n15111992",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetFlags().Return(models.ABFlags{
				TestIDs: tt.testIDs,
			})
			b := &requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			assert.Equal(t, tt.want, b.getTestIDs())
		})
	}
}

func TestRequestBuilder_getUID(t *testing.T) {
	type authArgs struct {
		auth    models.Auth
		authErr error
	}
	type testCase struct {
		name string
		authArgs
		want string
	}

	cases := []testCase{
		{
			name: "auth error",
			authArgs: authArgs{
				auth:    models.Auth{},
				authErr: errors.Error("auth error"),
			},
			want: "",
		},
		{
			name: "empty uid",
			authArgs: authArgs{
				auth:    models.Auth{},
				authErr: nil,
			},
			want: "",
		},
		{
			name: "regular case",
			authArgs: authArgs{
				auth: models.Auth{
					UID: "123",
				},
				authErr: nil,
			},
			want: "123",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetAuthOrErr().Return(tt.auth, tt.authErr)
			b := &requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			assert.Equal(t, tt.want, b.getUID())
		})
	}
}

func TestRequestBuilder_getUUID(t *testing.T) {
	type testCase struct {
		name string
		models.APIInfo
		models.AppInfo
		want string
	}

	cases := []testCase{
		{
			name: "desktop",
			AppInfo: models.AppInfo{
				UUID: "123",
			},
			want: "",
		},
		{
			name: "YaBrowser",
			APIInfo: models.APIInfo{
				RealName: "yabroswer",
			},
			AppInfo: models.AppInfo{
				UUID: "123",
			},
			want: "",
		},
		{
			name: "SearchApp without UUID",
			APIInfo: models.APIInfo{
				Name:    "search",
				Version: 2,
			},
			AppInfo: models.AppInfo{
				UUID: "",
			},
			want: "",
		},
		{
			name: "SearchApp with UUID",
			APIInfo: models.APIInfo{
				Name:    "search",
				Version: 2,
			},
			AppInfo: models.AppInfo{
				UUID: "123",
			},
			want: "123",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetRequest().Return(models.Request{
				APIInfo: tt.APIInfo,
			})
			componentsGetterMock.EXPECT().GetAppInfo().Return(tt.AppInfo).MaxTimes(1)
			b := &requestBuilder{
				componentsGetter: componentsGetterMock,
			}
			assert.Equal(t, tt.want, b.getUUID())
		})
	}
}

func TestRequestBuilder_isCryproxEnabled(t *testing.T) {
	type mockArgs struct {
		models.AADB
		geoSettings
	}
	type testCase struct {
		name       string
		pageNumber int
		mockArgs
		wantFunc assert.BoolAssertionFunc
	}

	cases := []testCase{
		{
			name:       "AAB is disabled",
			pageNumber: TouchPage,
			mockArgs: mockArgs{
				AADB: models.AADB{
					IsAddBlock: false,
				},
				geoSettings: geoSettings{},
			},
			wantFunc: assert.False,
		},
		{
			name:       "AAB is turned off by MADM settings",
			pageNumber: TouchPage,
			mockArgs: mockArgs{
				AADB: models.AADB{
					IsAddBlock: true,
				},
				geoSettings: geoSettings{
					Page:                 common.NewOptional(TouchPage),
					IsAntiAdblockEnabled: false,
				},
			},
			wantFunc: assert.False,
		},
		{
			name:       "regular case",
			pageNumber: TouchPage,
			mockArgs: mockArgs{
				AADB: models.AADB{
					IsAddBlock: true,
				},
				geoSettings: geoSettings{
					Page:                 common.NewOptional(TouchPage),
					IsAntiAdblockEnabled: true,
				},
			},
			wantFunc: assert.True,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			componentsGetterMock := NewMockcomponentsGetter(ctrl)
			componentsGetterMock.EXPECT().GetAADB().Return(tt.AADB).MaxTimes(1)

			geoSettingsGetterMock := NewMockgeoSettingsGetter(ctrl)
			geoSettingsGetterMock.EXPECT().Get().Return(&tt.geoSettings, nil).MaxTimes(1)

			b := &requestBuilder{
				componentsGetter:  componentsGetterMock,
				geoSettingsGetter: geoSettingsGetterMock,
			}
			tt.wantFunc(t, b.isCryproxEnabled(tt.pageNumber))
		})
	}
}
