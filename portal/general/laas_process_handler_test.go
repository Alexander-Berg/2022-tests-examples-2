package geo

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/laas"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
)

func Test_laasProcessHandler_getLAASRegionID(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		laasResponse *laas.Response
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    int
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get laas city id success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(213).Return(true)
					resolver.EXPECT().ResolveRegionID(213).Return(213, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
			},
			want:    213,
			wantErr: assert.NoError,
		},
		{
			name: "get laas city id failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(213).Return(true)
					resolver.EXPECT().ResolveRegionID(213).Return(0, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
			},
			want:    0,
			wantErr: assert.Error,
		},
		{
			name: "get laas region by ip id success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(213).Return(false)
					resolver.EXPECT().HasRegion(111).Return(true)
					resolver.EXPECT().ResolveRegionID(111).Return(111, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID:     213,
					RegionByIP: 111,
				},
			},
			want:    111,
			wantErr: assert.NoError,
		},
		{
			name: "get laas region by ip failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(213).Return(false)
					resolver.EXPECT().HasRegion(111).Return(true)
					resolver.EXPECT().ResolveRegionID(111).Return(0, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID:     213,
					RegionByIP: 111,
				},
			},
			want:    0,
			wantErr: assert.Error,
		},
		{
			name: "no region",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(213).Return(false)
					resolver.EXPECT().HasRegion(111).Return(false)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID:     213,
					RegionByIP: 111,
				},
			},
			want:    0,
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &laasProcessHandler{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			got, err := g.getLAASRegionID(tt.args.laasResponse)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_laasProcessHandler_processLAASResponse(t *testing.T) {
	type fields struct {
		createHandler     func(t *testing.T) *Mockhandler
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		laasResponse  *laas.Response
		superRegionID int
		smartRegionID int
		coords        coordinates.Coordinates
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get laas region id failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(0, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "laas zero id",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(false).Times(2)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID:     213,
					RegionByIP: 213,
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "process region with coordinates",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().ProcessRegion(gomock.Any(), gomock.Any(), gomock.Any(), coordinates.Coordinates{
						Latitude:  1,
						Longitude: 2,
					}).Return(true, nil)
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(213, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
				smartRegionID: 213,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "process region without coordinates",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().ProcessRegion(gomock.Any(), gomock.Any(), gomock.Any(), coordinates.Coordinates{}).
						Return(true, nil)
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(213, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
				smartRegionID: 111,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "process region failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().ProcessRegion(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(false, errors.Error("error"))
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(213, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
				smartRegionID: 111,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "process geo by super region",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().ProcessRegion(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(false, nil)
					handler.EXPECT().ProcessGeo(gomock.Any(), 222, gomock.Any()).Return(nil)
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(213, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
				superRegionID: 222,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "process geo by laas region",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().ProcessRegion(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(false, nil)
					handler.EXPECT().ProcessGeo(gomock.Any(), 213, gomock.Any()).Return(nil)
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(213, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "process geo failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().ProcessRegion(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(false, nil)
					handler.EXPECT().ProcessGeo(gomock.Any(), gomock.Any(), gomock.Any()).Return(errors.Error("error"))
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(213, nil)
					return resolver
				},
			},
			args: args{
				laasResponse: &laas.Response{
					CityID: 213,
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := &laasProcessHandler{
				handler:     tt.fields.createHandler(t),
				geoResolver: tt.fields.createGeoResolver(t),
			}

			tt.wantErr(t, l.processLAASResponse(nil, tt.args.laasResponse, tt.args.superRegionID, tt.args.smartRegionID, tt.args.coords))
		})
	}
}

func Test_laasProcessHandler_handle(t *testing.T) {
	type fields struct {
		createHandler          func(t *testing.T) *Mockhandler
		createGeoResolver      func(t *testing.T) *MockgeoResolver
		createGeoRequestParser func(t *testing.T) *MockgeoRequestParser
	}

	type args struct {
		createContext func(t *testing.T) *Mockcontext
		baseCtx       *mocks.Base
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get laas response failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLAASResponse().Return(nil, errors.Error("error"))
					return ctx
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "empty laas response",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLAASResponse().Return(nil, nil)
					return ctx
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "process laas response failed",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().GetCoordinates(gomock.Any(), gomock.Any()).Return(coordinates.Coordinates{
						Latitude:  1,
						Longitude: 2,
					}, nil)
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(0, errors.Error("error"))
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseSmartRegionID(gomock.Any()).Return(0)
					geoRequestParser.EXPECT().ParseSuperRegionID(gomock.Any()).Return(0)
					geoRequestParser.EXPECT().ParsePumpkinRegionID(gomock.Any()).Return(0)
					return geoRequestParser
				},
			},
			args: args{
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					return ctx
				}(),
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLAASResponse().Return(&laas.Response{
						CityID: 213,
					}, nil)
					return ctx
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "process laas response success",
			fields: fields{
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().GetCoordinates(gomock.Any(), gomock.Any()).Return(coordinates.Coordinates{
						Latitude:  1,
						Longitude: 2,
					}, nil)
					handler.EXPECT().ProcessRegion(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).Return(false, nil)
					handler.EXPECT().ProcessGeo(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil)
					return handler
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().HasRegion(gomock.Any()).Return(true)
					resolver.EXPECT().ResolveRegionID(gomock.Any()).Return(213, nil)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseSmartRegionID(gomock.Any()).Return(0)
					geoRequestParser.EXPECT().ParseSuperRegionID(gomock.Any()).Return(0)
					geoRequestParser.EXPECT().ParsePumpkinRegionID(gomock.Any()).Return(0)
					return geoRequestParser
				},
			},
			args: args{
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					return ctx
				}(),
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLAASResponse().Return(&laas.Response{
						CityID: 213,
					}, nil)
					return ctx
				},
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := &laasProcessHandler{
				handler:          tt.fields.createHandler(t),
				geoResolver:      tt.fields.createGeoResolver(t),
				geoRequestParser: tt.fields.createGeoRequestParser(t),
			}

			ctx := tt.args.createContext(t)

			tt.wantErr(t, l.handle(ctx, tt.args.baseCtx))
		})
	}
}
