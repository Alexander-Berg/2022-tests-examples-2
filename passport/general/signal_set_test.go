package unistat

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestSet(t *testing.T) {
	c := NewChunk()
	require.Equal(t, `[]`, string(c.Serialize()))

	set := c.CreateSignalSet("someprx_")
	check := func(exp string) {
		require.Equal(t, exp, string(c.Serialize()))
	}
	check(`[]`)

	set.IncSignal("signal1")
	check(`[]`)
	set.AddToSignal("signal1", 5)
	check(`[]`)

	set.CreateSignal("signal1")
	check(`[["someprx_signal1_dmmm",0]]`)

	set.IncSignal("signal1")
	check(`[["someprx_signal1_dmmm",1]]`)
	set.AddToSignal("signal1", 5)
	check(`[["someprx_signal1_dmmm",6]]`)

	set.CreateOrIncSignal("signal2")
	check(`[["someprx_signal1_dmmm",6],["someprx_signal2_dmmm",1]]`)

	set.CreateOrAddToSignal("signal3", 5)
	check(`[["someprx_signal1_dmmm",6],["someprx_signal2_dmmm",1],["someprx_signal3_dmmm",5]]`)
}
