package gortrpc

import (
	"encoding/json"
	"net"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"
)

func TestParseIpBin(t *testing.T) {
	t.Parallel()
	type args struct {
		s []byte
	}
	tests := []struct {
		name    string
		args    args
		want    IPBin
		wantErr bool
	}{
		{
			name:    "ipv4",
			args:    args{[]byte("_IP_BIN_<8d08b634>")},
			want:    IPBin(net.ParseIP("141.8.182.52")),
			wantErr: false,
		},
		{
			name:    "ipv4 str",
			args:    args{[]byte("141.8.182.52")},
			want:    IPBin(net.ParseIP("141.8.182.52")),
			wantErr: false,
		},
		{
			name:    "ipv6",
			args:    args{[]byte("_IP_BIN_<2a0206b8b000a20d0000000000000000>")},
			want:    IPBin(net.ParseIP("2a02:6b8:b000:a20d::")),
			wantErr: false,
		},
		{
			name:    "ipv6 str",
			args:    args{[]byte("2a02:6b8:b000:a20d::")},
			want:    IPBin(net.ParseIP("2a02:6b8:b000:a20d::")),
			wantErr: false,
		},
		{
			name:    "ipv6 bin escaped",
			args:    args{[]byte("_IP_BIN_\u003c2a0206b8b000a20d000000000000001e\u003e")},
			want:    IPBin(net.ParseIP("2a02:6b8:b000:a20d::1e")),
			wantErr: false,
		},
		{
			name:    "mailformed ipv4",
			args:    args{[]byte("_IP_BIN_<14dd>")},
			want:    IPBin{},
			wantErr: true,
		},
	}
	for _, test := range tests {
		tt := test
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			got, err := ParseIPBin(tt.args.s)
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
			require.True(t, got.Equal(tt.want),
				"ParseIPBin(), got: %v, want: %v", got, tt.want)
		})
	}
}
func TestParseIpBinFastJSON(t *testing.T) {
	t.Parallel()
	type args struct {
		s string
	}
	tests := []struct {
		name    string
		args    args
		want    IPBin
		wantErr bool
	}{
		{
			name:    "ipv4",
			args:    args{`{"ipBin": "_IP_BIN_<8d08b634>"}`},
			want:    IPBin(net.ParseIP("141.8.182.52")),
			wantErr: false,
		},
		{
			name:    "ipv6",
			args:    args{`{"ipBin": "_IP_BIN_<2a0206b8b000a20d0000000000000000>"}`},
			want:    IPBin(net.ParseIP("2a02:6b8:b000:a20d::")),
			wantErr: false,
		},
	}
	for _, test := range tests {
		tt := test
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			var p fastjson.Parser
			v, err := p.Parse(tt.args.s)
			require.NoError(t, err)
			got, err := ParseIPBin(v.GetStringBytes("ipBin"))
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
			require.True(t, got.Equal(tt.want),
				"fastjson ParseIPBin(), got: %v, want: %v", got, tt.want)
		})
	}
}

func TestIpBin_MarshalText(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name    string
		ipBin   IPBin
		want    []byte
		wantErr bool
	}{
		{
			name:    "ipv4",
			ipBin:   IPBin(net.ParseIP("141.8.182.52")),
			want:    []byte(`_IP_BIN_<8d08b634>`),
			wantErr: false,
		},
		{
			name:    "ipv6",
			ipBin:   IPBin(net.ParseIP("2a02:6b8:b000:a20d::")),
			want:    []byte(`_IP_BIN_<2a0206b8b000a20d0000000000000000>`),
			wantErr: false,
		},
		{
			name:    "ipv6_2",
			ipBin:   IPBin(net.ParseIP("2a02:6b8:b000:a20d::1e")),
			want:    []byte(`_IP_BIN_<2a0206b8b000a20d000000000000001e>`),
			wantErr: false,
		},
	}
	for _, test := range tests {
		tt := test
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			got, err := tt.ipBin.MarshalText()
			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
			require.Equal(t, string(tt.want), string(got))
		})
	}
}

func BenchmarkIpBinMarshal(b *testing.B) {
	type args struct {
		IPBin IPBin
	}
	benchmarks := []struct {
		name string
		args args
	}{
		{
			name: "1",
			args: args{IPBin(net.ParseIP("141.8.182.52"))},
		},
		{
			name: "2",
			args: args{IPBin(net.ParseIP("2a02:6b8:b000:a20d::1e"))},
		},
	}
	for _, bmf := range benchmarks {
		bm := bmf
		b.Run(bm.name, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				a, err := json.Marshal(&bm.args)
				if err != nil {
					b.Error(err)
				}
				if a == nil {
					b.Error("result is null")
				}
			}
		})
	}
}

func TestJsonPass(t *testing.T) {
	t.Parallel()
	type args struct {
		IPBin IPBin
	}
	tests := []struct {
		name string
		args args
	}{
		{
			name: "1",
			args: args{IPBin(net.ParseIP("141.8.182.52"))},
		},
		{
			name: "2",
			args: args{IPBin(net.ParseIP("2a02:6b8:b000:a20d::1e"))},
		},
	}
	for _, test := range tests {
		tt := test
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			b, err := json.Marshal(&tt.args)
			require.NoError(t, err, "can not encode")
			var a args
			err = json.Unmarshal(b, &a)
			require.NoError(t, err, "can not decode %v", string(b))
			require.True(t, a.IPBin.Equal(tt.args.IPBin),
				"encode/decode fail, got: %v, want: %v", a.IPBin, tt.args.IPBin)
		})
	}
}
