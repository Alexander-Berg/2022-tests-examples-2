package domains

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

func Test_keeper_GetDomain(t *testing.T) {
	type dataSource int
	const (
		none dataSource = iota
		fromCache
		fromParser
	)
	type parserResult struct {
		domain models.Domain
		error  error
	}
	tests := []struct {
		name             string
		cache            *models.Domain
		expectParserCall bool
		parserResult     parserResult
		wantSource       dataSource
		wantCacheUpdated bool
		wantErr          bool
	}{
		{
			name: "warm cache",
			cache: &models.Domain{
				Zone: "ua",
			},
			wantSource:       fromCache,
			wantCacheUpdated: false,
			wantErr:          false,
		},
		{
			name:             "cold cache",
			expectParserCall: true,
			parserResult: parserResult{
				domain: models.Domain{
					Zone: "ua",
				},
			},
			wantSource:       fromParser,
			wantCacheUpdated: true,
		},
		{
			name:             "cold cache and got error from parser",
			expectParserCall: true,
			parserResult: parserResult{
				domain: models.Domain{
					Zone: "ua",
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
			domainParser := NewMockdomainParser(gomock.NewController(t))
			if tt.expectParserCall {
				domainParser.EXPECT().Parse().Return(tt.parserResult.domain, tt.parserResult.error)
			}

			k := &keeper{
				parser: domainParser,
				cached: tt.cache,
			}

			got, err := k.GetDomainOrErr()

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

func Test_keeper_GetDomainIfUpdated(t *testing.T) {
	type fields struct {
		cached       *models.Domain
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *mordadata.Domain
	}{
		{
			name: "Not updated",
			fields: fields{
				cached:       &models.Domain{Zone: "ru"},
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
				cached:       &models.Domain{Zone: "ru"},
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "Updated, has not-nil cache",
			fields: fields{
				cached:       &models.Domain{Zone: "ru"},
				cacheUpdated: true,
			},
			want: &mordadata.Domain{Zone: []byte("ru")},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetDomainIfUpdated()
			assertpb.Equal(t, tt.want, got)
		})
	}
}
