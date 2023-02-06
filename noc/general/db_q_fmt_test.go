package slbcloghandler

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFormatWhereExpression(t *testing.T) {
	type testCases struct {
		input    []string
		expected string
	}
	testData := []testCases{
		{input: []string{"a", "b"}, expected: "a = $1 AND b = $2"},
	}
	for _, testCase := range testData {
		result, err := formatWhereExpression(testCase.input)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, result)
	}
}

func TestFormatValuesPlaceholder(t *testing.T) {
	type testCases struct {
		input    int
		expected string
	}
	testData := []testCases{
		{input: 3, expected: "$1, $2, $3"},
	}
	for _, testCase := range testData {
		result := formatValuesPlaceholder(testCase.input)
		assert.Equal(t, testCase.expected, result)
	}
}

func TestFormatDeleteQuery(t *testing.T) {
	type inputParams struct {
		table   string
		columns []string
	}
	type testCases struct {
		input    inputParams
		expected string
	}
	testData := []testCases{
		{input: inputParams{table: "test", columns: []string{"a", "b"}},
			expected: "DELETE FROM test WHERE a = $1 AND b = $2"},
	}
	for _, testCase := range testData {
		result, err := formatDeleteQuery(testCase.input.table, testCase.input.columns)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, result)
	}
}

func TestFormatUpsertQuery(t *testing.T) {
	type inputParams struct {
		table      string
		columns    []string
		keyColumns []string
	}
	type testCases struct {
		input    inputParams
		expected string
	}
	testData := []testCases{
		{input: inputParams{table: "test", columns: []string{"a", "b"}, keyColumns: []string{"a"}},
			expected: "INSERT INTO test (a,b) VALUES($1, $2) ON CONFLICT (a) DO UPDATE SET b=excluded.b"},
		{input: inputParams{table: "test", columns: []string{"a", "b"}, keyColumns: []string{"a", "b"}},
			expected: "INSERT INTO test (a,b) VALUES($1, $2) ON CONFLICT (a,b) DO NOTHING"},
	}
	for _, testCase := range testData {
		result, err := formatUpsertQuery(testCase.input.table, testCase.input.columns, testCase.input.keyColumns)
		assert.NoError(t, err)
		assert.Equal(t, testCase.expected, result)
	}
}
