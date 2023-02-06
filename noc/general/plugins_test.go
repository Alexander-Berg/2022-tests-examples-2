package plugins

import (
	"bytes"
	"fmt"
	"reflect"
	"testing"
)

func Test_formattingOutOfPlugin(t *testing.T) {
	type args struct {
		out    bytes.Buffer
		TTL    int
		plugin string
	}
	tests := []struct {
		name    string
		args    args
		want    []Host
		wantErr bool
	}{
		{
			name: "test-formatting-out-of-pluggin",
			args: args{
				out: func() bytes.Buffer {
					var out bytes.Buffer
					fmt.Fprintf(&out, "0.1 tst 172.28.102.213\n0.1 tst 2a02:6b8:0:40c:6c0c:5acc:2e9e:885\n")
					return out
				}(),
				TTL:    900,
				plugin: "default",
			},
			want: []Host{
				{
					Hostname: "tst",
					IP:       "172.28.102.213",
					TTL:      900,
				},
				{
					Hostname: "tst",
					IP:       "2a02:6b8:0:40c:6c0c:5acc:2e9e:885",
					TTL:      900,
				},
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := formattingOutOfPlugin(tt.args.out, tt.args.TTL, tt.args.plugin)
			if (err != nil) != tt.wantErr {
				t.Errorf("formattingOutOfPlugin() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("formattingOutOfPlugin() got = %v, want %v", got, tt.want)
			}
		})
	}
}
