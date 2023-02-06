package parser

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/pkg/macros/mctests"
)

type testCache struct {
	writeCount   int
	getInfoCount int
	getTypeCount int
	cacheHits    int

	cache *cache
}

var _ cacheInterface = &testCache{}

func newTestCache() *testCache {
	return &testCache{
		cache: newCache(),
	}
}

func (m *testCache) resetStat() {
	m.writeCount = 0
	m.getTypeCount = 0
	m.getInfoCount = 0
	m.cacheHits = 0
}

func (m *testCache) resetAll() {
	m.cache = newCache()
	m.resetStat()
}

func (m *testCache) write(str string, info Item) {
	m.writeCount++

	m.cache.write(str, info)
}

func (m *testCache) getInfo(str string, itemType ItemType) (Item, bool) {
	m.getInfoCount++

	info, ok := m.cache.getInfo(str, itemType)
	if ok {
		m.cacheHits++
	}

	return info, ok
}

func (m *testCache) getType(str string) ItemType {
	m.getTypeCount++

	ty := m.cache.getType(str)
	if ty != InvalidItem {
		m.cacheHits++
	}

	return ty
}

var (
	testCacheInstance = newTestCache()
	testParser        = &Parser{cache: testCacheInstance}
)

func TestCacheParseAll(t *testing.T) {
	//-------------------------------------------Preparing------------------------------------

	defMapOfArr := mctests.ReadMapOfArrays(mctests.FlatMacrosFilename)

	totalCnt := 0
	allElems := map[string]struct{}{}
	for _, exp := range defMapOfArr {
		for _, elem := range exp {
			allElems[elem] = struct{}{}
			totalCnt++
		}
	}
	totalDistinctCnt := len(allElems)

	//---------------------------------Filling out with ParseMacroItem------------------------

	require.Zero(t, testCacheInstance.writeCount)
	require.Zero(t, testCacheInstance.getInfoCount)
	require.Zero(t, testCacheInstance.getTypeCount)
	require.Zero(t, testCacheInstance.cacheHits)

	for _, exp := range defMapOfArr {
		for _, elem := range exp {
			_ = testParser.ParseMacroItem(elem)
		}
	}

	// Greater due to
	//   - projects which also write projectIDs and nets to cache
	//   - nets which also write IPs to cache
	require.GreaterOrEqual(t, len(testCacheInstance.cache.cache), totalDistinctCnt)
	require.GreaterOrEqual(t, testCacheInstance.writeCount, totalDistinctCnt)

	require.True(t, testCacheInstance.getInfoCount >= 0)
	require.True(t, testCacheInstance.getTypeCount >= 0)
	require.True(t, testCacheInstance.cacheHits >= 0)

	testCacheInstance.resetAll()

	//--------------------------------Filling out with GetMacroItemType-----------------------

	require.Zero(t, testCacheInstance.writeCount)
	require.Zero(t, testCacheInstance.getInfoCount)
	require.Zero(t, testCacheInstance.getTypeCount)
	require.Zero(t, testCacheInstance.cacheHits)

	for _, exp := range defMapOfArr {
		for _, elem := range exp {
			_ = testParser.GetMacroItemType(elem)
		}
	}

	// Greater due to
	//   - projects which also write projectIDs and nets to cache
	//   - nets which also write IPs to cache
	require.GreaterOrEqual(t, len(testCacheInstance.cache.cache), totalDistinctCnt)
	require.GreaterOrEqual(t, testCacheInstance.writeCount, totalDistinctCnt)

	require.True(t, testCacheInstance.getInfoCount >= 0)
	require.True(t, testCacheInstance.getTypeCount >= 0)
	require.True(t, testCacheInstance.cacheHits >= 0)

	testCacheInstance.resetStat()

	//----------------------------------Reading out with ParseMacroItem-----------------------

	for _, exp := range defMapOfArr {
		for _, elem := range exp {
			_ = testParser.ParseMacroItem(elem)
		}
	}

	require.Zero(t, testCacheInstance.writeCount)
	require.Equal(t, totalCnt, testCacheInstance.getInfoCount)
	require.Zero(t, testCacheInstance.getTypeCount)
	require.Equal(t, totalCnt, testCacheInstance.cacheHits)

	testCacheInstance.resetStat()

	//--------------------------------Reading out with GetMacroItemType-----------------------

	for _, exp := range defMapOfArr {
		for _, elem := range exp {
			_ = testParser.GetMacroItemType(elem)
		}
	}

	require.Zero(t, testCacheInstance.writeCount)
	require.Zero(t, testCacheInstance.getInfoCount)
	require.Equal(t, totalCnt, testCacheInstance.getTypeCount)
	require.Equal(t, totalCnt, testCacheInstance.cacheHits)
}
