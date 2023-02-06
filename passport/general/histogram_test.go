package unistat

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestHgram(t *testing.T) {
	c := NewChunk()
	require.Equal(t, `[]`, string(c.Serialize()))

	_, err := c.CreateSignalHgram("someprx_", createManyBounds())
	require.EqualError(t, err, "Length of bounds in Hgram cannot be > 50, got 51")
	_, err = c.CreateSignalHgram("someprx_", []float64{})
	require.EqualError(t, err, "Length of bounds in Hgram cannot be == 0")

	set, err := c.CreateSignalHgram("somename", []float64{5, 10, 20})
	require.NoError(t, err)
	check := func(exp string) {
		require.Equal(t, exp, string(c.Serialize()))
	}
	check(`[["somename_dhhh",[[0,0],[5,0],[10,0],[20,0]]]]`)

	set.Inc(3)
	set.Inc(3)
	check(`[["somename_dhhh",[[0,2],[5,0],[10,0],[20,0]]]]`)

	set.Inc(0)
	check(`[["somename_dhhh",[[0,3],[5,0],[10,0],[20,0]]]]`)

	set.Inc(5)
	check(`[["somename_dhhh",[[0,3],[5,1],[10,0],[20,0]]]]`)

	set.Inc(7)
	check(`[["somename_dhhh",[[0,3],[5,2],[10,0],[20,0]]]]`)

	set.Inc(100)
	check(`[["somename_dhhh",[[0,3],[5,2],[10,0],[20,1]]]]`)
}

func createManyBounds() []float64 {
	res := make([]float64, 0)

	for idx := 0; idx < 51; idx++ {
		res = append(res, float64(idx))
	}

	return res
}
