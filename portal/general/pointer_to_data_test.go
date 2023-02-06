package readers

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewPointerToData(t *testing.T) {
	testCases := []struct {
		name        string
		input       interface{}
		expectError bool
	}{
		{
			name:        "wrong last type",
			input:       &[]*string{},
			expectError: true,
		},
		{
			name:        "correct last type",
			input:       &[]*struct{}{},
			expectError: false,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			_, err := NewPointerToData(testCase.input)
			if testCase.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestGenerateParserOnKnownFields(t *testing.T) {
	data := []*struct {
		Name    string
		Float64 float64
		Color   Color `madm:"color"`
	}{}
	expectedParser := NewEntryParser(map[string]FieldParser{
		"Name":    NewStringParser(),
		"Float64": NewFloat64Parser(),
		"color":   NewColorParser(),
	})
	ptr, err := NewPointerToData(&data)
	require.NoError(t, err)
	parser, err := ptr.GenerateParser()
	require.NoError(t, err)
	assert.Equal(t, expectedParser, parser)
}

func TestGenerateParserOnUnknownField(t *testing.T) {
	data := []*struct {
		Name    string
		Float64 float64
		Color   Color `madm:"color"`
		Unknown struct{ field string }
	}{}
	ptr, err := NewPointerToData(&data)
	require.NoError(t, err)
	_, err = ptr.GenerateParser()
	require.Error(t, err)
}
