package req

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_jsonNumber_UnmarshalJSON(t *testing.T) {
	type testStruct struct {
		X jsonNumber
	}

	tests := []struct {
		name string
		json string
		want string
	}{
		{
			name: "int number",
			json: `{
				"x": 42
			}`,
			want: "42",
		},
		{
			name: "float number",
			json: `{
				"x": 42.42
			}`,
			want: "42.42",
		},
		{
			name: "long number",
			json: `{
				"x": 42424242424242424242424242424242
			}`,
			want: "42424242424242424242424242424242",
		},
		{
			name: "long negative number",
			json: `{
				"x": -42424242424242424242424242424242
			}`,
			want: "-42424242424242424242424242424242",
		},
		{
			name: "string",
			json: `{
				"x": "42"
			}`,
			want: "42",
		},
		{
			name: "non-numeric string",
			json: `{
				"x": "Hello World"
			}`,
			want: "Hello World",
		},
		{
			name: "double quoted string",
			json: `{
				"x": "\"42\""
			}`,
			want: "\"42\"",
		},
		{
			name: "object",
			json: `{
				"x": {}
			}`,
			want: "{}",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			str := testStruct{}

			err := json.Unmarshal([]byte(tt.json), &str)
			require.NoError(t, err)
			require.Equal(t, tt.want, str.X.String())
		})
	}
}
