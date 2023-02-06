package yabs

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func Test_keeper_GetYabs(t *testing.T) {
	type testCase struct {
		name         string
		cached       *models.Yabs
		cacheUpdated bool
		want         models.Yabs
	}

	tests := []testCase{
		{
			name:         "nil cache",
			cached:       nil,
			cacheUpdated: false,
			want:         models.Yabs{},
		},
		{
			name: "not nil cache",
			cached: &models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			cacheUpdated: false,
			want: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
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

			assert.Equal(t, tt.want, k.GetYabs())
		})
	}
}

func Test_keeper_GetYabsOrErr(t *testing.T) {
	type testCase struct {
		name        string
		cached      *models.Yabs
		want        models.Yabs
		wantErrFunc assert.ErrorAssertionFunc
	}

	tests := []testCase{
		{
			name:        "empty cache",
			cached:      nil,
			want:        models.Yabs{},
			wantErrFunc: assert.Error,
		},
		{
			name: "non-empty cache",
			cached: &models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			want: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger:       log3.NewLoggerStub(),
				cached:       tt.cached,
				cacheUpdated: false,
			}

			got, err := k.GetYabsOrErr()
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_keeper_GetYabsIfUpdated(t *testing.T) {
	type testCase struct {
		name         string
		cached       *models.Yabs
		cacheUpdated bool
		want         *mordadata.Yabs
	}

	tests := []testCase{
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
			cached: &models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			cacheUpdated: false,
			want:         nil,
		},
		{
			name: "non-empty cache, updated",
			cached: &models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			cacheUpdated: true,
			want: &mordadata.Yabs{
				BkFlags: map[string]*mordadata.Yabs_BkFlag{
					"some_flag": {
						ClickUrl: []byte("click_url"),
						CloseUrl: []byte("close_url"),
						LinkNext: []byte("link_next"),
					},
				},
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

			assertpb.Equal(t, tt.want, k.GetYabsIfUpdated())
		})
	}
}

func Test_keeper_ForceYabs(t *testing.T) {
	type state struct {
		cached       *models.Yabs
		cacheUpdated bool
	}
	type testCase struct {
		name string

		currentState state
		newData      models.Yabs
		wantState    state
	}

	tests := []testCase{
		{
			name: "empty cache",
			currentState: state{
				cached:       nil,
				cacheUpdated: false,
			},
			newData: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"some_flag": {
						ClickURL: "click_url",
						CloseURL: "close_url",
						LinkNext: "link_next",
					},
				},
			},
			wantState: state{
				cached: &models.Yabs{
					BKFlags: map[string]models.BKFlag{
						"some_flag": {
							ClickURL: "click_url",
							CloseURL: "close_url",
							LinkNext: "link_next",
						},
					},
				},
				cacheUpdated: true,
			},
		},
		{
			name: "non-empty cache",
			currentState: state{
				cached: &models.Yabs{
					BKFlags: map[string]models.BKFlag{
						"some_flag": {
							ClickURL: "click_url",
							CloseURL: "close_url",
							LinkNext: "link_next",
						},
					},
				},
				cacheUpdated: false,
			},
			newData: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"completely_new_flag": {
						ClickURL: "__click_url__",
						CloseURL: "__close_url__",
						LinkNext: "__link_next__",
					},
				},
			},
			wantState: state{
				cached: &models.Yabs{
					BKFlags: map[string]models.BKFlag{
						"completely_new_flag": {
							ClickURL: "__click_url__",
							CloseURL: "__close_url__",
							LinkNext: "__link_next__",
						},
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

			k.ForceYabs(tt.newData)

			assert.Equal(t, tt.wantState.cached, k.cached)
			assert.Equal(t, tt.wantState.cacheUpdated, k.cacheUpdated)
		})
	}
}
