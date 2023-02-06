package newinternal

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestReplaceCGIParam(t *testing.T) {
	type args struct {
		rawURL string
		key    string
		value  string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "Got zero key",
			args: args{
				rawURL: "htpp://test.com/foo?test=oops",
				key:    "",
				value:  "some_value",
			},
			want: "htpp://test.com/foo?test=oops",
		},
		{
			name: "New param",
			args: args{
				rawURL: "htpp://test.com/foo?test=oops",
				key:    "some_key",
				value:  "some_value",
			},
			want: "htpp://test.com/foo?some_key=some_value&test=oops",
		},
		{
			name: "Replace cgi param",
			args: args{
				rawURL: "htpp://test.com/foo?test=oops",
				key:    "test",
				value:  "some_value",
			},
			want: "htpp://test.com/foo?test=some_value",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ReplaceCGIParam(tt.args.rawURL, tt.args.key, tt.args.value)

			require.Equal(t, tt.want, got)
		})
	}
}
