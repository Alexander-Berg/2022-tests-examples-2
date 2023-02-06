package madmcontent

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_keeper_GetAppInfo(t *testing.T) {
	type fields struct {
		createParser func(t *testing.T) *MockmadmContentParser
		logger       log3.LoggerAlterable
		cached       *models.MadmContent
		cacheUpdated bool
	}

	tests := []struct {
		name   string
		fields fields
		want   models.MadmContent
	}{
		{
			name: "nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockmadmContentParser {
					parser := NewMockmadmContentParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.MadmContent{
						Values: []string{
							"big",
							"touch",
						},
					}, nil)
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.MadmContent{
				Values: []string{
					"big",
					"touch",
				},
			},
		},
		{
			name: "not nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockmadmContentParser {
					return nil
				},
				logger: log3.NewLoggerStub(),
				cached: &models.MadmContent{
					Values: []string{
						"big",
						"touch",
					},
				},
				cacheUpdated: false,
			},
			want: models.MadmContent{
				Values: []string{
					"big",
					"touch",
				},
			},
		},
		{
			name: "parse error",
			fields: fields{
				createParser: func(t *testing.T) *MockmadmContentParser {
					parser := NewMockmadmContentParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.MadmContent{
						Values: []string{
							"big",
							"touch",
						},
					}, errors.Error("error"))
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.MadmContent{
				Values: []string{
					"big",
					"touch",
				},
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

			assert.Equal(t, tt.want, k.GetMadmContent())
		})
	}
}
