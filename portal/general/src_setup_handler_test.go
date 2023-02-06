package geo

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
)

func Test_geoSrcSetupHandler_setupLBS(t *testing.T) {
	type fields struct {
		createLbsParamsValidator func(t *testing.T) *MocklbsParamsValidator
		createHandler            func(t *testing.T) *Mockhandler
	}
	type args struct {
		createContext func(t *testing.T) *Mockcontext
		request       models.Request
		appInfo       models.AppInfo
		coordinates   coordinates.Coordinates
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    bool
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "lbs validate params failed",
			fields: fields{
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					paramsValidator := NewMocklbsParamsValidator(gomock.NewController(t))
					paramsValidator.EXPECT().Validate(gomock.Any()).Return(false)
					return paramsValidator
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SkipLBS(gomock.Any(), gomock.Any()).Return(false)
					return handler
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				request: models.Request{
					CGI: map[string][]string{
						"wifi": {"1:2:3:4"},
					},
				},
				coordinates: coordinates.Coordinates{},
			},
			want:    false,
			wantErr: assert.NoError,
		},
		{
			name: "not empty coordinates",
			fields: fields{
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				request: models.Request{
					CGI: map[string][]string{
						"wifi": {"1:2:3:4"},
					},
				},
			},
			want:    false,
			wantErr: assert.NoError,
		},
		{
			name: "skip lbs",
			fields: fields{
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SkipLBS(gomock.Any(), gomock.Any()).Return(true)
					return handler
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				coordinates: coordinates.Coordinates{},
				request: models.Request{
					CGI: map[string][]string{
						"wifi": {"1:2:3:4"},
					},
				},
			},
			want:    false,
			wantErr: assert.NoError,
		},
		{
			name: "success",
			fields: fields{
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					paramsValidator := NewMocklbsParamsValidator(gomock.NewController(t))
					paramsValidator.EXPECT().Validate(gomock.Any()).Return(true)
					return paramsValidator
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SkipLBS(gomock.Any(), gomock.Any()).Return(false)
					return handler
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLBSRequest(gomock.Any()).Return(nil)
					return ctx
				},
				request: models.Request{
					CGI: map[string][]string{
						"wifi": {"1:2:3:4"},
					},
				},
				coordinates: coordinates.Coordinates{},
			},
			want:    true,
			wantErr: assert.NoError,
		},
		{
			name: "add lbs request failed",
			fields: fields{
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					paramsValidator := NewMocklbsParamsValidator(gomock.NewController(t))
					paramsValidator.EXPECT().Validate(gomock.Any()).Return(true)
					return paramsValidator
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SkipLBS(gomock.Any(), gomock.Any()).Return(false)
					return handler
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLBSRequest(gomock.Any()).Return(errors.Error("error"))
					return ctx
				},
				request: models.Request{
					CGI: map[string][]string{
						"wifi": {"1:2:3:4"},
					},
				},
				coordinates: coordinates.Coordinates{},
			},
			want:    false,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &srcSetupHandler{
				lbsParamsValidator: tt.fields.createLbsParamsValidator(t),
				handler:            tt.fields.createHandler(t),
			}

			ctx := tt.args.createContext(t)
			got, err := s.setupLBS(ctx, tt.args.request, tt.args.appInfo, tt.args.coordinates)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_srcSetupHandler_handle(t *testing.T) {
	type fields struct {
		createHandler            func(t *testing.T) *Mockhandler
		createLbsParamsValidator func(t *testing.T) *MocklbsParamsValidator
		createGeoResolver        func(t *testing.T) *MockgeoResolver
		createGeoRequestParser   func(t *testing.T) *MockgeoRequestParser
		createCoordinatesParser  func(t *testing.T) *MockcoordinatesParser
		createOptionsGetter      func(t *testing.T) *MockoptionsGetter
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
			name: "disable laas",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					optionsGetter := NewMockoptionsGetter(gomock.NewController(t))
					optionsGetter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							EnableLAASPercentage: 0,
						},
					})
					return optionsGetter
				},
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					return nil
				},
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(nil, errors.Error("error"))
					return ctx
				}(),
			},
			wantErr: assert.NoError,
		},
		{
			name: "get origin request failed",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					optionsGetter := NewMockoptionsGetter(gomock.NewController(t))
					optionsGetter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							EnableLAASPercentage: 100,
						},
					})
					return optionsGetter
				},
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					return nil
				},
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(nil, errors.Error("error"))
					return ctx
				}(),
			},
			wantErr: assert.Error,
		},
		{
			name: "pumpkin region",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					optionsGetter := NewMockoptionsGetter(gomock.NewController(t))
					optionsGetter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							EnableLAASPercentage: 100,
						},
					})
					return optionsGetter
				},
				createHandler: func(t *testing.T) *Mockhandler {
					return nil
				},
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(213).Return(true)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParsePumpkinRegionID(gomock.Any()).Return(213)
					return geoRequestParser
				},
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					return ctx
				}(),
			},
			wantErr: assert.NoError,
		},
		{
			name: "setup lbs failed",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					optionsGetter := NewMockoptionsGetter(gomock.NewController(t))
					optionsGetter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							EnableLAASPercentage: 100,
						},
					})
					return optionsGetter
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SkipLBS(gomock.Any(), gomock.Any()).Return(false)
					return handler
				},
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					validator := NewMocklbsParamsValidator(gomock.NewController(t))
					validator.EXPECT().Validate(gomock.Any()).Return(true)
					return validator
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(0).Return(false)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParsePumpkinRegionID(gomock.Any()).Return(0)
					return geoRequestParser
				},
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					parser := NewMockcoordinatesParser(gomock.NewController(t))
					parser.EXPECT().Parse(gomock.Any()).Return(coordinates.Coordinates{})
					return parser
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLBSRequest(gomock.Any()).Return(errors.Error("error"))
					return ctx
				},
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetAppInfo").Return(models.AppInfo{})
					return ctx
				}(),
			},
			wantErr: assert.Error,
		},
		{
			name: "setup lbs success",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					optionsGetter := NewMockoptionsGetter(gomock.NewController(t))
					optionsGetter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							EnableLAASPercentage: 100,
						},
					})
					return optionsGetter
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SkipLBS(gomock.Any(), gomock.Any()).Return(false)
					return handler
				},
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					validator := NewMocklbsParamsValidator(gomock.NewController(t))
					validator.EXPECT().Validate(gomock.Any()).Return(true)
					return validator
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(0).Return(false)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParsePumpkinRegionID(gomock.Any()).Return(0)
					return geoRequestParser
				},
				createCoordinatesParser: func(t *testing.T) *MockcoordinatesParser {
					parser := NewMockcoordinatesParser(gomock.NewController(t))
					parser.EXPECT().Parse(gomock.Any()).Return(coordinates.Coordinates{})
					return parser
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLBSRequest(gomock.Any()).Return(nil)
					return ctx
				},
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetAppInfo").Return(models.AppInfo{})
					return ctx
				}(),
			},
			wantErr: assert.NoError,
		},
		{
			name: "setup laas by gpauto failed",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					optionsGetter := NewMockoptionsGetter(gomock.NewController(t))
					optionsGetter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							EnableLAASPercentage: 100,
						},
					})
					return optionsGetter
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SetupLAASByGpAuto(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(errors.Error("error"))
					return handler
				},
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(0).Return(false)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParsePumpkinRegionID(gomock.Any()).Return(0)
					return geoRequestParser
				},
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
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetAppInfo").Return(models.AppInfo{})
					return ctx
				}(),
			},
			wantErr: assert.Error,
		},
		{
			name: "setup laas by gpauto",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					optionsGetter := NewMockoptionsGetter(gomock.NewController(t))
					optionsGetter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							EnableLAASPercentage: 100,
						},
					})
					return optionsGetter
				},
				createHandler: func(t *testing.T) *Mockhandler {
					handler := NewMockhandler(gomock.NewController(t))
					handler.EXPECT().SetupLAASByGpAuto(gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any(), gomock.Any()).
						Return(nil)
					return handler
				},
				createLbsParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(0).Return(false)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParsePumpkinRegionID(gomock.Any()).Return(0)
					return geoRequestParser
				},
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
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				baseCtx: func() *mocks.Base {
					ctx := &mocks.Base{}
					ctx.On("GetOriginRequest").Return(&models.OriginRequest{}, nil)
					ctx.On("GetRequest").Return(models.Request{})
					ctx.On("GetAppInfo").Return(models.AppInfo{})
					return ctx
				}(),
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &srcSetupHandler{
				handler:            tt.fields.createHandler(t),
				lbsParamsValidator: tt.fields.createLbsParamsValidator(t),
				geoResolver:        tt.fields.createGeoResolver(t),
				geoRequestParser:   tt.fields.createGeoRequestParser(t),
				coordinatesParser:  tt.fields.createCoordinatesParser(t),
				optionsGetter:      tt.fields.createOptionsGetter(t),
			}

			ctx := tt.args.createContext(t)

			got := s.handle(ctx, tt.args.baseCtx)
			tt.wantErr(t, got)
		})
	}
}
