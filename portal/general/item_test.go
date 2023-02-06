package madm

import (
	"fmt"
	"math"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"
)

func Test_selectRandomWeighted_cases(t *testing.T) {
	items := Items{
		itemWithWeight(0, defaultKey, 0),
		itemWithWeight(1, defaultKey, 0),
		itemWithWeight(2, defaultKey, 0),
	}
	require.Len(t, selectRandomWeighted(items, 0, defaultKey), 0)
	require.Len(t, selectRandomWeighted(items, 1, defaultKey), 0)

	items[0] = itemWithWeight(0, defaultKey, 1)
	require.Len(t, selectRandomWeighted(items, 0, defaultKey), 0)
	require.Len(t, selectRandomWeighted(items, 1, defaultKey), 1)

	items[1] = itemWithWeight(0, defaultKey, 1)
	items[2] = itemWithWeight(0, defaultKey, 1)
	require.Len(t, selectRandomWeighted(items, 0, defaultKey), 0)
	require.Len(t, selectRandomWeighted(items, 1, defaultKey), 1)
	require.Len(t, selectRandomWeighted(items, 2, defaultKey), 2)
	require.Len(t, selectRandomWeighted(items, 4, defaultKey), 3)

	require.Len(t, selectRandomWeighted(nil, 1, defaultKey), 0)
}

func Test_selectRandomWeighted_weightedSelection(t *testing.T) {
	for _, key := range []string{defaultKey, customKey} {
		t.Run(key, func(t *testing.T) {
			var seed int64 = 42
			newRandSeed = func() int64 {
				seed++
				return seed
			}
			items := Items{
				itemWithWeight(0, key, 0),
				itemWithWeight(1, key, 1),
				itemWithWeight(2, key, 3),
			}
			var counts = make(map[int]int)
			for i := 0; i < 10000; i++ {
				selected := selectRandomWeighted(items, 1, key)
				require.Equal(t, 1, len(selected))
				counts[selected[0].id]++
			}
			require.Zero(t, counts[0])
			require.True(t, math.Abs(float64(counts[2])/float64(counts[1])-3) < 0.1)
		})
	}
}

const (
	defaultKey = "weight"
	customKey  = "custom"
)

func itemWithWeight(id int, key string, weight int) Item {
	str := fmt.Sprintf(`{"%s": "%d"}`, key, weight)
	value := fastjson.MustParse(str)
	return Item{raw: value, id: id}
}
