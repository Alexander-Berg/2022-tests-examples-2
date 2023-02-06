package tacacs

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestDecodeArgs(t *testing.T) {
	testCases := [][]string{
		{"service=shell", "service=shell", "shell:roles*"},
		{"service=shell"},
		{"shell:roles=\"network-admin\""},
		{"shell:roles=\"network-admin\"", "service=unknown"},
	}

	for _, args := range testCases {
		t.Run("", func(t *testing.T) {
			decodedArgs, err := DecodeArgs(args)
			require.NoError(t, err)

			encodedArgs := EncodeArgs(decodedArgs)
			assert.Equal(t, args, encodedArgs)
		})
	}
}
