package parser

import (
	"net/http"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/country"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/mordacontent"
)

func Test_parser_parsePumpkinGeo(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		pumpkinRegionID int
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "not good region",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(213).Return(false)
					return resolver
				},
			},
			args: args{
				pumpkinRegionID: 213,
			},
			want:    nil,
			wantErr: assert.NoError,
		},
		{
			name: "get region geo failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(213).Return(true)
					resolver.EXPECT().GetRegionGeo(213).Return(nil, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				pumpkinRegionID: 213,
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().IsGoodRegion(213).Return(true)
					resolver.EXPECT().GetRegionGeo(213).Return(&models.Geo{
						RegionID: 213,
					}, nil)
					return resolver
				},
			},
			args: args{
				pumpkinRegionID: 213,
			},
			want: &models.Geo{
				RegionID: 213,
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			got, err := p.parsePumpkinGeo(tt.args.pumpkinRegionID)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_parser_makeFallback(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		err error
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get fallback region success with error",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().GetRegionGeo(fallbackRegionID).Return(&models.Geo{
						RegionID: fallbackRegionID,
					}, nil)
					return resolver
				},
			},
			args: args{
				err: errors.Error("error"),
			},
			want: models.Geo{
				RegionID: fallbackRegionID,
			},
			wantErr: assert.Error,
		},
		{
			name: "get fallback region success without error",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().GetRegionGeo(fallbackRegionID).Return(&models.Geo{
						RegionID: fallbackRegionID,
					}, nil)
					return resolver
				},
			},
			args: args{
				err: nil,
			},
			want: models.Geo{
				RegionID: fallbackRegionID,
			},
			wantErr: assert.NoError,
		},
		{
			name: "get fallback region success with error",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().GetRegionGeo(fallbackRegionID).Return(nil, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				err: errors.Error("error"),
			},
			want: models.Geo{
				RegionID: fallbackRegionID,
				CityID:   fallbackRegionID,
			},
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			got, err := p.makeFallback(tt.args.err)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_parser_parseLAASGPAutoFallback(t *testing.T) {
	type fields struct {
		createLAASFallBacker   func(t *testing.T) *MocklaasFallBacker
		createGeoRequestParser func(t *testing.T) *MockgeoRequestParser
		createGeoResolver      func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		superRegionID int
		smartRegionID int
		ip            string
		headers       http.Header
		coords        coordinates.Coordinates
		logger        log3.LoggerAlterable
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "empty coordinates",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					return nil
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					return nil
				},
			},
			args: args{
				coords: coordinates.Coordinates{},
			},
			want:    nil,
			wantErr: assert.NoError,
		},
		{
			name: "get fallback region id failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					return nil
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(0, errors.Error("error"))
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				logger: log3.NewLoggerStub(),
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "parse region success with coordinates",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), coordinates.Coordinates{
						Latitude:  1,
						Longitude: 2,
					}).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return geoRequestParser
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				smartRegionID: 111,
				logger:        log3.NewLoggerStub(),
			},
			want: &models.Geo{
				RegionID: 111,
			},
			wantErr: assert.NoError,
		},
		{
			name: "parse region success without coordinates",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), coordinates.Coordinates{}).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return geoRequestParser
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).
						Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				smartRegionID: 123,
				logger:        log3.NewLoggerStub(),
			},
			want: &models.Geo{
				RegionID: 111,
			},
			wantErr: assert.NoError,
		},
		{
			name: "parse region failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil, errors.Error("error"))
					return geoRequestParser
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				smartRegionID: 111,
				logger:        log3.NewLoggerStub(),
			},
			want: &models.Geo{
				RegionID: 111,
			},
			wantErr: assert.NoError,
		},
		{
			name: "parse geo by laas region success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil, nil)
					return geoRequestParser
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).
						Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				logger: log3.NewLoggerStub(),
			},
			want: &models.Geo{
				RegionID: 111,
			},
			wantErr: assert.NoError,
		},
		{
			name: "process geo by super region success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 123,
					}, nil)
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil, nil)
					return geoRequestParser
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				superRegionID: 123,
				ip:            "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				logger: log3.NewLoggerStub(),
			},
			want: &models.Geo{
				RegionID: 123,
			},
			wantErr: assert.NoError,
		},
		{
			name: "resolve geo failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(nil, errors.Error("error"))
					return resolver
				},
				createGeoRequestParser: func(t *testing.T) *MockgeoRequestParser {
					geoRequestParser := NewMockgeoRequestParser(gomock.NewController(t))
					geoRequestParser.EXPECT().ParseRegion(gomock.Any(), gomock.Any(), gomock.Any()).Return(nil, nil)
					return geoRequestParser
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
				logger: log3.NewLoggerStub(),
			},
			want:    nil,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				laasFallBacker:   tt.fields.createLAASFallBacker(t),
				geoResolver:      tt.fields.createGeoResolver(t),
				geoRequestParser: tt.fields.createGeoRequestParser(t),
				logger:           log3.NewLoggerStub(),
			}

			got, err := p.parseLAASGPAutoFallback(tt.args.superRegionID, tt.args.smartRegionID, tt.args.ip,
				tt.args.headers, tt.args.coords)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_parser_parseFallback(t *testing.T) {
	type fields struct {
		createGeoResolver func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		country country.Country
		coords  coordinates.Coordinates
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "from country",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().GetCapitalRegionID(gomock.Any()).Return(213)
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(&models.Geo{
						RegionID: 213,
					}, nil)
					return resolver
				},
			},
			args: args{
				country: country.RU,
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want: &models.Geo{
				RegionID: 213,
			},
			wantErr: assert.NoError,
		},
		{
			name: "empty region",
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
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want: &models.Geo{
				RegionID: 213,
			},
			wantErr: assert.NoError,
		},
		{
			name: "process geo failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(nil, errors.Error("error"))
					return resolver
				},
			},
			args: args{
				coords: coordinates.Coordinates{
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
			p := &parser{
				geoResolver: tt.fields.createGeoResolver(t),
			}

			got, err := p.parseFallback(tt.args.country, tt.args.coords)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_parser_parseLAASByIPFallback(t *testing.T) {
	type fields struct {
		createLAASFallBacker func(t *testing.T) *MocklaasFallBacker
		createGeoResolver    func(t *testing.T) *MockgeoResolver
	}

	type args struct {
		ip      string
		headers http.Header
		coords  coordinates.Coordinates
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get fallback laas region failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					return nil
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(0, errors.Error("error"))
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "process geo failed",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(gomock.Any(), gomock.Any()).Return(nil, errors.Error("error"))
					return resolver
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				createGeoResolver: func(t *testing.T) *MockgeoResolver {
					resolver := NewMockgeoResolver(gomock.NewController(t))
					resolver.EXPECT().ResolveGeo(111, gomock.Any()).Return(&models.Geo{
						RegionID: 111,
					}, nil)
					return resolver
				},
				createLAASFallBacker: func(t *testing.T) *MocklaasFallBacker {
					fallBacker := NewMocklaasFallBacker(gomock.NewController(t))
					fallBacker.EXPECT().GetRegionID(gomock.Any(), gomock.Any(), gomock.Any()).Return(111, nil)
					return fallBacker
				},
			},
			args: args{
				ip: "127.0.0.1",
				headers: map[string][]string{
					"X-Real-Ip": {"192.168.0.1"},
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want: &models.Geo{
				RegionID: 111,
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{
				laasFallBacker: tt.fields.createLAASFallBacker(t),
				geoResolver:    tt.fields.createGeoResolver(t),
			}

			got, err := p.parseLAASByIPFallback(tt.args.ip, tt.args.headers, tt.args.coords)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_parser_isRegionAmongParents(t *testing.T) {
	testCases := []struct {
		name           string
		haystack       []uint32
		needle         uint32
		expectedResult bool
	}{
		{
			name:           "among parents",
			haystack:       []uint32{1, 2, 3},
			needle:         1,
			expectedResult: true,
		},
		{
			name:           "not among parents",
			haystack:       []uint32{1, 2, 3},
			needle:         0,
			expectedResult: false,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			p := &parser{}
			geo := models.Geo{
				Parents: testCase.haystack,
			}
			assert.Equal(t, testCase.expectedResult, p.isRegionAmongParents(geo, testCase.needle))
		})
	}
}

func Test_parser_OverrideWithMordaZone(t *testing.T) {
	defaultGeo := models.Geo{
		RegionID: 1,
		Parents:  []uint32{1, 2, 3},
	}
	resolvedGeo := models.Geo{
		RegionID: 2,
		Parents:  []uint32{2, 3, 4},
	}
	testCases := []struct {
		name           string
		isRequestAPI   bool
		isRequestRobot bool
		requestURL     string
		mordaContent   string
		domain         string

		geo       models.Geo
		mordaZone string

		expectError    bool
		expectedResult models.Geo
	}{
		{
			name:           "no override",
			isRequestAPI:   true,
			isRequestRobot: false,
			requestURL:     "/",
			mordaContent:   mordacontent.SPOK,
			domain:         "yandex.ru",

			geo:       defaultGeo,
			mordaZone: "ru",

			expectError:    false,
			expectedResult: defaultGeo,
		},
		{
			name:           "override by domain for non api",
			isRequestAPI:   false,
			isRequestRobot: false,
			requestURL:     "/",
			mordaContent:   mordacontent.SPOK,
			domain:         "yandex.by",

			geo:       defaultGeo,
			mordaZone: "ru",

			expectError:    false,
			expectedResult: resolvedGeo,
		},
		{
			name:           "override by domain for robot",
			isRequestAPI:   true,
			isRequestRobot: true,
			requestURL:     "/",
			mordaContent:   mordacontent.SPOK,
			domain:         "yandex.by",

			geo:       defaultGeo,
			mordaZone: "ru",

			expectError:    false,
			expectedResult: resolvedGeo,
		},
		{
			name:           "override by domain for /ua... for matching mordacontent",
			isRequestAPI:   true,
			isRequestRobot: true,
			requestURL:     "/ua",
			mordaContent:   mordacontent.Mob,
			domain:         "yandex.by",

			geo:       defaultGeo,
			mordaZone: "ru",

			expectError:    false,
			expectedResult: resolvedGeo,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			ctl := gomock.NewController(t)
			apiInfo := models.APIInfo{}
			if testCase.isRequestAPI {
				apiInfo.Name = "search"
			}
			requestGetter := NewMockrequestGetter(ctl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{
				URL:     testCase.requestURL,
				APIInfo: apiInfo,
			})
			robotGetter := NewMockrobotGetter(ctl)
			robotGetter.EXPECT().GetRobot().Return(models.Robot{
				IsRobot: testCase.isRequestRobot,
			})
			mordaContentGetter := NewMockmordaContentGetter(ctl)
			mordaContentGetter.EXPECT().GetMordaContent().Return(models.MordaContent{
				Value: testCase.mordaContent,
			})
			domainGetter := NewMockdomainGetter(ctl)
			domainGetter.EXPECT().GetDomain().Return(models.Domain{
				Domain: testCase.domain,
			}).AnyTimes()
			geoResolver := NewMockgeoResolver(ctl)
			geoResolver.EXPECT().GetRegionGeo(gomock.Any()).Return(&resolvedGeo, nil).AnyTimes()

			domainConverter := NewMockdomainConverter(ctl)
			domainConverter.EXPECT().DomainToGeo(gomock.Any()).Return(uint32(111), true).MaxTimes(2)
			domainConverter.EXPECT().DomainToCity(gomock.Any()).Return(uint32(111), true).MaxTimes(2)

			p := &parser{
				requestGetter:      requestGetter,
				mordaContentGetter: mordaContentGetter,
				domainGetter:       domainGetter,
				domainConverter:    domainConverter,
				geoResolver:        geoResolver,
				robotGetter:        robotGetter,
			}
			result, err := p.OverrideWithMordaZone(testCase.geo, testCase.mordaZone)
			if testCase.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
			assert.Equal(t, testCase.expectedResult, result)
		})
	}
}
