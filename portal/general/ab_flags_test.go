package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestABFlags_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *ABFlags
		want  *mordadata.ABFlagsContext
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty model",
			model: &ABFlags{},
			want: &mordadata.ABFlagsContext{
				Flags:          map[string][]byte{},
				TestIDs:        []int64{},
				TestIDsBuckets: map[int64]*mordadata.TestIDBuckets{},
				SliceNames:     [][]byte{},
			},
		},
		{
			name: "partial empty model",
			model: &ABFlags{
				Flags: map[string]string{
					"1": "1",
				},
				TestIDs: nil,
				TestIDsBuckets: map[int][]int{
					1: nil,
				},
				SliceNames: []string{},
			},
			want: &mordadata.ABFlagsContext{
				Flags: map[string][]byte{
					"1": []byte("1"),
				},
				TestIDs: []int64{},
				TestIDsBuckets: map[int64]*mordadata.TestIDBuckets{
					1: {Buckets: []int64{}},
				},
			},
		},
		{
			name: "filled model",
			model: &ABFlags{
				Flags: map[string]string{
					"flag1": "1",
					"flag2": "0",
				},
				TestIDs: common.NewIntSet(3, 2, 1),
				TestIDsBuckets: map[int][]int{
					1: {1, 2},
					2: {2, 3},
				},
				SliceNames: []string{"slice_1", "slice_2"},
			},
			want: &mordadata.ABFlagsContext{
				Flags: map[string][]byte{
					"flag1": []byte("1"),
					"flag2": []byte("0"),
				},
				TestIDs: []int64{1, 2, 3},
				TestIDsBuckets: map[int64]*mordadata.TestIDBuckets{
					1: {Buckets: []int64{1, 2}},
					2: {Buckets: []int64{2, 3}},
				},
				SliceNames: [][]byte{[]byte("slice_1"), []byte("slice_2")},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestNewABFlags(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.ABFlagsContext
		want *ABFlags
	}{
		{
			name: "nil",
			dto:  nil,
			want: nil,
		},
		{
			name: "empty dto",
			dto:  &mordadata.ABFlagsContext{},
			want: &ABFlags{
				Flags:          map[string]string{},
				TestIDs:        common.NewIntSet(),
				TestIDsBuckets: map[int][]int{},
				SliceNames:     nil,
			},
		},
		{
			name: "partial empty dto",
			dto: &mordadata.ABFlagsContext{
				Flags: map[string][]byte{
					"1": []byte("1"),
				},
				TestIDs: nil,
				TestIDsBuckets: map[int64]*mordadata.TestIDBuckets{
					1: nil,
					2: {Buckets: nil},
				},
				SliceNames: [][]byte{},
			},
			want: &ABFlags{
				Flags: map[string]string{
					"1": "1",
				},
				TestIDs: common.NewIntSet(),
				TestIDsBuckets: map[int][]int{
					1: {},
					2: {},
				},
				SliceNames: []string{},
			},
		},
		{
			name: "filled dto",
			dto: &mordadata.ABFlagsContext{
				Flags: map[string][]byte{
					"flag1": []byte("1"),
					"flag2": []byte("0"),
				},
				TestIDs: []int64{1, 2, 3},
				TestIDsBuckets: map[int64]*mordadata.TestIDBuckets{
					1: {Buckets: []int64{1, 2}},
					2: {Buckets: []int64{2, 3}},
				},
				SliceNames: [][]byte{[]byte("slice_1"), []byte("slice_2")},
			},
			want: &ABFlags{
				Flags: map[string]string{
					"flag1": "1",
					"flag2": "0",
				},
				TestIDs: common.NewIntSet(1, 2, 3),
				TestIDsBuckets: map[int][]int{
					1: {1, 2},
					2: {2, 3},
				},
				SliceNames: []string{"slice_1", "slice_2"},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewABFlags(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}
