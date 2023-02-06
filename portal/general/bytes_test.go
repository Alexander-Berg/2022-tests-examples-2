package common

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConvertToBytesSlice(t *testing.T) {
	testItems := []struct {
		name     string
		input    []string
		expected [][]byte
	}{
		{
			name: "nil input",
		},
		{
			name:     "empty slice",
			input:    []string{},
			expected: [][]byte{},
		},
		{
			name: "convert",
			input: []string{
				"apple",
				"banana",
			},
			expected: [][]byte{
				[]byte("apple"),
				[]byte("banana"),
			},
		},
	}

	for _, item := range testItems {
		t.Run(item.name, func(t *testing.T) {
			assert.Equal(t, item.expected, ConvertToBytesSlice(item.input))
		})
	}
}
