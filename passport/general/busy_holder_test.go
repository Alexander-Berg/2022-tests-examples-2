package unistat

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestBusy(t *testing.T) {
	c := NewChunk()
	require.Equal(t, `[]`, string(c.Serialize()))

	abs := c.CreateSignalAbsoluteMax("abs_1")
	check := func(exp string) {
		require.Equal(t, exp, string(c.Serialize()))
	}
	check(`[["abs_1_axxx",0]]`)

	b := CreateBusyHolder(abs)
	check(`[["abs_1_axxx",1]]`)

	b.Release()
	check(`[["abs_1_axxx",0]]`)
}
