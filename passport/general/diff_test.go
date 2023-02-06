package unistat

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestDiff(t *testing.T) {
	c := NewChunk()
	require.Equal(t, `[]`, string(c.Serialize()))

	diff := c.CreateSignalDiff("d_1")
	check := func(exp string) {
		require.Equal(t, exp, string(c.Serialize()))
	}
	check(`[["d_1_dmmm",0]]`)

	diff.Inc()
	check(`[["d_1_dmmm",1]]`)

	diff.Add(5)
	check(`[["d_1_dmmm",6]]`)
}
