package laas

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/gpauto"
	"a.yandex-team.ru/portal/avocado/libs/utils/pointer"
)

func Test_parser_parseLocation(t *testing.T) {
	type args struct {
		locationString string
	}
	tests := []struct {
		name string
		args args
		want coordinates.Coordinates
	}{
		{
			name: "success",
			args: args{
				locationString: "55, 37, 42, 1602496863",
			},
			want: coordinates.Coordinates{
				Latitude:  55,
				Longitude: 37,
				Accuracy:  pointer.NewFloat64(42),
				Recency:   pointer.NewInt(1602496863),
			},
		},
		{
			name: "invalid parts count",
			args: args{
				locationString: "55, 37, 42, 1602496863, 123",
			},
			want: coordinates.Coordinates{},
		},
		{
			name: "invalid recency",
			args: args{
				locationString: "55, 37, 42, 0",
			},
			want: coordinates.Coordinates{},
		},
		{
			name: "invalid accuracy",
			args: args{
				locationString: "55, 37, 0, 1602496863",
			},
			want: coordinates.Coordinates{},
		},
		{
			name: "invalid max accuracy",
			args: args{
				locationString: "55, 37, 3000, 1602496863",
			},
			want: coordinates.Coordinates{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			assert.Equal(t, tt.want, p.parseLocation(tt.args.locationString))
		})
	}
}

func Test_parser_Parse(t *testing.T) {
	type args struct {
		headers  http.Header
		gpAuto   *gpauto.GpAuto
		unixTime int64
	}

	tests := []struct {
		name    string
		args    args
		want    *Response
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "empty x-laas-answered",
			args: args{
				headers:  make(map[string][]string),
				unixTime: 1602496863,
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "success",
			args: args{
				headers: map[string][]string{
					"X-Laas-Answered":  {"1"},
					"X-Region-City-Id": {"213"},
				},
				unixTime: 1602496863,
			},
			want: &Response{
				CityID: 213,
			},
			wantErr: assert.NoError,
		},
		{
			name: "success",
			args: args{
				headers: map[string][]string{
					"X-Laas-Answered":  {"1"},
					"X-Region-City-Id": {"213"},
					"X-Region-By-Ip":   {"123"},
				},
				unixTime: 1602496863,
			},
			want: &Response{
				CityID:     213,
				RegionByIP: 123,
			},
			wantErr: assert.NoError,
		},
		{
			name: "success with coordinates",
			args: args{
				headers: map[string][]string{
					"X-Laas-Answered":   {"1"},
					"X-Region-City-Id":  {"213"},
					"X-Region-By-Ip":    {"123"},
					"X-Region-Location": {"55, 37, 42, 1602496863"},
				},
				unixTime: 1602496863,
			},
			want: &Response{
				CityID:     213,
				RegionByIP: 123,
				Latitude:   55,
				Longitude:  37,
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			got, err := p.Parse(tt.args.headers, tt.args.gpAuto, tt.args.unixTime)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}
