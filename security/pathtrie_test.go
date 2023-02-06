package container

import (
	"runtime"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestPathTrie(t *testing.T) {
	// trie1

	trie1 := PathTrie{}
	_, ok := trie1.Insert(testPath("/"), 123)
	require.True(t, ok)
	v, ok := trie1.GetParent(testPath("/"))
	require.True(t, ok)
	require.Equal(t, 123, v)
	v, ok = trie1.GetParent(testPath("/usr/bin"))
	require.True(t, ok)
	require.Equal(t, 123, v)
	_, ok = trie1.Insert(testPath("/usr"), 234)
	require.True(t, ok)
	v, ok = trie1.GetParent(testPath("/etc"))
	require.True(t, ok)
	require.Equal(t, 123, v)
	v, ok = trie1.GetParent(testPath("/usr"))
	require.True(t, ok)
	require.Equal(t, 234, v)
	v, ok = trie1.GetParent(testPath("/usr/bin"))
	require.True(t, ok)
	require.Equal(t, 234, v)

	walkedPaths1 := map[string]int{}
	trie1.Walk(func(path string, value interface{}) {
		walkedPaths1[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/"):    123,
		testPath("/usr"): 234,
	}, walkedPaths1)

	walkedRoots1 := map[string]int{}
	trie1.WalkRoots(func(path string, value interface{}) {
		walkedRoots1[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/"): 123,
	}, walkedRoots1)

	trie1.LeaveOnlyRoots()
	walkedCleanedPaths1 := map[string]int{}
	trie1.WalkRoots(func(path string, value interface{}) {
		walkedCleanedPaths1[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/"): 123,
	}, walkedCleanedPaths1)

	// trie2

	trie2 := PathTrie{}
	_, ok = trie2.Insert(testPath("/etc/service/some/conf"), 345)
	require.True(t, ok)
	_, ok = trie2.Insert(testPath("/etc/service/some/conf"), 789)
	require.False(t, ok)
	_, ok = trie2.GetParent(testPath("/"))
	require.False(t, ok)
	_, ok = trie2.GetParent(testPath("/etc"))
	require.False(t, ok)
	_, ok = trie2.GetParent(testPath("/etc/service"))
	require.False(t, ok)
	_, ok = trie2.GetParent(testPath("/etc/service/some"))
	require.False(t, ok)
	v, ok = trie2.GetParent(testPath("/etc/service/some/conf"))
	require.True(t, ok)
	require.Equal(t, 345, v)
	_, ok = trie2.GetParent(testPath("/etc/service/some/conf2"))
	require.False(t, ok)
	_, ok = trie2.Insert(testPath("/etc/service/some/conf/another/level"), 12345)
	require.True(t, ok)
	v, ok = trie2.GetParent(testPath("/etc/service/some/conf/another"))
	require.True(t, ok)
	require.Equal(t, 345, v)
	v, ok = trie2.GetParent(testPath("/etc/service/some/conf/another/level"))
	require.True(t, ok)
	require.Equal(t, 12345, v)
	v, ok = trie2.GetParent(testPath("/etc/service/some/conf/another/level/"))
	require.True(t, ok)
	require.Equal(t, 12345, v)
	v, ok = trie2.GetParent(testPath("/etc/service/some/conf/another/level/yet"))
	require.True(t, ok)
	require.Equal(t, 12345, v)
	_, ok = trie2.Insert(testPath("/usr/share/service"), 56789)
	require.True(t, ok)

	walkedPaths2 := map[string]int{}
	trie2.Walk(func(path string, value interface{}) {
		walkedPaths2[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/etc/service/some/conf"):               345,
		testPath("/etc/service/some/conf/another/level"): 12345,
		testPath("/usr/share/service"):                   56789,
	}, walkedPaths2)

	walkedRoots2 := map[string]int{}
	trie2.WalkRoots(func(path string, value interface{}) {
		walkedRoots2[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/etc/service/some/conf"): 345,
		testPath("/usr/share/service"):     56789,
	}, walkedRoots2)

	trie2.LeaveOnlyRoots()
	walkedCleanedPaths2 := map[string]int{}
	trie2.WalkRoots(func(path string, value interface{}) {
		walkedCleanedPaths2[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/etc/service/some/conf"): 345,
		testPath("/usr/share/service"):     56789,
	}, walkedCleanedPaths2)

	// trie3

	trie3 := PathTrie{}
	trie3.WalkFrom(testPath("/"), func(path string, value interface{}) {
		t.Error("should be unreachable, got", path, value)
	})
	ok = trie3.Remove(testPath("/"))
	require.False(t, ok)
	ok = trie3.Remove(testPath("/usr"))
	require.False(t, ok)
	_, ok = trie3.Insert(testPath("/"), 1)
	require.True(t, ok)
	ok = trie3.Remove(testPath("/"))
	require.True(t, ok)
	ok = trie3.Remove(testPath("/"))
	require.False(t, ok)

	_, ok = trie3.Insert(testPath("/usr/bin"), 2)
	require.True(t, ok)
	_, ok = trie3.Insert(testPath("/usr/lib"), 3)
	require.True(t, ok)
	_, ok = trie3.Insert(testPath("/usr/bin/sh"), 4)
	require.True(t, ok)
	trie3.WalkFrom(testPath("/us"), func(path string, value interface{}) {
		t.Error("should be unreachable, got", path, value)
	})

	walked3 := map[string]int{}
	trie3.WalkFrom(testPath("/usr"), func(path string, value interface{}) {
		walked3[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/usr/bin"):    2,
		testPath("/usr/bin/sh"): 4,
		testPath("/usr/lib"):    3,
	}, walked3)

	walked3 = map[string]int{}
	trie3.WalkFrom(testPath("/usr/bin"), func(path string, value interface{}) {
		walked3[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/usr/bin"):    2,
		testPath("/usr/bin/sh"): 4,
	}, walked3)

	ok = trie3.Remove(testPath("/usr/bin"))
	require.True(t, ok)
	walked3 = map[string]int{}
	trie3.WalkFrom(testPath("/usr/bin"), func(path string, value interface{}) {
		walked3[path] = value.(int)
	})
	require.Equal(t, map[string]int{
		testPath("/usr/bin/sh"): 4,
	}, walked3)

	ok = trie3.Remove(testPath("/usr/bin/sh"))
	require.True(t, ok)
	trie3.WalkFrom(testPath("/usr/bin"), func(path string, value interface{}) {
		t.Error("should be unreachable, got", path, value)
	})
}

func testPath(path string) string {
	if runtime.GOOS == "windows" {
		p := strings.ReplaceAll(path, "/", "\\")
		if len(path) > 0 && path[0] == '/' {
			return "C:" + p
		}
		return p
	} else {
		return path
	}
}
