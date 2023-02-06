package tirole

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetRevisionFromHeader(t *testing.T) {
	cases := []struct {
		value    string
		expected string
		err      string
	}{
		{},
		{
			value: `"100500`,
			err:   `invalid header: 'somekey' contains incorrect revision '"100500'`,
		},
		{
			value: `100500`,
			err:   `invalid header: 'somekey' contains incorrect revision '100500'`,
		},
		{
			value:    `"100500"`,
			expected: "100500",
		},
		{
			value:    `"1618467217"`,
			expected: "1618467217",
		},
	}

	for idx, c := range cases {
		val, err := getRevisionFromHeader("somekey", c.value)
		if c.err == "" {
			require.NoError(t, err, idx)
		} else {
			require.EqualError(t, err, c.err, idx)
		}

		require.Equal(t, c.expected, val, idx)
	}
}
