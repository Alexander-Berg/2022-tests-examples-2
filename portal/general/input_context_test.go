package conditions

import (
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/uatraits"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func TestWithMordaZoneZone(t *testing.T) {
	ctrl := gomock.NewController(t)
	type args struct {
		mordazoneGetter mordaZoneGetter
	}

	tests := []struct {
		name    string
		args    args
		want    inputContextData
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "empty domain zone",
			args: args{
				mordazoneGetter: func() *MockmordaZoneGetter {
					getter := NewMockmordaZoneGetter(ctrl)
					getter.EXPECT().GetMordaZone().Return(models.MordaZone{}).MaxTimes(1)
					return getter
				}(),
			},
			want:    inputContextData{},
			wantErr: assert.NoError,
		},
		{
			name: "ru domain zone",
			args: args{
				mordazoneGetter: func() *MockmordaZoneGetter {
					getter := NewMockmordaZoneGetter(ctrl)
					getter.EXPECT().GetMordaZone().Return(models.MordaZone{
						Value: "ru",
					})
					return getter
				}(),
			},
			want: inputContextData{
				"tld": "ru",
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			option := WithMordaZone(tt.args.mordazoneGetter)

			context := inputContext{
				data: make(inputContextData),
			}
			err := option(&context)
			tt.wantErr(t, err)

			assert.Equal(t, tt.want, context.data)
		})
	}
}

func TestWithUATraits(t *testing.T) {
	type testCase struct {
		name    string
		device  models.Device
		want    inputContextData
		wantErr bool
	}
	cases := []testCase{
		{
			name: "empty traits",
			device: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: uatraits.Traits{},
				},
			},
			want:    inputContextData{},
			wantErr: false,
		},
		{
			name: "normal traits",
			device: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: uatraits.Traits{
						"BrowserName":    "YaBro",
						"BrowserVersion": "15.11.1992",
						"OSName":         "macOS",
					},
				},
			},
			want: inputContextData{
				"device.BrowserName":    "YaBro",
				"device.BrowserVersion": "15.11.1992",
				"device.OSName":         "macOS",
			},
			wantErr: false,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			deviceGetterMock := NewMockdeviceGetter(ctrl)
			deviceGetterMock.EXPECT().GetDevice().Return(tt.device)
			option := WithUATraits(deviceGetterMock)

			context := inputContext{
				data: make(inputContextData),
			}
			err := option(&context)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}

			assert.Equal(t, tt.want, context.data)
		})
	}
}

func TestWithMordaContent(t *testing.T) {
	type testCase struct {
		name         string
		mordaContent models.MordaContent
		want         inputContextData
		wantErr      bool
	}
	cases := []testCase{
		{
			name:         "empty morda content",
			mordaContent: models.MordaContent{},
			want: inputContextData{
				"content": "",
				"desktop": "0",
				"touch":   "0",
			},
			wantErr: false,
		},
		{
			name: "morda content big",
			mordaContent: models.MordaContent{
				Value: "big",
			},
			want: inputContextData{
				"content": "big",
				"desktop": "1",
				"touch":   "0",
			},
			wantErr: false,
		},
		{
			name: "morda content touch",
			mordaContent: models.MordaContent{
				Value: "touch",
			},
			want: inputContextData{
				"content": "touch",
				"desktop": "0",
				"touch":   "1",
			},
			wantErr: false,
		},
		{
			name: "other morda content",
			mordaContent: models.MordaContent{
				Value: "tv",
			},
			want: inputContextData{
				"content": "tv",
				"desktop": "0",
				"touch":   "0",
			},
			wantErr: false,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			mordaContentGetterMock := NewMockmordaContentGetter(ctrl)
			mordaContentGetterMock.EXPECT().GetMordaContent().Return(tt.mordaContent)
			option := WithMordaContent(mordaContentGetterMock)

			context := inputContext{
				data: make(inputContextData),
			}
			err := option(&context)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}

			assert.Equal(t, tt.want, context.data)
		})
	}
}

func TestWithCGIArgs(t *testing.T) {
	type testCase struct {
		name    string
		cgi     url.Values
		want    inputContextData
		wantErr bool
	}
	cases := []testCase{
		{
			name:    "no CGI args",
			cgi:     url.Values{},
			want:    inputContextData{},
			wantErr: false,
		},
		{
			name: "pass args",
			cgi: url.Values{
				"app_version":  []string{"20100300"},
				"app_id":       []string{"ru.yandex.searchplugin"},
				"app_platform": []string{"android"},
			},
			want: inputContextData{
				"cgi.app_version":  "20100300",
				"cgi.app_id":       "ru.yandex.searchplugin",
				"cgi.app_platform": "android",
			},
			wantErr: false,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			requestGetterMock := NewMockrequestGetter(ctrl)
			requestGetterMock.EXPECT().GetRequest().Return(models.Request{CGI: tt.cgi})
			option := WithCGIArgs(requestGetterMock)

			context := inputContext{
				data: make(inputContextData),
			}
			err := option(&context)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}

			assert.Equal(t, tt.want, context.data)
		})
	}
}

func TestNewInputContext(t *testing.T) {
	type testCase struct {
		name string

		device       models.Device
		request      models.Request
		mordaContent models.MordaContent
		domain       models.MordaZone

		want inputContextData
	}
	testCases := []testCase{
		{
			name: "query from SearchApp",
			request: models.Request{
				CGI: url.Values{
					"app_version":       {"15111992"},
					"app_id":            {"superapp"},
					"app_platform":      {"iphone"},
					"app_build_version": {"15111992000"},
					"some_other_arg":    {"value"},
					"ab_flags":          {"k1=v1:k2=v2"},
				},
			},
			mordaContent: models.MordaContent{
				Value: "touch",
			},
			domain: models.MordaZone{
				Value: "ru",
			},
			device: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: map[string]string{
						"OSFamily":       "ios",
						"BrowserName":    "Yandex SuperApp",
						"SomeOtherTrait": "yes",
					},
				},
			},
			want: inputContextData{
				"cgi.app_version":       "15111992",
				"cgi.app_id":            "superapp",
				"cgi.app_platform":      "iphone",
				"cgi.app_build_version": "15111992000",
				"cgi.some_other_arg":    "value",
				"cgi.ab_flags":          "k1=v1:k2=v2",
				"content":               "touch",
				"desktop":               "0",
				"touch":                 "1",
				"device.OSFamily":       "ios",
				"device.BrowserName":    "Yandex SuperApp",
				"device.SomeOtherTrait": "yes",
				"tld":                   "ru",
			},
		},
		{
			name: "query from touch",
			request: models.Request{
				CGI: url.Values{
					"clid":     {"123456"},
					"ab_flags": {"k1=v1:k2=v2"},
				},
			},
			mordaContent: models.MordaContent{
				Value: "touch",
			},
			domain: models.MordaZone{
				Value: "ru",
			},
			device: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: map[string]string{
						"OSFamily":       "ios",
						"BrowserName":    "Safari",
						"SomeOtherTrait": "yes",
					},
				},
			},
			want: inputContextData{
				"cgi.clid":              "123456",
				"cgi.ab_flags":          "k1=v1:k2=v2",
				"content":               "touch",
				"desktop":               "0",
				"touch":                 "1",
				"device.OSFamily":       "ios",
				"device.BrowserName":    "Safari",
				"device.SomeOtherTrait": "yes",
				"tld":                   "ru",
			},
		},
		{
			name: "query from desktop",
			request: models.Request{
				CGI: url.Values{
					"clid":     {"123456"},
					"ab_flags": {"k1=v1:k2=v2"},
				},
			},
			mordaContent: models.MordaContent{
				Value: "big",
			},
			domain: models.MordaZone{
				Value: "ru",
			},
			device: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: map[string]string{
						"OSFamily":    "Windows",
						"BrowserName": "Edge",
					},
				},
			},
			want: inputContextData{
				"cgi.clid":           "123456",
				"cgi.ab_flags":       "k1=v1:k2=v2",
				"content":            "big",
				"desktop":            "1",
				"touch":              "0",
				"device.OSFamily":    "Windows",
				"device.BrowserName": "Edge",
				"tld":                "ru",
			},
		},
	}

	for _, tt := range testCases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			deviceGetter := NewMockdeviceGetter(ctrl)
			deviceGetter.EXPECT().GetDevice().Return(tt.device).Times(1)

			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(tt.request)

			mordazoneGetter := NewMockmordaZoneGetter(ctrl)
			mordazoneGetter.EXPECT().GetMordaZone().Return(tt.domain)

			mordaContentGetter := NewMockmordaContentGetter(ctrl)
			mordaContentGetter.EXPECT().GetMordaContent().Return(tt.mordaContent)

			actual, err := NewInputContext(WithCGIArgs(requestGetter), WithUATraits(deviceGetter),
				WithMordaContent(mordaContentGetter), WithMordaZone(mordazoneGetter))
			require.NoError(t, err)
			require.NotNil(t, actual)
			assert.Equal(t, tt.want, actual.data)
		})
	}
}

func TestGetMissedKeys(t *testing.T) {
	testCases := []struct {
		keys     map[string]string
		action   func(*inputContext)
		expected []string
		caseName string
	}{
		{
			keys: map[string]string{
				"int_flag":    "42",
				"bool_flag":   "1",
				"string_flag": "apple",
			},
			action: func(context *inputContext) {
				_ = context.GetBool("bool_flag")
				_, _ = context.GetInteger("int_flag")
				_ = context.GetString("string_flag")
			},
			expected: []string{},
			caseName: "all keys are presented",
		},
		{
			keys: map[string]string{
				"int_flag":    "42",
				"bool_flag":   "1",
				"string_flag": "apple",
			},
			action: func(context *inputContext) {
				_ = context.GetBool("bool_flag")
				_, _ = context.GetInteger("int_flag")
				_ = context.GetString("string_flag")
				_ = context.GetString("missed_key")
			},
			expected: []string{"missed_key"},
			caseName: "one key is missed",
		},
		{
			keys: map[string]string{
				"flag": "42",
			},
			action: func(context *inputContext) {
				_ = context.GetBool("B")
				_, _ = context.GetInteger("I")
				_ = context.GetString("S")
				_ = context.HasKey("Z")
			},
			expected: []string{"B", "I", "S", "Z"},
			caseName: "all keys are missed",
		},
		{
			keys: map[string]string{
				"flag": "42",
			},
			action: func(context *inputContext) {
				_ = context.GetBool("C")
				_, _ = context.GetInteger("C")
				_ = context.GetString("B")
				_ = context.HasKey("B")
			},
			expected: []string{"B", "C"},
			caseName: "duplicated keys",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			actual, err := NewInputContext()
			require.NoError(t, err)
			require.NotNil(t, actual)
			actual.data = testCase.keys

			testCase.action(actual)

			assert.Equal(t, testCase.expected, actual.GetMissedKeys())
		})
	}
}

func Test_inputContext_addMissedKey(t *testing.T) {
	type args struct {
		key string
	}

	tests := []struct {
		name string
		args args
		want common.StringSet
	}{
		{
			name: "device key",
			args: args{
				key: "device.test",
			},
			want: common.NewStringSet(),
		},
		{
			name: "cgi key",
			args: args{
				key: "cgi.test",
			},
			want: common.NewStringSet(),
		},
		{
			name: "random key",
			args: args{
				key: "test",
			},
			want: common.NewStringSet("test"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctx := &inputContext{
				missedKeys: common.NewStringSet(),
			}

			ctx.addMissedKey(tt.args.key)
			assert.Equal(t, tt.want, ctx.missedKeys)
		})
	}
}
