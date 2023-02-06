package prepared

import (
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

var (
	TestABFlagsModelVer1 = models.ABFlags{
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
	}

	TestABFlagsDTOVer1 = mordadata.ABFlagsContext{
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
	}

	TestABFlagsModelVer2 = models.ABFlags{
		Flags: map[string]string{
			"flag1": "0",
			"flag4": "1",
		},
		TestIDs: common.NewIntSet(2, 3, 4),
		TestIDsBuckets: map[int][]int{
			1: {1, 2, 4},
			3: {1, 3},
		},
		SliceNames: []string{"slice_1_etalon", "slice_2"},
	}

	TestABFlagsDTOVer2 = mordadata.ABFlagsContext{
		Flags: map[string][]byte{
			"flag1": []byte("0"),
			"flag4": []byte("1"),
		},
		TestIDs: []int64{2, 3, 4},
		TestIDsBuckets: map[int64]*mordadata.TestIDBuckets{
			1: {Buckets: []int64{1, 2, 4}},
			3: {Buckets: []int64{1, 3}},
		},
		SliceNames: [][]byte{[]byte("slice_1_etalon"), []byte("slice_2")},
	}
)
