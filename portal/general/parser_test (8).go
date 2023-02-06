package devices

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/uatraits"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
)

func TestIsGramps(t *testing.T) {
	_, _ = DefaultDetector()

	type mockFlags struct {
		isInternalRequest bool
		hasGrampsParam    bool
	}
	tests := []struct {
		name   string
		madm   MADMOptions
		traits uatraits.Traits
		mocks  mockFlags
		want   bool
	}{
		{
			name: "old iOS",
			traits: map[string]string{
				"OSFamily":  "iOS",
				"OSVersion": "10.1",
			},
			want: true,
		},
		{
			name: "actual iOS",
			traits: map[string]string{
				"OSFamily":  "iOS",
				"OSVersion": "13.1",
			},
			want: false,
		},
		{
			name: "old Android",
			traits: map[string]string{
				"OSFamily":  "Android",
				"OSVersion": "4.9",
			},
			want: true,
		},
		{
			name: "actual Android",
			traits: map[string]string{
				"OSFamily":  "Android",
				"OSVersion": "6",
			},
			want: false,
		},
		{
			name: "Edge not Chromium based",
			traits: map[string]string{
				"BrowserName": "Edge",
				"BrowserBase": "NotChromium",
			},
			want: true,
		},
		{
			name: "old Chromium",
			traits: map[string]string{
				"BrowserBase":        "Chromium",
				"BrowserBaseVersion": "49",
			},
			want: true,
		},
		{
			name: "actual Chromium",
			traits: map[string]string{
				"BrowserBase":        "Chromium",
				"BrowserBaseVersion": "51",
			},
			want: false,
		},
		{
			name: "old Gecko",
			traits: map[string]string{
				"BrowserEngine":        "Gecko",
				"BrowserEngineVersion": "28.1",
			},
			want: true,
		},
		{
			name: "actual Gecko",
			traits: map[string]string{
				"BrowserEngine":        "Gecko",
				"BrowserEngineVersion": "29.1",
			},
			want: false,
		},
		{
			name: "Presto",
			traits: map[string]string{
				"BrowserEngine": "Presto",
			},
			want: true,
		},
		{
			name: "old MSIE",
			traits: map[string]string{
				"BrowserName":    "MSIE",
				"BrowserVersion": "10",
			},
			want: true,
		},
		{
			name: "actual MSIE",
			traits: map[string]string{
				"BrowserName":    "MSIE",
				"BrowserVersion": "11",
			},
			want: false,
		},
		{
			name: "old Safari",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "5",
			},
			want: true,
		},
		{
			name: "actual Safari",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "6.5",
			},
			want: false,
		},
		{
			name: "old mobile Safari",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "5",
			},
			want: true,
		},
		{
			name: "actual mobile Safari",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "6.5",
			},
			want: false,
		},
		{
			name: "mobile Safari 6.1",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "6.1",
				"isMobile":       "true",
			},
			want: true,
		},
		{
			name: "desktop Safari 6.1",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "6.1",
				"isMobile":       "false",
			},
			want: false,
		},
		{
			name: "actual Chromium with disabled 2021 checks",
			traits: map[string]string{
				"BrowserBase":        "Chromium",
				"BrowserBaseVersion": "30",
			},
			madm: MADMOptions{
				DisableGrampsDesktop2021:     true,
				DisableGrampsDesktop2021iOS:  true,
				DisableGrampsDesktop2021Edge: true,
			},
			want: false,
		},
		{
			name: "actual Gecko with disabled 2021 checks",
			traits: map[string]string{
				"BrowserEngine":        "Gecko",
				"BrowserEngineVersion": "28.1",
			},
			madm: MADMOptions{
				DisableGrampsDesktop2021:     true,
				DisableGrampsDesktop2021iOS:  true,
				DisableGrampsDesktop2021Edge: true,
			},
			want: false,
		},
		{
			name: "not Chromium based Edge with disabled 2021 checks",
			traits: map[string]string{
				"BrowserName": "Gecko",
				"BrowserBase": "notChromium",
			},
			madm: MADMOptions{
				DisableGrampsDesktop2021:     true,
				DisableGrampsDesktop2021iOS:  true,
				DisableGrampsDesktop2021Edge: true,
			},
			want: false,
		},
		{
			name: "actual iOS with disabled 2021 checks",
			traits: map[string]string{
				"OSFamily":  "iOS",
				"OSVersion": "10",
			},
			madm: MADMOptions{
				DisableGrampsDesktop2021:     true,
				DisableGrampsDesktop2021iOS:  true,
				DisableGrampsDesktop2021Edge: true,
			},
			want: false,
		},
		{
			name: "actual Android browser with disabled 2021 checks",
			traits: map[string]string{
				"OSFamily":    "Android",
				"OSVersion":   "4.4.5",
				"BrowserName": "AndroidBrowser",
			},
			madm: MADMOptions{
				DisableGrampsDesktop2021:     true,
				DisableGrampsDesktop2021iOS:  true,
				DisableGrampsDesktop2021Edge: true,
			},
			want: false,
		},
		{
			name:   "with debug params",
			traits: map[string]string{},
			mocks: mockFlags{
				isInternalRequest: true,
				hasGrampsParam:    true,
			},
			want: true,
		},
		{
			name: "bad traits",
			traits: map[string]string{
				"BrowserBase":          "bad",
				"BrowserEngine":        "bad",
				"BrowserName":          "bad",
				"BrowserBaseVersion":   "100",
				"BrowserEngineVersion": "100",
				"BrowserNameVersion":   "100",
			},
			want: false,
		},
		{
			name: "bad os",
			traits: map[string]string{
				"OSFamily":  "bad",
				"OSVersion": "100",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cgi := make(map[string][]string)
			if tt.mocks.hasGrampsParam {
				cgi["gramps"] = []string{"1"}
			}

			request := models.Request{
				IsInternal: tt.mocks.isInternalRequest,
				CGI:        cgi,
			}

			p := parser{
				madmOptions: tt.madm,
			}

			got := p.isGramps(request, tt.traits)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestIsTouchGramps(t *testing.T) {
	_, _ = DefaultDetector()

	type mockFlags struct {
		isInternalRequest bool
		hasGrampsParam    bool
		apiInfoName       string
	}
	tests := []struct {
		name   string
		traits uatraits.Traits
		mocks  mockFlags
		zone   string
		want   bool
	}{
		{
			name: "Bada",
			traits: map[string]string{
				"OSFamily": "Bada",
			},
			want: true,
		},
		{
			name: "old iOS",
			traits: map[string]string{
				"OSFamily":  "iOS",
				"OSVersion": "10.1",
			},
			want: true,
		},
		{
			name: "actual iOS",
			traits: map[string]string{
				"OSFamily":  "iOS",
				"OSVersion": "13.1",
			},
			want: false,
		},
		{
			name: "old Android",
			traits: map[string]string{
				"OSFamily":  "Android",
				"OSVersion": "4.9",
			},
			want: true,
		},
		{
			name: "actual Android",
			traits: map[string]string{
				"OSFamily":  "Android",
				"OSVersion": "6",
			},
			want: false,
		},
		{
			name: "old UCBrowser",
			traits: map[string]string{
				"OSFamily":       "Android",
				"OSVersion":      "10",
				"BrowserName":    "UCBrowser",
				"BrowserVersion": "9.9",
			},
			want: true,
		},
		{
			name: "actual UCBrowser",
			traits: map[string]string{
				"OSFamily":       "Android",
				"OSVersion":      "10",
				"BrowserName":    "UCBrowser",
				"BrowserVersion": "10.9",
			},
			want: false,
		},
		{
			name: "old Chromium",
			traits: map[string]string{
				"BrowserBase":        "Chromium",
				"BrowserBaseVersion": "49",
			},
			want: true,
		},
		{
			name: "actual Chromium",
			traits: map[string]string{
				"BrowserBase":        "Chromium",
				"BrowserBaseVersion": "51",
			},
			want: false,
		},
		{
			name: "old Gecko",
			traits: map[string]string{
				"BrowserEngine":        "Gecko",
				"BrowserEngineVersion": "27.1",
			},
			want: true,
		},
		{
			name: "actual Gecko",
			traits: map[string]string{
				"BrowserEngine":        "Gecko",
				"BrowserEngineVersion": "28.1",
			},
			want: false,
		},
		{
			name: "Presto",
			traits: map[string]string{
				"BrowserEngine": "Presto",
			},
			want: true,
		},
		{
			name: "actual MSIE",
			traits: map[string]string{
				"BrowserName":    "MSIE",
				"BrowserVersion": "11",
			},
			want: false,
		},
		{
			name: "old Safari",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "5",
			},
			want: false,
		},
		{
			name: "actual Safari",
			traits: map[string]string{
				"BrowserName":    "Safari",
				"BrowserVersion": "6.5",
			},
			want: false,
		},
		{
			name: "trident",
			traits: map[string]string{
				"BrowserEngine": "Trident",
			},
			want: true,
		},
		{
			name: "old WebKit",
			traits: map[string]string{
				"BrowserEngine":        "WebKit",
				"BrowserEngineVersion": "537.3",
			},
			want: true,
		},
		{
			name: "actual WebKit",
			traits: map[string]string{
				"BrowserEngine":        "WebKit",
				"BrowserEngineVersion": "537.4",
			},
			want: true,
		},
		{
			name: "WindowsPhone",
			traits: map[string]string{
				"OSFamily": "WindowsPhone",
			},
			want: true,
		},
		{
			name:   "with debug params",
			traits: map[string]string{},
			mocks: mockFlags{
				isInternalRequest: true,
				hasGrampsParam:    true,
			},
			want: true,
		},
		{
			name: "bad traits",
			traits: map[string]string{
				"BrowserBase":          "bad",
				"BrowserEngine":        "bad",
				"BrowserName":          "bad",
				"BrowserBaseVersion":   "100",
				"BrowserEngineVersion": "100",
				"BrowserNameVersion":   "100",
			},
			want: false,
		},
		{
			name: "bad os",
			traits: map[string]string{
				"OSFamily":  "bad",
				"OSVersion": "100",
			},
			want: false,
		},
		{
			name: "com.tr old WebKit",
			traits: map[string]string{
				"BrowserEngine":        "WebKit",
				"BrowserEngineVersion": "537.3",
			},
			zone: "com.tr",
			want: false,
		},
		{
			name:   "com.tr with debug params",
			traits: map[string]string{},
			mocks: mockFlags{
				isInternalRequest: true,
				hasGrampsParam:    true,
			},
			zone: "com.tr",
			want: false,
		},
		{
			name:   "it's search app",
			traits: map[string]string{},
			mocks: mockFlags{
				apiInfoName: "searchapp",
			},
			want: false,
		},
		{
			name: "it's search app with old android",
			traits: map[string]string{
				"OSFamily":  "Android",
				"OSVersion": "4.9",
			},
			mocks: mockFlags{
				apiInfoName: "searchapp",
			},
			want: false,
		},
		{
			name: "it's search app with debug params",
			traits: map[string]string{
				"OSFamily":  "Android",
				"OSVersion": "4.9",
			},
			mocks: mockFlags{
				isInternalRequest: true,
				hasGrampsParam:    true,
				apiInfoName:       "searchapp",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cgi := make(map[string][]string)
			if tt.mocks.hasGrampsParam {
				cgi["touch_gramps"] = []string{"1"}
			}

			request := models.Request{
				IsInternal: tt.mocks.isInternalRequest,
				CGI:        cgi,
				APIInfo:    models.APIInfo{Name: tt.mocks.apiInfoName},
			}

			p := parser{}

			got := p.isTouchGramps(request, tt.traits, tt.zone)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestHasGrampsQueryParam(t *testing.T) {
	tests := []struct {
		name    string
		request models.Request
		want    bool
	}{
		{
			name: "normal",
			request: models.Request{
				CGI: map[string][]string{
					"gramps": {},
				},
			},
			want: true,
		},
		{
			name: "normal with equal",
			request: models.Request{
				CGI: map[string][]string{
					"gramps": {"1"},
				},
			},
			want: true,
		},
		{
			name: "normal with several params",
			request: models.Request{
				CGI: map[string][]string{
					"gramps": {"1"},
					"test":   {"1"},
				},
			},
			want: true,
		},
		{
			name: "normal with another broken param",
			request: models.Request{
				CGI: map[string][]string{
					"gramps": {"1"},
					"test":   {},
				},
			},
			want: true,
		},
		{
			name: "uppercase",
			request: models.Request{
				CGI: map[string][]string{
					"Gramps": {"1"},
				},
			},
			want: false,
		},
		{
			name:    "without gramps",
			request: models.Request{},
			want:    false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			got := p.hasGrampsQueryParam(tt.request)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestHasTouchGrampsQueryParam(t *testing.T) {
	tests := []struct {
		name    string
		request models.Request
		want    bool
	}{
		{
			name: "normal",
			request: models.Request{
				CGI: map[string][]string{
					"touch_gramps": {},
				},
			},
			want: true,
		},
		{
			name: "normal with equal",
			request: models.Request{
				CGI: map[string][]string{
					"touch_gramps": {"1"},
				},
			},
			want: true,
		},
		{
			name: "normal with several params",
			request: models.Request{
				CGI: map[string][]string{
					"touch_gramps": {"1"},
					"test":         {"1"},
				},
			},
			want: true,
		},
		{
			name: "normal with another broken param",
			request: models.Request{
				CGI: map[string][]string{
					"touch_gramps": {"1"},
					"test":         {},
				},
			},
			want: true,
		},
		{
			name: "uppercase",
			request: models.Request{
				CGI: map[string][]string{
					"Touch_Gramps": {"1"},
				},
			},
			want: false,
		},
		{
			name:    "without gramps",
			request: models.Request{},
			want:    false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			got := p.hasTouchGrampsQueryParam(tt.request)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	type fields struct {
		detectedTraits uatraits.Traits
	}
	type args struct {
		originRequest      *models.OriginRequest
		request            models.Request
		appInfo            models.AppInfo
		yaCookies          models.YaCookies
		originRequestError error
		httpHeadersError   error
	}
	tests := []struct {
		name    string
		fields  fields
		args    args
		want    models.Device
		wantErr bool
	}{
		{
			name: "Got user agent from http header",
			fields: fields{
				detectedTraits: nil,
			},
			args: args{
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"User-Agent": {"from http headers"},
					},
				},
				request: models.Request{
					URL: "/",
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					UserAgent: "from http headers",
				},
			},
			wantErr: false,
		},
		{
			name: "Got user agent from http header with multiple values",
			fields: fields{
				detectedTraits: nil,
			},
			args: args{
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"User-Agent": {"B", "D", "A", "E", "C"},
					},
				},
				request: models.Request{
					URL: "/",
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					UserAgent: "C",
				},
			},
			wantErr: false,
		},
		{
			name: "Got user agent from http header with multiple values, with versions",
			fields: fields{
				detectedTraits: nil,
			},
			args: args{
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"User-Agent": {"SomeBrowser 1.0", "SomeBrowser 3.0", "SomeBrowser 2.0"},
					},
				},
				request: models.Request{
					URL: "/",
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					UserAgent: "SomeBrowser 2.0",
				},
			},
			wantErr: false,
		},
		{
			name: "Got error from origin request getter while try to get http headers",
			fields: fields{
				detectedTraits: nil,
			},
			args: args{
				originRequest:    &models.OriginRequest{},
				httpHeadersError: errors.Error("some kind of error"),
				request: models.Request{
					URL: "/",
				},
			},
			want:    models.Device{},
			wantErr: true,
		},
		{
			name: "Got user agent from http header; but got error from origin request getter while try to get origin request",
			fields: fields{
				detectedTraits: nil,
			},
			args: args{
				originRequestError: errors.Error("some kind of error"),
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"User-Agent": {"from http headers"},
					},
				},
				request: models.Request{
					URL: "/",
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					UserAgent: "from http headers",
				},
			},
			wantErr: false,
		},
		{
			name: "check default DPI and default screen for API",
			fields: fields{
				detectedTraits: nil,
			},
			args: args{
				originRequestError: errors.Error("some kind of error"),
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"User-Agent": {"from http headers"},
					},
				},
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					URL: "/",
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					UserAgent: "from http headers",
					DPI:       1,
					Screen: models.Screen{
						X: 1080,
						Y: 1350,
					},
				},
			},
			wantErr: false,
		},
		{
			name: "check screen for Web",
			fields: fields{
				detectedTraits: nil,
			},
			args: args{
				originRequestError: errors.Error("some kind of error"),
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"User-Agent": {"from http headers"},
					},
				},
				request: models.Request{
					URL: "/",
				},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"sz": {
								Name:  "sz",
								Value: "100x500",
							},
						},
					},
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					UserAgent: "from http headers",
					Screen: models.Screen{
						X: 100,
						Y: 500,
					},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			detectorMock := NewMocktraitsDetector(ctrl)
			detectorMock.EXPECT().DetectByHeaders(gomock.Any()).Return(tt.fields.detectedTraits).MaxTimes(1)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.args.originRequest, tt.args.httpHeadersError).MaxTimes(1)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.args.originRequest, tt.args.originRequestError).MaxTimes(1)
			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(tt.args.request).MaxTimes(1)
			appInfoGetterMock := NewMockappInfoGetter(ctrl)
			appInfoGetterMock.EXPECT().GetAppInfo().Return(tt.args.appInfo).MaxTimes(1)
			yaCookiesGetterMock := NewMockyaCookiesGetter(ctrl)
			yaCookiesGetterMock.EXPECT().GetYaCookies().Return(tt.args.yaCookies).MaxTimes(1)

			p := &parser{
				detector:            detectorMock,
				originRequestKeeper: originRequestKeeperMock,
				requestGetter:       requestGetterMock,
				appInfoGetter:       appInfoGetterMock,
				yaCookiesGetter:     yaCookiesGetterMock,
			}

			got, err := p.Parse()

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}

func Test_parser_extendTraitsForSearchApp(t *testing.T) {
	type args struct {
		appInfo models.AppInfo
		traits  uatraits.Traits
	}

	tests := []struct {
		name string
		args args
		want uatraits.Traits
	}{
		{
			name: "tabled android",
			args: args{
				appInfo: models.AppInfo{
					Platform: "apad",
				},
				traits: make(map[string]string),
			},
			want: map[string]string{
				"isTablet":  "true",
				"OSFamily":  "Android",
				"isTouch":   "true",
				"isMobile":  "true",
				"OSVersion": "0",
			},
		},
		{
			name: "tabled ios",
			args: args{
				appInfo: models.AppInfo{
					Platform: "ipad",
				},
				traits: make(map[string]string),
			},
			want: map[string]string{
				"isTablet":  "true",
				"OSFamily":  "iOS",
				"isTouch":   "true",
				"isMobile":  "true",
				"OSVersion": "0",
			},
		},
		{
			name: "win phone",
			args: args{
				appInfo: models.AppInfo{
					Platform: "wp",
				},
				traits: make(map[string]string),
			},
			want: map[string]string{
				"OSFamily":  "windowsphone",
				"isTouch":   "true",
				"isMobile":  "true",
				"OSVersion": "0",
			},
		},
		{
			name: "os version",
			args: args{
				appInfo: models.AppInfo{
					OSVersion: "15.3",
				},
				traits: make(map[string]string),
			},
			want: map[string]string{
				"isTouch":   "true",
				"isMobile":  "true",
				"OSVersion": "15.3",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			assert.Equal(t, tt.want, p.extendTraitsForSearchApp(tt.args.appInfo, tt.args.traits))
		})
	}
}

func Test_parser_getTraits(t *testing.T) {
	type fields struct {
		createDetector func(t *testing.T) *MocktraitsDetector
	}

	type args struct {
		headers http.Header
		request models.Request
		appInfo models.AppInfo
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   uatraits.Traits
	}{
		{
			name: "nil traits",
			fields: fields{
				createDetector: func(t *testing.T) *MocktraitsDetector {
					detector := NewMocktraitsDetector(gomock.NewController(t))
					detector.EXPECT().DetectByHeaders(gomock.Any()).Return(nil)
					return detector
				},
			},
			args: args{
				headers: http.Header{},
				request: models.Request{
					URL: "/",
				},
				appInfo: models.AppInfo{},
			},
			want: nil,
		},
		{
			name: "not api and not data",
			fields: fields{
				createDetector: func(t *testing.T) *MocktraitsDetector {
					detector := NewMocktraitsDetector(gomock.NewController(t))
					detector.EXPECT().DetectByHeaders(gomock.Any()).Return(uatraits.Traits{
						"test": "true",
					})
					return detector
				},
			},
			args: args{
				headers: http.Header{},
				request: models.Request{
					URL: "/",
				},
				appInfo: models.AppInfo{},
			},
			want: map[string]string{
				"test": "true",
			},
		},
		{
			name: "api data",
			fields: fields{
				createDetector: func(t *testing.T) *MocktraitsDetector {
					detector := NewMocktraitsDetector(gomock.NewController(t))
					detector.EXPECT().DetectByHeaders(gomock.Any()).Return(uatraits.Traits{
						"test": "true",
					})
					return detector
				},
			},
			args: args{
				headers: http.Header{},
				request: models.Request{
					URL: "/portal/api/data/1",
					APIInfo: models.APIInfo{
						Name:    "data",
						Version: 1,
					},
				},
				appInfo: models.AppInfo{},
			},
			want: map[string]string{
				"test": "true",
			},
		},
		{
			name: "extend devices",
			fields: fields{
				createDetector: func(t *testing.T) *MocktraitsDetector {
					detector := NewMocktraitsDetector(gomock.NewController(t))
					detector.EXPECT().DetectByHeaders(gomock.Any()).Return(uatraits.Traits{
						"test": "true",
					})
					return detector
				},
			},
			args: args{
				headers: http.Header{},
				request: models.Request{
					URL: "/portal/api/1/data",
					APIInfo: models.APIInfo{
						Name: "1",
					},
				},
				appInfo: models.AppInfo{
					Platform: "apad",
				},
			},
			want: map[string]string{
				"test":      "true",
				"isTablet":  "true",
				"OSFamily":  "Android",
				"isTouch":   "true",
				"isMobile":  "true",
				"OSVersion": "0",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				detector: tt.fields.createDetector(t),
			}

			assert.Equal(t, tt.want, p.getTraits(tt.args.headers, tt.args.request, tt.args.appInfo))
		})
	}
}

func Test_parser_getDpi(t *testing.T) {
	type args struct {
		request models.Request
		appInfo models.AppInfo
	}

	tests := []struct {
		name string
		args args
		want float32
	}{
		{
			name: "isAPI is false",
			args: args{
				request: models.Request{
					URL: "/",
				},
				appInfo: models.AppInfo{},
			},
			want: 0,
		},
		{
			name: "without dpi",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{},
				},
				appInfo: models.AppInfo{},
			},
			want: 1,
		},
		{
			name: "dpi=501",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dpi=501",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dpi": {"501"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 4,
		},
		{
			name: "dpi=200",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dpi=201",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dpi": {"201"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 1.5,
		},
		{
			name: "dpi=0",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dpi=0",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dpi": {"0"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 1,
		},
		{
			name: "dpi=0&dp=1.5",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dpi=0&dp=1.5",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dpi": {"0"}, "dp": {"1.5"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 1.5,
		},
		{
			name: "dpi=0&dp=2.5",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dpi=0&dp=2.5",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dpi": {"0"}, "dp": {"2.5"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 2,
		},
		{
			name: "dpi=100&dp=2.5",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dpi=100&dp=2.5",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dpi": {"0"}, "dp": {"2.5"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 2,
		},
		{
			name: "dpi=500&dp=0",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dpi=500&dp=0",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dpi": {"500"}, "dp": {"0"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 3,
		},
		{
			name: "dp=0",
			args: args{
				request: models.Request{
					URL: "/portal/api/search/2/?dp=0",
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"dp": {"0"}},
				},
				appInfo: models.AppInfo{},
			},
			want: 1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			assert.Equal(t, tt.want, p.getDpi(tt.args.request, tt.args.appInfo))
		})
	}
}

func Test_parser_getScreen(t *testing.T) {
	type args struct {
		request   models.Request
		yaCookies models.YaCookies
	}

	tests := []struct {
		name string
		args args
		want models.Screen
	}{
		{
			name: "yaCookies is empty and AppInfo is empty",
			args: args{
				request:   models.Request{},
				yaCookies: models.YaCookies{},
			},
			want: models.Screen{},
		},
		{
			name: "yaCookies have valid szm",
			args: args{
				request: models.Request{},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"szm": {
								Name:  "szm",
								Value: "100500:200x300",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 200,
				Y: 300,
			},
		},
		{
			name: "yaCookies have valid szm. YS",
			args: args{
				request: models.Request{},
				yaCookies: models.YaCookies{
					Ys: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"szm": {
								Name:  "szm",
								Value: "100500:200x300",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 200,
				Y: 300,
			},
		},
		{
			name: "yaCookies have no valid szm",
			args: args{
				request: models.Request{},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"szm": {
								Name:  "szm",
								Value: "100500_200x300",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 0,
				Y: 0,
			},
		},
		{
			name: "yaCookies have sz and szm",
			args: args{
				request: models.Request{},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"szm": {
								Name:  "szm",
								Value: "100500:200x300",
							},
							"sz": {
								Name:  "sz",
								Value: "100x500",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 200,
				Y: 300,
			},
		},
		{
			name: "yaCookies have sz without szm",
			args: args{
				request: models.Request{},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"sz": {
								Name:  "sz",
								Value: "100x500",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 100,
				Y: 500,
			},
		},
		{
			name: "Cgi.size is more important than cookie.sz",
			args: args{
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"size": {"400,500"}},
				},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"sz": {
								Name:  "sz",
								Value: "100x500",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 400,
				Y: 500,
			},
		},
		{
			name: "Cgi.size is more important than cgi.poiy",
			args: args{
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"size": {"400,500"}, "poiy": {"400"}},
				},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"sz": {
								Name:  "sz",
								Value: "100x500",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 400,
				Y: 500,
			},
		},
		{
			name: "Cgi.poiy exists but x is empty",
			args: args{
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{"size": {""}, "poiy": {"400"}},
				},
				yaCookies: models.YaCookies{},
			},
			want: models.Screen{
				X: 1080,
				Y: 1350,
			},
		},
		{
			name: "default",
			args: args{
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{},
				},
				yaCookies: models.YaCookies{},
			},
			want: models.Screen{
				X: 1080,
				Y: 1350,
			},
		},
		{
			name: "API with yacookies",
			args: args{
				request: models.Request{
					APIInfo: models.APIInfo{
						Name: "search",
					},
					CGI: url.Values{},
				},
				yaCookies: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"sz": {
								Name:  "sz",
								Value: "100x500",
							},
						},
					},
				},
			},
			want: models.Screen{
				X: 1080,
				Y: 1350,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}

			assert.Equal(t, tt.want, p.getScreen(tt.args.request, tt.args.yaCookies))
		})
	}
}
