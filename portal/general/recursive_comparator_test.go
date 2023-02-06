package compare

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func makeStringTreeFromPaths(paths ...string) common.StringTree {
	ret := common.NewStringTree()
	for _, path := range paths {
		ret.Add(strings.Split(path, ".")...)
	}
	return ret
}

func Test_recursiveComparator_Compare(t *testing.T) {
	testCases := []struct {
		name        string
		keys        common.StringTree
		expected    interface{}
		got         interface{}
		expectError bool
	}{
		{
			name: "unguided trivial",
		},
		{
			name:     "unguided trivial alt",
			expected: 1,
			got:      1,
		},
		{
			name:        "unguided trivial alt2",
			expected:    1,
			expectError: true,
		},
		{
			name:        "unguided type conflict",
			expected:    map[string]interface{}{},
			expectError: true,
		},
		{
			name:        "unguided type conflict alt",
			expected:    map[string]interface{}{},
			got:         1,
			expectError: true,
		},
		{
			name:        "unguided type conflict alt",
			expected:    1,
			got:         map[string]interface{}{},
			expectError: true,
		},
		{
			name: "unguided deep",
			expected: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 321,
				},
				"c": 1,
			},
			got: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 345,
				},
				"c": 2,
			},
			expectError: true,
		},
		{
			name: "guided deep",
			keys: makeStringTreeFromPaths("nested"),
			expected: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 321,
				},
				"c": 1,
			},
			got: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 345,
				},
				"c": 2,
			},
			expectError: true,
		},
		{
			name: "guided deep alt",
			keys: makeStringTreeFromPaths("nested.a"),
			expected: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 321,
				},
				"c": 1,
			},
			got: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 345,
				},
				"c": 2,
			},
		},
		{
			name: "guided deep alt2",
			keys: makeStringTreeFromPaths("c"),
			expected: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 321,
				},
				"c": 1,
			},
			got: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 345,
				},
				"c": 2,
			},
			expectError: true,
		},
		{
			name: "guided deep alt3",
			keys: makeStringTreeFromPaths("c"),
			expected: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 321,
				},
				"c": 1,
			},
			got: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 345,
				},
				"c": 1,
			},
		},
		{
			name: "guided deep alt4",
			keys: makeStringTreeFromPaths("d"),
			expected: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 321,
				},
				"c": 1,
			},
			got: map[string]interface{}{
				"nested": map[string]interface{}{
					"a": 123,
					"b": 345,
				},
				"c": 1,
			},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			comparator := NewRecursiveComparator(testCase.keys)
			err := comparator.Compare(testCase.expected, testCase.got)
			if testCase.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}
