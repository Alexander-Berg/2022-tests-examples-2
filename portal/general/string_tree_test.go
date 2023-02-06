package common

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func assertRepresentation(t *testing.T, have [][]string, repr []string) {
	want := [][]string{}
	for _, r := range repr {
		want = append(want, strings.Split(r, "/"))
	}
	assert.Equal(t, want, have)
}

func assertPath(t *testing.T, have []string, repr string) {
	assert.Equal(t, strings.Split(repr, "/"), have)
}

func TestStringTree(t *testing.T) {
	tree := NewStringTree()
	assertRepresentation(t, tree.LeafPaths(), nil)
	assertRepresentation(t, tree.AllPaths(), nil)

	tree.Add("a", "b", "c")
	assertRepresentation(t, tree.LeafPaths(), []string{"a/b/c"})
	assertRepresentation(t, tree.AllPaths(), []string{"a", "a/b", "a/b/c"})

	tree.Add("a")
	assertRepresentation(t, tree.LeafPaths(), []string{"a/b/c"})
	assertRepresentation(t, tree.AllPaths(), []string{"a", "a/b", "a/b/c"})

	tree.Add("a", "b", "a")
	assertRepresentation(t, tree.LeafPaths(), []string{"a/b/a", "a/b/c"})
	assertRepresentation(t, tree.AllPaths(), []string{"a", "a/b", "a/b/a", "a/b/c"})

	tree.Add("b")
	assertRepresentation(t, tree.LeafPaths(), []string{"a/b/a", "a/b/c", "b"})
	assertRepresentation(t, tree.AllPaths(), []string{"a", "a/b", "a/b/a", "a/b/c", "b"})

	subtree := tree.GetSubtree("a", "b")
	assertRepresentation(t, subtree.LeafPaths(), []string{"a", "c"})
	assertRepresentation(t, subtree.AllPaths(), []string{"a", "c"})

	path, res := tree.Seek("a", "b", "d")
	assert.False(t, res)
	assertPath(t, path, "a/b/d")

	path, res = tree.Seek("a", "c", "b")
	assert.False(t, res)
	assertPath(t, path, "a/c")

	path, res = tree.Seek("a", "b", "c")
	assert.True(t, res)
	assertPath(t, path, "a/b/c")

	path, res = tree.Seek("a", "b")
	assert.True(t, res)
	assertPath(t, path, "a/b")

	tree.Remove("c")
	assertRepresentation(t, tree.LeafPaths(), []string{"a/b/a", "a/b/c", "b"})
	assertRepresentation(t, tree.AllPaths(), []string{"a", "a/b", "a/b/a", "a/b/c", "b"})

	tree.Remove("b")
	assertRepresentation(t, tree.LeafPaths(), []string{"a/b/a", "a/b/c"})
	assertRepresentation(t, tree.AllPaths(), []string{"a", "a/b", "a/b/a", "a/b/c"})

	tree.Remove("a", "b")
	assertRepresentation(t, tree.LeafPaths(), []string{"a"})
	assertRepresentation(t, tree.AllPaths(), []string{"a"})
}

func buildTree(paths ...string) stringTree {
	ret := NewStringTree()
	for _, path := range paths {
		pathSplit := strings.Split(path, "/")
		ret.Add(pathSplit...)
	}
	return ret
}

func TestAdd(t *testing.T) {
	type testCase struct {
		name                 string
		tree                 stringTree
		addPath              string
		expectPanic          bool
		expectRepresentation []string
	}
	testCases := []testCase{
		{
			name:        "nil",
			tree:        nil,
			addPath:     "something",
			expectPanic: true,
		},
		{
			name:                 "new path",
			tree:                 NewStringTree(),
			addPath:              "a/b",
			expectRepresentation: []string{"a/b"},
		},
		{
			name:                 "path without collisions",
			tree:                 buildTree("a/b"),
			addPath:              "c/b",
			expectRepresentation: []string{"a/b", "c/b"},
		},
		{
			name:                 "path with partial collision",
			tree:                 buildTree("a/b"),
			addPath:              "a/c",
			expectRepresentation: []string{"a/b", "a/c"},
		},
		{
			name:                 "path with full collision",
			tree:                 buildTree("a/b"),
			addPath:              "a/b",
			expectRepresentation: []string{"a/b"},
		},
		{
			name:                 "path contained in other path",
			tree:                 buildTree("a/b/c"),
			addPath:              "a/b",
			expectRepresentation: []string{"a/b/c"},
		},
		{
			name:                 "path extending other path",
			tree:                 buildTree("a/b"),
			addPath:              "a/b/c",
			expectRepresentation: []string{"a/b/c"},
		},
		{
			name:                 "no path",
			tree:                 buildTree("a/b"),
			expectRepresentation: []string{"a/b"},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			if testCase.expectPanic {
				defer func() {
					require.Error(t, recover().(error))
				}()
			}
			if testCase.addPath == "" {
				testCase.tree.Add()
			} else {
				testCase.tree.Add(strings.Split(testCase.addPath, "/")...)
			}
			assertRepresentation(t, testCase.tree.LeafPaths(), testCase.expectRepresentation)
		})
	}
}

func TestRemove(t *testing.T) {
	type testCase struct {
		name                 string
		tree                 stringTree
		removePath           string
		expectPanic          bool
		expectRepresentation []string
	}
	testCases := []testCase{
		{
			name:                 "nil",
			tree:                 nil,
			removePath:           "something",
			expectRepresentation: nil,
		},
		{
			name:                 "no path",
			tree:                 buildTree("a/b"),
			removePath:           "",
			expectRepresentation: []string{"a/b"}, //условно ожидаемое поведение, но можно оспорить
		},
		{
			name:                 "new path",
			tree:                 NewStringTree(),
			removePath:           "a/b",
			expectRepresentation: nil,
		},
		{
			name:                 "path without collisions",
			tree:                 buildTree("a/b"),
			removePath:           "c/b",
			expectRepresentation: []string{"a/b"},
		},
		{
			name:                 "path extending existing path",
			tree:                 buildTree("a/b"),
			removePath:           "a/b/c",
			expectRepresentation: []string{"a/b"},
		},
		{
			name:                 "path to leaf",
			tree:                 buildTree("a/b", "c/d"),
			removePath:           "a/b",
			expectRepresentation: []string{"a", "c/d"},
		},
		{
			name:                 "path to non-leaf",
			tree:                 buildTree("a/b/c/d", "a/b/d", "c/b/a"),
			removePath:           "a/b",
			expectRepresentation: []string{"a", "c/b/a"},
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			if testCase.expectPanic {
				defer func() {
					require.Error(t, recover().(error))
				}()
			}
			if testCase.removePath == "" {
				testCase.tree.Remove()
			} else {
				testCase.tree.Remove(strings.Split(testCase.removePath, "/")...)
			}
			assertRepresentation(t, testCase.tree.LeafPaths(), testCase.expectRepresentation)
		})
	}
}

func TestGetSubtree(t *testing.T) {
	type testCase struct {
		name        string
		tree        stringTree
		subtreePath string
		expectTree  stringTree
	}
	testCases := []testCase{
		{
			name:        "nil",
			tree:        nil,
			subtreePath: "something",
			expectTree:  nil,
		},
		{
			name:        "empty map",
			tree:        buildTree(),
			subtreePath: "",
			expectTree:  buildTree(),
		},
		{
			name:        "root subtree",
			tree:        buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			subtreePath: "",
			expectTree:  buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
		},
		{
			name:        "nonexisting subtree",
			tree:        buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			subtreePath: "e",
			expectTree:  nil,
		},
		{
			name:        "path to leaf",
			tree:        buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			subtreePath: "a/b/c",
			expectTree:  buildTree(),
		},
		{
			name:        "path to nonleaf",
			tree:        buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			subtreePath: "a",
			expectTree:  buildTree("b/c", "b/d", "c"),
		},
		{
			name:        "path to nonleaf alt",
			tree:        buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			subtreePath: "c",
			expectTree:  buildTree("d"),
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			var subtree StringTree
			if testCase.subtreePath == "" {
				subtree = testCase.tree.GetSubtree()
			} else {
				subtree = testCase.tree.GetSubtree(strings.Split(testCase.subtreePath, "/")...)
			}
			subtreeCasted := stringTree(nil)
			if subtree != nil {
				subtreeCasted = subtree.(stringTree)
			}
			assert.Equal(t, testCase.expectTree.LeafPaths(), subtreeCasted.LeafPaths())
		})
	}
}

func TestHas(t *testing.T) {
	type testCase struct {
		name    string
		tree    stringTree
		hasPath string
		result  bool
	}
	testCases := []testCase{
		{
			name:    "nil",
			tree:    nil,
			hasPath: "something",
			result:  false,
		},
		{
			name:    "nil has itself",
			tree:    nil,
			hasPath: "",
			result:  false,
		},
		{
			name:    "empty has itself",
			tree:    buildTree(),
			hasPath: "",
			result:  true,
		},
		{
			name:    "has leaf",
			tree:    buildTree("a/b"),
			hasPath: "a/b",
			result:  true,
		},
		{
			name:    "has node",
			tree:    buildTree("a/b"),
			hasPath: "a",
			result:  true,
		},
		{
			name:    "doesn't have",
			tree:    buildTree("a/b"),
			hasPath: "b",
			result:  false,
		},
		{
			name:    "doesn't have alt",
			tree:    buildTree("a/b"),
			hasPath: "a/c",
			result:  false,
		},
		{
			name:    "bigger path",
			tree:    buildTree("a/b"),
			hasPath: "a/b/c/d",
			result:  false,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			var result bool
			if testCase.hasPath == "" {
				result = testCase.tree.Has()
			} else {
				result = testCase.tree.Has(strings.Split(testCase.hasPath, "/")...)
			}
			assert.Equal(t, testCase.result, result)
		})
	}
}

func TestHasLeaf(t *testing.T) {
	type testCase struct {
		name    string
		tree    stringTree
		hasPath string
		result  bool
	}
	testCases := []testCase{
		{
			name:    "nil",
			tree:    nil,
			hasPath: "something",
			result:  false,
		},
		{
			name:    "nil has leaf itself",
			tree:    nil,
			hasPath: "",
			result:  false,
		},
		{
			name:    "empty has leaf itself",
			tree:    buildTree(),
			hasPath: "",
			result:  true,
		},
		{
			name:    "has leaf",
			tree:    buildTree("a/b"),
			hasPath: "a/b",
			result:  true,
		},
		{
			name:    "has node",
			tree:    buildTree("a/b"),
			hasPath: "a",
			result:  false,
		},
		{
			name:    "doesn't have",
			tree:    buildTree("a/b"),
			hasPath: "b",
			result:  false,
		},
		{
			name:    "doesn't have alt",
			tree:    buildTree("a/b"),
			hasPath: "a/c",
			result:  false,
		},
		{
			name:    "bigger path",
			tree:    buildTree("a/b"),
			hasPath: "a/b/c/d",
			result:  false,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			var result bool
			if testCase.hasPath == "" {
				result = testCase.tree.HasLeaf()
			} else {
				result = testCase.tree.HasLeaf(strings.Split(testCase.hasPath, "/")...)
			}
			assert.Equal(t, testCase.result, result)
		})
	}
}

func TestIsLeaf(t *testing.T) {
	type testCase struct {
		name   string
		tree   stringTree
		result bool
	}
	testCases := []testCase{
		{
			name:   "nil",
			tree:   nil,
			result: false,
		},
		{
			name:   "not a leaf",
			tree:   buildTree("a/b"),
			result: false,
		},
		{
			name:   "still not a leaf",
			tree:   buildTree("a"),
			result: false,
		},
		{
			name:   "a leaf",
			tree:   buildTree(),
			result: true,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			assert.Equal(t, testCase.result, testCase.tree.IsLeaf())
		})
	}
}

func TestIsEmpty(t *testing.T) {
	type testCase struct {
		name   string
		tree   stringTree
		result bool
	}
	testCases := []testCase{
		{
			name:   "nil",
			tree:   nil,
			result: true,
		},
		{
			name:   "not empty",
			tree:   buildTree("a/b"),
			result: false,
		},
		{
			name:   "still not empty",
			tree:   buildTree("a"),
			result: false,
		},
		{
			name:   "empty",
			tree:   buildTree(),
			result: true,
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			assert.Equal(t, testCase.result, testCase.tree.IsEmpty())
		})
	}
}

func TestSeek(t *testing.T) {
	type testCase struct {
		name       string
		tree       stringTree
		seekPath   string
		resultPath string
		result     bool
	}
	testCases := []testCase{
		{
			name:     "nil, seek some",
			tree:     nil,
			seekPath: "some",
			result:   false,
		},
		{
			name:     "nil, seek none",
			tree:     nil,
			seekPath: "",
			result:   false,
		},
		{
			name:       "empty, seek some",
			tree:       buildTree(),
			seekPath:   "some",
			result:     false,
			resultPath: "some",
		},
		{
			name:       "empty, seek none",
			tree:       buildTree(),
			seekPath:   "",
			result:     true,
			resultPath: "",
		},
		{
			name:       "no collision",
			tree:       buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			seekPath:   "f/d/e",
			result:     false,
			resultPath: "f",
		},
		{
			name:       "partial collision",
			tree:       buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			seekPath:   "a/f/d/e",
			result:     false,
			resultPath: "a/f",
		},
		{
			name:       "path to node",
			tree:       buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			seekPath:   "a/b",
			result:     true,
			resultPath: "a/b",
		},
		{
			name:       "path to leaf",
			tree:       buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			seekPath:   "a/b/c",
			result:     true,
			resultPath: "a/b/c",
		},
		{
			name:       "path to beyond leaf",
			tree:       buildTree("a/b/c", "a/b/d", "a/c", "c/d", "e"),
			seekPath:   "a/b/c/d/e",
			result:     false,
			resultPath: "a/b/c/d",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			var resultPath []string
			var result bool
			if testCase.seekPath == "" {
				resultPath, result = testCase.tree.Seek()
			} else {
				resultPath, result = testCase.tree.Seek(strings.Split(testCase.seekPath, "/")...)
			}
			var expectedResultPathSplit []string
			if testCase.resultPath != "" {
				expectedResultPathSplit = strings.Split(testCase.resultPath, "/")
			}
			assert.Equal(t, testCase.result, result)
			assert.Equal(t, resultPath, expectedResultPathSplit)
		})
	}
}
