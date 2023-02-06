package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

func Test_bigBComparator_compareBigB(t *testing.T) {
	createBigBGetter := func(ctrl *gomock.Controller, bigBModel models.BigB) *MockbigBGetter {
		getter := NewMockbigBGetter(ctrl)
		getter.EXPECT().GetBigBOrErr().Return(bigBModel, nil).AnyTimes()
		getter.EXPECT().GetBigB().Return(bigBModel).AnyTimes()

		return getter
	}

	tests := []struct {
		name string

		expected models.BigB
		got      models.BigB

		wantErr bool
	}{
		{
			name:     "both are undef",
			expected: models.BigB{},
			got:      models.BigB{},
			wantErr:  false,
		},
		{
			name: "equal",
			expected: models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"557:333": {},
					},
				},
			},
			got: models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"557:333": {},
					},
				},
			},
			wantErr: false,
		},
		{
			name: "not equal",
			expected: models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"557:333": {},
					},
				},
			},
			got: models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
				},
			},
			wantErr: true,
		},
		{
			name:     "same big response",
			expected: prepared.TestModelBigBVer1,
			got:      prepared.TestModelBigBVer1,
			wantErr:  false,
		},
		{
			name:     "not equal big response",
			expected: prepared.TestModelBigBVer1,
			got:      prepared.TestModelBigBVer2,
			wantErr:  true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			expectedGetter := createBigBGetter(ctrl, tt.expected)
			gotGetter := createBigBGetter(ctrl, tt.got)

			c := &bigBComparator{}
			err := c.compareBigB(expectedGetter, gotGetter)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
