package robot

import (
	"net/http"
	"testing"

	"github.com/golang/mock/gomock"
	lru "github.com/hashicorp/golang-lru"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/uatraits"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_parser_getByUATraits(t *testing.T) {

	tests := []struct {
		name   string
		traits uatraits.Traits
		want   bool
	}{
		{
			name: "isRobot true",
			traits: map[string]string{
				"isRobot": "true",
			},
			want: true,
		},
		{
			name: "isRobot not true",
			traits: map[string]string{
				"isRobot": "not true",
			},
			want: false,
		},
		{
			name:   "isRobot not set",
			traits: map[string]string{},
			want:   false,
		},
		{
			name:   "isRobot not set",
			traits: nil,
			want:   false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := parser{}
			got := p.getByUATraits(tt.traits)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_parser_getByHeaders(t *testing.T) {

	tests := []struct {
		name    string
		headers http.Header
		want    bool
	}{
		{
			name:    "empty header",
			headers: map[string][]string{},
			want:    false,
		},
		{
			name: "X-MOZ prefetch header",
			headers: map[string][]string{
				xmozPrefetchHeader: {"prefetch"},
			},
			want: true,
		},
		{
			name: "X-MOZ not prefetch header",
			headers: map[string][]string{
				xmozPrefetchHeader: {"other"},
			},
			want: false,
		},
		{
			name: "robotness more than 0 header",
			headers: map[string][]string{
				antirobotHeader: {"0.2"},
			},
			want: true,
		},
		{
			name: "robotness is 0 header",
			headers: map[string][]string{
				antirobotHeader: {"0.0"},
			},
			want: false,
		},
		{
			name: "robotness is not float header",
			headers: map[string][]string{
				antirobotHeader: {"xxx"},
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			h := http.Header{}
			for key, value := range tt.headers {
				for _, v := range value {
					h.Add(key, v)
				}
			}
			got := p.getByHeaders(h)
			assert.Equal(t, got, tt.want)
		})
	}
}

func Test_parser_getByUserAgent(t *testing.T) {

	tests := []struct {
		name      string
		userAgent string
		want      bool
	}{
		{
			name:      "empty ua",
			userAgent: "",
			want:      true,
		},
		{
			name:      "Mozilla/5.1",
			userAgent: "Mozilla/5.1",
			want:      true,
		},
		{
			name:      "googlebot",
			userAgent: "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/W.X.Y.Z Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
			want:      true,
		},
		{
			name:      "bingbot",
			userAgent: "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
			want:      true,
		},
		{
			name:      "okhttp",
			userAgent: "okhttp/4.9.3",
			want:      true,
		},
		{
			name:      "Dart",
			userAgent: "Dart/2.17 (dart:io)",
			want:      true,
		},
		{
			name:      "casual user agent",
			userAgent: "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET4.0C)",
			want:      false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			got := p.getByUserAgent(tt.userAgent)
			assert.Equal(t, got, tt.want)
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	type fields struct {
		originRequest      *models.OriginRequest
		originRequestError error

		device models.Device
	}
	tests := []struct {
		name    string
		fields  fields
		want    models.Robot
		wantErr bool
	}{
		{
			name: "casual situation with standart User Agent",
			fields: fields{
				originRequest: &models.OriginRequest{},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						UserAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
					},
				},
			},
			want:    models.Robot{IsRobot: false},
			wantErr: false,
		},
		{
			name: "robot by Header X-MOZ",
			fields: fields{
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"X-Moz": {"prefetch"},
					},
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						UserAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
					},
				},
			},
			want:    models.Robot{IsRobot: true},
			wantErr: false,
		},
		{
			name: "robot by UserAgent",
			fields: fields{
				originRequest: &models.OriginRequest{},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						UserAgent: "Dart/2.17 (dart:io)",
					},
				},
			},
			want:    models.Robot{IsRobot: true},
			wantErr: false,
		},
		{
			name: "robot by uatraits",
			fields: fields{
				originRequest: &models.OriginRequest{},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{
							"isRobot": "true",
						},
						UserAgent: "not empty",
					},
				},
			},
			want:    models.Robot{IsRobot: true},
			wantErr: false,
		},
		{
			name: "robot by all",
			fields: fields{
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"X-Moz": {"prefetch"},
					},
				},
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{
							"isRobot": "true",
						},
						UserAgent: "Dart/2.17 (dart:io)",
					},
				},
			},
			want:    models.Robot{IsRobot: true},
			wantErr: false,
		},
		{
			name: "got error, but robot by traits",
			fields: fields{
				originRequest: &models.OriginRequest{
					Headers: map[string][]string{
						"X-Moz": {"prefetch"},
					},
				},
				originRequestError: assert.AnError,
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{
							"isRobot": "true",
						},
						UserAgent: "not empty",
					},
				},
			},
			want:    models.Robot{IsRobot: true},
			wantErr: true,
		},
		{
			name: "nil origin request",
			fields: fields{
				originRequest:      nil,
				originRequestError: assert.AnError,
				device: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{
							"isRobot": "true",
						},
						UserAgent: "not empty",
					},
				},
			},
			want:    models.Robot{IsRobot: true},
			wantErr: true,
		},

		{
			name: "all is nil",
			fields: fields{
				originRequest:      nil,
				originRequestError: assert.AnError,
				device: models.Device{
					BrowserDesc: nil,
				},
			},
			want:    models.Robot{IsRobot: false},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			originRequestKeeperMock := NewMockoriginRequestKeeper(ctrl)
			originRequestKeeperMock.EXPECT().GetOriginRequest().Return(tt.fields.originRequest, tt.fields.originRequestError).MaxTimes(1)
			deviceGetterMock := NewMockdeviceGetter(ctrl)
			deviceGetterMock.EXPECT().GetDevice().Return(tt.fields.device).MaxTimes(1)
			cache, err := lru.New(1)
			require.NoError(t, err)

			p := &parser{
				originRequestKeeper: originRequestKeeperMock,
				deviceGetter:        deviceGetterMock,

				cache: cache,
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
