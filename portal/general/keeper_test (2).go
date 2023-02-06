package appinfo

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_keeper_GetAppInfo(t *testing.T) {
	type fields struct {
		createParser func(t *testing.T) *MockappInfoParser
		logger       log3.LoggerAlterable
		cached       *models.AppInfo
		cacheUpdated bool
	}

	tests := []struct {
		name   string
		fields fields
		want   models.AppInfo
	}{
		{
			name: "nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockappInfoParser {
					parser := NewMockappInfoParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.AppInfo{
						ID:       "ru.search.plugin",
						Version:  "78000000",
						Platform: "android",
						UUID:     "123456789",
						DID:      "987654321",
					})
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.AppInfo{
				ID:       "ru.search.plugin",
				Version:  "78000000",
				Platform: "android",
				UUID:     "123456789",
				DID:      "987654321",
			},
		},
		{
			name: "not nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockappInfoParser {
					return nil
				},
				logger: log3.NewLoggerStub(),
				cached: &models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "78000000",
					Platform: "android",
					UUID:     "123456789",
					DID:      "987654321",
				},
				cacheUpdated: false,
			},
			want: models.AppInfo{
				ID:       "ru.search.plugin",
				Version:  "78000000",
				Platform: "android",
				UUID:     "123456789",
				DID:      "987654321",
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
			assert.Equal(t, tt.want, k.GetAppInfo())
		})
	}
}
