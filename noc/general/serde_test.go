package graph

import (
	"context"
	"io/ioutil"
	"path"
	"sort"
	"testing"

	"cuelang.org/go/pkg/strings"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
)

func dirEqual(t *testing.T, dir1, dir2 string) {
	dir1Content, err := ioutil.ReadDir(dir1)
	require.NoError(t, err)
	for _, entry := range dir1Content {
		content1, err := ioutil.ReadFile(path.Join(dir1, entry.Name()))
		require.NoError(t, err)
		strs1 := strings.Split(string(content1), "\n")
		sort.Strings(strs1)

		content2, err := ioutil.ReadFile(path.Join(dir2, entry.Name()))
		require.NoError(t, err)
		strs2 := strings.Split(string(content2), "\n")
		sort.Strings(strs2)

		assert.Equal(t, strs1, strs2)
	}
}

func TestSerDe(t *testing.T) {
	g := newTestGraph(t)
	g.addMacro("_ABC_", "a1.com")
	g.addRuleset(`add allow tcp from { _ABC_ } to { b1.com }`)
	g.commit()

	g.addRuleset(`add allow tcp from { a2.com } to { b1.com }`)
	g.commit()

	g.addRuleset(`add allow tcp from { a1.com } to { b1.com }`)
	g.commit()

	dir := yatest.OutputPath("serde_simple_1")
	err := g.Save(dir)
	require.NoError(t, err)

	g2, err := g.Clone(context.Background())
	require.NoError(t, err)

	assert.Equal(t, len(g.store), len(g2.store))
	for name := range g.store {
		assert.Equal(t, len(g.store[name].down), len(g2.store[name].down))
	}
	assert.Equal(t, len(g.lastRev), len(g2.lastRev))

	dir2 := yatest.OutputPath("serde_simple_2")
	err = g2.Save(dir2)
	require.NoError(t, err)

	dirEqual(t, dir, dir2)
}
