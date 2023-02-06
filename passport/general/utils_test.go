package pgadapter

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

var testTable = []struct {
	name         string
	old          []uint64
	new          []uint64
	expectedDiff DiffUInt64
}{
	{
		"Keep all ordered",
		[]uint64{1, 2, 3},
		[]uint64{1, 2, 3},
		DiffUInt64{
			ToAdd:    []uint64{},
			ToRemove: []uint64{},
			NoChange: []uint64{1, 2, 3},
		},
	},
	{
		"Keep all unordered",
		[]uint64{1, 2, 3},
		[]uint64{3, 2, 1},
		DiffUInt64{
			ToAdd:    []uint64{},
			ToRemove: []uint64{},
			NoChange: []uint64{3, 2, 1},
		},
	},
	{
		"Add all",
		[]uint64{},
		[]uint64{1, 2, 3},
		DiffUInt64{
			ToAdd:    []uint64{1, 2, 3},
			ToRemove: []uint64{},
			NoChange: []uint64{},
		},
	},
	{
		"Remove all",
		[]uint64{1, 2, 3},
		[]uint64{},
		DiffUInt64{
			ToAdd:    []uint64{},
			ToRemove: []uint64{1, 2, 3},
			NoChange: []uint64{},
		},
	},
	{
		"Mixed",
		[]uint64{1, 2, 3},
		[]uint64{2, 3, 4},
		DiffUInt64{
			ToAdd:    []uint64{4},
			ToRemove: []uint64{1},
			NoChange: []uint64{2, 3},
		},
	},
}

func TestDiff(t *testing.T) {
	for _, tt := range testTable {
		t.Run(
			tt.name,
			func(t *testing.T) {
				diff := utilDiffDomainIDs(tt.old, tt.new)
				assert.Equal(t, tt.expectedDiff, diff)
			},
		)
	}
}
