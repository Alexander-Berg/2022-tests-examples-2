package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_localeComparator_compareLocale(t *testing.T) {
	type args struct {
		expected string
		got      string
	}

	createLocaleGetter := func(ctrl *gomock.Controller, locale string) *MocklocaleGetter {
		getter := NewMocklocaleGetter(ctrl)
		getter.EXPECT().GetLocale().Return(models.Locale{
			Value: locale,
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
				expected: "ru",
				got:      "ru",
			},
		},
		{
			name: "different locale",
			args: args{
				expected: "ru",
				got:      "ua",
			},
			wantErr: true,
			want:    "diff: ([ExpectedLocale], [GotLocale])",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			expectedLocale := createLocaleGetter(ctrl, tt.args.expected)
			gotLocale := createLocaleGetter(ctrl, tt.args.got)

			c := &localeComparator{}
			err := c.compareLocale(expectedLocale, gotLocale)
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
