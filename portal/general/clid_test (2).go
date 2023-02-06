package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_clidComparator_compareClid(t *testing.T) {
	type args struct {
		expected string
		got      string
	}

	createClidGetter := func(ctrl *gomock.Controller, clid string) *MockclidGetter {
		getter := NewMockclidGetter(ctrl)
		getter.EXPECT().GetClid().Return(models.Clid{
			Client: clid,
		})

		return getter
	}

	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "no diff",
			args: args{
				expected: "12893",
				got:      "12893",
			},
		},
		{
			name: "different clid",
			args: args{
				expected: "12893",
				got:      "32109",
			},
			wantErr: true,
			want:    "diff: ([ExpectedClid], [GotClid])",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			expectedClid := createClidGetter(ctrl, tt.args.expected)
			gotClid := createClidGetter(ctrl, tt.args.got)

			c := &clidComparator{}
			err := c.compareClid(expectedClid, gotClid)
			if tt.wantErr {
				require.Error(t, err)
				additionalErr, ok := err.(errorTemplated)
				require.True(t, ok)

				template, _ := additionalErr.GetTemplated()
				require.Equal(t, tt.want, template)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
