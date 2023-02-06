package common

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetDevSuffix(t *testing.T) {
	type args struct {
		host string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "Simple dev host name",
			args: args{
				host: "morda-dev-v195.sas.yp-c.yandex.net",
			},
			want: "v195",
		},
		{
			name: "Localhost?",
			args: args{
				host: "localhost",
			},
			want: "",
		},
		{
			name: "Prod example",
			args: args{
				host: "stable-portal-mordago-13.sas.yp-c.yandex.net",
			},
			want: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := GetDevSuffix(tt.args.host)

			require.Equal(t, tt.want, got)
		})
	}
}
