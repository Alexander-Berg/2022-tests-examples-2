package geo

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_keeper_GetGeo(t *testing.T) {
	type fields struct {
		createParser func(t *testing.T) *MockgeoParser
		logger       log3.LoggerAlterable
		cached       *models.Geo
		cacheUpdated bool
	}

	tests := []struct {
		name   string
		fields fields
		want   models.Geo
	}{
		{
			name: "nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockgeoParser {
					parser := NewMockgeoParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.Geo{
						RegionID: 213,
						CityID:   213,
					}, nil)
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.Geo{
				RegionID: 213,
				CityID:   213,
			},
		},
		{
			name: "parse error",
			fields: fields{
				createParser: func(t *testing.T) *MockgeoParser {
					parser := NewMockgeoParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.Geo{}, errors.Error("error"))
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.Geo{},
		},
		{
			name: "not nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockgeoParser {
					return nil
				},
				logger: log3.NewLoggerStub(),
				cached: &models.Geo{
					RegionID: 213,
					CityID:   213,
				},
				cacheUpdated: false,
			},
			want: models.Geo{
				RegionID: 213,
				CityID:   213,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				parser:       tt.fields.createParser(t),
				logger:       tt.fields.logger,
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			assert.Equal(t, tt.want, k.GetGeo())
		})
	}
}
