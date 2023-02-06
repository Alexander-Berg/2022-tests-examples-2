package segset

import (
	"math/rand"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func Random(cnt int) SegmentSet {
	result := make(SegmentSet, cnt)
	result[0] = uint64(rand.Uint32())
	for i := 1; i < cnt; i++ {
		result[i] = result[i-1] + 1 + uint64(rand.Uint32())
	}
	return result
}

func TestVolume(t *testing.T) {
	var empty SegmentSet
	assert.Equal(t, uint64(0), empty.Volume())
	first := SegmentSet{1, 2, 3, 4}
	assert.Equal(t, uint64(2), first.Volume())
}

func TestIntersect_Reflexivity(t *testing.T) {
	var empty SegmentSet
	assert.Equal(t, empty.Intersect(empty), empty)
	first := SegmentSet{1, 2, 3, 4}
	assert.Equal(t, first.Intersect(first), first)
	second := Random(100)
	assert.Equal(t, second.Intersect(second), second)
}

func TestIntersect_Symmetry(t *testing.T) {
	first := Random(100)
	second := Random(100)
	assert.Equal(t, first.Intersect(second), second.Intersect(first))
}

func TestIntersect_VolumeIsLess(t *testing.T) {
	first := Random(100)
	second := Random(100)
	result := first.Intersect(second)
	assert.Less(t, result.Volume(), first.Volume(), result)
	assert.Less(t, result.Volume(), second.Volume(), result)
}

func TestIntersect_ResultIsValid(t *testing.T) {
	first := Random(100)
	second := Random(100)
	result := first.Intersect(second)
	require.True(t, len(result)%2 == 0)
	for i := 0; i < len(result)-1; i++ {
		assert.Less(t, result[i], result[i+1])
	}
}

func TestIntersect_AlwaysIsNeutral(t *testing.T) {
	first := Random(100)
	result := first.Intersect(all)
	assert.Equal(t, result, first)
}

func TestIntersect_NeverDominates(t *testing.T) {
	first := Random(100)
	result := first.Intersect(None)
	assert.Equal(t, None, result)
}

func TestUnion_Reflexivity(t *testing.T) {
	var empty SegmentSet
	assert.Equal(t, empty.Union(empty), empty)
	first := SegmentSet{1, 2, 3, 4}
	assert.Equal(t, first.Union(first), first)
	second := Random(100)
	assert.Equal(t, second.Union(second), second)
}

func TestUnion_Symmetry(t *testing.T) {
	first := Random(100)
	second := Random(100)
	assert.Equal(t, first.Union(second), second.Union(first))
}

func TestUnion_VolumeIsMore(t *testing.T) {
	first := Random(100)
	second := Random(100)
	result := first.Union(second)
	assert.Greater(t, result.Volume(), first.Volume(), result)
	assert.Greater(t, result.Volume(), second.Volume(), result)
}

func TestUnion_ResultIsValid(t *testing.T) {
	first := Random(100)
	second := Random(100)
	result := first.Union(second)
	require.True(t, len(result)%2 == 0)
	for i := 0; i < len(result)-1; i++ {
		assert.Less(t, result[i], result[i+1])
	}
}

func TestUnion_AlwaysDominates(t *testing.T) {
	first := Random(100)
	result := first.Union(all)
	assert.True(t, result.IsAll())
}

func TestUnion_NeverNeutral(t *testing.T) {
	first := Random(100)
	result := first.Union(None)
	assert.Equal(t, first, result)
}
