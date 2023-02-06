package mordainit

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_abFlagRequestLimiter_Allow(t *testing.T) {
	type testCase struct {
		name     string
		flagName string
		abFlags  map[string]string
		wantFunc assert.BoolAssertionFunc
	}

	cases := []testCase{
		{
			name:     "has flag",
			flagName: "test_flag",
			abFlags: map[string]string{
				"test_flag": "1",
			},
			wantFunc: assert.True,
		},
		{
			name:     "no flag",
			flagName: "test_flag",
			abFlags: map[string]string{
				"some_other_test_flag": "1",
			},
			wantFunc: assert.False,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			abFlagsGetterMock := NewMockflagsGetter(ctrl)
			abFlagsGetterMock.EXPECT().GetFlags().Return(models.ABFlags{
				Flags: tt.abFlags,
			})
			limiter := NewABFlagRequestLimiter(abFlagsGetterMock, tt.flagName)
			tt.wantFunc(t, limiter.Allow())
		})
	}
}
