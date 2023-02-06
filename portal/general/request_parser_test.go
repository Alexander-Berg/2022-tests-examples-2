package parser

import (
	"net/http"
	"net/url"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/lbs"
	"a.yandex-team.ru/portal/avocado/libs/utils/pointer"
)

func Test_requestParser_getGoodRegion(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		name string
		cgi  url.Values
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   int
	}{
		{
			name: "success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(gomock.Any()).Return(true)
					return resolver
				},
			},
			args: args{
				name: "test",
				cgi: map[string][]string{
					"test": {"213"},
				},
			},
			want: 213,
		},
		{
			name: "failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(gomock.Any()).Return(false)
					return resolver
				},
			},
			args: args{
				name: "test",
				cgi: map[string][]string{
					"test": {"213"},
				},
			},
			want: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestParser{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			got := r.getGoodRegion(tt.args.name, tt.args.cgi)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestParser_ParsePumpkinRegionID(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		headers http.Header
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   int
	}{
		{
			name: "success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(213).Return(true)
					return resolver
				},
			},
			args: args{
				headers: http.Header{
					"X-Yandex-Morda-Pumpkin-Geo": {"213"},
				},
			},
			want: 213,
		},
		{
			name: "empty headers",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(0).Return(true)
					return resolver
				},
			},
			args: args{
				headers: http.Header{},
			},
			want: 0,
		},
		{
			name: "has not region",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(213).Return(false)
					return resolver
				},
			},
			args: args{
				headers: http.Header{
					"X-Yandex-Morda-Pumpkin-Geo": {"213"},
				},
			},
			want: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestParser{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			got := r.ParsePumpkinRegionID(tt.args.headers)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestParser_GetCoordinates(t *testing.T) {
	type fields struct {
		createCoordinatesParser func(t *testing.T) *MockcoordinatesParser
	}

	type args struct {
		cgi         url.Values
		lbsLocation *lbs.Location
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    coordinates.Coordinates
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get lbs from location",
			fields: fields{
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					return nil
				},
			},
			args: args{
				lbsLocation: &lbs.Location{
					Found:     true,
					Latitude:  1,
					Longitude: 2,
					Radius:    20000,
				},
			},
			want: coordinates.Coordinates{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  pointer.NewFloat64(20000),
				Recency:   pointer.NewInt(60000),
			},
			wantErr: assert.NoError,
		},
		{
			name: "get from cgi and nil lbs location",
			fields: fields{
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					parser := NewMockcoordinatesParser(gomock.NewController(t))
					parser.EXPECT().Parse(gomock.Any()).Return(coordinates.Coordinates{
						Latitude:  1,
						Longitude: 2,
					})
					return parser
				},
			},
			args: args{
				lbsLocation: nil,
				cgi: map[string][]string{
					"latitude":  {"1"},
					"longitude": {"2"},
				},
			},
			want: coordinates.Coordinates{
				Latitude:  1,
				Longitude: 2,
			},
			wantErr: assert.NoError,
		},
		{
			name: "get from cgi and nil lbs location not found",
			fields: fields{
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					parser := NewMockcoordinatesParser(gomock.NewController(t))
					parser.EXPECT().Parse(gomock.Any()).Return(coordinates.Coordinates{
						Latitude:  1,
						Longitude: 2,
					})
					return parser
				},
			},
			args: args{
				lbsLocation: &lbs.Location{
					Found: false,
				},
				cgi: map[string][]string{
					"latitude":  {"1"},
					"longitude": {"2"},
				},
			},
			want: coordinates.Coordinates{
				Latitude:  1,
				Longitude: 2,
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestParser{
				coordinatesParser: tt.fields.createCoordinatesParser(t),
			}

			got := r.GetCoordinates(tt.args.cgi, tt.args.lbsLocation)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestParser_ParseRegion(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		smartRegionID int
		superRegionID int
		coordinates   coordinates.Coordinates
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "empty smart region",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
			},
			args: args{
				smartRegionID: 0,
			},
			want:    nil,
			wantErr: assert.NoError,
		},
		{
			name: "resolve smart region",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(111, gomock.Any()).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return resolver
				},
			},
			args: args{
				smartRegionID: 111,
				superRegionID: 0,
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want: &models.Geo{
				RegionID: 111,
			},
			wantErr: assert.NoError,
		},
		{
			name: "resolve super region",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(222, gomock.Any()).Return(&models.Geo{
						RegionID: 222,
					}, nil)
					return resolver
				},
			},
			args: args{
				smartRegionID: 111,
				superRegionID: 222,
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want: &models.Geo{
				RegionID: 222,
			},
			wantErr: assert.NoError,
		},
		{
			name: "resolve geo failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(222, gomock.Any()).Return(nil, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				smartRegionID: 111,
				superRegionID: 222,
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestParser{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			got, err := r.ParseRegion(tt.args.smartRegionID, tt.args.superRegionID, tt.args.coordinates)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}
