package mordacontent

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_keeper_GetMordaContent(t *testing.T) {
	type fields struct {
		createParser func(t *testing.T) *MockmordaContentParser
		logger       log3.LoggerAlterable
		cached       *models.MordaContent
		cacheUpdated bool
	}

	tests := []struct {
		name   string
		fields fields
		want   models.MordaContent
	}{
		{
			name: "nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockmordaContentParser {
					parser := NewMockmordaContentParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.MordaContent{
						Value: "big",
					}, nil)
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name: "parse error",
			fields: fields{
				createParser: func(t *testing.T) *MockmordaContentParser {
					parser := NewMockmordaContentParser(gomock.NewController(t))
					parser.EXPECT().Parse().Return(models.MordaContent{
						Value: defaultMordaContent,
					}, errors.Error("error"))
					return parser
				},
				logger:       log3.NewLoggerStub(),
				cached:       nil,
				cacheUpdated: false,
			},
			want: models.MordaContent{
				Value: "big",
			},
		},
		{
			name: "not nil cache",
			fields: fields{
				createParser: func(t *testing.T) *MockmordaContentParser {
					return nil
				},
				logger: log3.NewLoggerStub(),
				cached: &models.MordaContent{
					Value: "big",
				},
				cacheUpdated: false,
			},
			want: models.MordaContent{
				Value: "big",
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

			assert.Equal(t, tt.want, k.GetMordaContent())
		})
	}
}

func Test_keeper_ForceMordaContent(t *testing.T) {
	type fields struct {
		cached       *models.MordaContent
		cacheUpdated bool
	}
	type args struct {
		newContent models.MordaContent
	}
	tests := []struct {
		name             string
		fields           fields
		args             args
		wantCache        *models.MordaContent
		wantCacheUpdated bool
	}{
		{
			name: "cache was empty",
			fields: fields{
				cached:       nil,
				cacheUpdated: false,
			},
			args: args{
				newContent: models.MordaContent{
					Value: "new",
				},
			},
			wantCache: &models.MordaContent{
				Value: "new",
			},
			wantCacheUpdated: true,
		},
		{
			name: "cache was not empty",
			fields: fields{
				cached: &models.MordaContent{
					Value: "old_cache",
				},
				cacheUpdated: false,
			},
			args: args{
				newContent: models.MordaContent{
					Value: "new",
				},
			},
			wantCache: &models.MordaContent{
				Value: "new",
			},
			wantCacheUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger:       log3.NewLoggerStub(),
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			k.ForceMordaContent(tt.args.newContent)

			require.Equal(t, tt.wantCache, k.cached)
			require.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}
