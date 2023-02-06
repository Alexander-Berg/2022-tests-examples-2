package unistat

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestTime(t *testing.T) {
	c := NewChunk()
	require.Equal(t, `[]`, string(c.Serialize()))

	sig, err := c.CreateTimeStats("somename", CreateTimeBoundsFromMilliseconds([]uint64{5, 10, 20}))
	require.NoError(t, err)
	check := func(exp string) {
		require.Equal(t, exp, string(c.Serialize()))
	}
	check(`[["somename_dhhh",[[0,0],[5,0],[10,0],[20,0]]]]`)

	sig.Insert(time.Millisecond)
	check(`[["somename_dhhh",[[0,1],[5,0],[10,0],[20,0]]]]`)
	sig.Insert(time.Second)
	check(`[["somename_dhhh",[[0,1],[5,0],[10,0],[20,1]]]]`)
}

func TestBounds(t *testing.T) {
	expected := make([]time.Duration, 0)
	for idx := 0; idx < 49; idx++ {
		expected = append(expected, time.Duration(idx)*time.Second)
	}
	expected = append(expected, 50*time.Second)

	require.Equal(t, expected, CreateTimeBoundsFromMaxValue(50*time.Second))
}
