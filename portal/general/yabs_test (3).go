package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_yabsComparator_findBkFlagsDiff(t *testing.T) {
	type testCase struct {
		name     string
		expected models.Yabs
		got      models.Yabs
		want     yabsBkFlagDiff
	}

	cases := []testCase{
		{
			name:     "both nil",
			expected: models.Yabs{},
			got:      models.Yabs{},
			want:     yabsBkFlagDiff{},
		},
		{
			name: "both are empty",
			expected: models.Yabs{
				BKFlags: make(map[string]models.BKFlag),
			},
			got: models.Yabs{
				BKFlags: make(map[string]models.BKFlag),
			},
			want: yabsBkFlagDiff{},
		},
		{
			name: "missing key",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"missing_key": {},
					"found_key":   {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_key": {},
				},
			},
			want: yabsBkFlagDiff{
				missing: []string{"missing_key"},
			},
		},
		{
			name: "extra key",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_key": {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_key": {},
					"extra_key": {},
				},
			},
			want: yabsBkFlagDiff{
				extra: []string{"extra_key"},
			},
		},
		{
			name: "missing and extra key",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_key":   {},
					"missing_key": {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_key": {},
					"extra_key": {},
				},
			},
			want: yabsBkFlagDiff{
				missing: []string{"missing_key"},
				extra:   []string{"extra_key"},
			},
		},
		{
			name: "several keys",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"B":      {},
					"E":      {},
					"C":      {},
					"A":      {},
					"D":      {},
					"common": {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"common": {},
					"H":      {},
					"J":      {},
					"F":      {},
					"I":      {},
					"G":      {},
				},
			},
			want: yabsBkFlagDiff{
				missing: []string{"A", "B", "C", "D", "E"},
				extra:   []string{"F", "G", "H", "I", "J"},
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			c := &yabsComparator{}
			actualDiff := c.findBkFlagsDiff(tt.expected, tt.got)
			assert.Equal(t, tt.want, actualDiff)
		})
	}
}

func Test_yabsComparator_formatStringSlice(t *testing.T) {
	type testCase struct {
		name string
		arg  []string
		want string
	}

	cases := []testCase{
		{
			name: "empty slice",
			arg:  make([]string, 0),
			want: `[]`,
		},
		{
			name: "single item",
			arg:  []string{"apple"},
			want: `["apple"]`,
		},
		{
			name: "two items",
			arg:  []string{"apple", "banana"},
			want: `["apple", "banana"]`,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			c := &yabsComparator{}
			got := c.formatStringSlice(tt.arg)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_yabsComparator_compareYabsGetters(t *testing.T) {
	type testCase struct {
		name              string
		expected          models.Yabs
		got               models.Yabs
		wantErrorTemplate string
		wantErr           bool
	}

	createYabsMockGetter := func(ctrl *gomock.Controller, yabs models.Yabs) *MockyabsGetter {
		getter := NewMockyabsGetter(ctrl)
		getter.EXPECT().GetYabsOrErr().Return(yabs, nil)
		return getter
	}

	tests := []testCase{
		{
			name: "both are nil",
			expected: models.Yabs{
				BKFlags: nil,
			},
			got: models.Yabs{
				BKFlags: nil,
			},
			wantErr: false,
		},
		{
			name: "empty bk flags",
			expected: models.Yabs{
				BKFlags: make(map[string]models.BKFlag),
			},
			got: models.Yabs{
				BKFlags: make(map[string]models.BKFlag),
			},
			wantErr: false,
		},
		{
			name: "missing flags",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"missing_flag": {},
					"found_flag":   {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_flag": {},
				},
			},
			wantErr:           true,
			wantErrorTemplate: "BKFlags are not equal; ([ExpectedBKFlags], [GotBKFlags], [MissingBKFlags])",
		},
		{
			name: "extra flags",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_flag": {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_flag": {},
					"extra_flag": {},
				},
			},
			wantErr:           true,
			wantErrorTemplate: "BKFlags are not equal; ([ExpectedBKFlags], [GotBKFlags], [ExtraBKFlags])",
		},
		{
			name: "both missing and extra flags",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"missing_flag": {},
					"found_flag":   {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_flag": {},
					"extra_flag": {},
				},
			},
			wantErr:           true,
			wantErrorTemplate: "BKFlags are not equal; ([ExpectedBKFlags], [GotBKFlags], [MissingBKFlags], [ExtraBKFlags])",
		},
		{
			name: "equal flags",
			expected: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_flag": {},
				},
			},
			got: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"found_flag": {},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			defer ctrl.Finish()

			expectedGetter := createYabsMockGetter(ctrl, tt.expected)
			gotGetter := createYabsMockGetter(ctrl, tt.got)

			c := &yabsComparator{}
			err := c.compareYabsGetters(expectedGetter, gotGetter)
			if tt.wantErr {
				require.Error(t, err)
				additionalErr, ok := err.(errorTemplated)
				require.True(t, ok)

				template, _ := additionalErr.GetTemplated()
				require.Equal(t, tt.wantErrorTemplate, template)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
