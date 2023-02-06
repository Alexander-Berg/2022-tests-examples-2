package tacacs_test

import (
	"fmt"
	"math/big"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/nocauth/pkg/tacacs"
)

func TestAlphabetCoder_Encode(t *testing.T) {
	testCases := []struct {
		input    *big.Int
		expected string
	}{
		{big.NewInt(0), "0"},
		{big.NewInt(1), "1"},
		{big.NewInt(61), "Z"},
		{big.NewInt(62), "10"},
		{big.NewInt(123456), "w7e"},
		{big.NewInt(60000000000), "13uxSTu"},
		{big.NewInt(2).Exp(big.NewInt(2), big.NewInt(160), nil), "AwGeptL1TMEBFSqZfp4BXWGY80w"},
	}

	coder := tacacs.StdAlphabetCoder
	for _, tc := range testCases {
		t.Run(fmt.Sprintf("%d", tc.input), func(t *testing.T) {
			assert.Equal(t, []byte(tc.expected), coder.Encode(tc.input))
		})
	}
}

func TestAlphabetCoder_Decode(t *testing.T) {
	testCases := []struct {
		input    string
		expected *big.Int
		hasError bool
	}{
		{"0", big.NewInt(0), false},
		{"1", big.NewInt(1), false},
		{"Z", big.NewInt(61), false},
		{"10", big.NewInt(62), false},
		{"w7e", big.NewInt(123456), false},
		{"13uxSTu", big.NewInt(60000000000), false},
		{
			"AwGeptL1TMEBFSqZfp4BXWGY80w",
			big.NewInt(2).Exp(big.NewInt(2), big.NewInt(160), nil),
			false,
		},

		{"0123=", big.NewInt(0), true},
		{"aA!", big.NewInt(0), true},
		{"/", big.NewInt(0), true},
	}

	coder := tacacs.StdAlphabetCoder
	for _, tc := range testCases {
		t.Run(tc.input, func(t *testing.T) {
			actual, err := coder.Decode([]byte(tc.input))
			if tc.hasError {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			assert.Equal(t, tc.expected, actual)
		})
	}
}
