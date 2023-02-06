package apicdn

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNumberGenerator_Next(t *testing.T) {
	g := NewNumberGenerator(make(map[int64]struct{}))
	require.Equal(t, 1, int(g.Next()))
	require.Equal(t, 2, int(g.Next()))
	require.Equal(t, 3, int(g.Next()))
	require.Equal(t, 4, int(g.Next()))
	require.Equal(t, 5, int(g.Next()))
}

func TestNumberGenerator_Next2(t *testing.T) {
	g := NewNumberGenerator(map[int64]struct{}{3: {}, 5: {}})
	require.Equal(t, 1, int(g.Next()))
	require.Equal(t, 2, int(g.Next()))
	require.Equal(t, 4, int(g.Next()))
	require.Equal(t, 6, int(g.Next()))
}
