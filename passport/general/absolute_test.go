package unistat

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestAbsMax(t *testing.T) {
	c := NewChunk()
	require.Equal(t, `[]`, string(c.Serialize()))

	abs := c.CreateSignalAbsoluteMax("abs_1")
	check := func(exp string) {
		require.Equal(t, exp, string(c.Serialize()))
	}
	check(`[["abs_1_axxx",0]]`)

	abs.Add(1)
	check(`[["abs_1_axxx",1]]`)

	abs.Add(5)
	check(`[["abs_1_axxx",6]]`)

	abs.Sub(2)
	check(`[["abs_1_axxx",4]]`)

	abs.Sub(1)
	check(`[["abs_1_axxx",3]]`)

	abs.Store(100500)
	check(`[["abs_1_axxx",100500]]`)
}

func TestAbsAver(t *testing.T) {
	c := NewChunk()
	require.Equal(t, `[]`, string(c.Serialize()))

	abs := c.CreateSignalAbsoluteAverage("abs_1")
	check := func(exp string) {
		require.Equal(t, exp, string(c.Serialize()))
	}
	check(`[["abs_1_avvv",0]]`)

	abs.Add(1)
	check(`[["abs_1_avvv",1]]`)

	abs.Add(5)
	check(`[["abs_1_avvv",6]]`)

	abs.Sub(2)
	check(`[["abs_1_avvv",4]]`)

	abs.Sub(1)
	check(`[["abs_1_avvv",3]]`)

	abs.Store(100500)
	check(`[["abs_1_avvv",100500]]`)
}
