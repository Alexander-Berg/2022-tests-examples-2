package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestReverseUnixtime(t *testing.T) {
	require.Equal(t, uint64(9223372036854775807), reverseUnixtime(0))
	require.Equal(t, uint64(9223372036854675307), reverseUnixtime(100500))
	require.Equal(t, uint64(9223372035240261985), reverseUnixtime(1614513822))
}

func TestSerializeUIntListIN(t *testing.T) {
	cases := []struct {
		in  []uint64
		out string
	}{
		{},
		{
			in:  []uint64{100500},
			out: `100500`,
		},
		{
			in:  []uint64{17, 129},
			out: `17,129`,
		},
	}

	for idx, c := range cases {
		require.Equal(t, c.out, serializeUIntListIN(c.in), idx)
	}
}

func TestSerializeConditionIN(t *testing.T) {
	cases := []struct {
		in  []string
		out string
	}{
		{},
		{
			in:  []string{"foo", "bar"},
			out: `"foo","bar"`,
		},
		{
			in:  []string{`f"); SELECT * FROM bar`, "kek"},
			out: `"f\"); SELECT * FROM bar","kek"`,
		},
	}

	for idx, c := range cases {
		require.Equal(t, c.out, serializeConditionIN(c.in), idx)
	}
}

func TestOrderByString(t *testing.T) {
	require.Equal(t, "ASC", orderByString(true))
	require.Equal(t, "DESC", orderByString(false))
}
