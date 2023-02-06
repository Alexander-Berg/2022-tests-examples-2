package experiments

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

func Test_keeper_ForceABFlags(t *testing.T) {
	type state struct {
		cached       *models.ABFlags
		cacheUpdated bool
	}
	tests := []struct {
		name string

		currentState state
		newData      models.ABFlags
		wantState    state
	}{
		{
			name: "empty cache",
			currentState: state{
				cached:       nil,
				cacheUpdated: false,
			},
			newData: prepared.TestABFlagsModelVer1,
			wantState: state{
				cached:       &prepared.TestABFlagsModelVer1,
				cacheUpdated: true,
			},
		},
		{
			name: "not empty cache",
			currentState: state{
				cached:       &prepared.TestABFlagsModelVer2,
				cacheUpdated: false,
			},
			newData: prepared.TestABFlagsModelVer1,
			wantState: state{
				cached:       &prepared.TestABFlagsModelVer1,
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

			k.ForceABFlags(tt.newData)

			assert.Equal(t, tt.wantState.cached, k.cached)
			assert.Equal(t, tt.wantState.cacheUpdated, k.cacheUpdated)
		})
	}
}

func Test_keeper_GetFlags(t *testing.T) {
	tests := []struct {
		name         string
		cached       *models.ABFlags
		parserAnswer models.ABFlags

		parserErr error
		want      models.ABFlags
	}{
		{
			name:         "empty cache",
			cached:       nil,
			parserAnswer: prepared.TestABFlagsModelVer1,
			parserErr:    nil,
			want:         prepared.TestABFlagsModelVer1,
		},
		{
			name:         "empty cache, parse with error",
			cached:       nil,
			parserAnswer: prepared.TestABFlagsModelVer1,
			parserErr:    errors.Error("err"),
			want:         prepared.TestABFlagsModelVer1,
		},
		{
			name:   "non-empty cache",
			cached: &prepared.TestABFlagsModelVer1,
			want:   prepared.TestABFlagsModelVer1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{}).MaxTimes(1)

			parser := NewMockflagsParser(ctrl)
			parser.EXPECT().parse(false).Return(tt.parserAnswer, tt.parserErr).MaxTimes(1)

			k := &keeper{
				logger:        log3.NewLoggerStub(),
				cached:        tt.cached,
				parser:        parser,
				requestGetter: requestGetter,
			}

			assert.Equal(t, tt.want, k.GetFlags())
		})
	}
}

func Test_keeper_GetFlagsIfUpdated(t *testing.T) {
	tests := []struct {
		name         string
		cached       *models.ABFlags
		cacheUpdated bool
		want         *mordadata.ABFlagsContext
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
			name:         "non-empty cache, not updated",
			cached:       &prepared.TestABFlagsModelVer1,
			cacheUpdated: false,
			want:         nil,
		},
		{
			name:         "non-empty cache, updated",
			cached:       &prepared.TestABFlagsModelVer1,
			cacheUpdated: true,
			want:         &prepared.TestABFlagsDTOVer1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			k := &keeper{
				logger:       log3.NewLoggerStub(),
				cached:       tt.cached,
				cacheUpdated: tt.cacheUpdated,
			}

			assertpb.Equal(t, tt.want, k.GetFlagsIfUpdated())
		})
	}
}

func Test_keeper_GetFlagsOrErr(t *testing.T) {
	tests := []struct {
		name         string
		cached       *models.ABFlags
		parserAnswer models.ABFlags
		parserErr    error
		want         models.ABFlags
		wantErrFunc  assert.ErrorAssertionFunc
	}{
		{
			name:         "empty cache",
			cached:       nil,
			parserAnswer: prepared.TestABFlagsModelVer1,
			parserErr:    nil,
			want:         prepared.TestABFlagsModelVer1,
			wantErrFunc:  assert.NoError,
		},
		{
			name:         "empty cache, parse with error",
			cached:       nil,
			parserAnswer: prepared.TestABFlagsModelVer1,
			parserErr:    errors.Error("err"),
			want:         prepared.TestABFlagsModelVer1,
			wantErrFunc:  assert.Error,
		},
		{
			name:        "non-empty cache",
			cached:      &prepared.TestABFlagsModelVer1,
			want:        prepared.TestABFlagsModelVer1,
			wantErrFunc: assert.NoError,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			requestGetter := NewMockrequestGetter(ctrl)
			requestGetter.EXPECT().GetRequest().Return(models.Request{}).MaxTimes(1)

			parser := NewMockflagsParser(ctrl)
			parser.EXPECT().parse(false).Return(tt.parserAnswer, tt.parserErr).MaxTimes(1)

			k := &keeper{
				logger:        log3.NewLoggerStub(),
				cached:        tt.cached,
				parser:        parser,
				requestGetter: requestGetter,
			}

			got, err := k.GetFlagsOrErr()
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}
