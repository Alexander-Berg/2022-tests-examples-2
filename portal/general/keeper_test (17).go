package mordazone

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func Test_keeper_GetMordaZone(t *testing.T) {
	type dataSource int
	const (
		none dataSource = iota
		fromCache
		fromParser
	)
	type parserResult struct {
		domain models.MordaZone
		error  error
	}
	tests := []struct {
		name             string
		cache            *models.MordaZone
		expectParserCall bool
		parserResult     parserResult
		wantSource       dataSource
		wantCacheUpdated bool
		wantErr          bool
	}{
		{
			name: "warm cache",
			cache: &models.MordaZone{
				Value: "ua",
			},
			wantSource:       fromCache,
			wantCacheUpdated: false,
			wantErr:          false,
		},
		{
			name:             "cold cache",
			expectParserCall: true,
			parserResult: parserResult{
				domain: models.MordaZone{
					Value: "ua",
				},
			},
			wantSource:       fromParser,
			wantCacheUpdated: true,
		},
		{
			name:             "cold cache and got error from parser",
			expectParserCall: true,
			parserResult: parserResult{
				domain: models.MordaZone{
					Value: "ua",
				},
				error: errors.Error("some error"),
			},
			wantSource:       fromParser,
			wantCacheUpdated: true,
			wantErr:          true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mordazoneParser := NewMockmordazoneParser(gomock.NewController(t))
			if tt.expectParserCall {
				mordazoneParser.EXPECT().Parse().Return(tt.parserResult.domain, tt.parserResult.error)
			}

			k := &keeper{
				parser: mordazoneParser,
				cached: tt.cache,
			}

			got, err := k.GetMordaZoneOrErr()

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
			switch tt.wantSource {
			case none:
				assert.Zero(t, got)
			case fromCache:
				assert.Equal(t, *tt.cache, got)
			case fromParser:
				assert.Equal(t, tt.parserResult.domain, got)
			}

			assert.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetMordaZoneIfUpdated(t *testing.T) {
	type fields struct {
		cached       *models.MordaZone
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *mordadata.MordaZone
	}{
		{
			name: "Not updated",
			fields: fields{
				cached:       &models.MordaZone{Value: "ru"},
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "Updated, but cache is nil",
			fields: fields{
				cached:       nil,
				cacheUpdated: true,
			},
			want: nil,
		},
		{
			name: "Not updated",
			fields: fields{
				cached:       &models.MordaZone{Value: "ru"},
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "Updated, has not-nil cache",
			fields: fields{
				cached:       &models.MordaZone{Value: "ru"},
				cacheUpdated: true,
			},
			want: &mordadata.MordaZone{Value: []byte("ru")},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetMordaZoneIfUpdated()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_ForceMordaZone(t *testing.T) {
	type fields struct {
		cached       *models.MordaZone
		cacheUpdated bool
	}
	type args struct {
		newMordaZone models.MordaZone
	}
	tests := []struct {
		name             string
		fields           fields
		args             args
		wantCache        *models.MordaZone
		wantCacheUpdated bool
	}{
		{
			name: "cache was empty",
			fields: fields{
				cached:       nil,
				cacheUpdated: false,
			},
			args: args{
				newMordaZone: models.MordaZone{
					Value: "new_zone",
				},
			},
			wantCache: &models.MordaZone{
				Value: "new_zone",
			},
			wantCacheUpdated: true,
		},
		{
			name: "cache was not empty",
			fields: fields{
				cached: &models.MordaZone{
					Value: "old_zone",
				},
				cacheUpdated: true,
			},
			args: args{
				newMordaZone: models.MordaZone{
					Value: "new_zone",
				},
			},
			wantCache: &models.MordaZone{
				Value: "new_zone",
			},
			wantCacheUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			k.ForceMordaZone(tt.args.newMordaZone)

			require.Equal(t, tt.wantCache, k.cached)
			require.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}
