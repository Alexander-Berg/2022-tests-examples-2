package mysql

import (
	"context"
	"fmt"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/filter"
	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

func TestMySQLProvider_GetGatesCount(t *testing.T) {
	provider, _ := initProvider()
	count, err := provider.GetGatesCount(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, uint64(3), count)
}

func TestMySQLProvider_prepareSelectGatesQuery(t *testing.T) {
	query, args, err := PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.FieldFilter{
		Field:     model.GateIDFieldAlias,
		CompareOp: filter.Equal,
		Values:    []string{"113"},
	}, DBEntitySpec{filterFields: gatesFilterFields, selectPredicate: selectGatesPredicate, selectQueryTemplate: selectGatesQueryTemplate, tableName: gatesTableName})
	require.NoError(t, err)
	tail := strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t, `gateid > ? AND gateid IN (?) ORDER BY gateid LIMIT ?;`, tail)
	require.EqualValues(t, []interface{}{uint64(0), "113", uint64(100)}, args)

	query, args, err = PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.LogicOpFilter{
		LogicOp: filter.LogicAnd,
		Args: []filter.FilterContainer{
			{
				Filter: &filter.FieldFilter{
					Field:     "fromname",
					CompareOp: filter.Contains,
					Values:    []string{"yandex"},
				},
			},
			{
				Filter: &filter.FieldFilter{
					Field:     "aliase",
					CompareOp: filter.StartsWith,
					Values:    []string{"mi", "info"},
				},
			},
		},
	}, DBEntitySpec{filterFields: gatesFilterFields, selectPredicate: selectGatesPredicate, selectQueryTemplate: selectGatesQueryTemplate, tableName: gatesTableName})
	require.NoError(t, err)
	tail = strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t, `gateid > ? AND (fromname LIKE ? AND (aliase LIKE ? OR aliase LIKE ?)) ORDER BY gateid LIMIT ?;`, tail)
	require.EqualValues(t, []interface{}{uint64(0), "%yandex%", "mi%", "info%", uint64(100)}, args)
}

func TestMySQLProvider_GetGates_All(t *testing.T) {
	provider, _ := initProvider()

	gates, err := provider.GetGates(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.GateWithAudit{
		{Gate: model.Gate{ID: "113", Alias: "mitto", AlphaName: "Yandex", Consumer: "yandex", Contractor: "mitto"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
		{Gate: model.Gate{ID: "114", Alias: "m1", AlphaName: "Yandex", Consumer: "yandex", Contractor: "m1service"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
		{Gate: model.Gate{ID: "115", Alias: "infobipvrt", AlphaName: "o.yandex.ru", Consumer: "vertis", Contractor: "infobip"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
	}, gates)
}

func TestMySQLProvider_GetGates_CheckPages(t *testing.T) {
	provider, _ := initProvider()

	gates, err := provider.GetGates(context.Background(), "0", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.GateWithAudit{
		{Gate: model.Gate{ID: "113", Alias: "mitto", AlphaName: "Yandex", Consumer: "yandex", Contractor: "mitto"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
	}, gates)

	gates, err = provider.GetGates(context.Background(), "113", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.GateWithAudit{
		{Gate: model.Gate{ID: "114", Alias: "m1", AlphaName: "Yandex", Consumer: "yandex", Contractor: "m1service"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
	}, gates)

	gates, err = provider.GetGates(context.Background(), "114", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.GateWithAudit{
		{Gate: model.Gate{ID: "115", Alias: "infobipvrt", AlphaName: "o.yandex.ru", Consumer: "vertis", Contractor: "infobip"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
	}, gates)

	gates, err = provider.GetGates(context.Background(), "115", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.GateWithAudit{}, gates)

	gates, err = provider.GetGates(context.Background(), "113", 2, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.GateWithAudit{
		{Gate: model.Gate{ID: "114", Alias: "m1", AlphaName: "Yandex", Consumer: "yandex", Contractor: "m1service"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
		{Gate: model.Gate{ID: "115", Alias: "infobipvrt", AlphaName: "o.yandex.ru", Consumer: "vertis", Contractor: "infobip"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
	}, gates)
}

func checkDeletedGates(t *testing.T, provider *Provider, toDelete []model.EntityID, toRemain []model.EntityID, affected int64) {
	err := provider.SetGates(context.Background(), toDelete, nil, nil, nil)
	if affected == 0 {
		require.Error(t, err)
	} else {
		require.NoError(t, err)
	}
	actualGates, err := provider.GetGates(context.Background(), "0", 200, nil)
	require.NoError(t, err)
	require.Equal(t, len(toRemain), len(actualGates))
	for i := range actualGates {
		require.Equal(t, toRemain[i], actualGates[i].ID)
	}
}

func addFakeGates(t *testing.T, provider *Provider, n int) {
	gates := make([]*model.Gate, 0, n)
	for i := 0; i < n; i++ {
		gates = append(gates, &model.Gate{
			ID:         "0",
			Alias:      fmt.Sprintf("alias-%d", i),
			AlphaName:  fmt.Sprintf("fromname-%d", i),
			Consumer:   fmt.Sprintf("consumer-%d", i),
			Contractor: fmt.Sprintf("contractor-%d", i),
			Extra: map[string]string{
				"extra": fmt.Sprintf("extra-%d", i),
			},
		})
	}
	err := provider.SetGates(context.Background(), nil, gates, nil, nil)
	require.NoError(t, err)
}

func TestMySQLProvider_DeleteGates_Some(t *testing.T) {
	provider, _ := initProvider()
	addFakeGates(t, provider, 3)
	checkDeletedGates(t, provider, []model.EntityID{"113", "116", "117", "118"}, []model.EntityID{"113", "114", "115", "116", "117", "118"}, 0)
	checkDeletedGates(t, provider, []model.EntityID{"117"}, []model.EntityID{"113", "114", "115", "116", "118"}, 1)
	checkDeletedGates(t, provider, []model.EntityID{"117"}, []model.EntityID{"113", "114", "115", "116", "118"}, 0)
	checkDeletedGates(t, provider, []model.EntityID{"116"}, []model.EntityID{"113", "114", "115", "118"}, 1)
	checkDeletedGates(t, provider, []model.EntityID{"118"}, []model.EntityID{"113", "114", "115"}, 1)
}

func TestMySQLProvider_DeleteGates_All(t *testing.T) {
	provider, _ := initProvider()
	addFakeGates(t, provider, 3)
	checkDeletedGates(t, provider, []model.EntityID{"116", "117", "118"}, []model.EntityID{"113", "114", "115"}, 3)
}

func TestMySQLProvider_CreateGates(t *testing.T) {
	provider, _ := initProvider()
	addFakeGates(t, provider, 2)
	gates, err := provider.GetGates(context.Background(), "0", 200, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.GateWithAudit{
		{Gate: model.Gate{ID: "113", Alias: "mitto", AlphaName: "Yandex", Consumer: "yandex", Contractor: "mitto"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
		{Gate: model.Gate{ID: "114", Alias: "m1", AlphaName: "Yandex", Consumer: "yandex", Contractor: "m1service"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
		{Gate: model.Gate{ID: "115", Alias: "infobipvrt", AlphaName: "o.yandex.ru", Consumer: "vertis", Contractor: "infobip"}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
		{Gate: model.Gate{ID: "116", Alias: "alias-0", AlphaName: "fromname-0", Consumer: "consumer-0", Contractor: "contractor-0", Extra: map[string]string{"extra": "extra-0"}}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
		{Gate: model.Gate{ID: "117", Alias: "alias-1", AlphaName: "fromname-1", Consumer: "consumer-1", Contractor: "contractor-1", Extra: map[string]string{"extra": "extra-1"}}, EntityCommon: model.EntityCommon{AuditCreate: model.EventInfo{ChangeID: "", TS: 0}, AuditModify: model.EventInfo{ChangeID: "", TS: 0}}},
	}, gates)
}

func TestMySQLProvider_UpdateGates(t *testing.T) {
	provider, _ := initProvider()
	a := []*model.Gate{
		{ID: "116", Alias: "alias-0", AlphaName: "fromname-0", Consumer: "consumer-0", Contractor: "contractor-0", Extra: map[string]string{"extra": "extra-0"}},
	}
	err := provider.SetGates(context.Background(), nil, nil, a, nil)
	require.Error(t, err)
	a = []*model.Gate{
		{ID: "113", Alias: "alias-0", AlphaName: "fromname-0", Consumer: "consumer-0", Contractor: "contractor-0", Extra: map[string]string{"extra": "extra-0"}},
		{ID: "115", Alias: "alias-1", AlphaName: "fromname-1", Consumer: "consumer-0", Contractor: "contractor-0", Extra: map[string]string{"extra": "extra-0"}},
	}
	err = provider.SetGates(context.Background(), nil, nil, a, nil)
	require.NoError(t, err)
}

func TestMySQLProvider_GetGates_WithFilter(t *testing.T) {
	type TestCase struct {
		gatesFilter   filter.Filter
		expectedGates []model.EntityID
		expectedCount uint64
		err           string
	}

	cases := []TestCase{
		{
			gatesFilter: &filter.FieldFilter{
				Field:     "some_random_field",
				CompareOp: filter.Equal,
				Values:    []string{"some_random_value"},
			},
			err: "unexpected field 'some_random_field'",
		},
		{
			gatesFilter: &filter.FieldFilter{
				Field:     model.GateIDFieldAlias,
				CompareOp: filter.Equal,
				Values:    []string{"113"},
			},
			expectedGates: []model.EntityID{"113"},
			expectedCount: 1,
		},
		{
			gatesFilter: &filter.FieldFilter{
				Field:     model.FromnameFieldAlias,
				CompareOp: filter.Contains,
				Values:    []string{"ndex"},
			},
			expectedGates: []model.EntityID{"113", "114", "115"},
			expectedCount: 3,
		},
		{
			gatesFilter: &filter.FieldFilter{
				Field:     model.AliaseFieldAlias,
				CompareOp: filter.StartsWith,
				Values:    []string{"mi", "info"},
			},
			expectedGates: []model.EntityID{"113", "115"},
			expectedCount: 2,
		},
	}

	provider, _ := initProvider()

	for idx, c := range cases {
		actualGates, err := provider.GetGates(context.Background(), "0", 200, c.gatesFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, len(c.expectedGates), len(actualGates), idx)
			for i := 0; i < len(actualGates); i++ {
				require.Equal(t, c.expectedGates[i], actualGates[i].ID)
			}
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
		totalCount, err := provider.GetGatesCount(context.Background(), c.gatesFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, c.expectedCount, totalCount)
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
	}
}
