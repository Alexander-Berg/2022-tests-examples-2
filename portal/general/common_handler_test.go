package geo

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
	"a.yandex-team.ru/portal/avocado/morda-go/pkg/its"
)

func Test_commonHandler_SetupLAASByGpAuto(t *testing.T) {
	type fields struct {
		createOptionsGetter      func(t *testing.T) *MockoptionsGetter
		createLBSParamsValidator func(t *testing.T) *MocklbsParamsValidator
	}

	type args struct {
		createContext func(t *testing.T) *Mockcontext
		request       models.Request
		coordinates   coordinates.Coordinates
		headers       http.Header
		appInfo       models.AppInfo
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "empty coordinates and skip lbs",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					getter := NewMockoptionsGetter(gomock.NewController(t))
					getter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							SkipLBS: true,
						},
					})

					return getter
				},
				createLBSParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLAASByGPAutoRequest(gomock.Any()).Return(nil)
					ctx.EXPECT().AddLAASByGPAutoBalancingHint(gomock.Any()).Return(nil)
					return ctx
				},
				coordinates: coordinates.Coordinates{},
				request: models.Request{
					IP: "127.0.0.1",
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "use lbs params",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					getter := NewMockoptionsGetter(gomock.NewController(t))
					getter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							SkipLBS: false,
						},
					})

					return getter
				},
				createLBSParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					validator := NewMocklbsParamsValidator(gomock.NewController(t))
					validator.EXPECT().Validate(gomock.Any()).Return(true)
					return validator
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLAASByGPAutoRequest(gomock.Any()).Return(nil)
					ctx.EXPECT().AddLAASByGPAutoBalancingHint(gomock.Any()).Return(nil)
					return ctx
				},
				coordinates: coordinates.Coordinates{},
				request: models.Request{
					URL: "/portal/api/search/2",
					CGI: map[string][]string{
						"wifi": {"ec:43:f6:06:2e:a8,-62;e2:43:f6:06:2e:a8,-61;74:da:88:cf:54:53,-85;18:0f:76:90:33:dd,-84;58:8b:f3:6b:c1:90,-93;50:ff:20:30:a3:15,-89;20:4e:7f:7d:9b:6f,-92"},
					},
					IP: "127.0.0.1",
					APIInfo: models.APIInfo{
						Name:     "search",
						RealName: "search",
						Version:  2,
					},
				},
				appInfo: models.AppInfo{
					ID:       "ru.searchplugin",
					Version:  "21050500",
					Platform: "android",
					UUID:     "456",
					DID:      "789",
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "use coordinates",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					getter := NewMockoptionsGetter(gomock.NewController(t))
					getter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							SkipLBS: true,
						},
					})

					return getter
				},
				createLBSParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLAASByGPAutoRequest(gomock.Any()).Return(nil)
					ctx.EXPECT().AddLAASByGPAutoBalancingHint(gomock.Any()).Return(nil)
					return ctx
				},
				request: models.Request{
					IP: "127.0.0.1",
				},
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				appInfo: models.AppInfo{
					ID:       "ru.searchplugin",
					Version:  "123",
					Platform: "android",
					UUID:     "456",
					DID:      "789",
				},
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.NoError,
		},
		{
			name: "build laas request by gpauto failed",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					getter := NewMockoptionsGetter(gomock.NewController(t))
					getter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							SkipLBS: true,
						},
					})

					return getter
				},
				createLBSParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				appInfo: models.AppInfo{
					ID:       "ru.searchplugin",
					Version:  "123",
					Platform: "android",
					UUID:     "456",
					DID:      "789",
				},
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "add laas request by gpauto failed",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					getter := NewMockoptionsGetter(gomock.NewController(t))
					getter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							SkipLBS: true,
						},
					})

					return getter
				},
				createLBSParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLAASByGPAutoRequest(gomock.Any()).Return(errors.Error("error"))
					return ctx
				},
				request: models.Request{
					IP: "127.0.0.1",
				},
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				appInfo: models.AppInfo{
					ID:       "ru.searchplugin",
					Version:  "123",
					Platform: "android",
					UUID:     "456",
					DID:      "789",
				},
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "add laas balancing hint failed",
			fields: fields{
				createOptionsGetter: func(t *testing.T) *MockoptionsGetter {
					getter := NewMockoptionsGetter(gomock.NewController(t))
					getter.EXPECT().Get().Return(its.Options{
						Geo: its.Geo{
							SkipLBS: true,
						},
					})

					return getter
				},
				createLBSParamsValidator: func(t *testing.T) *MocklbsParamsValidator {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().AddLAASByGPAutoRequest(gomock.Any()).Return(nil)
					ctx.EXPECT().AddLAASByGPAutoBalancingHint(gomock.Any()).Return(errors.Error("error"))
					return ctx
				},
				request: models.Request{
					IP: "127.0.0.1",
				},
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				appInfo: models.AppInfo{
					ID:       "ru.searchplugin",
					Version:  "123",
					Platform: "android",
					UUID:     "456",
					DID:      "789",
				},
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			b := &commonHandler{
				optionsGetter:      tt.fields.createOptionsGetter(t),
				lbsParamsValidator: tt.fields.createLBSParamsValidator(t),
			}

			ctx := tt.args.createContext(t)
			err := b.SetupLAASByGpAuto(ctx, tt.args.request, tt.args.coordinates, tt.args.headers, tt.args.appInfo)
			tt.wantErr(t, err)
		})
	}
}

func Test_commonHandler_ProcessRegion(t *testing.T) {
	type fields struct {
		createGeoRequestParser func(t *testing.T) *MockgeoRequestParser
	}

	type args struct {
		createContext func(t *testing.T) *Mockcontext
		smartRegionID int
		superRegionID int
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
			name: "success",
			fields: fields{
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return geoRequestParser
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().UpdateGeo(gomock.Any()).Return(nil)
					return ctx
				},
				smartRegionID: 111,
				superRegionID: 0,
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    true,
			wantErr: assert.NoError,
		},
		{
			name: "resolve geo failed",
			fields: fields{
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil, errors.Error("error"))
					return geoRequestParser
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				smartRegionID: 111,
				superRegionID: 222,
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    false,
			wantErr: assert.Error,
		},
		{
			name: "resolve empty geo",
			fields: fields{
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil, nil)
					return geoRequestParser
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				smartRegionID: 111,
				superRegionID: 222,
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    false,
			wantErr: assert.NoError,
		},
		{
			name: "update geo failed",
			fields: fields{
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return geoRequestParser
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().UpdateGeo(gomock.Any()).Return(errors.Error("error"))
					return ctx
				},
				smartRegionID: 111,
				superRegionID: 222,
				coordinates: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    false,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &commonHandler{
				geoRequestParser: tt.fields.createGeoRequestParser(t),
			}

			ctx := tt.args.createContext(t)

			got, err := c.ProcessRegion(ctx, tt.args.smartRegionID, tt.args.superRegionID, tt.args.coordinates)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_commonHandler_GetCoordinates(t *testing.T) {
	type fields struct {
		createGeoRequestParser func(t *testing.T) *MockgeoRequestParser
	}

	type args struct {
		createContext func(t *testing.T) *Mockcontext
		cgi           url.Values
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    coordinates.Coordinates
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get lbs location failed",
			fields: fields{
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					return nil
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLBSLocation().Return(&lbs.Location{}, errors.Error("error"))
					return ctx
				},
			},
			want:    coordinates.Coordinates{},
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().GetCoordinates(gomock.Any(), gomock.Any()).Return(coordinates.Coordinates{
						Latitude:  1,
						Longitude: 2,
						Accuracy:  pointer.NewFloat64(20000),
						Recency:   pointer.NewInt(60000),
					})
					return geoRequestParser
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().GetLBSLocation().Return(&lbs.Location{
						Found:     true,
						Latitude:  1,
						Longitude: 2,
						Radius:    20000,
					}, nil)
					return ctx
				},
				cgi: map[string][]string{
					"latitude":  {"1"},
					"longitude": {"2"},
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
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &commonHandler{
				geoRequestParser: tt.fields.createGeoRequestParser(t),
			}

			ctx := tt.args.createContext(t)

			got, err := c.GetCoordinates(ctx, tt.args.cgi)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_commonHandler_ProcessGeo(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		createContext func(t *testing.T) *Mockcontext
		regionID      int
		coords        coordinates.Coordinates
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "resolve geo failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(nil, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					return nil
				},
				regionID: 213,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "update geo failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 213,
					}, nil)
					return resolver
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().UpdateGeo(gomock.Any()).Return(errors.Error("error"))
					return ctx
				},
				regionID: 213,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 213,
					}, nil)
					return resolver
				},
			},
			args: args{
				createContext: func(t *testing.T) *Mockcontext {
					ctx := NewMockcontext(gomock.NewController(t))
					ctx.EXPECT().UpdateGeo(gomock.Any())
					return ctx
				},
				regionID: 213,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &commonHandler{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			ctx := tt.args.createContext(t)

			tt.wantErr(t, c.ProcessGeo(ctx, tt.args.regionID, tt.args.coords))
		})
	}
}
