package laas

import (
	"net/http"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	gb "a.yandex-team.ru/library/go/yandex/geobase"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
)

func Test_fallBacker_GetRegionID(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		ip      string
		headers http.Header
		gpAuto  string
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    int
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					input := gb.GeolocationInput{
						IP:            "127.0.0.1",
						YandexGID:     -1,
						IsTrusted:     true,
						XForwardedFor: "192.168.0.1",
						AllowYandex:   false,
					}

					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().MakePinpointGeolocation(input, "", gomock.Any()).Return(gb.Geolocation{
						RegionID: 213,
					}, nil)
					return geoBase
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Forwarded-For": {"192.168.0.1"},
				},
			},
			want:    213,
			wantErr: assert.NoError,
		},
		{
			name: "success with coordinates",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					input := gb.GeolocationInput{
						IP:            "127.0.0.1",
						YandexGID:     -1,
						IsTrusted:     true,
						XForwardedFor: "192.168.0.1",
						GpAuto:        "1:2:85:0:1643672808",
						AllowYandex:   false,
					}

					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().MakePinpointGeolocation(input, "", gomock.Any()).Return(gb.Geolocation{
						RegionID: 213,
					}, nil)
					return geoBase
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Forwarded-For": {"192.168.0.1"},
				},
				gpAuto: "1:2:85:0:1643672808",
			},
			want:    213,
			wantErr: assert.NoError,
		},
		{
			name: "make pinpoint geo location failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					input := gb.GeolocationInput{
						IP:            "127.0.0.1",
						YandexGID:     -1,
						IsTrusted:     true,
						XForwardedFor: "192.168.0.1",
						GpAuto:        "1:2:85:0:1643672808",
						AllowYandex:   false,
					}

					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().MakePinpointGeolocation(input, "", gomock.Any()).
						Return(gb.Geolocation{}, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Forwarded-For": {"192.168.0.1"},
				},
				gpAuto: "1:2:85:0:1643672808",
			},
			want:    0,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			f := &fallBacker{
				geoBase: tt.fields.createGeoBase(t),
			}

			got, err := f.GetRegionID(tt.args.ip, tt.args.headers, tt.args.gpAuto)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}
