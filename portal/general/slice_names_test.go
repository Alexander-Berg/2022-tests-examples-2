package compare

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Test_sliceNamesComparator_diffCompareSliceNames(t *testing.T) {
	type args struct {
		expected []string
		got      []string
	}
	tests := []struct {
		name        string
		args        args
		wantExtra   []string
		wantMissing []string
	}{
		{
			name:        "both nil",
			wantExtra:   []string{},
			wantMissing: []string{},
		},
		{
			name: "both empty",
			args: args{
				expected: []string{},
				got:      []string{},
			},
			wantExtra:   []string{},
			wantMissing: []string{},
		},
		{
			name: "only extra",
			args: args{
				expected: []string{"1", "2"},
				got:      []string{"1", "2", "3", "4"},
			},
			wantExtra:   []string{"3", "4"},
			wantMissing: []string{},
		},
		{
			name: "only missing",
			args: args{
				expected: []string{"1", "2"},
				got:      nil,
			},
			wantExtra:   []string{},
			wantMissing: []string{"1", "2"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &sliceNamesComparator{}
			gotExtra, gotMissing := c.diffCompareSliceNames(tt.args.expected, tt.args.got)

			assert.Equal(t, tt.wantExtra, gotExtra)
			assert.Equal(t, tt.wantMissing, gotMissing)
		})
	}
}

func Test_sliceNamesComparator_formatCompareSliceNamesError(t *testing.T) {
	type args struct {
		extra   []string
		missing []string
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name:    "nil args",
			wantErr: false,
		},
		{
			name: "no diff",
			args: args{
				extra:   []string{},
				missing: []string{},
			},
			wantErr: false,
		},
		{
			name: "extra and missing",
			args: args{
				extra:   []string{"1", "2"},
				missing: []string{"3"},
			},
			want:    "diff: ([ExtraSliceNames], [MissingSliceNames], [ExpectedSliceNames], [GotSliceNames])",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			co := &sliceNamesComparator{}
			err := co.formatCompareSliceNamesError([]string{}, []string{}, tt.args.extra, tt.args.missing)

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

func Test_sliceNamesComparator_compareSliceNames(t *testing.T) {
	type args struct {
		expected []string
		got      []string
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name:    "nil slices",
			wantErr: false,
		},
		{
			name: "same empty slices",
			args: args{
				expected: []string{},
				got:      []string{},
			},
			wantErr: false,
		},
		{
			name: "missing only",
			args: args{
				expected: []string{"1", "2"},
				got:      []string{},
			},
			want:    "diff: ([MissingSliceNames], [ExpectedSliceNames], [GotSliceNames])",
			wantErr: true,
		},
		{
			name: "extra only",
			args: args{
				expected: []string{"1"},
				got:      []string{"1", "2", "3"},
			},
			want:    "diff: ([ExtraSliceNames], [ExpectedSliceNames], [GotSliceNames])",
			wantErr: true,
		},
		{
			name: "extra and missing",
			args: args{
				expected: []string{"1", "2"},
				got:      []string{"3", "4"},
			},
			want:    "diff: ([ExtraSliceNames], [MissingSliceNames], [ExpectedSliceNames], [GotSliceNames])",
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &sliceNamesComparator{}
			err := c.compareSliceNames(tt.args.expected, tt.args.got)

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
