package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_deviceComparator_compareDevice(t *testing.T) {
	type args struct {
		IsGramps      bool
		IsTouchGramps bool
		DPI           float32
		ScaleFactor   float32
		Screen        models.Screen
	}

	createMockComparableContexts := func(ctrl *gomock.Controller, expectedArgs, gotArgs args) (
		*MockComparableContextExpected, *MockComparableContextGot) {
		expected := NewMockComparableContextExpected(ctrl)
		expected.EXPECT().GetDevice().Return(models.Device{
			BrowserDesc: &models.BrowserDesc{
				IsGramps:      expectedArgs.IsGramps,
				IsTouchGramps: expectedArgs.IsTouchGramps,
				DPI:           expectedArgs.DPI,
				Screen:        expectedArgs.Screen,
			},
		})
		expected.EXPECT().GetPerlScaleFactor().Return(expectedArgs.ScaleFactor)

		got := NewMockComparableContextGot(ctrl)
		got.EXPECT().GetDevice().Return(models.Device{
			BrowserDesc: &models.BrowserDesc{
				IsGramps:      gotArgs.IsGramps,
				IsTouchGramps: gotArgs.IsTouchGramps,
				DPI:           gotArgs.DPI,
				Screen:        gotArgs.Screen,
			},
		})
		got.EXPECT().GetPerlScaleFactor().Return(gotArgs.ScaleFactor)

		return expected, got
	}

	tests := []struct {
		name         string
		expectedArgs args
		gotArgs      args
		wantErr      bool
		want         string
	}{
		{
			name: "everyone is equal",
			expectedArgs: args{
				IsGramps:      true,
				IsTouchGramps: true,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			gotArgs: args{
				IsGramps:      true,
				IsTouchGramps: true,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: false,
		},
		{
			name: "everyone is not equal",
			expectedArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           1,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 2, Y: 3},
			},
			gotArgs: args{
				IsGramps:      true,
				IsTouchGramps: true,
				DPI:           -1,
				ScaleFactor:   0.5,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: true,
			want:    "collapsed errors:\n\tIsGramps not equal; ([ExpectedIsGramps], [GotIsGramps])\n\tIsTouchGramps not equal; ([ExpectedIsTouchGramps], [GotIsTouchGramps])\n\tDPI not equal; ([ExpectedDPI], [GotDPI])\n\tScaleFactor not equal; ([ExpectedScaleFactor], [GotScaleFactor])\n\tScreen not equal; ([ExpectedScreen], [GotScreen])",
		},
		{
			name: "IsGramps is not equal",
			expectedArgs: args{
				IsGramps:      true,
				IsTouchGramps: true,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			gotArgs: args{
				IsGramps:      false,
				IsTouchGramps: true,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: true,
			want:    "IsGramps not equal; ([ExpectedIsGramps], [GotIsGramps])",
		},
		{
			name: "IsTouchGramps is not equal",
			expectedArgs: args{
				IsGramps:      true,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			gotArgs: args{
				IsGramps:      true,
				IsTouchGramps: true,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: true,
			want:    "IsTouchGramps not equal; ([ExpectedIsTouchGramps], [GotIsTouchGramps])",
		},
		{
			name: "DPI is not equal",
			expectedArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.7,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			gotArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: true,
			want:    "DPI not equal; ([ExpectedDPI], [GotDPI])",
		},
		{
			name: "ScaleFactor not equal",
			expectedArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			gotArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   0.5,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: true,
			want:    "ScaleFactor not equal; ([ExpectedScaleFactor], [GotScaleFactor])",
		},
		{
			name: "Screen.X is not equal",
			expectedArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 0, Y: 2},
			},
			gotArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: true,
			want:    "Screen not equal; ([ExpectedScreen], [GotScreen])",
		},
		{
			name: "Screen.Y is not equal",
			expectedArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 1},
			},
			gotArgs: args{
				IsGramps:      false,
				IsTouchGramps: false,
				DPI:           0.5,
				ScaleFactor:   1,
				Screen:        models.Screen{X: 1, Y: 2},
			},
			wantErr: true,
			want:    "Screen not equal; ([ExpectedScreen], [GotScreen])",
		},
		{
			name:         "empty device",
			expectedArgs: args{},
			gotArgs:      args{},
			wantErr:      false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			expectedGetter, gotGetter := createMockComparableContexts(ctrl, tt.expectedArgs, tt.gotArgs)

			c := &deviceComparator{}
			err := c.compareDevice(expectedGetter, gotGetter)

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

func Test_deviceComparator_compareIsGrampsField(t *testing.T) {
	type args struct {
		field            string
		expectedIsGramps bool
		gotIsGramps      bool
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
		want    string
	}{
		{
			name: "true true",
			args: args{
				field:            "IsGramps",
				expectedIsGramps: true,
				gotIsGramps:      true,
			},
			wantErr: false,
		},
		{
			name: "true false",
			args: args{
				field:            "IsGramps",
				expectedIsGramps: true,
				gotIsGramps:      false,
			},
			wantErr: true,
			want:    "IsGramps not equal; ([ExpectedIsGramps], [GotIsGramps])",
		},
		{
			name: "false true",
			args: args{
				field:            "IsTouchGramps",
				expectedIsGramps: false,
				gotIsGramps:      true,
			},
			wantErr: true,
			want:    "IsTouchGramps not equal; ([ExpectedIsTouchGramps], [GotIsTouchGramps])",
		},
		{
			name: "false, false",
			args: args{
				field:            "IsTouchGramps",
				expectedIsGramps: false,
				gotIsGramps:      false,
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &deviceComparator{}
			err := c.compareIsGrampsField(tt.args.field, tt.args.expectedIsGramps, tt.args.gotIsGramps)

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

func Test_deviceComparator_compareDPI(t *testing.T) {
	type args struct {
		expectedDPI float32
		gotDPI      float32
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
		want    string
	}{
		{
			name: "equal",
			args: args{
				expectedDPI: 2.3,
				gotDPI:      2.3,
			},
			wantErr: false,
		},
		{
			name: "not equal",
			args: args{
				expectedDPI: 1.1,
				gotDPI:      0.5,
			},
			wantErr: true,
			want:    "DPI not equal; ([ExpectedDPI], [GotDPI])",
		},
		{
			name: "different signs",
			args: args{
				expectedDPI: -3.4,
				gotDPI:      3.4,
			},
			wantErr: true,
			want:    "DPI not equal; ([ExpectedDPI], [GotDPI])",
		},
		{
			name: "zeros",
			args: args{
				expectedDPI: 0,
				gotDPI:      -0,
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &deviceComparator{}
			err := c.compareDPI(tt.args.expectedDPI, tt.args.gotDPI)

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

func Test_deviceComparator_compareScaleFactor(t *testing.T) {
	type args struct {
		expectedScaleFactor float32
		gotScaleFactor      float32
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
		want    string
	}{
		{
			name: "equal",
			args: args{
				expectedScaleFactor: 2.3,
				gotScaleFactor:      2.3,
			},
			wantErr: false,
		},
		{
			name: "not equal",
			args: args{
				expectedScaleFactor: 1.1,
				gotScaleFactor:      0.5,
			},
			wantErr: true,
			want:    "ScaleFactor not equal; ([ExpectedScaleFactor], [GotScaleFactor])",
		},
		{
			name: "different signs",
			args: args{
				expectedScaleFactor: -3.4,
				gotScaleFactor:      3.4,
			},
			wantErr: true,
			want:    "ScaleFactor not equal; ([ExpectedScaleFactor], [GotScaleFactor])",
		},
		{
			name: "zeros",
			args: args{
				expectedScaleFactor: 0,
				gotScaleFactor:      -0,
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &deviceComparator{}
			err := c.compareScaleFactor(tt.args.expectedScaleFactor, tt.args.gotScaleFactor)

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

func Test_deviceComparator_compareScreen(t *testing.T) {
	type args struct {
		expectedScreen models.Screen
		gotScreen      models.Screen
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
		want    string
	}{
		{
			name: "equal",
			args: args{
				expectedScreen: models.Screen{X: 2, Y: 3},
				gotScreen:      models.Screen{X: 2, Y: 3},
			},
			wantErr: false,
		},
		{
			name: "not equal Y",
			args: args{
				expectedScreen: models.Screen{X: 2, Y: 3},
				gotScreen:      models.Screen{X: 2, Y: 5},
			},
			wantErr: true,
			want:    "Screen not equal; ([ExpectedScreen], [GotScreen])",
		},
		{
			name: "not equal X",
			args: args{
				expectedScreen: models.Screen{X: 2, Y: 3},
				gotScreen:      models.Screen{X: 5, Y: 3},
			},
			wantErr: true,
			want:    "Screen not equal; ([ExpectedScreen], [GotScreen])",
		},
		{
			name: "not equal X and Y",
			args: args{
				expectedScreen: models.Screen{X: 2, Y: 3},
				gotScreen:      models.Screen{X: 5, Y: 5},
			},
			wantErr: true,
			want:    "Screen not equal; ([ExpectedScreen], [GotScreen])",
		},
		{
			name: "zeros",
			args: args{
				expectedScreen: models.Screen{X: 0, Y: 0},
				gotScreen:      models.Screen{X: 0, Y: 0},
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &deviceComparator{}
			err := c.compareScreen(tt.args.expectedScreen, tt.args.gotScreen)

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

func Test_deviceComparator_force(t *testing.T) {
	type args struct {
		expected models.Device
		got      models.Device
	}
	tests := []struct {
		name    string
		args    args
		want    models.Device
		wantErr bool
	}{
		{
			name: "no uatraits in perl, other fields are different",
			args: args{
				expected: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits:        nil,
						IsGramps:      false,
						IsTouchGramps: true,
						UserAgent:     "",
						DPI:           4.2,
						Screen:        models.Screen{X: 1, Y: 2},
					},
				},
				got: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits: map[string]string{
							"os":        "ios",
							"osVersion": "11.1",
						},
						IsGramps:      true,
						IsTouchGramps: false,
						UserAgent:     "iOS Safari",
						DPI:           4.5,
						Screen:        models.Screen{X: 2, Y: 3},
					},
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits: map[string]string{
						"os":        "ios",
						"osVersion": "11.1",
					},
					IsGramps:      false,
					IsTouchGramps: true,
					UserAgent:     "iOS Safari",
					DPI:           4.2,
					Screen:        models.Screen{X: 1, Y: 2},
				},
			},
		},
		{
			name: "nil browserDesc in go",
			args: args{
				expected: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits:        nil,
						IsGramps:      false,
						IsTouchGramps: true,
						UserAgent:     "",
						DPI:           4.2,
						Screen:        models.Screen{X: 1, Y: 2},
					},
				},
				got: models.Device{
					BrowserDesc: nil,
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits:        nil,
					IsGramps:      false,
					IsTouchGramps: true,
					UserAgent:     "",
					DPI:           4.2,
					Screen:        models.Screen{X: 1, Y: 2},
				},
			},
		},
		{
			name: "nil browserDesc in perl",
			args: args{
				expected: models.Device{
					BrowserDesc: nil,
				},
				got: models.Device{
					BrowserDesc: &models.BrowserDesc{
						Traits:        nil,
						IsGramps:      false,
						IsTouchGramps: true,
						UserAgent:     "",
						DPI:           4.2,
						Screen:        models.Screen{X: 1, Y: 2},
					},
				},
			},
			want: models.Device{
				BrowserDesc: &models.BrowserDesc{
					Traits:        nil,
					IsGramps:      false,
					IsTouchGramps: false,
					UserAgent:     "",
					DPI:           0,
					Screen:        models.Screen{},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			expectedContextMock := NewMockComparableContextExpected(ctrl)
			expectedContextMock.EXPECT().GetDevice().Return(tt.args.expected).Times(1)
			gotContextMock := NewMockForceableContextGot(ctrl)
			gotContextMock.EXPECT().GetDevice().Return(tt.args.got).Times(1)
			gotContextMock.EXPECT().ForceDevice(tt.want).Times(1)

			c := &deviceComparator{}

			gotErr := c.force(expectedContextMock, gotContextMock)
			if tt.wantErr {
				require.Error(t, gotErr)
			} else {
				require.NoError(t, gotErr)
			}
		})
	}
}
