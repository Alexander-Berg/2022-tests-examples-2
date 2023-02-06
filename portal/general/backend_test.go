package morda

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/cookies"
	"a.yandex-team.ru/portal/avocado/libs/utils/devices"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
)

func Test_backendSetupHandler_isBig(t *testing.T) {
	tests := []struct {
		name     string
		initMock func(*testing.T, *mocks.Base)
		want     bool
	}{
		{
			name: "Iphone user-agent",
			initMock: func(t *testing.T, base *mocks.Base) {
				headers := http.Header{"User-Agent": []string{"Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"}}
				detector, err := devices.DefaultDetector()
				require.NoError(t, err)
				traits := detector.DetectByHeaders(headers)

				base.On("GetDevice").Return(models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: traits,
					},
				}).Once()
				base.On("GetCookie").Return(models.Cookie{}).Maybe()
			},
			want: false,
		},
		{
			name: "Safari",
			initMock: func(t *testing.T, base *mocks.Base) {
				headers := http.Header{"User-Agent": []string{"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"}}
				detector, err := devices.DefaultDetector()
				require.NoError(t, err)
				traits := detector.DetectByHeaders(headers)

				base.On("GetDevice").Return(models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: traits,
					},
				}).Once()
				base.On("GetCookie").Return(models.Cookie{}).Maybe()
			},
			want: true,
		},
		{
			name: "Iphone user-agent with forced desktop",
			initMock: func(t *testing.T, base *mocks.Base) {
				headers := http.Header{"User-Agent": []string{"Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"}}
				detector, err := devices.DefaultDetector()
				require.NoError(t, err)
				traits := detector.DetectByHeaders(headers)

				rawMy := "YywBAQA="
				my, err := cookies.NewParserMy().Parse(rawMy)
				assert.NoError(t, err)

				base.On("GetDevice").Return(models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: traits,
					},
				}).Once()
				base.On("GetCookie").Return(models.Cookie{
					Parsed: map[string][]string{
						"my": {rawMy},
					},
					My: my,
				}).Maybe()
			},
			want: false,
		},
		{
			name: "Safari with forced mobile by my-cookie",
			initMock: func(t *testing.T, base *mocks.Base) {
				headers := http.Header{"User-Agent": []string{"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"}}
				detector, err := devices.DefaultDetector()
				require.NoError(t, err)
				traits := detector.DetectByHeaders(headers)

				rawMy := "YywBAAA="
				my, err := cookies.NewParserMy().Parse(rawMy)
				assert.NoError(t, err)

				base.On("GetDevice").Return(models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: traits,
					},
				}).Once()
				base.On("GetCookie").Return(models.Cookie{
					Parsed: map[string][]string{
						"my": {rawMy},
					},
					My: my,
				}).Maybe()
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			baseMock := &mocks.Base{}
			ctxMock := &mocks.Morda{}
			tt.initMock(t, baseMock)
			ctxMock.On("Base").Return(baseMock)
			h := &backendSetupHandler{
				ctx: ctxMock,
			}

			got := h.isBig()
			require.Equal(t, tt.want, got)

			ctxMock.AssertExpectations(t)
		})
	}
}

func Test_backendSetupHandler_isForcedMobileByCookie(t *testing.T) {
	tests := []struct {
		name          string
		initMock      func(*mocks.Base)
		myCookieValue string
		want          bool
	}{
		{
			name:          "No cookie",
			myCookieValue: "",
			want:          false,
		},
		{
			name:          "Empty value: []",
			myCookieValue: "YwA=",
			want:          false,
		},
		{
			name:          "touch forced: [0]",
			myCookieValue: "YywBAAA=",
			want:          true,
		},
		{
			name:          "big forced: [1]",
			myCookieValue: "YywBAQA=",
			want:          false,
		},
		{
			name:          "touch forced: [0] with some languages set",
			myCookieValue: "YycCAAMsAQAA",
			want:          true,
		},
		{
			name:          "nothing forced: [2]",
			myCookieValue: "YywBAgA=",
			want:          false,
		},
		{
			name:          "touch forced, two values: [0, 42]",
			myCookieValue: "YywCACoA",
			want:          true,
		},
		{
			name:          "touch forced, two values: [0, 0]",
			myCookieValue: "YywCAAAA",
			want:          true,
		},
		{
			name:          "touch forced, two values: [0, 1]",
			myCookieValue: "YywCAAEA",
			want:          true,
		},
		{
			name:          "big forced, two values: [1, 1]",
			myCookieValue: "YywCAQEA",
			want:          false,
		},
		{
			name:          "big forced, two values: [1, 0]",
			myCookieValue: "YywCAQAA",
			want:          false,
		},
		{
			name:          "big forced, two values: [1, 42]",
			myCookieValue: "YywCASoA",
			want:          false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cookie := models.Cookie{
				Parsed: map[string][]string{},
			}
			if len(tt.myCookieValue) > 0 {
				cookie.Parsed["my"] = []string{tt.myCookieValue}
			}
			my, err := cookies.NewParserMy().Parse(tt.myCookieValue)
			assert.NoError(t, err)
			cookie.My = my

			baseMock := &mocks.Base{}
			baseMock.On("GetCookie").Return(cookie).Once()

			ctxMock := &mocks.Morda{}
			ctxMock.On("Base").Return(baseMock).Once()
			h := &backendSetupHandler{
				ctx: ctxMock,
			}

			got := h.isForcedMobileByCookie()

			require.Equal(t, tt.want, got)
			ctxMock.AssertExpectations(t)
		})
	}
}

func Test_backendSetupHandler_isRelevantHost(t *testing.T) {
	type args struct {
		host string
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "prod",
			args: args{
				host: "yandex.ru",
			},
			want: true,
		},
		{
			name: "hamster",
			args: args{
				host: "hamster.yandex.ru",
			},
			want: true,
		},
		{
			name: "br",
			args: args{
				host: "yandex.br",
			},
			want: false,
		},
		{
			name: "pr betas",
			args: args{
				host: "morda-go-pr-1914243.hometest.yandex.ru",
			},
			want: true,
		},
		{
			name: "rc betas",
			args: args{
				host: "morda-gorc.hometest.yandex.ru",
			},
			want: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			h := &backendSetupHandler{}

			got := h.isRelevantHost(tt.args.host)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_backendSetupHandler_isRelevantPath(t *testing.T) {
	type args struct {
		path string
		cgi  url.Values
	}
	tests := []struct {
		name    string
		args    args
		want    bool
		wantErr bool
	}{
		{
			name: "Root path",
			args: args{
				path: "/",
			},
			want: true,
		},
		{
			name: "With srcrwr",
			args: args{
				path: "/",
				cgi:  url.Values{"srcrwr": {"MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400"}},
			},
			want: true,
		},
		{
			name: "With srcrwr and graph",
			args: args{
				path: "/",
				cgi: url.Values{
					"srcrwr": {"MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400"},
					"graph":  {"testing"},
				},
			},
			want: true,
		},
		{
			name: "Not only srcrwr and graph",
			args: args{
				path: "/",
				cgi: url.Values{
					"srcrwr": {"MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400"},
					"graph":  {"testing"},
					"test":   {"1"},
				},
			},
			want: false,
		},
		{
			name: "Not root path",
			args: args{
				path: "/m",
			},
			want: false,
		},
		{
			name: "Not root with srcrwr",
			args: args{
				path: "/m?srcrwr=MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400",
				cgi: url.Values{
					"srcrwr": {"MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400"},
				},
			},
			want: false,
		},
		{
			name: "clid acceptable",
			args: args{
				path: "/",
				cgi: url.Values{
					"clid": {"12420"},
				},
			},
			want: true,
		},
		{
			name: "clid and srcrwr",
			args: args{
				path: "/",
				cgi: url.Values{
					"srcrwr": {"MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400"},
					"clid":   {"12420"},
				},
			},
			want: true,
		},
		{
			name: "had not relevant query param",
			args: args{
				path: "/?clid=12420&srcrwr=MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400&test=123",
				cgi: url.Values{
					"srcrwr": {"MORDA__MORDA_GO_BACKEND%3Amorda-dev-v194.sas.yp-c.yandex.net%3A20400"},
					"clid":   {"12420"},
					"test":   {"123"},
				},
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			h := &backendSetupHandler{}

			got, err := h.isRelevantPath(tt.args.path, tt.args.cgi)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}

func Test_backendSetupHandler_zenLibFilter(t *testing.T) {
	type testCase struct {
		name   string
		device models.Device
		want   bool
	}

	var tests []testCase

	type version struct {
		v      string
		actual bool
	}

	var desktopTests []testCase

	var chromiumVersions []version
	for _, v := range []string{"0", "-10", "-45", "41.99"} {
		chromiumVersions = append(chromiumVersions, version{v, false})
	}
	for _, v := range []string{"42", "42.1", "43"} {
		chromiumVersions = append(chromiumVersions, version{v, true})
	}

	for _, v := range chromiumVersions {
		desktopTests = append(desktopTests, testCase{
			name: "desktop Chromium version " + v.v,
			device: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: map[string]string{
						"isMobile":           "false",
						"isTablet":           "false",
						"BrowserBase":        "Chromium",
						"BrowserBaseVersion": v.v,
					},
				},
			},
			want: v.actual,
		})
	}

	browsers := []struct {
		name                        string
		actualVersions, badVersions []string
	}{
		{
			name:           "Edge",
			badVersions:    []string{"", "0", "-1", "11", "11.99"},
			actualVersions: []string{"12", "12.0", "12.1", "42"},
		},
		{
			name:           "MSIE",
			badVersions:    []string{"qweqwe.qwe", "10", "10.90999"},
			actualVersions: []string{"11", "11.0001", "12"},
		},
		{
			name:           "Firefox",
			badVersions:    []string{".45", "44.1b", "45b.1"},
			actualVersions: []string{"45", "45.1b", "46", "99999"},
		},
		{
			name:           "Safari",
			badVersions:    []string{"8.1", "08.1"},
			actualVersions: []string{"9", "9.0", "10", "10.0.0.11.23.32"},
		},
	}

	for _, b := range browsers {
		var versions []version
		for _, v := range b.actualVersions {
			versions = append(versions, version{v, true})
		}
		for _, v := range b.badVersions {
			versions = append(versions, version{v, false})
		}

		for _, v := range versions {
			desktopTests = append(desktopTests, testCase{
				name: "desktop " + b.name + " version " + v.v,
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{
							"isMobile":       "false",
							"isTablet":       "false",
							"BrowserName":    b.name,
							"BrowserVersion": v.v,
						},
					},
				},
				want: v.actual,
			})
		}
	}

	var nonDesktopTests []testCase
	for _, tt := range desktopTests {
		for _, c := range []struct {
			isMobile, isTablet string
		}{{"false", "true"}, {"true", "false"}, {"true", "true"}} {
			traits := map[string]string{}
			for k, v := range tt.device.GetTraits() {
				traits[k] = v
			}
			traits["isMobile"] = c.isMobile
			traits["isTablet"] = c.isTablet
			nonDesktopTests = append(nonDesktopTests, testCase{
				name: "not " + tt.name,
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: traits,
					},
				},
				want: false,
			})
		}
	}

	var mobileTests []testCase

	mobiles := []struct {
		os                          string
		actualVersions, badVersions []string
	}{
		{
			os:             "Android",
			actualVersions: []string{"4.4", "4.33", "4.5", "6", "7.0", "8.999", "10.1"},
			badVersions:    []string{"0.0", "1", "2.5", "4", "4.3"},
		},
		{
			os:             "iOS",
			actualVersions: []string{"8", "8.1", "8.111", "9", "9.99", "125.1.2.3.4"},
			badVersions:    []string{"1", "6.7.8.9", "7.99"},
		},
	}
	for _, m := range mobiles {
		var versions []version
		for _, v := range m.actualVersions {
			versions = append(versions, version{v, true})
		}
		for _, v := range m.badVersions {
			versions = append(versions, version{v, false})
		}

		for _, v := range versions {
			for _, c := range []struct {
				isMobile, isTablet string
				isMobileDevice     bool
			}{
				{"false", "false", false},
				{"false", "true", true},
				{"true", "false", true},
				{"true", "true", true},
			} {
				mobileTests = append(mobileTests, testCase{
					name: "mobile " + m.os + " version " + v.v,
					device: models.Device{
						BrowserDesc: &models.BrowserDesc{
							Traits: map[string]string{
								"isMobile":  c.isMobile,
								"isTablet":  c.isTablet,
								"OSFamily":  m.os,
								"OSVersion": v.v,
							},
						},
					},
					want: v.actual && c.isMobileDevice,
				})
			}
		}
	}

	tests = append(tests, desktopTests...)
	tests = append(tests, nonDesktopTests...)
	tests = append(tests, mobileTests...)

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			baseMock := &mocks.Base{}
			ctxMock := &mocks.Morda{}
			baseMock.On("GetDevice").Return(tt.device).Once()
			ctxMock.On("Base").Return(baseMock).Once()
			h := &backendSetupHandler{ctx: ctxMock}

			got := h.zenLibFilter()

			require.Equal(t, tt.want, got)

			ctxMock.AssertExpectations(t)
			baseMock.AssertExpectations(t)
		})
	}
}
