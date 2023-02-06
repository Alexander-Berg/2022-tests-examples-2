package handler

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_checker_Check(t *testing.T) {
	type args struct {
		path string
	}

	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "root path",
			args: args{
				path: "/",
			},
			want: true,
		}, {
			name: "root path 2",
			args: args{
				path: "//",
			},
			want: true,
		},
		{
			name: "m path",
			args: args{
				path: "/m",
			},
			want: true,
		},
		{
			name: "M path",
			args: args{
				path: "/M",
			},
			want: true,
		},
		{
			name: "m path 2",
			args: args{
				path: "/m/",
			},
			want: true,
		},
		{
			name: "m path 3",
			args: args{
				path: "/m//",
			},
			want: true,
		},
		{
			name: "m path 4",
			args: args{
				path: "//m/",
			},
			want: true,
		},
		{
			name: "d path",
			args: args{
				path: "/d",
			},
			want: true,
		},
		{
			name: "beta path",
			args: args{
				path: "/beta",
			},
			want: true,
		},
		{
			name: "ua path",
			args: args{
				path: "/ua",
			},
			want: true,
		},
		{
			name: "not exist path",
			args: args{
				path: "/not/exist/path",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &checker{}

			assert.Equal(t, tt.want, c.Check(tt.args.path))
		})
	}
}
