package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_zoneComparator_compareZone(t *testing.T) {
	type args struct {
		expectedZone string
		expectedErr  error
		gotZone      string
		gotErr       error
	}

	createMockMordaZoneGetter := func(ctrl *gomock.Controller, zone string) *MockmordazoneGetter {
		getter := NewMockmordazoneGetter(ctrl)
		getter.EXPECT().GetMordaZone().Return(models.MordaZone{Value: zone})
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
				expectedZone: "ru",
				gotZone:      "ru",
			},
		},
		{
			name: "different zones",
			args: args{
				expectedZone: "ru",
				gotZone:      "en",
			},
			wantErr: true,
			want:    "diff: ([ExpectedMordaZone], [GotMordaZone])",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			expectedGetter := createMockMordaZoneGetter(ctrl, tt.args.expectedZone)
			gotGetter := createMockMordaZoneGetter(ctrl, tt.args.gotZone)

			c := &zoneComparator{}
			err := c.compareZone(expectedGetter, gotGetter)
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
