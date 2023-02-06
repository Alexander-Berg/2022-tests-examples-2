package devices

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_versionsComparator_Equal(t *testing.T) {
	type args struct {
		left  Version
		right Version
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "3.4.1 == 3.4.1",
			args: args{
				left:  []int{3, 4, 1},
				right: []int{3, 4, 1},
			},
			want: true,
		},
		{
			name: "3.4.1 == 3.4.2",
			args: args{
				left:  []int{3, 4, 1},
				right: []int{3, 4, 2},
			},
			want: false,
		},
		{
			name: "2 == 2.0.1",
			args: args{
				left:  []int{2},
				right: []int{2, 0, 1},
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			v := &versionsComparator{}

			got := v.Equal(tt.args.left, tt.args.right)

			require.Equal(t, tt.want, got)
		})
	}
}

func Test_versionsComparator_CompareByStrings(t *testing.T) {
	type args struct {
		left     string
		operator string
		right    string
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "0 < 1",
			args: args{
				left:     "0",
				operator: "<",
				right:    "1",
			},
			want: true,
		},
		{
			name: "0.0 <= 1.1",
			args: args{
				left:     "0.0",
				operator: "<=",
				right:    "1.1",
			},
			want: true,
		},
		{
			name: "1.1 < 1.2",
			args: args{
				left:     "1.1",
				operator: "<",
				right:    "1.2",
			},
			want: true,
		},
		{
			name: "2.3 > 1.2",
			args: args{
				left:     "2.3",
				operator: ">",
				right:    "1.2",
			},
			want: true,
		},
		{
			name: "3.4.1 > 3.4",
			args: args{
				left:     "3.4.1",
				operator: ">",
				right:    "3.4",
			},
			want: true,
		},
		{
			name: "2.3 >= 1.2",
			args: args{
				left:     "2.3",
				operator: ">=",
				right:    "1.2",
			},
			want: true,
		},
		{
			name: "3.4.1 > 3.4.0",
			args: args{
				left:     "3.4.1",
				operator: ">",
				right:    "3.4.0",
			},
			want: true,
		},
		{
			name: "3.4.2 > 3.4.1",
			args: args{
				left:     "3.4.2",
				operator: ">",
				right:    "3.4.1",
			},
			want: true,
		},
		{
			name: "3.4.2 >= 3.4.1",
			args: args{
				left:     "3.4.2",
				operator: ">=",
				right:    "3.4.1",
			},
			want: true,
		},
		{
			name: "4 >= 3.4.1",
			args: args{
				left:     "4",
				operator: ">=",
				right:    "3.4.1",
			},
			want: true,
		},
		{
			name: "4 > 3.4.1",
			args: args{
				left:     "4",
				operator: ">",
				right:    "3.4.1",
			},
			want: true,
		},
		{
			name: "4 < 5.0.0.0",
			args: args{
				left:     "4",
				operator: "<",
				right:    "5.0.0.0",
			},
			want: true,
		},
		{
			name: "4 < 4.0.0.0.1",
			args: args{
				left:     "4",
				operator: "<",
				right:    "4.0.0.0.1",
			},
			want: true,
		},
		{
			name: "4a < 4.0.0.0.1",
			args: args{
				left:     "4a",
				operator: "<",
				right:    "4.0.0.0.1",
			},
			want: true,
		},
		{
			name: "4..3 >= 4",
			args: args{
				left:     "4..3",
				operator: ">=",
				right:    "4",
			},
			want: true,
		},
		{
			name: "2.3 >= 2.3",
			args: args{
				left:     "2.3",
				operator: ">=",
				right:    "2.3",
			},
			want: true,
		},
		{
			name: "1 == 1",
			args: args{
				left:     "1",
				operator: "==",
				right:    "1",
			},
			want: true,
		},
		{
			name: "2 == 2.0",
			args: args{
				left:     "2",
				operator: "==",
				right:    "2.0",
			},
			want: true,
		},
		{
			name: "2.2 == 2.2.0",
			args: args{
				left:     "2.2",
				operator: "==",
				right:    "2.2.0",
			},
			want: true,
		},
		{
			name: "2 == 2.0.0.0.0",
			args: args{
				left:     "2",
				operator: "==",
				right:    "2.0.0.0.0",
			},
			want: true,
		},
		{
			name: "7.5 == 7.5",
			args: args{
				left:     "7.5",
				operator: "==",
				right:    "7.5",
			},
			want: true,
		},
		{
			name: "7.4 != 7.5",
			args: args{
				left:     "7.4",
				operator: "!=",
				right:    "7.5",
			},
			want: true,
		},
		{
			name: "7.4.5 != 7.5.5",
			args: args{
				left:     "7.4.5",
				operator: "!=",
				right:    "7.5.5",
			},
			want: true,
		},
		{
			name: "6.0 >= 6",
			args: args{
				left:     "6.0",
				operator: ">=",
				right:    "6",
			},
			want: true,
		},
		{
			name: "6.0 >= 6.0",
			args: args{
				left:     "6.0",
				operator: ">=",
				right:    "6.0",
			},
			want: true,
		},
		{
			name: "6.1.3 >= 6",
			args: args{
				left:     "6.1.3",
				operator: ">=",
				right:    "6",
			},
			want: true,
		},
		{
			name: "6.1.3c >= 6",
			args: args{
				left:     "6.1.3c",
				operator: ">=",
				right:    "6",
			},
			want: true,
		},
		{
			name: "7.0 >= 7",
			args: args{
				left:     "7.0",
				operator: ">=",
				right:    "7",
			},
			want: true,
		},
		{
			name: "7.0 >= 7.0",
			args: args{
				left:     "7.0",
				operator: ">=",
				right:    "7.0",
			},
			want: true,
		},
		{
			name: "7.0 >= 7",
			args: args{
				left:     "7.0",
				operator: ">=",
				right:    "7",
			},
			want: true,
		},
		{
			name: "7.4 != 7.4",
			args: args{
				left:     "7.4",
				operator: "!=",
				right:    "7.4",
			},
			want: false,
		},
		{
			name: "7.4 == 7.5",
			args: args{
				left:     "7.4",
				operator: "==",
				right:    "7.5",
			},
			want: false,
		},
		{
			name: "5.4 == 6.5",
			args: args{
				left:     "5.4",
				operator: "==",
				right:    "6.5",
			},
			want: false,
		},
		{
			name: "5.5 == 6.5",
			args: args{
				left:     "5.5",
				operator: "==",
				right:    "6.5",
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			v := &versionsComparator{}

			got := v.CompareByStrings(tt.args.left, tt.args.operator, tt.args.right)

			require.Equal(t, tt.want, got)
		})
	}
}
