package gpauto

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
	"a.yandex-team.ru/portal/avocado/libs/utils/pointer"
)

func TestConvertFromCoordinates(t *testing.T) {
	type args struct {
		coords     coordinates.Coordinates
		isFallback bool
	}

	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "empty coords",
			args: args{
				coords: coordinates.Coordinates{},
			},
			want: "",
		},
		{
			name: "generate gpuato",
			args: args{
				coords: coordinates.Coordinates{
					Latitude:  1.0,
					Longitude: 2.0,
					Accuracy:  pointer.NewFloat64(10),
					Recency:   pointer.NewInt(20),
				},
				isFallback: false,
			},
			want: "1:2:10:0:1643302525",
		},
		{
			name: "generate gpuato fallback",
			args: args{
				coords: coordinates.Coordinates{
					Latitude:  1.0,
					Longitude: 2.0,
					Accuracy:  pointer.NewFloat64(9.9),
					Recency:   pointer.NewInt(20),
				},
				isFallback: true,
			},
			want: "1:2:3_3000000000000003:0:1643302525",
		},
		{
			name: "generate gpuato default accuracy",
			args: args{
				coords: coordinates.Coordinates{
					Latitude:  1.0,
					Longitude: 2.0,
					Recency:   pointer.NewInt(20),
				},
				isFallback: false,
			},
			want: "1:2:85:0:1643302525",
		},
		{
			name: "generate gpuato default recency",
			args: args{
				coords: coordinates.Coordinates{
					Latitude:  1.0,
					Longitude: 2.0,
					Accuracy:  pointer.NewFloat64(10),
				},
				isFallback: false,
			},
			want: "1:2:10:0:1643302515",
		},
	}

	unixTime := time.Unix(1643302525, 0).Unix()

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ConvertFromCoordinates(tt.args.coords, unixTime, tt.args.isFallback)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestNewFromYaCookie(t *testing.T) {
	type args struct {
		yaCookie models.YaCookies
	}

	tests := []struct {
		name    string
		args    args
		want    *GpAuto
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "parse from ys",
			args: args{
				yaCookie: models.YaCookies{
					Ys: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "1:2:10:0:1643302525",
							},
						},
					},
				},
			},
			want: &GpAuto{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  10,
				Device:    0,
				Age:       1643302525,
			},
			wantErr: assert.NoError,
		},
		{
			name: "parse from yp",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "1:2:10:0:1643302525",
							},
						},
					},
				},
			},
			want: &GpAuto{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  10,
				Device:    0,
				Age:       1643302525,
			},
			wantErr: assert.NoError,
		},
		{
			name: "no value",
			args: args{
				yaCookie: models.YaCookies{},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "invalid latitude value",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "abc:2:10:0:1643302525",
							},
						},
					},
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "invalid longitude value",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "1:abc:10:0:1643302525",
							},
						},
					},
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "invalid accuracy value",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "1:2:abc:0:1643302525",
							},
						},
					},
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "invalid device value",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "1:2:10:abc:1643302525",
							},
						},
					},
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "invalid age value",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "1:2:10:0:abc",
							},
						},
					},
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "invalid signature",
			args: args{
				yaCookie: models.YaCookies{
					Yp: models.YCookie{
						Subcookies: map[string]models.YSubcookie{
							"gpauto": {
								Name:  "gpauto",
								Value: "1:2:10:0:1643302525:1643302525",
							},
						},
					},
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := NewFromYaCookie(tt.args.yaCookie)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func TestGpAuto_ProcessCoordinates(t *testing.T) {
	type fields struct {
		Lat      float64
		Lon      float64
		Accuracy float64
		Device   int
		Age      int64
	}

	type args struct {
		coords   coordinates.Coordinates
		unixTime int64
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   coordinates.Coordinates
	}{
		{
			name: "check coordinates max accuracy failed",
			fields: fields{
				Lat:      1,
				Lon:      2,
				Accuracy: coordinates.MaxAccuracy + 1,
			},
			args: args{
				coords: coordinates.Coordinates{
					Latitude:  3,
					Longitude: 4,
				},
				unixTime: 1643672818,
			},
			want: coordinates.Coordinates{
				Latitude:  3,
				Longitude: 4,
			},
		},
		{
			name: "check age failed",
			fields: fields{
				Lat:      1,
				Lon:      2,
				Accuracy: 1000,
				Age:      1000,
			},
			args: args{
				coords: coordinates.Coordinates{
					Latitude:  3,
					Longitude: 4,
					Recency: func() *int {
						value := 1643672818 - 100
						return &value
					}(),
				},
				unixTime: 1643672818,
			},
			want: coordinates.Coordinates{
				Latitude:  3,
				Longitude: 4,
				Recency: func() *int {
					value := 1643672818 - 100
					return &value
				}(),
			},
		},
		{
			name: "check diff failed",
			fields: fields{
				Lat:      1,
				Lon:      2,
				Accuracy: 1000,
				Age:      1000,
			},
			args: args{
				coords: coordinates.Coordinates{
					Latitude:  3,
					Longitude: 4,
					Recency: func() *int {
						value := 1643672818 - 2000
						return &value
					}(),
				},
				unixTime: 1643672818,
			},
			want: coordinates.Coordinates{},
		},
		{
			name: "success",
			fields: fields{
				Lat:      1,
				Lon:      2,
				Accuracy: 1000,
				Age:      1000,
			},
			args: args{
				coords:   coordinates.Coordinates{},
				unixTime: 1643672818,
			},
			want: coordinates.Coordinates{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  pointer.NewFloat64(1000),
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &GpAuto{
				Latitude:  tt.fields.Lat,
				Longitude: tt.fields.Lon,
				Accuracy:  tt.fields.Accuracy,
				Device:    tt.fields.Device,
				Age:       tt.fields.Age,
			}
			assert.Equal(t, tt.want, g.ProcessCoordinates(tt.args.coords, tt.args.unixTime))
		})
	}
}
