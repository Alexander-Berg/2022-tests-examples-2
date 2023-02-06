package batcher

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCleanName(t *testing.T) {
	require.Equal(t, "a_b-c.d", cleanName("a_b-c.d"))
	require.Equal(t, "a__b", cleanName("a@/b"))
}
