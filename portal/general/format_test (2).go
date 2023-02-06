package compare

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_formatStringSlice(t *testing.T) {
	type testCase struct {
		name string
		arg  []string
		want string
	}

	cases := []testCase{
		{
			name: "empty slice",
			arg:  make([]string, 0),
			want: `[]`,
		},
		{
			name: "single item",
			arg:  []string{"apple"},
			want: `["apple"]`,
		},
		{
			name: "two items",
			arg:  []string{"apple", "banana"},
			want: `["apple", "banana"]`,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			got := formatStringSlice(tt.arg)
			assert.Equal(t, tt.want, got)
		})
	}
}
