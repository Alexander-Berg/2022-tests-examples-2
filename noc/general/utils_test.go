package mcutils

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestMakeSetFromArray(t *testing.T) {
	arr := make([]string, 0)
	m := MakeSetFromArray(arr)
	require.Equal(t, map[string]struct{}{}, m)

	arr = nil
	m = MakeSetFromArray(arr)
	require.Nil(t, m)

	arr = []string{"a", "c", "b"}
	m = MakeSetFromArray(arr)
	require.Equal(t, map[string]struct{}{
		"a": {},
		"c": {},
		"b": {},
	}, m)
}

func TestMakeArrayFromSet(t *testing.T) {
	m := make(map[string]struct{})
	arr := MakeArrayFromSet(m)
	require.Equal(t, []string{}, arr)

	m = nil
	arr = MakeArrayFromSet(m)
	require.Nil(t, arr)

	m = map[string]struct{}{
		"a": {},
		"c": {},
		"b": {},
	}
	arr = MakeArrayFromSet(m)
	require.ElementsMatch(t, []string{"a", "c", "b"}, arr)
}

func TestMakeAllArrFromAllSet(t *testing.T) {
	m := make(map[string]map[string]struct{})
	arr := MakeAllArrFromAllSet(m)
	require.Equal(t, map[string][]string{}, arr)

	m = nil
	arr = MakeAllArrFromAllSet(m)
	require.Nil(t, arr)

	m = map[string]map[string]struct{}{
		"a": {
			"c": {},
			"k": {},
		},
		"b": {},
		"c": nil,
	}
	arr = MakeAllArrFromAllSet(m)
	require.Equal(t, 3, len(arr))
	require.ElementsMatch(t, []string{"c", "k"}, arr["a"])
	require.Equal(t, []string{}, arr["b"])
	require.Nil(t, arr["c"])
}

func TestMakeAllSetFromAllArr(t *testing.T) {
	m := make(map[string][]string)
	set := MakeAllSetFromAllArr(m)
	require.Equal(t, map[string]map[string]struct{}{}, set)

	m = nil
	set = MakeAllSetFromAllArr(m)
	require.Nil(t, set)

	m = map[string][]string{
		"a": {"c", "k"},
		"b": {},
		"c": nil,
	}
	set = MakeAllSetFromAllArr(m)
	require.Equal(t, 3, len(set))
	require.Equal(t, map[string]map[string]struct{}{
		"a": {
			"c": {},
			"k": {},
		},
		"b": {},
		"c": nil,
	}, set)
}

func TestMergeWithoutDuplicates(t *testing.T) {
	first := make([]string, 0)
	second := make([]string, 0)
	res := MergeWithoutDuplicates(first, second...)
	require.Equal(t, []string{}, res)

	first = nil
	second = nil
	res = MergeWithoutDuplicates(first, second...)
	require.Nil(t, res)

	first = nil
	second = []string{"a", "d"}
	res = MergeWithoutDuplicates(first, second...)
	require.ElementsMatch(t, []string{"a", "d"}, res)

	first = []string{"a", "b", "c"}
	second = nil
	res = MergeWithoutDuplicates(first, second...)
	require.ElementsMatch(t, first, res)

	first = []string{"a", "b", "c"}
	second = []string{"a", "d"}
	res = MergeWithoutDuplicates(first, second...)
	require.ElementsMatch(t, []string{"a", "b", "c", "d"}, res)
}

func TestMakeArrayStr(t *testing.T) {
	arr := make([]string, 0)
	str := MakeArrayStr(arr)
	require.Equal(t, "[]", str)

	arr = nil
	str = MakeArrayStr(arr)
	require.Equal(t, "[]", str)

	arr = []string{"a", "b"}
	str = MakeArrayStr(arr)
	require.Equal(t, "[a, b]", str)

	arr = []string{"a", ", ", "b"}
	str = MakeArrayStr(arr)
	require.Equal(t, "[a, , , b]", str)
}

func TestCopyArr(t *testing.T) {
	arr := make([]string, 0)
	cp := CopyArr(arr)
	require.Equal(t, []string{}, cp)

	arr = nil
	cp = CopyArr(arr)
	require.Nil(t, cp)

	arr = []string{"a", "b"}
	cp = CopyArr(arr)
	require.Equal(t, []string{"a", "b"}, cp)

	arr = append(arr, "c")
	require.Equal(t, []string{"a", "b", "c"}, arr)
	require.Equal(t, []string{"a", "b"}, cp)
}

func TestFlattenArr(t *testing.T) {
	arr := [][]uint32{
		{1, 2, 3},
		{4, 5, 6},
	}
	flatArr := FlattenArr(arr)
	require.Equal(t, []uint32{1, 2, 3, 4, 5, 6}, flatArr)

	arr = [][]uint32{}
	flatArr = FlattenArr(arr)
	require.Equal(t, []uint32{}, flatArr)

	arr = nil
	flatArr = FlattenArr(arr)
	require.Nil(t, flatArr)
}

func TestRemoveDuplicatesAndEmpty(t *testing.T) {
	arr := make([]string, 0)
	res := RemoveDuplicatesAndEmpty(arr)
	require.Equal(t, []string{}, res)

	arr = nil
	res = RemoveDuplicatesAndEmpty(arr)
	require.Nil(t, res)

	arr = []string{"a", "b", "c"}
	res = RemoveDuplicatesAndEmpty(arr)
	require.Equal(t, []string{"a", "b", "c"}, res)

	arr = []string{"a", "b", "a"}
	res = RemoveDuplicatesAndEmpty(arr)
	require.Equal(t, []string{"a", "b"}, res)

	arr = []string{"a", "b", "", "b", "d"}
	res = RemoveDuplicatesAndEmpty(arr)
	require.Equal(t, []string{"a", "b", "d"}, res)

	arr = []string{"", "", "", ""}
	res = RemoveDuplicatesAndEmpty(arr)
	require.Equal(t, []string{}, res)
}

func TestRevertMap(t *testing.T) {
	m := make(map[string]map[string]struct{})
	rev := RevertMap(m)
	require.Equal(t, map[string]map[string]struct{}{}, rev)

	m = nil
	rev = RevertMap(m)
	require.Nil(t, rev)

	m = map[string]map[string]struct{}{
		"1": {
			"2": {},
			"3": {},
			"4": {},
		},
		"2": {
			"3": {},
			"6": {},
		},
		"8":   {},
		"nil": nil,
	}
	rev = RevertMap(m)
	require.Equal(t, map[string]map[string]struct{}{
		"2": {
			"1": {},
		},
		"3": {
			"1": {},
			"2": {},
		},
		"4": {
			"1": {},
		},
		"6": {
			"2": {},
		},
	}, rev)
}

func TestFullyRevertMap(t *testing.T) {
	m := make(map[string]map[string]struct{})
	rev := FullyRevertMap(m)
	require.Equal(t, map[string]map[string]struct{}{}, rev)

	m = nil
	rev = FullyRevertMap(m)
	require.Nil(t, rev)

	m = map[string]map[string]struct{}{
		"1": {
			"2": {},
			"3": {},
			"4": {},
		},
		"2": {
			"3": {},
			"6": {},
		},
		"8":   {},
		"nil": nil,
	}
	rev = FullyRevertMap(m)
	require.Equal(t, map[string]map[string]struct{}{
		"1": {},
		"2": {
			"1": {},
		},
		"3": {
			"1": {},
			"2": {},
		},
		"4": {
			"1": {},
		},
		"6": {
			"2": {},
		},
		"8":   {},
		"nil": {},
	}, rev)
}

func TestCopySet(t *testing.T) {
	m := map[string]struct{}{}
	cp := CopySet(m)
	require.Equal(t, map[string]struct{}{}, cp)

	m = nil
	cp = CopySet(m)
	require.Nil(t, cp)

	m = map[string]struct{}{
		"a": {},
		"b": {},
	}
	cp = CopySet(m)
	require.Equal(t, map[string]struct{}{
		"a": {},
		"b": {},
	}, cp)

	m["c"] = struct{}{}
	require.Equal(t, map[string]struct{}{
		"a": {},
		"b": {},
		"c": {},
	}, m)
	require.Equal(t, map[string]struct{}{
		"a": {},
		"b": {},
	}, cp)
}

func TestAppendSet(t *testing.T) {
	base := make(map[string]struct{})
	add := map[string]struct{}{
		"key": {},
	}
	AppendSet(base, add)
	require.Equal(t, map[string]struct{}{
		"key": {},
	}, base)
	require.Equal(t, map[string]struct{}{
		"key": {},
	}, add)

	base = nil
	add = nil
	AppendSet(base, add)
	require.Nil(t, base)
	require.Nil(t, add)

	base = nil
	add = map[string]struct{}{
		"key": {},
	}
	AppendSet(base, add)
	require.Nil(t, base)
	require.Equal(t, map[string]struct{}{
		"key": {},
	}, add)

	base = map[string]struct{}{
		"key": {},
	}
	add = nil
	AppendSet(base, add)
	require.Equal(t, map[string]struct{}{
		"key": {},
	}, base)
	require.Nil(t, add)

	base = map[string]struct{}{
		"key": {},
	}
	add = map[string]struct{}{
		"anotherKey": {},
	}
	AppendSet(base, add)
	require.Equal(t, map[string]struct{}{
		"key":        {},
		"anotherKey": {},
	}, base)
	require.Equal(t, map[string]struct{}{
		"anotherKey": {},
	}, add)
}

func TestGetExtraElements(t *testing.T) {
	base := map[string]struct{}{}
	sample := map[string]struct{}{}
	extra := GetExtraElements(base, sample)
	require.Equal(t, map[string]struct{}{}, extra)

	base = nil
	sample = nil
	extra = GetExtraElements(base, sample)
	require.Equal(t, map[string]struct{}{}, extra)

	base = map[string]struct{}{
		"a": {},
	}
	sample = nil
	extra = GetExtraElements(base, sample)
	require.Equal(t, map[string]struct{}{}, extra)

	base = nil
	sample = map[string]struct{}{
		"a": {},
	}
	extra = GetExtraElements(base, sample)
	require.Equal(t, map[string]struct{}{
		"a": {},
	}, extra)

	base = map[string]struct{}{
		"a": {},
		"b": {},
		"c": {},
	}
	sample = map[string]struct{}{
		"c": {},
		"d": {},
		"b": {},
	}
	extra = GetExtraElements(base, sample)
	require.Equal(t, map[string]struct{}{
		"d": {},
	}, extra)
}

func TestSetsEqual(t *testing.T) {
	first := map[string]struct{}{}
	second := map[string]struct{}{}
	require.True(t, SetsEqual(first, second))

	first = nil
	second = nil
	require.True(t, SetsEqual(first, second))

	first = map[string]struct{}{}
	second = nil
	require.False(t, SetsEqual(first, second))

	first = nil
	second = map[string]struct{}{}
	require.False(t, SetsEqual(first, second))

	first = map[string]struct{}{
		"a": {},
		"b": {},
		"c": {},
	}
	second = map[string]struct{}{
		"c": {},
		"b": {},
		"a": {},
	}
	require.True(t, SetsEqual(first, second))

	first = map[string]struct{}{
		"a": {},
		"b": {},
	}
	second = map[string]struct{}{
		"a": {},
		"c": {},
	}
	require.False(t, SetsEqual(first, second))

	first = map[string]struct{}{
		"a": {},
	}
	second = map[string]struct{}{
		"a": {},
		"c": {},
	}
	require.False(t, SetsEqual(first, second))

	first = map[string]struct{}{
		"a": {},
		"b": {},
	}
	second = map[string]struct{}{
		"a": {},
	}
	require.False(t, SetsEqual(first, second))
}

func TestIntersect(t *testing.T) {
	first := map[string]struct{}{}
	second := map[string]struct{}{}
	intersect := Intersect(first, second)
	require.Equal(t, map[string]struct{}{}, intersect)

	first = nil
	second = nil
	intersect = Intersect(first, second)
	require.Nil(t, intersect)

	first = map[string]struct{}{}
	second = nil
	intersect = Intersect(first, second)
	require.Equal(t, map[string]struct{}{}, intersect)

	first = nil
	second = map[string]struct{}{}
	intersect = Intersect(first, second)
	require.Equal(t, map[string]struct{}{}, intersect)

	first = map[string]struct{}{
		"a": {},
		"b": {},
		"c": {},
	}
	second = nil
	intersect = Intersect(first, second)
	require.Equal(t, map[string]struct{}{
		"a": {},
		"b": {},
		"c": {},
	}, intersect)

	first = nil
	second = map[string]struct{}{
		"a": {},
		"b": {},
		"c": {},
	}
	intersect = Intersect(first, second)
	require.Equal(t, map[string]struct{}{
		"a": {},
		"b": {},
		"c": {},
	}, intersect)

	first = map[string]struct{}{
		"a": {},
		"b": {},
	}
	second = map[string]struct{}{
		"a": {},
		"c": {},
	}
	intersect = Intersect(first, second)
	require.Equal(t, map[string]struct{}{
		"a": {},
	}, intersect)

	first = map[string]struct{}{
		"a": {},
	}
	second = map[string]struct{}{
		"a": {},
		"b": {},
	}
	intersect = Intersect(first, second)
	require.Equal(t, map[string]struct{}{
		"a": {},
	}, intersect)

	first = map[string]struct{}{
		"a": {},
		"b": {},
	}
	second = map[string]struct{}{
		"a": {},
	}
	intersect = Intersect(first, second)
	require.Equal(t, map[string]struct{}{
		"a": {},
	}, intersect)
}

func TestMakeSetStr(t *testing.T) {
	m := map[string]struct{}{}
	str := MakeSetStr(m)
	require.Equal(t, "{}", str)

	m = nil
	str = MakeSetStr(m)
	require.Equal(t, "{}", str)

	m = map[string]struct{}{
		"a": {},
		"b": {},
	}
	str = MakeSetStr(m)
	require.Contains(t, []string{"{a, b}", "{b, a}"}, str)
}
