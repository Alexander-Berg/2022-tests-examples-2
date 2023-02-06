package common

import (
	"math"
	"strconv"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestParseRobustInteger(t *testing.T) {
	testItems := []struct {
		input  string
		output int
	}{
		{
			input:  "0",
			output: 0,
		},
		{
			input:  "1",
			output: 1,
		},
		{
			input:  "-1",
			output: -1,
		},
		{
			input:  "123",
			output: 123,
		},
		{
			input:  "deadbeef",
			output: 0,
		},
		{
			input:  "",
			output: 0,
		},
	}
	for _, item := range testItems {
		assert.Equal(t, item.output, ParseRobustInteger(item.input), "%s", item.input)
	}
}

func TestParseRobustInt32(t *testing.T) {
	testItems := []struct {
		input  string
		output int32
	}{
		{
			input:  "0",
			output: 0,
		},
		{
			input:  "1",
			output: 1,
		},
		{
			input:  "-1",
			output: -1,
		},
		{
			input:  "123",
			output: 123,
		},
		{
			input:  "deadbeef",
			output: 0,
		},
		{
			input:  "",
			output: 0,
		},
		{
			input:  strconv.FormatInt(math.MaxInt32, 10),
			output: math.MaxInt32,
		},
		{
			input:  strconv.FormatInt(math.MinInt32, 10),
			output: math.MinInt32,
		},
		{
			input:  strconv.FormatInt(math.MaxInt32+1, 10),
			output: 0,
		},
		{
			input:  strconv.FormatInt(math.MinInt32-1, 10),
			output: 0,
		},
	}
	for _, item := range testItems {
		assert.Equal(t, item.output, ParseRobustInt32(item.input), "%s", item.input)
	}
}

func TestParseRobustInt64(t *testing.T) {
	testItems := []struct {
		input  string
		output int64
	}{
		{
			input:  "0",
			output: 0,
		},
		{
			input:  "1",
			output: 1,
		},
		{
			input:  "-1",
			output: -1,
		},
		{
			input:  "123",
			output: 123,
		},
		{
			input:  "deadbeef",
			output: 0,
		},
		{
			input:  "",
			output: 0,
		},
		{
			input:  strconv.FormatInt(math.MaxInt64, 10),
			output: math.MaxInt64,
		},
		{
			input:  strconv.FormatInt(math.MinInt64, 10),
			output: math.MinInt64,
		},
		{
			input:  "9223372036854775808", // MaxInt64 + 1
			output: 0,
		},
		{
			input:  "-9223372036854775809", // MinInt64 - 1
			output: 0,
		},
	}
	for _, item := range testItems {
		assert.Equal(t, item.output, ParseRobustInt64(item.input), "%s", item.input)
	}
}

func TestParseRobustUInt(t *testing.T) {
	testItems := []struct {
		input  string
		output uint
	}{
		{
			input:  "0",
			output: 0,
		},
		{
			input:  "1",
			output: 1,
		},
		{
			input:  "-1",
			output: 0,
		},
		{
			input:  "123",
			output: 123,
		},
		{
			input:  "deadbeef",
			output: 0,
		},
		{
			input:  "",
			output: 0,
		},
		{
			input:  strconv.FormatUint(math.MaxUint, 10),
			output: math.MaxUint,
		},
	}
	for _, item := range testItems {
		assert.Equal(t, item.output, ParseRobustUInt(item.input), "%s", item.input)
	}
}

func TestParseRobustBoolean(t *testing.T) {
	testItems := []struct {
		input  string
		output bool
	}{
		{
			input:  "0",
			output: false,
		},
		{
			input:  "1",
			output: true,
		},
		{
			input:  "-1",
			output: true,
		},
		{
			input:  "42",
			output: true,
		},
		{
			input:  "true",
			output: true,
		},
		{
			input:  "false",
			output: false,
		},
		{
			input:  "",
			output: false,
		},
	}
	for _, item := range testItems {
		assert.Equal(t, item.output, ParseRobustBoolean(item.input), "%s", item.input)
	}
}

func TestConvertToStringSlice(t *testing.T) {
	testItems := []struct {
		name     string
		input    [][]byte
		expected []string
	}{
		{
			name: "nil input",
		},
		{
			name:     "empty slice",
			input:    [][]byte{},
			expected: []string{},
		},
		{
			name: "convert",
			input: [][]byte{
				[]byte("apple"),
				[]byte("banana"),
			},
			expected: []string{
				"apple",
				"banana",
			},
		},
	}

	for _, item := range testItems {
		t.Run(item.name, func(t *testing.T) {
			assert.Equal(t, item.expected, ConvertToStringSlice(item.input))
		})
	}
}

func TestIsTrueValue(t *testing.T) {
	type args struct {
		value string
	}
	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "true",
			args: args{
				value: "true",
			},
			want: true,
		},
		{
			name: "True",
			args: args{
				value: "True",
			},
			want: true,
		},
		{
			name: "TRUE",
			args: args{
				value: "TRUE",
			},
			want: true,
		},
		{
			name: "1",
			args: args{
				value: "1",
			},
			want: true,
		},
		{
			name: "yes",
			args: args{
				value: "yes",
			},
			want: true,
		},
		{
			name: "Yes",
			args: args{
				value: "Yes",
			},
			want: true,
		},
		{
			name: "YES",
			args: args{
				value: "YES",
			},
			want: true,
		},
		{
			name: "Something",
			args: args{
				value: "smth",
			},
			want: false,
		},
		{
			name: "Empty string",
			args: args{
				value: "",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := IsTrueValue(tt.args.value)

			require.Equal(t, tt.want, got)
		})
	}
}
