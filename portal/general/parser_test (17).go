package mordacontent

import (
	"fmt"
	"net/http"
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/uatraits"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_parser_getMordaContentByDomain(t *testing.T) {
	testCases := []struct {
		caseName      string
		requestDomain string
		expected      string
	}{
		{
			caseName:      "yandex.tld",
			requestDomain: "yandex.",
			expected:      Big,
		},
		{
			caseName:      "www.yandex.tld",
			requestDomain: "www.yandex.",
			expected:      Big,
		},
		{
			caseName:      "l7test.yandex.tld",
			requestDomain: "l7test.yandex.",
			expected:      Big,
		},
		{
			caseName:      "m.yandex.tld",
			requestDomain: "m.yandex.",
			expected:      Mob,
		},
		{
			caseName:      "fallback to default on requestDomain=unknown.yandex.tld",
			requestDomain: "unknown.yandex.",
			expected:      Big,
		},
	}

	zones := []string{"ru", "ua", "kz", "by", "uz"}
	for _, tt := range testCases {
		for _, mordaZone := range zones {
			t.Run(fmt.Sprintf("%s, zone %s", tt.caseName, mordaZone), func(t *testing.T) {
				ctrl := gomock.NewController(t)

				domainGetterMock := NewMockdomainGetter(ctrl)
				domainGetterMock.EXPECT().GetDomain().Return(models.Domain{Subdomain: "wwwc"}).MaxTimes(1)

				spokSettingsMock := NewMockspokSettings(ctrl)
				spokSettingsMock.EXPECT().IsSpokDomain(gomock.Any()).Return(false).AnyTimes()

				parser := NewParser(nil, nil, nil, nil, spokSettingsMock, nil, domainGetterMock, common.Development, nil)
				testDomain := tt.requestDomain + mordaZone
				got := parser.getMordaContentByDomain(testDomain)

				assert.Equal(t, tt.expected, got, fmt.Sprintf("got=%s expect=%s", got, tt.expected))
			})
		}
	}

	testCasesCom := []struct {
		caseName      string
		requestDomain string
		expected      string
	}{
		{
			caseName:      "yandex.com",
			requestDomain: "yandex.com",
			expected:      Com,
		},
		{
			caseName:      "www.yandex.com",
			requestDomain: "www.yandex.com",
			expected:      Com,
		},
		{
			caseName:      "tel.yandex.ru",
			requestDomain: "tel.yandex.ru",
			expected:      Tel,
		},
	}
	for _, tt := range testCasesCom {
		t.Run(tt.caseName, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			domainGetterMock := NewMockdomainGetter(ctrl)
			domainGetterMock.EXPECT().GetDomain().Return(models.Domain{}).Times(1)

			spokSettingsMock := NewMockspokSettings(ctrl)
			spokSettingsMock.EXPECT().IsSpokDomain(gomock.Any()).Return(true).AnyTimes()

			parser := NewParser(nil, nil, nil, nil, spokSettingsMock, nil, domainGetterMock, common.Development, nil)
			testDomain := tt.requestDomain
			got := parser.getMordaContentByDomain(testDomain)

			assert.Equal(t, tt.expected, got, fmt.Sprintf("got=%s expect=%s", got, tt.expected))
		})
	}
}

func Test_parser_getRequestDomain(t *testing.T) {
	type testCase struct {
		name          string
		originRequest *models.OriginRequest
		want          string
		wantErr       bool
	}
	cases := []testCase{
		{
			name:    "no origin request",
			wantErr: true,
		},
		{
			name:          "no Host header",
			originRequest: &models.OriginRequest{},
		},
		{
			name: "empty Host header value",
			originRequest: &models.OriginRequest{
				Headers: map[string][]string{
					"Host": {},
				},
			},
		},
		{
			name: "regular Host header value",
			originRequest: &models.OriginRequest{
				Headers: map[string][]string{
					"Host": {"yandex.ru"},
				},
			},
			want: "yandex.ru",
		},
		{
			name: "upper case Host header value",
			originRequest: &models.OriginRequest{
				Headers: map[string][]string{
					"Host": {"YANDEX.RU"},
				},
			},
			want: "yandex.ru",
		},
		{
			name: "Host header value starts with capital letter",
			originRequest: &models.OriginRequest{
				Headers: map[string][]string{
					"Host": {"Yandex.ru"},
				},
			},
			want: "yandex.ru",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			if tt.originRequest != nil {
				originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.originRequest, nil)
			} else {
				originRequestKeeperMock.EXPECT().GetOriginRequest().Return(nil, errors.Error("nil origin request"))
			}

			domainGetterMock := NewMockdomainGetter(ctrl)
			domainGetterMock.EXPECT().GetDomain().Return(models.Domain{}).Times(1)

			spokSettingsMock := NewMockspokSettings(ctrl)
			spokSettingsMock.EXPECT().IsSpokDomain(gomock.Any()).Return(true).AnyTimes()

			p := NewParser(nil, originRequestKeeperMock, nil, nil, spokSettingsMock, nil, domainGetterMock, common.Development, nil)
			actual, err := p.getRequestDomain()
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.want, actual)
			}
		})
	}
}

func Test_parser_getLayoutKey(t *testing.T) {
	type testCase struct {
		name string

		mordaContent string
		forcedMordaContent

		want string
	}

	cases := []testCase{
		// noForcedContent
		{
			name:               "from big without forced",
			mordaContent:       Big,
			forcedMordaContent: noForcedContent,
			want:               "*",
		},
		{
			name:               "from touch without forced",
			mordaContent:       Touch,
			forcedMordaContent: noForcedContent,
			want:               "*",
		},
		{
			name:               "from mobile without forced",
			mordaContent:       Mob,
			forcedMordaContent: noForcedContent,
			want:               "m",
		},
		// touchForced
		{
			name:               "from big with touch forced",
			mordaContent:       Big,
			forcedMordaContent: forcedTouch,
			want:               "m",
		},
		{
			name:               "from touch with touch forced",
			mordaContent:       Touch,
			forcedMordaContent: forcedTouch,
			want:               "m",
		},
		{
			name:               "from touch with mob forced",
			mordaContent:       Mob,
			forcedMordaContent: forcedTouch,
			want:               "m",
		},
		// bigForced
		{
			name:               "from big with big forced",
			mordaContent:       Big,
			forcedMordaContent: forcedBig,
			want:               "d",
		},
		{
			name:               "from touch with big forced",
			mordaContent:       Touch,
			forcedMordaContent: forcedBig,
			want:               "d",
		},
		{
			name:               "from mobile with big forced",
			mordaContent:       Mob,
			forcedMordaContent: forcedBig,
			want:               "m",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			parser := &parser{}
			got := parser.getLayoutKey(tt.mordaContent, tt.forcedMordaContent)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_getLayouts(t *testing.T) {
	testCases := []struct {
		caseName          string
		mordaContent      string
		requestDomain     string
		userAgent         string
		xOperaMiniPhoneUA string
		expected          map[string][]string
	}{
		{
			caseName:      "// 0",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (SMART-TV; X11; Linux i686) AppleWebKit/535.20+ (KHTML, like Gecko) Version/5.0 Safari/535.20+",
			expected: map[string][]string{
				"*": {"tv"},
				"m": {"tv"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 1 and mordaContent=Big",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 1 and mordaContent=Mob",
			mordaContent:  Mob,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 1 and mordaContent=Com",
			mordaContent:  Com,
			requestDomain: "yandex.com",
			userAgent:     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 2.1",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (Linux; arm_64; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 BroPP/1.0 SA/3 Mobile Safari/537.36 YandexSearch/21.115.1",
			expected: map[string][]string{
				"*": {"touch_android", "touch", "pda"},
				"m": {"touch_android", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 2.2 mordaContent = Com",
			mordaContent:  Com,
			requestDomain: "yandex.com",
			userAgent:     "Mozilla/5.0 (Linux; arm_64; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 BroPP/1.0 SA/3 Mobile Safari/537.36 YandexSearch/21.115.1",
			expected: map[string][]string{
				"*": {"touch_android", "touch", "pda"},
				"m": {"touch_android", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 3.1",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (Linux; arm_64; Android 11; SM-T505) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 BroPP/1.0 SA/3 Mobile Safari/537.36 YandexSearch/21.115.1/apad",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch_android", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 3.2",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Opera/9.80 (Android 4.1.1; Linux; Opera Tablet/ADY-1111101223; U; ru) Presto/2.9.201 Version/11.00",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch_pda", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 4",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 YaBrowser/19.5.2.38.10/apad YaApp_iOS/92.00 Safari/604.1 SA/3",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch_ios", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 5",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 YaBrowser/19.5.2.38.10 YaApp_iOS/92.00 Safari/604.1 SA/3",
			expected: map[string][]string{
				"*": {"touch_ios", "touch", "pda"},
				"m": {"touch_ios", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 6.1",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (Mobile; Windows Phone 8.1; Android 4.0; ARM; Trident/7.0; Touch; rv:11.0",
			expected: map[string][]string{
				"*": {"touch_wp7", "touch", "pda"},
				"m": {"touch_wp7", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 6.2",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (Mobile; Windows Phone 8.1; Android 4.0; AppleWebKit/537.35+; ARM; Touch; rv:11.0",
			expected: map[string][]string{
				"*": {"touch_wp7", "touch", "pda"},
				"m": {"touch_wp7", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 6.3",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (Windows NT 6.2; ARM; Trident/7.0; Touch; rv:11.0; WPDesktop; Lumia 540 Dual SIM) like Gecko",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch_wp7", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 6.4",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (BB10; Kbd) AppleWebKit/537.35+ (KHTML%2C like Gecko) Version/10.3.2.2876 Mobile Safari/537.35+",
			expected: map[string][]string{
				"*": {"touch_blackberry", "touch", "pda"},
				"m": {"touch_blackberry", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 7",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (SAMSUNG; SAMSUNG-GT-S5380D/S5380DXXLF1; U; Bada/2.0; ru-ru) AppleWebKit/534.20 (KHTML, like Gecko) Dolfin/3.0 Mobile HVGA SMM-MMS/1.2.0 OPN-B",
			expected: map[string][]string{
				"*": {"touch_bada", "touch", "pda"},
				"m": {"touch_bada", "touch", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 8",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (X11; U; Linux armv6l; en; rv:1.9a6pre) Gecko/20070810 Firefox/3.0a1 Tablet browser 0.1.16 RX-34_2007SE_4.2007.38-2",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch_pda", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:          "// 8 with UA from Opera",
			mordaContent:      Big,
			requestDomain:     "yandex.ru",
			userAgent:         "Opera/9.80 (iPad; Opera Mini/7.0.5/191.262; U; ru) Presto/2.12.423 Version/12.16",
			xOperaMiniPhoneUA: "Mozilla/5.0 (iPad; U; CPU iPhone OS 9_3_6 like Mac OS X; ru-ru)",
			expected: map[string][]string{
				"*": {"pc"},
				"m": {"touch_pda", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 9",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/5.0 (SAMSUNG; SAMSUNG-GT-S5250/S5250XEKJ3; U; Bada/1.0; ru-ru) AppleWebKit/533.1 (KHTML, like Gecko) Dolfin/2.0 Mobile WQVGA SMM-MMS/1.2.0 NexPlayer/3.0 profile/MIDP-2.1 configuration/CLDC-1.1 OPN-B",
			expected: map[string][]string{
				"*": {"pda"},
				"m": {"pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:          "// 9 with UA from Opera",
			mordaContent:      Big,
			requestDomain:     "yandex.ru",
			userAgent:         "Opera/9.80 (X11; Linux zvav; U; ru) Presto/2.12.423 Version/12.16",
			xOperaMiniPhoneUA: "NokiaX2-00/5.0 (04.80) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+",
			expected: map[string][]string{
				"*": {"pda"},
				"m": {"pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 10",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; IEMobile 6.12) ASUS-GalaxyII/1.0",
			expected: map[string][]string{
				"*": {"pda"},
				"m": {"pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 11.1",
			mordaContent:  Big,
			requestDomain: "yandex.com.tr",
			userAgent:     "61D_11C_HW (MRE/3.1.00(800);MAUI/MD03_S01_V10_20170929;BDATE/2017/09/29 14:49;LCD/240320;CHIP/MT6261;KEY/Normal;TOUCH/0;CAMERA/1;SENSOR/0;DEV/61D_11C_HW;WAP Browser/MAUI ();GMOBI/001;MBOUNCE/002;MOMAGIC/003;INDEX/004;SPICEI2I/005;GAMELOFT/006;MOBIM/007;KKFUN/008;MTONE) S107_MD03_S01_V10_20170929 Release/2017.09.29 WAP Browser/MAUI Profile/  Q03C1-2.40 ru-RU",
			expected: map[string][]string{
				"*": {"pda"},
				"m": {"pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 11.2",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "61D_11C_HW (MRE/3.1.00(800);MAUI/MD03_S01_V10_20170929;BDATE/2017/09/29 14:49;LCD/240320;CHIP/MT6261;KEY/Normal;TOUCH/0;CAMERA/1;SENSOR/0;DEV/61D_11C_HW;WAP Browser/MAUI ();GMOBI/001;MBOUNCE/002;MOMAGIC/003;INDEX/004;SPICEI2I/005;GAMELOFT/006;MOBIM/007;KKFUN/008;MTONE) S107_MD03_S01_V10_20170929 Release/2017.09.29 WAP Browser/MAUI Profile/  Q03C1-2.40 ru-RU",
			expected: map[string][]string{
				"*": {"tel", "pda"},
				"m": {"tel", "pda"},
				"d": {"pc"},
			},
		},
		{
			caseName:      "// 12",
			mordaContent:  Big,
			requestDomain: "yandex.ru",
			userAgent:     "Dalvik/2.1.0 (Linux; U; Android 7.1.2; MI Build/NHG47K) YandexSearch/10.30/apad",
			expected: map[string][]string{
				"*": {"pda"},
				"m": {"pda"},
				"d": {"pc"},
			},
		},
	}

	for _, tt := range testCases {
		t.Run(tt.caseName, func(t *testing.T) {
			headers := make(http.Header)
			headers.Set("User-Agent", tt.userAgent)
			headers.Set("X-OperaMini-Phone-UA", tt.xOperaMiniPhoneUA)

			detector, err := uatraits.NewDetector()
			assert.NoError(t, err)

			traits := detector.DetectByHeaders(headers)

			ctrl := gomock.NewController(t)

			deviceGetter := NewMockdeviceGetter(ctrl)
			deviceGetter.EXPECT().GetDevice().Return(models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: traits,
				},
			})

			parser := &parser{
				deviceGetter: deviceGetter,
			}

			got := parser.getLayouts(tt.mordaContent, tt.requestDomain)

			assert.Equal(t, tt.expected, got)
		})
	}
}

func Test_parser_Parse(t *testing.T) {

	detector, err := uatraits.NewDetector()
	require.NoError(t, err)
	desktopBrowserTraits := detector.Detect("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.0.2054 Yowser/2.5 Safari/537.36")
	mobileBrowserTraits := detector.Detect("Mozilla/5.0 (Linux; arm; Android 10; COL-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.216 BroPP/1.0 SA/3 Mobile Safari/537.36 YandexSearch/21.51.1")

	var (
		noContentForcedMyCookie = models.MyCookie{}
		mobileForcedMyCookie    = models.MyCookie{
			Parsed: map[uint32][]int32{
				44: {0},
			},
		}
		desktopForcedMyCookie = models.MyCookie{
			Parsed: map[uint32][]int32{
				44: {1},
			},
		}
	)

	type testCase struct {
		name     string
		uatraits uatraits.Traits
		host     string
		path     string
		myCookie models.MyCookie
		isSpok   bool
		env      common.Environment
		request  models.Request

		want models.MordaContent
	}

	cases := []testCase{
		{
			name:     "request from desktop",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/",
			myCookie: noContentForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from desktop to /d",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/d",
			myCookie: noContentForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from desktop to /m",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/m",
			myCookie: noContentForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from desktop with forced desktop in my cookie",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/",
			myCookie: desktopForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from desktop to /d with forced desktop in my cookie",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/d",
			myCookie: desktopForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from desktop to /m with forced desktop in my cookie",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/m",
			myCookie: desktopForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from desktop with forced mobile in my cookie",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/",
			myCookie: mobileForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from desktop to /d with forced mobile in my cookie",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/d",
			myCookie: mobileForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from desktop to /m with forced mobile in my cookie",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/m",
			myCookie: mobileForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from mobile",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/",
			myCookie: noContentForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from mobile to /d",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/d",
			myCookie: noContentForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from mobile to /m",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/m",
			myCookie: noContentForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from mobile with forced desktop in my cookie",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/",
			myCookie: desktopForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from mobile to /d with forced desktop in my cookie",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/d",
			myCookie: desktopForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from mobile to /m with forced desktop in my cookie",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/m",
			myCookie: desktopForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from mobile with forced mobile in my cookie",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/",
			myCookie: mobileForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "request from mobile to /d with forced mobile in my cookie",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/d",
			myCookie: mobileForcedMyCookie,

			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "request from mobile to /m with forced mobile in my cookie",
			uatraits: mobileBrowserTraits,
			host:     "yandex.ru",
			path:     "/m",
			myCookie: mobileForcedMyCookie,

			want: models.MordaContent{
				Value: "touch",
			},
		},
		{
			name:     "from bot to mobile MD",
			uatraits: detector.Detect("Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"),
			host:     "m.yandex.md",
			path:     "/",
			isSpok:   true,
			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "from bot to mobile TJ",
			uatraits: detector.Detect("Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"),
			host:     "m.yandex.tj",
			path:     "/",
			isSpok:   true,
			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "from bot to mobile LT",
			uatraits: detector.Detect("Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"),
			host:     "m.yandex.lt",
			path:     "/",
			isSpok:   true,
			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name:     "from bot to FR",
			uatraits: detector.Detect("Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"),
			host:     "yandex.fr:443",
			path:     "/",
			isSpok:   true,
			want: models.MordaContent{
				Value: "spok",
			},
		},
		{
			name:     "HOME-77557",
			uatraits: detector.Detect("Mozilla/5.0 (Linux; U) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36 SmartTV/7.0 (NetCast) Android"),
			host:     "yandex.ru",
			path:     "/m/",
			isSpok:   false,
			want: models.MordaContent{
				Value: "mob",
			},
		},
		{
			name:     "big redefined as touch by apiInfo",
			uatraits: desktopBrowserTraits,
			host:     "yandex.ru",
			path:     "/portal/api/search/2",
			request: models.Request{
				APIInfo: models.APIInfo{
					Name:    "search",
					Version: 2,
				},
			},
			want: models.MordaContent{
				Value: Touch,
			},
		},
		{
			name:     "overridden by cgi",
			uatraits: detector.Detect("Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"),
			host:     "m.yandex.lt",
			path:     "/",
			request: models.Request{
				CGI: url.Values{"content": {"embedstream_touch_iphone"}},
			},
			want: models.MordaContent{
				Value: "embedstream_touch",
			},
			isSpok: true,
		},
		{
			name:     "yaru",
			uatraits: desktopBrowserTraits,
			host:     "ya.ru",
			path:     "/",
			want: models.MordaContent{
				Value: "yaru",
			},
			isSpok: false,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			deviceGetterMock := NewMockdeviceGetter(ctrl)

			device := models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: tt.uatraits,
				},
			}
			deviceGetterMock.EXPECT().GetDevice().Return(device).AnyTimes()

			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(&models.OriginRequest{
				Headers: map[string][]string{
					"Host": {tt.host},
				},
				Path: tt.path,
			}, nil).AnyTimes()

			cookieGetterMock := NewMockcookieGetter(ctrl)
			cookieGetterMock.EXPECT().GetCookie().Return(models.Cookie{
				My: tt.myCookie,
			}).AnyTimes()

			mockMordaContentMetrics := NewMockmordaContentMetrics(ctrl)
			mockMordaContentMetrics.EXPECT().UpdateMordaContent(gomock.Any(), gomock.Any()).AnyTimes()

			spokSettingsMock := NewMockspokSettings(ctrl)
			spokSettingsMock.EXPECT().IsSpokDomain(gomock.Any()).Return(tt.isSpok).AnyTimes()

			tt.request.URL = tt.host + tt.path
			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(tt.request).AnyTimes()

			domainGetterMock := NewMockdomainGetter(ctrl)
			domainGetterMock.EXPECT().GetDomain().Return(models.Domain{}).MaxTimes(1)

			p := NewParser(log3.NewLoggerStub(), originRequestKeeperMock, deviceGetterMock, cookieGetterMock, spokSettingsMock,
				requestGetterMock, domainGetterMock, tt.env, mockMordaContentMetrics)

			actual, err := p.Parse()
			require.NoError(t, err)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_extractURI(t *testing.T) {
	type testCase struct {
		name string
		url  string
		want string
	}

	cases := []testCase{
		{
			name: "empty URL",
			url:  "",
			want: "",
		},
		{
			name: "only slash",
			url:  "/",
			want: "/",
		},
		{
			name: "some path with args",
			url:  "/m?a=1&b=2",
			want: "/m",
		},
		{
			name: "some path with trailing slash and args",
			url:  "/m/?a=1&b=2",
			want: "/m/",
		},
		{
			name: "only args",
			url:  "?a=1&b=2",
			want: "",
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := parser{}
			actual := p.extractURI(tt.url)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_redefineMordaContent(t *testing.T) {
	type testCase struct {
		name                   string
		requestURL             string
		initialMordaContent    string
		mordaContentByMyCookie forcedMordaContent

		want redefinedContent
	}

	cases := []testCase{
		{
			name: "from desktop to / without cookies",

			requestURL:             "/",
			initialMordaContent:    Big,
			mordaContentByMyCookie: noForcedContent,

			want: redefinedContent{
				forcedMordaContent:  noForcedContent,
				updatedMordaContent: Big,
			},
		},
		{
			name: "from desktop to /m without cookies",

			requestURL:             "/m",
			initialMordaContent:    Big,
			mordaContentByMyCookie: noForcedContent,

			want: redefinedContent{
				forcedMordaContent:  forcedTouch,
				updatedMordaContent: Mob,
			},
		},
		{
			name: "from desktop to /d without cookies",

			requestURL:             "/d",
			initialMordaContent:    Big,
			mordaContentByMyCookie: noForcedContent,

			want: redefinedContent{
				forcedMordaContent:  forcedBig,
				updatedMordaContent: Big,
			},
		},
		{
			name: "from touch to / without cookies",

			requestURL:             "/",
			initialMordaContent:    Touch,
			mordaContentByMyCookie: noForcedContent,

			want: redefinedContent{
				forcedMordaContent:  noForcedContent,
				updatedMordaContent: Touch,
			},
		},
		{
			name: "from touch to /m without cookies",

			requestURL:             "/m",
			initialMordaContent:    Touch,
			mordaContentByMyCookie: noForcedContent,

			want: redefinedContent{
				forcedMordaContent:  forcedTouch,
				updatedMordaContent: Touch,
			},
		},
		{
			name: "from touch to /d without cookies",

			requestURL:             "/d",
			initialMordaContent:    Touch,
			mordaContentByMyCookie: noForcedContent,

			want: redefinedContent{
				forcedMordaContent:  forcedBig,
				updatedMordaContent: Touch,
			},
		},
		{
			name: "from desktop to / with forced touch in my cookie",

			requestURL:             "/",
			initialMordaContent:    Big,
			mordaContentByMyCookie: forcedTouch,

			want: redefinedContent{
				forcedMordaContent:  forcedTouch,
				updatedMordaContent: Big,
			},
		},
		{
			name: "from touch to / with forced desktop in my cookie",

			requestURL:             "/",
			initialMordaContent:    Touch,
			mordaContentByMyCookie: forcedBig,

			want: redefinedContent{
				forcedMordaContent:  forcedBig,
				updatedMordaContent: Touch,
			},
		},
		{
			name: "from desktop to /d with forced touch in my cookie",

			requestURL:             "/d",
			initialMordaContent:    Big,
			mordaContentByMyCookie: forcedTouch,

			want: redefinedContent{
				forcedMordaContent:  forcedBig,
				updatedMordaContent: Big,
			},
		},
		{
			name: "from touch to /d with forced desktop in my cookie",

			requestURL:             "/d",
			initialMordaContent:    Touch,
			mordaContentByMyCookie: forcedBig,

			want: redefinedContent{
				forcedMordaContent:  forcedBig,
				updatedMordaContent: Touch,
			},
		},
		{
			name: "from desktop to /m with forced touch in my cookie",

			requestURL:             "/m",
			initialMordaContent:    Big,
			mordaContentByMyCookie: forcedTouch,

			want: redefinedContent{
				forcedMordaContent:  forcedTouch,
				updatedMordaContent: Mob,
			},
		},
		{
			name: "from touch to /m with forced desktop in my cookie",

			requestURL:             "/m",
			initialMordaContent:    Touch,
			mordaContentByMyCookie: forcedBig,

			want: redefinedContent{
				forcedMordaContent:  forcedTouch,
				updatedMordaContent: Touch,
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			actual := p.redefineMordaContent(tt.requestURL, tt.initialMordaContent, tt.mordaContentByMyCookie)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func Test_parser_getOverriddenMordaContentFromCGI(t *testing.T) {
	tests := []struct {
		name    string
		request models.Request
		env     common.Environment
		want    string
	}{
		{
			name: "production request",
			request: models.Request{
				IsInternal: false,
			},
			env:  common.Production,
			want: "",
		},
		{
			name: "testing env, empty content",
			request: models.Request{
				CGI: url.Values{"content": {""}},
			},
			env:  common.Testing,
			want: "",
		},
		{
			name: "internal request, no content value in available list",
			request: models.Request{
				IsInternal: true,
				CGI:        url.Values{"content": {"incorrect"}},
			},
			want: "",
		},
		{
			name: "internal request, content value in available list",
			request: models.Request{
				IsInternal: true,
				CGI:        url.Values{"content": {"tvchannels_handler_touch"}},
			},
			want: "tvchannels_handler_touch",
		},
		{
			name: "internal request, content value in additional list",
			request: models.Request{
				IsInternal: true,
				CGI:        url.Values{"content": {"videohub_touch"}},
			},
			want: "videohub_touch",
		},
		{
			name: "internal request, content value in additional list with suffix",
			request: models.Request{
				IsInternal: true,
				CGI:        url.Values{"content": {"videohub_touch_iphone"}},
			},
			want: "videohub_touch",
		},
		{
			name: "internal request, content value in additional list with extra suffix",
			request: models.Request{
				IsInternal: true,
				CGI:        url.Values{"content": {"big_iphone_mob"}},
			},
			want: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			requestGetterMock := NewMockrequestGetter(gomock.NewController(t))
			requestGetterMock.EXPECT().GetRequest().Return(tt.request)
			p := &parser{
				requestGetter: requestGetterMock,
				env:           tt.env,
			}
			got := p.getMordaContentFromCGI()
			assert.Equal(t, tt.want, got)
		})
	}
}
