package clids

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"google.golang.org/protobuf/proto"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func Test_keeper_GetClid(t *testing.T) {
	type fields struct {
		cached       *models.Clid
		cacheUpdated bool
	}
	type parserAnswer struct {
		clid models.Clid
	}
	tests := []struct {
		name             string
		fields           fields
		parserAnswer     *parserAnswer
		want             models.Clid
		wantCacheUpdated bool
	}{
		{
			name: "Got data from cache",
			fields: fields{
				cached: &models.Clid{
					Client: "213",
				},
			},
			want: models.Clid{
				Client: "213",
			},
		},
		{
			name: "Got data from parser",
			fields: fields{
				cached:       nil,
				cacheUpdated: false,
			},
			parserAnswer: &parserAnswer{
				clid: models.Clid{
					Client: "9148",
				},
			},
			want: models.Clid{
				Client: "9148",
			},
			wantCacheUpdated: true,
		},
		{
			name: "Got empty data from parser",
			fields: fields{
				cached:       nil,
				cacheUpdated: false,
			},
			parserAnswer: &parserAnswer{
				clid: models.Clid{},
			},
			want:             models.Clid{},
			wantCacheUpdated: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			parserMock := NewMockclidParser(ctrl)
			if tt.parserAnswer != nil {
				parserMock.EXPECT().parse().Return(tt.parserAnswer.clid).Times(1)
			}
			k := &keeper{
				parser:       parserMock,
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetClid()

			require.Equal(t, tt.want, got)
			require.Equal(t, tt.wantCacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetClidIfUpdated(t *testing.T) {
	type fields struct {
		cached       *models.Clid
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *mordadata.Clid
	}{
		{
			name: "Cache updated is false",
			fields: fields{
				cached: &models.Clid{
					Client: "19284",
				},
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "Cache updated is true, got model in cache",
			fields: fields{
				cached: &models.Clid{
					Client: "19284",
				},
				cacheUpdated: true,
			},
			want: &mordadata.Clid{
				Client: []byte("19284"),
			},
		},
		{
			name: "Cache updated is true but model is empty",
			fields: fields{
				cached:       nil,
				cacheUpdated: true,
			},
			want: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetClidIfUpdated()

			require.True(t, proto.Equal(tt.want, got))
		})
	}
}

func Test_keeper_ForceClid(t *testing.T) {
	type fields struct {
		cached       *models.Clid
		cacheUpdated bool
	}
	type args struct {
		clid models.Clid
	}
	tests := []struct {
		name        string
		fields      fields
		args        args
		wantCache   *models.Clid
		wantUpdated bool
	}{
		{
			name: "update cache",
			fields: fields{
				cached: &models.Clid{
					Client: "123",
				},
				cacheUpdated: false,
			},
			args: args{
				clid: models.Clid{
					Client: "456",
				},
			},
			wantCache: &models.Clid{
				Client: "456",
			},
			wantUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}
			k.ForceClid(tt.args.clid)
			assert.Equal(t, tt.wantCache, k.cached)
			assert.Equal(t, tt.wantUpdated, k.cacheUpdated)
		})
	}
}
