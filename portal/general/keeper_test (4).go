package blackbox

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func Test_keeper_ForceAuth(t *testing.T) {
	type state struct {
		cached       *models.Auth
		cacheUpdated bool
	}
	tests := []struct {
		name string

		currentState state
		newData      models.Auth
		wantState    state
	}{
		{
			name: "empty cache",
			currentState: state{
				cached:       nil,
				cacheUpdated: false,
			},
			newData: models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
			wantState: state{
				cached: &models.Auth{
					UID: "111",
					Sids: map[string]string{
						"a": "abc",
						"b": "bcd",
					},
				},
				cacheUpdated: true,
			},
		},
		{
			name: "not empty cache",
			currentState: state{
				cached: &models.Auth{
					UID: "222",
					Sids: map[string]string{
						"a": "abc",
					},
				},
				cacheUpdated: false,
			},
			newData: models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
			wantState: state{
				cached: &models.Auth{
					UID: "111",
					Sids: map[string]string{
						"a": "abc",
						"b": "bcd",
					},
				},
				cacheUpdated: true,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger:       log3.NewLoggerStub(),
				cached:       tt.currentState.cached,
				cacheUpdated: tt.currentState.cacheUpdated,
			}

			k.ForceAuth(tt.newData)

			assert.Equal(t, tt.wantState.cached, k.cached)
			assert.Equal(t, tt.wantState.cacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetAuth(t *testing.T) {
	tests := []struct {
		name   string
		cached *models.Auth
		want   models.Auth
	}{
		{
			name:   "nil cache",
			cached: nil,
			want:   models.Auth{},
		},
		{
			name: "not nil cache",
			cached: &models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
			want: models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger: log3.NewLoggerStub(),
				cached: tt.cached,
			}

			assert.Equal(t, tt.want, k.GetAuth())
		})
	}
}

func Test_keeper_GetAuthIfUpdated(t *testing.T) {
	tests := []struct {
		name         string
		cached       *models.Auth
		cacheUpdated bool
		want         *mordadata.Auth
	}{
		{
			name:         "empty cache, not updated",
			cached:       nil,
			cacheUpdated: false,
			want:         nil,
		},
		{
			name:         "empty cache, updated",
			cached:       nil,
			cacheUpdated: true,
			want:         nil,
		},
		{
			name: "non-empty cache, not updated",
			cached: &models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
			cacheUpdated: false,
			want:         nil,
		},
		{
			name: "non-empty cache, updated",
			cached: &models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
			cacheUpdated: true,
			want: &mordadata.Auth{
				UID: []byte("111"),
				Sids: map[string][]byte{
					"a": []byte("abc"),
					"b": []byte("bcd"),
				},
				PlusSubscription: &mordadata.PlusSubscription{},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger:       log3.NewLoggerStub(),
				cached:       tt.cached,
				cacheUpdated: tt.cacheUpdated,
			}

			assertpb.Equal(t, tt.want, k.GetAuthIfUpdated())
		})
	}
}

func Test_keeper_GetAuthOrErr(t *testing.T) {
	tests := []struct {
		name        string
		cached      *models.Auth
		want        models.Auth
		wantErrFunc assert.ErrorAssertionFunc
	}{
		{
			name:        "empty cache",
			cached:      nil,
			want:        models.Auth{},
			wantErrFunc: assert.Error,
		},
		{
			name: "non-empty cache",
			cached: &models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
			want: models.Auth{
				UID: "111",
				Sids: map[string]string{
					"a": "abc",
					"b": "bcd",
				},
			},
			wantErrFunc: assert.NoError,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger: log3.NewLoggerStub(),
				cached: tt.cached,
			}

			got, err := k.GetAuthOrErr()
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}
