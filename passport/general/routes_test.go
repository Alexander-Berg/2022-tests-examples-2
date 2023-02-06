package mysql

import (
	"context"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/filter"
	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

func TestMySQLProvider_prepareSelectRoutesQuery(t *testing.T) {
	query, args, err := PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.FieldFilter{
		Field:     model.GateIDFieldAlias,
		CompareOp: filter.Equal,
		Values:    []string{"113"},
	}, DBEntitySpec{filterFields: routesFilterFields, selectPredicate: selectRoutesPredicate, selectQueryTemplate: selectRoutesInfoQueryTemplate, tableName: routesTableName})
	require.NoError(t, err)
	tail := strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t, `ruleid > ? AND routes.gateid IN (?)
ORDER BY routes.ruleid
LIMIT ?
`, tail)
	require.EqualValues(t, []interface{}{uint64(0), "113", uint64(100)}, args)

	query, args, err = PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.LogicOpFilter{
		LogicOp: filter.LogicAnd,
		Args: []filter.FilterContainer{
			{
				Filter: &filter.FieldFilter{
					Field:     "mode",
					CompareOp: filter.Contains,
					Values:    []string{"taxi"},
				},
			},
			{
				Filter: &filter.FieldFilter{
					Field:     "destination",
					CompareOp: filter.StartsWith,
					Values:    []string{"+7", "+20"},
				},
			},
		},
	}, DBEntitySpec{filterFields: routesFilterFields, selectPredicate: selectRoutesPredicate, selectQueryTemplate: selectRoutesInfoQueryTemplate, tableName: routesTableName})
	require.NoError(t, err)
	tail = strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t, `ruleid > ? AND (routes.mode LIKE ? AND (routes.destination LIKE ? OR routes.destination LIKE ?))
ORDER BY routes.ruleid
LIMIT ?
`, tail)
	require.EqualValues(t, []interface{}{uint64(0), "%taxi%", "+7%", "+20%", uint64(100)}, args)
}

func TestMySQLProvider_GetRoutesCount(t *testing.T) {
	provider, _ := initProvider()

	count, err := provider.GetRoutesCount(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, uint64(3), count)

	count, err = provider.GetRoutesCount(context.Background(), &filter.FieldFilter{
		Field:     model.ModeFieldAlias,
		CompareOp: filter.Contains,
		Values:    []string{"lida"},
	})
	require.NoError(t, err)
	require.Equal(t, uint64(2), count)

	count, err = provider.GetRoutesCount(context.Background(), &filter.FieldFilter{
		Field:     model.GateIDFieldAlias,
		CompareOp: filter.Equal,
		Values:    []string{"666"},
	})
	require.NoError(t, err)
	require.Equal(t, uint64(0), count)

	count, err = provider.GetRoutesCount(context.Background(), &filter.FieldFilter{
		Field:     model.FromnameFieldAlias,
		CompareOp: filter.Equal,
		Values:    []string{"Yandex"},
	})
	require.NoError(t, err)
	require.Equal(t, uint64(2), count)
}

func TestMySQLProvider_GetRoutesInfo_GetAll(t *testing.T) {
	provider, _ := initProvider()

	routes, err := provider.GetRoutesInfo(context.Background(), "0", 300, nil)
	require.NoError(t, err)
	require.Equal(t, 3, len(routes))
	require.Equal(t, "4484", routes[0].ID)
	require.Equal(t, "4485", routes[1].ID)
	require.Equal(t, "4486", routes[2].ID)
}

func TestMySQLProvider_GetRoutesInfo_CheckPages1(t *testing.T) {
	provider, _ := initProvider()

	expectedRoutes := []*model.RouteInfo{
		{
			ID:          "4484",
			PhonePrefix: "+7123",
			Gates: []*model.Gate{
				{ID: "113", Alias: "mitto", AlphaName: "Yandex", Contractor: "mitto", Consumer: "yandex"},
				{ID: "114", Alias: "m1", AlphaName: "Yandex", Contractor: "m1service", Consumer: "yandex"},
				{ID: "115", Alias: "infobipvrt", AlphaName: "o.yandex.ru", Contractor: "infobip", Consumer: "vertis"},
			},
			Weight: 1,
			Mode:   "default",
		},
	}

	actualRoutes, err := provider.GetRoutesInfo(context.Background(), "0", 1, nil)
	require.NoError(t, err)
	require.Equal(t, expectedRoutes, actualRoutes)
}

func TestMySQLProvider_GetRoutesInfo_CheckPages2(t *testing.T) {
	provider, _ := initProvider()

	expectedRoutes := []*model.RouteInfo{
		{
			ID:          "4485",
			PhonePrefix: "+225",
			Gates: []*model.Gate{
				{ID: "115", Alias: "infobipvrt", AlphaName: "o.yandex.ru", Contractor: "infobip", Consumer: "vertis"},
				{ID: "114", Alias: "m1", AlphaName: "Yandex", Contractor: "m1service", Consumer: "yandex"},
			},
			Weight: 1,
			Mode:   "validate",
		},
		{
			ID:          "4486",
			PhonePrefix: "+99833",
			Gates: []*model.Gate{
				{ID: "114", Alias: "m1", AlphaName: "Yandex", Contractor: "m1service", Consumer: "yandex"},
			},
			Weight: 2,
			Mode:   "validate",
		},
	}

	actualRoutes, err := provider.GetRoutesInfo(context.Background(), "4484", 2, nil)
	require.NoError(t, err)
	require.Equal(t, expectedRoutes, actualRoutes)
}

func TestMySQLProvider_GetRoutesInfo_CheckPages3(t *testing.T) {
	provider, _ := initProvider()

	actualRoutes, err := provider.GetRoutesInfo(context.Background(), "4486", 200, nil)
	require.NoError(t, err)
	require.Equal(t, 0, len(actualRoutes))
}

func TestMySQLProvider_GetRoutesInfo_WithFilter(t *testing.T) {
	type TestCase struct {
		limit          uint64
		routesFilter   filter.Filter
		expectedRoutes []model.EntityID
		err            string
	}

	cases := []TestCase{
		{
			limit: 3,
			routesFilter: &filter.FieldFilter{
				Field:     "some_random_field",
				CompareOp: filter.Equal,
				Values:    []string{"some_random_value"},
			},
			err: "unexpected field 'some_random_field'",
		},
		{
			limit: 3,
			routesFilter: &filter.FieldFilter{
				Field:     model.GateIDFieldAlias,
				CompareOp: filter.Equal,
				Values:    []string{"113"},
			},
			expectedRoutes: []model.EntityID{"4484"},
		},
		{
			limit: 3,
			routesFilter: &filter.FieldFilter{
				Field:     model.ModeFieldAlias,
				CompareOp: filter.Contains,
				Values:    []string{"lida"},
			},
			expectedRoutes: []model.EntityID{"4485", "4486"},
		},
		{
			limit: 3,
			routesFilter: &filter.FieldFilter{
				Field:     model.DestinationFieldAlias,
				CompareOp: filter.StartsWith,
				Values:    []string{"+99", "+7"},
			},
			expectedRoutes: []model.EntityID{"4484", "4486"},
		},
		{
			limit: 1,
			routesFilter: &filter.FieldFilter{
				Field:     model.ModeFieldAlias,
				CompareOp: filter.Contains,
				Values:    []string{"lida"},
			},
			expectedRoutes: []model.EntityID{"4485"},
		},
		{
			limit: 1,
			routesFilter: &filter.FieldFilter{
				Field:     model.WeightFieldAlias,
				CompareOp: filter.More,
				Values:    []string{"1"},
			},
			expectedRoutes: []model.EntityID{"4486"},
		},
		{
			limit: 1,
			routesFilter: &filter.FieldFilter{
				Field:     model.AliaseFieldAlias,
				CompareOp: filter.StartsWith,
				Values:    []string{"mi"},
			},
			expectedRoutes: []model.EntityID{"4484"},
		},
	}

	provider, _ := initProvider()

	for idx, c := range cases {
		actualRoutes, err := provider.GetRoutesInfo(context.Background(), "0", c.limit, c.routesFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, len(c.expectedRoutes), len(actualRoutes), idx)
			for i := 0; i < len(actualRoutes); i++ {
				require.Equal(t, c.expectedRoutes[i], actualRoutes[i].ID)
			}
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
	}
}

func checkDeletedRoutes(t *testing.T, provider *Provider, toDelete []model.EntityID, toRemain []model.EntityID) {
	routes, _ := provider.GetRoutesInfo(context.Background(), "0", 200, nil)
	err := provider.SetRoutes(context.Background(), toDelete, nil, nil, &model.AuditLogBulkParams{Author: "author", Issue: []string{"issue"}, Comment: "comment"})
	if len(toRemain) == len(routes) {
		require.Error(t, err)
	} else {
		require.NoError(t, err)
	}
	actualRoutes, err := provider.GetRoutesInfo(context.Background(), "0", 200, nil)
	require.NoError(t, err)
	require.Equal(t, len(toRemain), len(actualRoutes))
	for i := range actualRoutes {
		require.Equal(t, toRemain[i], actualRoutes[i].ID)
	}
}

func TestMySQLProvider_DeleteRoutes_Some(t *testing.T) {
	provider, _ := initProvider()

	checkDeletedRoutes(t, provider, []model.EntityID{"1", "2", "3", "4484", "4485", "4486"}, []model.EntityID{"4484", "4485", "4486"})
	checkDeletedRoutes(t, provider, []model.EntityID{"4485"}, []model.EntityID{"4484", "4486"})
	checkDeletedRoutes(t, provider, []model.EntityID{"4485"}, []model.EntityID{"4484", "4486"})
	checkDeletedRoutes(t, provider, []model.EntityID{"4484"}, []model.EntityID{"4486"})
	checkDeletedRoutes(t, provider, []model.EntityID{"4486"}, []model.EntityID{})
}

func TestMySQLProvider_DeleteRoutes_All(t *testing.T) {
	provider, _ := initProvider()

	checkDeletedRoutes(t, provider, []model.EntityID{"4484", "4485", "4486"}, []model.EntityID{})
}

func TestMySQLProvider_CreateRoutes(t *testing.T) {
	provider, _ := initProvider()
	a := []*model.Route{
		{
			ID:          "1",
			PhonePrefix: "+123",
			Gates:       []model.EntityID{"113", "114", "117"},
			Mode:        "default",
		},
	}
	err := provider.SetRoutes(context.Background(), nil, a, nil, &model.AuditLogBulkParams{Author: "author", Issue: []string{"issue"}, Comment: "comment"})
	require.Error(t, err)

	a = []*model.Route{
		{
			ID:          "1",
			PhonePrefix: "+123",
			Gates:       []model.EntityID{"114"},
			Mode:        "validate",
		},
		{
			ID:          "2",
			PhonePrefix: "+133",
			Gates:       []model.EntityID{"114", "113", "114"},
			Mode:        "default",
		},
	}
	err = provider.SetRoutes(context.Background(), nil, a, nil, &model.AuditLogBulkParams{Author: "author", Issue: []string{"issue"}, Comment: "comment"})
	require.NoError(t, err)
}

func TestMySQLProvider_UpdateRoutes(t *testing.T) {
	provider, _ := initProvider()
	a := []*model.Route{
		{
			ID:          "4484",
			PhonePrefix: "+123",
			Gates:       []model.EntityID{"1"},
		},
	}
	err := provider.SetRoutes(context.Background(), nil, nil, a, &model.AuditLogBulkParams{Author: "author", Issue: []string{"issue"}, Comment: "comment"})
	require.Error(t, err)
	a = []*model.Route{
		{
			ID:          "4484",
			PhonePrefix: "+123",
			Gates:       []model.EntityID{"114"},
		},
	}
	err = provider.SetRoutes(context.Background(), nil, nil, a, &model.AuditLogBulkParams{Author: "author", Issue: []string{"issue"}, Comment: "comment"})
	require.NoError(t, err)
}
