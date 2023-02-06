package container

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestStringSet(t *testing.T) {
	set1 := StringSet{}
	require.True(t, set1.Insert("1"))
	require.False(t, set1.Insert("1"))
	require.True(t, set1.Insert("2"))
	set1.Remove("1")
	require.True(t, set1.Insert("1"))
	require.True(t, set1.Contains("2"))

	set2 := MakeStringSet([]string{"1", "1", "3"})
	require.True(t, set2.Contains("1"))
	require.False(t, set2.Contains("2"))
	require.True(t, set2.Contains("3"))
}
