package text_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/puncher/lib/text"
)

func TestIntersect(t *testing.T) {
	tests := []struct {
		slices   [][]string
		expected []string
	}{
		{
			slices:   nil,
			expected: nil,
		},
		{
			slices: [][]string{
				nil,
				{"a"},
			},
			expected: nil,
		},
		{
			slices: [][]string{
				{"a"},
				{"b"},
			},
			expected: nil,
		},
		{
			slices: [][]string{
				{"a"},
				{"a"},
			},
			expected: []string{"a"},
		},
		{
			slices: [][]string{
				{"a", "a", "b", "c"},
				{"a", "b", "b", "d"},
			},
			expected: []string{"a", "b"},
		},
		{
			slices: [][]string{
				{"a", "b"},
				{"a", "c"},
				{"b", "c"},
			},
			expected: nil,
		},
		{
			slices: [][]string{
				{"a", "b"},
				{"a", "c"},
				{"b", "a"},
			},
			expected: []string{"a"},
		},
	}

	for _, test := range tests {
		assert.ElementsMatch(t, test.expected, text.Intersect(test.slices...))
	}
}
