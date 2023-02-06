package internal

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

var truncateTextTestTable = []struct {
	name     string
	from     string
	maxLen   int
	expected string
}{
	{
		"empty",
		"",
		1000,
		"",
	},
	{
		"fits",
		"some text",
		9,
		"some text",
	},
	{
		"needs to be truncated",
		"some text",
		8,
		"some ...",
	},
}

func TestTruncateText(t *testing.T) {
	for _, tt := range truncateTextTestTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				actual := truncateText(tt.from, tt.maxLen)
				assert.Equal(t, tt.expected, actual)
			},
		)
	}
}
