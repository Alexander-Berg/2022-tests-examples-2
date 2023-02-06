package mysql

import (
	"context"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/filter"
	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

var fallbacksList = []*model.Fallback{
	{
		ID:      "33",
		SrcGate: "infobip",
		SrcName: "Yandex",
		DstGate: "gms",
		DstName: "Yandex",
		Order:   0,
	},
	{
		ID:      "42",
		SrcGate: "gms",
		SrcName: "Yandex",
		DstGate: "m1",
		DstName: "Yandex",
		Order:   1,
	},
}

func TestMySQLProvider_GetFallbacksCount(t *testing.T) {
	provider, _ := initProvider()
	count, err := provider.GetFallbacksCount(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, uint64(2), count)
}

func TestMySQLProvider_GetFallbacks_All(t *testing.T) {
	provider, _ := initProvider()
	fallbacks, err := provider.GetFallbacks(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, fallbacksList, fallbacks)
}

func TestMySQLProvider_GetFallbacks_CheckPages(t *testing.T) {
	provider, _ := initProvider()

	fallbacks, err := provider.GetFallbacks(context.Background(), "0", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Fallback{
		fallbacksList[0],
	}, fallbacks)

	fallbacks, err = provider.GetFallbacks(context.Background(), "33", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Fallback{
		fallbacksList[1],
	}, fallbacks)

	fallbacks, err = provider.GetFallbacks(context.Background(), "42", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Fallback{}, fallbacks)
}

func checkDeletedFallbacks(t *testing.T, provider *Provider, toDelete []model.EntityID, toRemain []model.EntityID, affected int64) {
	err := provider.SetFallbacks(context.Background(), toDelete, nil, nil, nil)
	if affected == 0 {
		require.Error(t, err)
	} else {
		require.NoError(t, err)
	}
	fallbacks, err := provider.GetFallbacks(context.Background(), "0", 200, nil)
	require.NoError(t, err)
	require.Equal(t, len(toRemain), len(fallbacks))
	for i := range fallbacks {
		require.Equal(t, toRemain[i], fallbacks[i].ID)
	}
}

func TestMySQLProvider_DeleteFallbacks_Some(t *testing.T) {
	provider, _ := initProvider()
	checkDeletedFallbacks(t, provider, []model.EntityID{"0", "33"}, []model.EntityID{"33", "42"}, 0)
	checkDeletedFallbacks(t, provider, []model.EntityID{"33"}, []model.EntityID{"42"}, 1)
	checkDeletedFallbacks(t, provider, []model.EntityID{"33"}, []model.EntityID{"42"}, 0)
	checkDeletedFallbacks(t, provider, []model.EntityID{"42"}, []model.EntityID{}, 1)
}

func TestMySQLProvider_DeleteFallbacks_All(t *testing.T) {
	provider, _ := initProvider()
	checkDeletedFallbacks(t, provider, []model.EntityID{"33", "42"}, []model.EntityID{}, 2)
}

func TestMySQLProvider_CreateFallbacks(t *testing.T) {
	provider, _ := initProvider()
	newFallback := &model.Fallback{
		SrcGate: "infobip",
		SrcName: "Ya.Market",
		DstGate: "gms",
		DstName: "Yandex",
		Order:   11,
	}
	err := provider.SetFallbacks(context.Background(), nil, []*model.Fallback{newFallback}, nil, nil)
	require.NoError(t, err)

	fallbacks, err := provider.GetFallbacks(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	newFallback.ID = "43"
	require.Equal(t, []*model.Fallback{
		fallbacks[0],
		fallbacks[1],
		newFallback,
	}, fallbacks)
}

func TestMySQLProvider_UpdateFallbacks(t *testing.T) {
	provider, _ := initProvider()
	newFallback := &model.Fallback{
		ID:      "13",
		SrcGate: "infobip",
		SrcName: "Ya.Market",
		DstGate: "m1",
		DstName: "Yandex",
		Order:   0,
	}
	err := provider.SetFallbacks(context.Background(), nil, nil, []*model.Fallback{newFallback}, nil)
	require.Error(t, err)
	fallbacks, err := provider.GetFallbacks(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, fallbacksList, fallbacks)

	newFallback.ID = "33"
	err = provider.SetFallbacks(context.Background(), nil, nil, []*model.Fallback{newFallback}, nil)
	require.NoError(t, err)
	fallbacks, err = provider.GetFallbacks(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Fallback{
		newFallback,
		fallbacks[1],
	}, fallbacks)
}

func TestMySQLProvider_prepareSelectFallbacksQuery(t *testing.T) {
	query, args, err := PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.FieldFilter{
		Field:     model.FallBackIDAlias,
		CompareOp: filter.Equal,
		Values:    []string{"33"},
	}, DBEntitySpec{filterFields: fallbacksFilterFields, selectPredicate: selectFallbacksPredicate, selectQueryTemplate: selectFallbacksQueryTemplate, tableName: fallbacksTableName})
	require.NoError(t, err)
	tail := strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t, "id > ? AND id IN (?) ORDER BY id LIMIT ?", tail)
	require.EqualValues(t, []interface{}{uint64(0), "33", uint64(100)}, args)

	query, args, err = PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.LogicOpFilter{
		LogicOp: filter.LogicAnd,
		Args: []filter.FilterContainer{
			{
				Filter: &filter.FieldFilter{
					Field:     model.SrcgateAlias,
					CompareOp: filter.Contains,
					Values:    []string{"bip"},
				},
			},
			{
				Filter: &filter.FieldFilter{
					Field:     model.OrderAlias,
					CompareOp: filter.Less,
					Values:    []string{"1"},
				},
			},
		},
	}, DBEntitySpec{filterFields: fallbacksFilterFields, selectPredicate: selectFallbacksPredicate, selectQueryTemplate: selectFallbacksQueryTemplate, tableName: fallbacksTableName})
	require.NoError(t, err)
	tail = strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t, "id > ? AND (srcgate LIKE ? AND `order` < ?) ORDER BY id LIMIT ?", tail)
	require.EqualValues(t, []interface{}{uint64(0), "%bip%", "1", uint64(100)}, args)
}

func TestMySQLProvider_GetFallbacks_WithFilter(t *testing.T) {
	type TestCase struct {
		fallbacksFilter   filter.Filter
		expectedFallbacks []model.EntityID
		expectedCount     uint64
		err               string
	}

	cases := []TestCase{
		{
			fallbacksFilter: &filter.FieldFilter{
				Field:     "some_random_field",
				CompareOp: filter.Equal,
				Values:    []string{"some_random_value"},
			},
			err: "unexpected field 'some_random_field'",
		},
		{
			fallbacksFilter: &filter.FieldFilter{
				Field:     model.FallBackIDAlias,
				CompareOp: filter.Equal,
				Values:    []string{"33"},
			},
			expectedFallbacks: []model.EntityID{"33"},
			expectedCount:     1,
		},
		{
			fallbacksFilter: &filter.FieldFilter{
				Field:     model.SrcgateAlias,
				CompareOp: filter.StartsWith,
				Values:    []string{"info"},
			},
			expectedFallbacks: []model.EntityID{"33"},
			expectedCount:     1,
		},
		{
			fallbacksFilter: &filter.FieldFilter{
				Field:     model.OrderAlias,
				CompareOp: filter.More,
				Values:    []string{"0"},
			},
			expectedFallbacks: []model.EntityID{"42"},
			expectedCount:     1,
		},
	}

	provider, _ := initProvider()

	for idx, c := range cases {
		actualFallbacks, err := provider.GetFallbacks(context.Background(), "0", 200, c.fallbacksFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, len(c.expectedFallbacks), len(actualFallbacks), idx)
			for i := 0; i < len(actualFallbacks); i++ {
				require.Equal(t, c.expectedFallbacks[i], actualFallbacks[i].ID)
			}
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
		totalCount, err := provider.GetFallbacksCount(context.Background(), c.fallbacksFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, c.expectedCount, totalCount)
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
	}
}
