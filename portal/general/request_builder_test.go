package bigb

import (
	"testing"

	"github.com/golang/protobuf/proto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	protobigb "a.yandex-team.ru/ads/bsyeti/eagle/collect/proto"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func TestBuildRequest(t *testing.T) {
	tests := []struct {
		name string

		auth      models.Auth
		appInfo   models.AppInfo
		yaCookies models.YaCookies

		want *protobigb.TQueryParams

		shouldError bool
		errMsg      string
	}{
		{
			name: "nil",

			auth:      models.Auth{},
			appInfo:   models.AppInfo{},
			yaCookies: models.YaCookies{},

			want: nil,

			shouldError: true,
			errMsg:      "bigbUID or puid or uuid is required",
		},
		{
			name: "auth.UID is defined",

			auth: models.Auth{
				UID: "123",
			},
			appInfo:   models.AppInfo{},
			yaCookies: models.YaCookies{},

			want: &protobigb.TQueryParams{
				Puid: proto.Uint64(123),

				Clients: []*protobigb.TClient{
					{
						Name:   proto.String("morda"),
						Format: proto.String("protobuf"),
					},
				},
			},

			shouldError: false,
		},
		{
			name: "appInfo.UUID is defined",

			auth: models.Auth{},
			appInfo: models.AppInfo{
				UUID: "1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a",
			},
			yaCookies: models.YaCookies{},

			want: &protobigb.TQueryParams{
				Uuid: proto.String("1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"),

				Clients: []*protobigb.TClient{
					{
						Name:   proto.String("morda"),
						Format: proto.String("protobuf"),
					},
				},
			},

			shouldError: false,
		},
		{
			name: "appInfo.UUID is defined",

			auth: models.Auth{},
			appInfo: models.AppInfo{
				UUID: "0",
			},
			yaCookies: models.YaCookies{},

			want: nil,

			shouldError: true,
			errMsg:      "bigbUID or puid or uuid is required",
		},
		{
			name: "yaCookies.YandexUID is defined",

			auth:    models.Auth{},
			appInfo: models.AppInfo{},
			yaCookies: models.YaCookies{
				YandexUID: "789",
			},

			want: &protobigb.TQueryParams{
				BigbUid: &[]uint64{789}[0],

				Clients: []*protobigb.TClient{
					{
						Name:   proto.String("morda"),
						Format: proto.String("protobuf"),
					},
				},
			},

			shouldError: false,
		},
		{
			name: "auth.UID and appInfo.UUID is defined",

			auth: models.Auth{
				UID: "123",
			},
			appInfo: models.AppInfo{
				UUID: "1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a",
			},
			yaCookies: models.YaCookies{},

			want: &protobigb.TQueryParams{
				Puid: proto.Uint64(123),
				Uuid: proto.String("1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"),

				Clients: []*protobigb.TClient{
					{
						Name:   proto.String("morda"),
						Format: proto.String("protobuf"),
					},
				},
			},

			shouldError: false,
		},
		{
			name: "auth.UID and yaCookies.YandexUID is defined",

			auth: models.Auth{
				UID: "123",
			},
			appInfo: models.AppInfo{},
			yaCookies: models.YaCookies{
				YandexUID: "789",
			},

			want: &protobigb.TQueryParams{
				Puid:    proto.Uint64(123),
				BigbUid: proto.Uint64(789),

				Clients: []*protobigb.TClient{
					{
						Name:   proto.String("morda"),
						Format: proto.String("protobuf"),
					},
				},
			},

			shouldError: false,
		},
		{
			name: "appInfo.UUID and yaCookies.YandexUID is defined",

			auth: models.Auth{},
			appInfo: models.AppInfo{
				UUID: "1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a",
			},
			yaCookies: models.YaCookies{
				YandexUID: "789",
			},

			want: &protobigb.TQueryParams{
				Uuid:    proto.String("1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"),
				BigbUid: proto.Uint64(789),

				Clients: []*protobigb.TClient{
					{
						Name:   proto.String("morda"),
						Format: proto.String("protobuf"),
					},
				},
			},

			shouldError: false,
		},
		{
			name: "auth.UID and appInfo.UUID and yaCookies.YandexUID is defined",

			auth: models.Auth{
				UID: "123",
			},
			appInfo: models.AppInfo{
				UUID: "1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a",
			},
			yaCookies: models.YaCookies{
				YandexUID: "789",
			},

			want: &protobigb.TQueryParams{
				Puid:    proto.Uint64(123),
				Uuid:    proto.String("1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"),
				BigbUid: proto.Uint64(789),

				Clients: []*protobigb.TClient{
					{
						Name:   proto.String("morda"),
						Format: proto.String("protobuf"),
					},
				},
			},

			shouldError: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := requestBuilder{}
			actual, err := r.BuildRequest(tt.auth, tt.appInfo, tt.yaCookies, log3.NewLoggerStub())
			if tt.shouldError {
				require.EqualError(t, err, tt.errMsg)
			} else {
				require.NoError(t, err)
			}
			assert.Equal(t, actual, tt.want)
		})
	}
}
