package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_mordaContentComparator_compareMordaContent(t *testing.T) {
	type args struct {
		expected string
		got      string
	}

	createRequestGetter := func(ctrl *gomock.Controller, mordaContent string) *MockmordaContentGetter {
		getter := NewMockmordaContentGetter(ctrl)
		getter.EXPECT().GetMordaContent().Return(models.MordaContent{
			Value: mordaContent,
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
				expected: "big",
				got:      "big",
			},
		},
		{
			name: "different morda content",
			args: args{
				expected: "big",
				got:      "touch",
			},
			wantErr: true,
			want:    "diff: ([ExpectedMordaContent], [GotMordaContent])",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			expectedGetter := createRequestGetter(ctrl, tt.args.expected)
			gotGetter := createRequestGetter(ctrl, tt.args.got)

			c := &mordaContentComparator{}
			err := c.compareMordaContent(expectedGetter, gotGetter)
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
