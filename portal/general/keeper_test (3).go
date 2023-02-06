package bigb

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

func Test_keeper_ForceBigB(t *testing.T) {
	type state struct {
		cached       *models.BigB
		cacheUpdated bool
	}
	tests := []struct {
		name         string
		currentState state
		newData      models.BigB
		wantState    state
	}{
		{
			name: "nil cache",
			currentState: state{
				cached:       nil,
				cacheUpdated: false,
			},
			newData: prepared.TestModelBigBVer1,
			wantState: state{
				cached:       &prepared.TestModelBigBVer1,
				cacheUpdated: true,
			},
		},
		{
			name: "not nil cache",
			currentState: state{
				cached:       &prepared.TestModelBigBVer1,
				cacheUpdated: true,
			},
			newData: prepared.TestModelBigBVer2,
			wantState: state{
				cached:       &prepared.TestModelBigBVer2,
				cacheUpdated: true,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.currentState.cached,
				cacheUpdated: tt.currentState.cacheUpdated,
			}
			k.ForceBigB(tt.newData)
			assert.Equal(t, tt.wantState.cached, k.cached)
			assert.Equal(t, tt.wantState.cacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetBigB(t *testing.T) {
	tests := []struct {
		name   string
		cached *models.BigB
		want   models.BigB
	}{
		{
			name:   "nil cache",
			cached: nil,
			want:   models.BigB{},
		},
		{
			name:   "not nil cache",
			cached: &prepared.TestModelBigBVer1,
			want:   prepared.TestModelBigBVer1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger: log3.NewLoggerStub(),
				cached: tt.cached,
			}
			got := k.GetBigB()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_GetBigBIfUpdated(t *testing.T) {
	tests := []struct {
		name         string
		cached       *models.BigB
		cacheUpdated bool
		want         *mordadata.BigB
	}{
		{
			name:         "nil cache, not updated",
			cached:       nil,
			cacheUpdated: false,
			want:         nil,
		},
		{
			name:         "nil cache, updated",
			cached:       nil,
			cacheUpdated: true,
			want:         nil,
		},
		{
			name:         "not nil cache, not updated",
			cached:       &prepared.TestModelBigBVer1,
			cacheUpdated: false,
			want:         nil,
		},
		{
			name:         "not nil cache, updated",
			cached:       &prepared.TestModelBigBVer1,
			cacheUpdated: true,
			want:         prepared.TestDTOBigBVer1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached:       tt.cached,
				cacheUpdated: tt.cacheUpdated,
			}
			got := k.GetBigBIfUpdated()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_GetBigBOrErr(t *testing.T) {
	tests := []struct {
		name    string
		cached  *models.BigB
		want    models.BigB
		wantErr bool
	}{
		{
			name:    "nil cache",
			cached:  nil,
			want:    models.BigB{},
			wantErr: true,
		},
		{
			name:    "not nil cache",
			cached:  &prepared.TestModelBigBVer1,
			want:    prepared.TestModelBigBVer1,
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				cached: tt.cached,
			}
			got, err := k.GetBigBOrErr()
			assert.Equal(t, tt.wantErr, err != nil)
			assert.Equal(t, tt.want, got)
		})
	}
}
