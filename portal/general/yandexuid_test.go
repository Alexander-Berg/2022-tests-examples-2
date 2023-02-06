package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_yandexUIDComparator_compareYandexUID(t *testing.T) {
	type args struct {
		expected string
		got      string
	}

	createMockYaCookiesGetter := func(ctrl *gomock.Controller, yandexUID string) *MockyaCookiesGetter {
		getter := NewMockyaCookiesGetter(ctrl)
		getter.EXPECT().GetYaCookies().Return(models.YaCookies{YandexUID: yandexUID})
		return getter
	}

	tests := []struct {
		name    string
		args    args
		wantErr bool
		want    string
	}{
		{
			name: "no diff",
			args: args{
				expected: "1234567890987",
				got:      "1234567890987",
			},
		},
		{
			name: "different yandexuid",
			args: args{
				expected: "1234567890987",
				got:      "1234567890986",
			},
			wantErr: true,
			want:    "diff: ([ExpectedYandexUID], [GotYandexUID])",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			expectedGetter := createMockYaCookiesGetter(ctrl, tt.args.expected)
			gotGetter := createMockYaCookiesGetter(ctrl, tt.args.got)

			c := &yandexUIDComparator{}
			err := c.compareYandexUIDs(expectedGetter, gotGetter)
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
