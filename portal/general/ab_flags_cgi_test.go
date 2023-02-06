package common

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseABFlagsFromCGIArgument(t *testing.T) {
	testCases := []struct {
		caseName    string
		cgiArgument string
		expected    map[string]string
	}{
		{
			caseName:    "single flag",
			cgiArgument: "fruit=apple",
			expected: map[string]string{
				"fruit": "apple",
			},
		},
		{
			caseName:    "several flags",
			cgiArgument: "fruit=apple:city=spb",
			expected: map[string]string{
				"fruit": "apple",
				"city":  "spb",
			},
		},
		{
			caseName:    "repeated flag",
			cgiArgument: "fruit=apple:fruit=banana",
			expected: map[string]string{
				"fruit": "banana",
			},
		},
		{
			caseName:    "flag without value",
			cgiArgument: "fruit=apple:city",
			expected: map[string]string{
				"fruit": "apple",
				"city":  "1",
			},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			actualFlags := parseABFlagsFromCGIArgument(testCase.cgiArgument)
			assert.Equal(t, testCase.expected, actualFlags)
		})
	}
}
