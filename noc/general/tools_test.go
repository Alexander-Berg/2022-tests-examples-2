package tools

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

type truncTestData struct {
	inValue  string
	expected string
	max      int
}

func TestTruncateText(t *testing.T) {
	for _, test := range []truncTestData{
		{inValue: "test", expected: "test", max: 10},
		{inValue: "test", expected: "te...", max: 2},
	} {
		res := TruncateText(test.inValue, test.max)
		assert.Equal(t, test.expected, res)
	}
}
