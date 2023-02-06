package common

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNumericComparable_IsEqual(t *testing.T) {
	tests := []struct {
		name  string
		c     NumericComparable
		other interface{}
		want  bool
	}{
		{
			name:  "nil",
			c:     15,
			other: nil,
			want:  false,
		},
		{
			name:  "equal int",
			c:     15,
			other: 15,
			want:  true,
		},
		{
			name:  "not equal int",
			c:     15,
			other: 10,
			want:  false,
		},
		{
			name:  "equal float",
			c:     15,
			other: 15.0,
			want:  true,
		},
		{
			name:  "not equal float",
			c:     15,
			other: 16.5,
			want:  false,
		},
		{
			name:  "equal string",
			c:     15,
			other: "15",
			want:  true,
		},
		{
			name:  "not equal string",
			c:     15,
			other: "16",
			want:  false,
		},
		{
			name:  "float in string",
			c:     15,
			other: "15.0",
			want:  false,
		},
		{
			name:  "bool",
			c:     15,
			other: false,
			want:  false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equalf(t, tt.want, tt.c.IsEqual(tt.other), "IsEqual(%v)", tt.other)
		})
	}
}

func TestBoolComparable_IsEqual(t *testing.T) {
	tests := []struct {
		name  string
		c     BoolComparable
		other interface{}
		want  bool
	}{
		{
			name:  "true with nil",
			c:     true,
			other: nil,
			want:  false,
		},
		{
			name:  "false with nil",
			c:     false,
			other: nil,
			want:  true,
		},
		{
			name:  "both true",
			c:     true,
			other: true,
			want:  true,
		},
		{
			name:  "both false",
			c:     false,
			other: false,
			want:  true,
		},
		{
			name:  "true false",
			c:     true,
			other: false,
			want:  false,
		},
		{
			name:  "false true",
			c:     false,
			other: true,
			want:  false,
		},
		{
			name:  "zero in string",
			c:     false,
			other: "0",
			want:  true,
		},
		{
			name:  "false in string",
			c:     false,
			other: false,
			want:  true,
		},
		{
			name:  "one in string",
			c:     true,
			other: "1",
			want:  true,
		},
		{
			name:  "true in string",
			c:     true,
			other: "true",
			want:  true,
		},
		{
			name:  "true and true float",
			c:     true,
			other: float64(1),
			want:  true,
		},
		{
			name:  "true and false float",
			c:     true,
			other: float64(0),
			want:  false,
		},
		{
			name:  "false and true float",
			c:     false,
			other: float64(1),
			want:  false,
		},
		{
			name:  "false and false float",
			c:     false,
			other: float64(0),
			want:  true,
		},
		{
			name:  "empty struct",
			c:     false,
			other: struct{}{},
			want:  false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equalf(t, tt.want, tt.c.IsEqual(tt.other), "IsEqual(%v)", tt.other)
		})
	}
}

func TestStringComparable_IsEqual(t *testing.T) {
	tests := []struct {
		name  string
		c     StringComparable
		other interface{}
		want  bool
	}{
		{
			name:  "empty string and nil",
			c:     "",
			other: nil,
			want:  true,
		},
		{
			name:  "not empty string ans nil",
			c:     "test",
			other: nil,
			want:  false,
		},
		{
			name:  "int",
			c:     "1",
			other: 1,
			want:  false,
		},
		{
			name:  "float",
			c:     "1.5",
			other: 1.5,
			want:  false,
		},
		{
			name:  "bool",
			c:     "true",
			other: true,
			want:  false,
		},
		{
			name:  "equal strings",
			c:     "test",
			other: "test",
			want:  true,
		},
		{
			name:  "empty strings",
			c:     "",
			other: "",
			want:  true,
		},
		{
			name:  "not equal strings",
			c:     "test",
			other: "Test",
			want:  false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equalf(t, tt.want, tt.c.IsEqual(tt.other), "IsEqual(%v)", tt.other)
		})
	}
}
