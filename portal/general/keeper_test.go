package aadb

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewKeeper(t *testing.T) {
	logger := log3.NewLoggerStub()
	ctrl := gomock.NewController(t)
	parserMock := NewMockaadbParser(ctrl)

	type args struct {
		cache      *mordadata.AntiAdblock
		logger     log3.Logger
		aadbParser aadbParser
	}
	tests := []struct {
		name string
		args args
		want *keeper
	}{
		{
			name: "All nils",
			args: args{
				cache:      nil,
				logger:     nil,
				aadbParser: nil,
			},
			want: &keeper{
				aadbParser:   nil,
				logger:       nil,
				cached:       nil,
				cacheUpdated: false,
			},
		},
		{
			name: "Nil cache",
			args: args{
				cache:      nil,
				logger:     logger,
				aadbParser: parserMock,
			},
			want: &keeper{
				aadbParser:   parserMock,
				logger:       logger,
				cached:       nil,
				cacheUpdated: false,
			},
		},
		{
			name: "Init with cache",
			args: args{
				cache:      &mordadata.AntiAdblock{IsAddBlock: true},
				logger:     logger,
				aadbParser: parserMock,
			},
			want: &keeper{
				aadbParser:   parserMock,
				logger:       logger,
				cached:       &models.AADB{IsAddBlock: true},
				cacheUpdated: false,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewKeeper(tt.args.cache, tt.args.logger, tt.args.aadbParser)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_GetAADB(t *testing.T) {
	type fields struct {
		cached       *models.AADB
		cacheUpdated bool
	}
	type parserAnswer struct {
		model models.AADB
		err   error
	}
	tests := []struct {
		name         string
		fields       fields
		parserAnswer *parserAnswer
		want         models.AADB
		wantUpdated  bool
	}{
		{
			name: "Got from cache",
			fields: fields{
				cached:       &models.AADB{IsAddBlock: true},
				cacheUpdated: false,
			},
			parserAnswer: nil,
			want:         models.AADB{IsAddBlock: true},
			wantUpdated:  false,
		},
		{
			name: "Got from cache and was updated before",
			fields: fields{
				cached:       &models.AADB{IsAddBlock: true},
				cacheUpdated: true,
			},
			parserAnswer: nil,
			want:         models.AADB{IsAddBlock: true},
			wantUpdated:  true,
		},
		{
			name: "No cached; got from parser",
			fields: fields{
				cached:       nil,
				cacheUpdated: false,
			},
			parserAnswer: &parserAnswer{
				model: models.AADB{IsAddBlock: true},
				err:   nil,
			},
			want:        models.AADB{IsAddBlock: true},
			wantUpdated: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			parserMock := NewMockaadbParser(ctrl)
			if tt.parserAnswer != nil {
				parserMock.EXPECT().Parse().Return(tt.parserAnswer.model, tt.parserAnswer.err).Times(1)
			}
			k := &keeper{
				aadbParser:   parserMock,
				logger:       log3.NewLoggerStub(),
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetAADB()

			require.Equal(t, tt.want, got)
			require.Equal(t, tt.wantUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetAntiAdblockIfUpdated(t *testing.T) {
	type fields struct {
		cached       *models.AADB
		cacheUpdated bool
	}
	tests := []struct {
		name   string
		fields fields
		want   *mordadata.AntiAdblock
	}{
		{
			name: "Updated false",
			fields: fields{
				cached:       &models.AADB{IsAddBlock: true},
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "Updated true, but cache nil",
			fields: fields{
				cached:       nil,
				cacheUpdated: true,
			},
			want: nil,
		},
		{
			name: "Not updated",
			fields: fields{
				cached:       &models.AADB{IsAddBlock: true},
				cacheUpdated: false,
			},
			want: nil,
		},
		{
			name: "Was updated",
			fields: fields{
				cached:       &models.AADB{IsAddBlock: true},
				cacheUpdated: true,
			},
			want: &mordadata.AntiAdblock{IsAddBlock: true},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger:       log3.NewLoggerStub(),
				cached:       tt.fields.cached,
				cacheUpdated: tt.fields.cacheUpdated,
			}

			got := k.GetAntiAdblockIfUpdated()

			require.Equal(t, tt.want, got)
		})
	}
}
