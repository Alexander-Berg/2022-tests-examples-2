package text

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestStringSlicesEqual(t *testing.T) {
	tests := []struct {
		s1       []string
		s2       []string
		expected bool
	}{
		{
			s1:       nil,
			s2:       nil,
			expected: true,
		},
		{
			s1:       nil,
			s2:       []string{},
			expected: true,
		},
		{
			s1:       []string{},
			s2:       []string{},
			expected: true,
		},
		{
			s1:       []string{"a"},
			s2:       []string{"a"},
			expected: true,
		},
		{
			s1:       []string{"a"},
			s2:       []string{"a", "a", "a"},
			expected: false,
		},
		{
			s1:       []string{"a"},
			s2:       []string{"b"},
			expected: false,
		},
		{
			s1:       []string{"a", "b"},
			s2:       []string{"b", "a"},
			expected: true,
		},
		{
			s1:       []string{"a", "b"},
			s2:       []string{"a", "b", "c"},
			expected: false,
		},
		{
			s1:       []string{"a", "b", "c"},
			s2:       []string{"c", "b", "a"},
			expected: true,
		},
	}

	for _, test := range tests {
		assert.Equalf(t, test.expected, StringSlicesEqual(test.s1, test.s2), "s1: %s, s2: %s", test.s1, test.s2)
		assert.Equalf(t, test.expected, StringSlicesEqual(test.s2, test.s1), "s1: %s, s2: %s", test.s2, test.s1)
	}
}
