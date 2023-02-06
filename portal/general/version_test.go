package devices

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNewVersion(t *testing.T) {
	type args struct {
		s string
	}
	tests := []struct {
		name string
		args args
		want Version
	}{
		{
			name: "simple",
			args: args{
				s: "1.2.3.4.5",
			},
			want: []int{1, 2, 3, 4, 5},
		},
		{
			name: "one zero in the end",
			args: args{
				s: "1.35.4.0",
			},
			want: []int{1, 35, 4},
		},
		{
			name: "several zeros in the end",
			args: args{
				s: "1.543.123.0.0.0.0.0.00",
			},
			want: []int{1, 543, 123},
		},
		{
			name: "several zeros in the middle",
			args: args{
				s: "5.0.12.0.0.2",
			},
			want: []int{5, 0, 12, 0, 0, 2},
		},
		{
			name: "zeros in the end and in the middle",
			args: args{
				s: "1.0.0.1.0.0",
			},
			want: []int{1, 0, 0, 1},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewVersion(tt.args.s)

			require.Equal(t, tt.want, got)
		})
	}
}
