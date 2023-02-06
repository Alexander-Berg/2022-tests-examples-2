package compare

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Test_abFlagsComparator_compareABFlags(t *testing.T) {
	type args struct {
		expected map[string]string
		got      map[string]string
	}

	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "same nil flags",
			args: args{
				expected: nil,
				got:      nil,
			},
			wantErr: false,
		},
		{
			name: "same empty flags",
			args: args{
				expected: map[string]string{},
				got:      map[string]string{},
			},
			wantErr: false,
		},
		{
			name: "same flags",
			args: args{
				expected: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
				got: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
			},
			wantErr: false,
		},
		{
			name: "one extra flag",
			args: args{
				expected: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
				got: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
					"name":  "vasya",
				},
			},
			wantErr: true,
			want:    "diff: ([ExtraABFlags], [ExpectedABFlags], [GotABFlags])",
		},
		{
			name: "several extra flags",
			args: args{
				expected: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
				got: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
					"name":  "vasya",
					"lang":  "java",
				},
			},
			wantErr: true,
			want:    "diff: ([ExtraABFlags], [ExpectedABFlags], [GotABFlags])",
		},
		{
			name: "several missing flags, one different value",
			args: args{
				expected: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
				got: map[string]string{
					"city": "spb",
				},
			},
			wantErr: true,
			want:    "diff: ([MissingABFlags], [DifferentABFlags], [ExpectedABFlags], [GotABFlags])",
		},
		{
			name: "missing, expected and different flags",
			args: args{
				expected: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
				got: map[string]string{
					"city": "spb",
					"car":  "tesla",
					"name": "vasya",
					"lang": "java",
				},
			},
			wantErr: true,
			want:    "diff: ([ExtraABFlags], [MissingABFlags], [DifferentABFlags], [ExpectedABFlags], [GotABFlags])",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &abFlagsComparator{}
			err := c.compareFlags(tt.args.expected, tt.args.got)

			if !tt.wantErr {
				require.NoError(t, err)
			} else {
				require.Error(t, err)
				errTemplated, ok := err.(errorTemplated)
				require.True(t, ok)

				template, _ := errTemplated.GetTemplated()
				require.Equal(t, tt.want, template)
			}
		})
	}
}

func Test_abFlagsComparator_diffCompareFlags(t *testing.T) {
	type args struct {
		expected map[string]string
		got      map[string]string
	}
	tests := []struct {
		name        string
		args        args
		wantExtra   keyValueSlice
		wantMissing keyValueSlice
		wantDiff    keyExpectedGotSlice
	}{
		{
			name: "same flags",
			args: args{
				expected: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
				got: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
			},
			wantExtra:   nil,
			wantMissing: nil,
			wantDiff:    nil,
		},
		{
			name: "missing, expected and different flags",
			args: args{
				expected: map[string]string{
					"city":  "moscow",
					"car":   "bmw",
					"phone": "nokia",
				},
				got: map[string]string{
					"city": "spb",
					"car":  "tesla",
					"name": "vasya",
					"lang": "java",
				},
			},
			wantExtra: keyValueSlice{
				{"lang", "java"},
				{"name", "vasya"},
			},
			wantMissing: keyValueSlice{
				{"phone", "nokia"},
			},
			wantDiff: keyExpectedGotSlice{
				{"car", "bmw", "tesla"},
				{"city", "moscow", "spb"},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &abFlagsComparator{}
			gotExtra, gotMissing, gotDiff := c.diffCompareFlags(tt.args.expected, tt.args.got)

			assert.Equal(t, tt.wantExtra, gotExtra)
			assert.Equal(t, tt.wantMissing, gotMissing)
			assert.Equal(t, tt.wantDiff, gotDiff)
		})
	}
}

func Test_abFlagsComparator_formatCompareFlags(t *testing.T) {
	type args struct {
		extra   keyValueSlice
		missing keyValueSlice
		diff    keyExpectedGotSlice
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name:    "no diff",
			args:    args{nil, nil, nil},
			wantErr: false,
		},
		{
			name: "missing, expected and different flags",
			args: args{
				extra: keyValueSlice{
					{"lang", "java"},
					{"name", "vasya"},
				},
				missing: keyValueSlice{
					{"phone", "nokia"},
				},
				diff: keyExpectedGotSlice{
					{"car", "bmw", "tesla"},
					{"city", "moscow", "spb"},
				},
			},
			want:    "diff: ([ExtraABFlags], [MissingABFlags], [DifferentABFlags], [ExpectedABFlags], [GotABFlags])",
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &abFlagsComparator{}
			err := c.formatCompareFlagsError(nil, nil, tt.args.extra, tt.args.missing, tt.args.diff)

			if !tt.wantErr {
				require.NoError(t, err)
			} else {
				require.Error(t, err)
				errTemplated, ok := err.(errorTemplated)
				require.True(t, ok)

				template, _ := errTemplated.GetTemplated()
				require.Equal(t, tt.want, template)
			}
		})
	}
}
