package lbs

import (
	"net/url"
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_paramsValidator_parseCGIValue(t *testing.T) {
	type args struct {
		name string
		cgi  url.Values
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "wifi success",
			args: args{
				name: "wifi",
				cgi: map[string][]string{
					"wifi": {"ec:43:f6:06:2e:a8,-62;e2:43:f6:06:2e:a8,-61;74:da:88:cf:54:53,-85;18:0f:76:90:33:dd,-84;58:8b:f3:6b:c1:90,-93;50:ff:20:30:a3:15,-89;20:4e:7f:7d:9b:6f,-92"},
				},
			},
			want: "ec:43:f6:06:2e:a8,-62;e2:43:f6:06:2e:a8,-61;74:da:88:cf:54:53,-85;18:0f:76:90:33:dd,-84;58:8b:f3:6b:c1:90,-93;50:ff:20:30:a3:15,-89;20:4e:7f:7d:9b:6f,-92",
		},
		{
			name: "wifi failed",
			args: args{
				name: "wifi",
				cgi: map[string][]string{
					"wifi": {"abc"},
				},
			},
			want: "",
		},
		{
			name: "cellid success",
			args: args{
				name: "cellid",
				cgi: map[string][]string{
					"cellid": {"250,01,108943876,50542,-115"},
				},
			},
			want: "250,01,108943876,50542,-115",
		},
		{
			name: "cellid failed",
			args: args{
				name: "cellid",
				cgi: map[string][]string{
					"cellid": {"250,01,108943876,50542,-115"},
				},
			},
			want: "250,01,108943876,50542,-115",
		},
		{
			name: "unknown name",
			args: args{
				name: "name",
				cgi: map[string][]string{
					"name": {"123"},
				},
			},
			want: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &paramsValidator{}
			assert.Equal(t, tt.want, p.parseCGIValue(tt.args.name, tt.args.cgi))
		})
	}
}

func Test_paramsValidator_Validate(t *testing.T) {
	type args struct {
		cgi url.Values
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "success wifi and cellid",
			args: args{
				cgi: map[string][]string{
					"wifi":   {"ec:43:f6:06:2e:a8,-62;e2:43:f6:06:2e:a8,-61;74:da:88:cf:54:53,-85;18:0f:76:90:33:dd,-84;58:8b:f3:6b:c1:90,-93;50:ff:20:30:a3:15,-89;20:4e:7f:7d:9b:6f,-92"},
					"cellid": {"250,01,108943876,50542,-115"},
				},
			},
			want: true,
		},
		{
			name: "success wifi",
			args: args{
				cgi: map[string][]string{
					"wifi": {"ec:43:f6:06:2e:a8,-62;e2:43:f6:06:2e:a8,-61;74:da:88:cf:54:53,-85;18:0f:76:90:33:dd,-84;58:8b:f3:6b:c1:90,-93;50:ff:20:30:a3:15,-89;20:4e:7f:7d:9b:6f,-92"},
				},
			},
			want: true,
		},
		{
			name: "success cellid",
			args: args{
				cgi: map[string][]string{
					"cellid": {"250,01,108943876,50542,-115"},
				},
			},
			want: true,
		},
		{
			name: "success failed",
			args: args{
				cgi: map[string][]string{},
			},
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &paramsValidator{}
			assert.Equal(t, tt.want, p.Validate(tt.args.cgi))
		})
	}
}
