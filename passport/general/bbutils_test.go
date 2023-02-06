package bbutils

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

var MaskOAuthTokenTestTable = []struct {
	title    string
	original string
	expected string
}{
	{
		"empty",
		"",
		"***",
	},
	{
		"short string",
		"foobar",
		"foo***",
	},
	{
		"long string",
		"some_very_very_long_string",
		"some_very_ver***",
	},
}

func TestMaskOAuthToken(t *testing.T) {
	for _, tt := range MaskOAuthTokenTestTable {
		t.Run(
			tt.title,
			func(t *testing.T) {
				masked := MaskOAuthToken(tt.original)
				assert.Equal(t, masked, tt.expected)
			},
		)
	}
}
