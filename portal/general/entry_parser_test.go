package readers

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEntryParser(t *testing.T) {
	testCases := []struct {
		name           string
		parsers        map[string]FieldParser
		input          unparsedEntry
		expectError    bool
		expectedResult parsedEntry
	}{
		{
			name:           "correctness test",
			parsers:        map[string]FieldParser{"string": NewStringParser()},
			input:          unparsedEntry{"string": []byte(`"abc"`), "number": []byte(`1`)},
			expectedResult: parsedEntry{"string": "abc", "number": float64(1)},
		},
		{
			name:        "error test",
			parsers:     map[string]FieldParser{"string": NewStringParser()},
			input:       unparsedEntry{"string": []byte(`"abc`), "int": []byte(`1`)},
			expectError: true,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			parser := NewEntryParser(testCase.parsers)
			result, err := parser.ParseJSON(testCase.input)
			if testCase.expectError {
				assert.Error(t, err)
				return
			}
			require.NoError(t, err)
			assert.Equal(t, testCase.expectedResult, result)
		})
	}
}
