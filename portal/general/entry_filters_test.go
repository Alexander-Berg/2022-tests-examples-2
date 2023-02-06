package readers

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDisabledFilter(t *testing.T) {
	testCases := []struct {
		name           string
		entry          parsedEntry
		expectError    bool
		expectedResult bool
	}{
		{
			name:           "no `disabled`",
			entry:          parsedEntry{},
			expectedResult: true,
		},
		{
			name:           "string disabled",
			entry:          parsedEntry{"disabled": "1"},
			expectedResult: false,
		},
		{
			name:           "string not disabled",
			entry:          parsedEntry{"disabled": "0"},
			expectedResult: true,
		},
		{
			name:           "bool disabled",
			entry:          parsedEntry{"disabled": true},
			expectedResult: false,
		},
		{
			name:           "bool not disabled",
			entry:          parsedEntry{"disabled": false},
			expectedResult: true,
		},
		{
			name:           "int disabled",
			entry:          parsedEntry{"disabled": 1},
			expectedResult: false,
		},
		{
			name:           "int not disabled",
			entry:          parsedEntry{"disabled": 0},
			expectedResult: true,
		},
		{
			name:        "unexpected `disabled`",
			entry:       parsedEntry{"disabled": struct{}{}},
			expectError: true,
		},
	}
	filter := NewDisabledFilter()
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			result, err := filter.Filter(testCase.entry)
			if testCase.expectError {
				assert.Error(t, err)
				return
			}
			require.NoError(t, err)
			assert.Equal(t, testCase.expectedResult, result)
		})
	}
}
