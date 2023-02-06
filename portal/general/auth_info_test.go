package blackbox

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_authString_UnmarshalJSON(t *testing.T) {
	tests := []struct {
		name    string
		data    []byte
		want    authString
		wantErr bool
	}{
		{
			name:    "simple string",
			data:    []byte(`"some text"`),
			want:    "some text",
			wantErr: false,
		},
		{
			name:    "empty string",
			data:    []byte(`""`),
			want:    "",
			wantErr: false,
		},
		{
			name:    "null",
			data:    []byte(`null`),
			want:    "",
			wantErr: false,
		},
		{
			name:    "zero",
			data:    []byte(`0`),
			want:    "0",
			wantErr: false,
		},
		{
			name:    "big number",
			data:    []byte(`123123123`),
			want:    "123123123",
			wantErr: false,
		},
		{
			name:    "float number",
			data:    []byte(`1.1`),
			want:    "",
			wantErr: true,
		},
		{
			name:    "object",
			data:    []byte(`{"key": "value"}`),
			want:    "",
			wantErr: true,
		},
		{
			name:    "array",
			data:    []byte(`[1,2,3]`),
			want:    "",
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var str authString
			err := str.UnmarshalJSON(tt.data)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.Equal(t, tt.want, str)
				require.NoError(t, err)
			}
		})
	}
}

func Test_authInt_UnmarshalJSON(t *testing.T) {
	tests := []struct {
		name    string
		data    []byte
		want    authInt
		wantErr bool
	}{
		{
			name:    "simple number",
			data:    []byte(`1`),
			want:    1,
			wantErr: false,
		},
		{
			name:    "zero",
			data:    []byte(`0`),
			want:    0,
			wantErr: false,
		},
		{
			name:    "string number",
			data:    []byte(`"123"`),
			want:    123,
			wantErr: false,
		},
		{
			name:    "zero in string",
			data:    []byte(`"0"`),
			want:    0,
			wantErr: false,
		},
		{
			name:    "empty string",
			data:    []byte(`""`),
			want:    0,
			wantErr: true,
		},
		{
			name:    "float in string",
			data:    []byte(`"1.1"`),
			want:    0,
			wantErr: true,
		},
		{
			name:    "object",
			data:    []byte(`{"key": "value"}`),
			want:    0,
			wantErr: true,
		},
		{
			name:    "array",
			data:    []byte(`[1,2,3]`),
			want:    0,
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var num authInt
			err := num.UnmarshalJSON(tt.data)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.Equal(t, tt.want, num)
				require.NoError(t, err)
			}
		})
	}
}
