package mysql

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/filter"
	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

var blockedPhonesList = []*model.BlockedPhone{
	{
		ID:          "54",
		PhoneNumber: "+79037177191",
		BlockType:   model.BlockTypePermanent,
		BlockUntil:  time.Date(2021, 12, 29, 16, 9, 48, 0, time.UTC),
	},
	{
		ID:          "55",
		PhoneNumber: "+79095856762",
		BlockType:   model.BlockTypePermanent,
		BlockUntil:  time.Date(2070, 12, 29, 16, 19, 31, 0, time.UTC),
	},
}

func TestMySQLProvider_GetBlockedPhonesCount(t *testing.T) {
	provider, _ := initProvider()
	count, err := provider.GetBlockedPhonesCount(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, uint64(2), count)
}

func TestMySQLProvider_GetBlockedPhones_All(t *testing.T) {
	provider, _ := initProvider()
	blockedPhones, err := provider.GetBlockedPhones(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, blockedPhonesList, blockedPhones)
}

func TestMySQLProvider_GetBlockedPhones_CheckPages(t *testing.T) {
	provider, _ := initProvider()

	blockedPhones, err := provider.GetBlockedPhones(context.Background(), "0", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.BlockedPhone{
		blockedPhonesList[0],
	}, blockedPhones)

	blockedPhones, err = provider.GetBlockedPhones(context.Background(), "54", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.BlockedPhone{
		blockedPhonesList[1],
	}, blockedPhones)

	blockedPhones, err = provider.GetBlockedPhones(context.Background(), "55", 1, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.BlockedPhone{}, blockedPhones)
}

func checkDeletedBlockedPhones(t *testing.T, provider *Provider, toDelete []model.EntityID, toRemain []model.EntityID, affected int64) {
	err := provider.SetBlockedPhones(context.Background(), toDelete, nil, nil, nil)
	if affected == 0 {
		require.Error(t, err)
	} else {
		require.NoError(t, err)
	}
	blockedPhones, err := provider.GetBlockedPhones(context.Background(), "0", 200, nil)
	require.NoError(t, err)
	require.Equal(t, len(toRemain), len(blockedPhones))
	for i := range blockedPhones {
		require.Equal(t, toRemain[i], blockedPhones[i].ID)
	}
}

func TestMySQLProvider_DeleteBlockedPhones_Some(t *testing.T) {
	provider, _ := initProvider()
	checkDeletedBlockedPhones(t, provider, []model.EntityID{"1", "54"}, []model.EntityID{"54", "55"}, 0)
	checkDeletedBlockedPhones(t, provider, []model.EntityID{"54"}, []model.EntityID{"55"}, 1)
	checkDeletedBlockedPhones(t, provider, []model.EntityID{"54"}, []model.EntityID{"55"}, 0)
	checkDeletedBlockedPhones(t, provider, []model.EntityID{"55"}, []model.EntityID{}, 1)
}

func TestMySQLProvider_DeleteBlockedPhones_All(t *testing.T) {
	provider, _ := initProvider()
	checkDeletedBlockedPhones(t, provider, []model.EntityID{"54", "55"}, []model.EntityID{}, 2)
}

func TestMySQLProvider_CreateBlockedPhones(t *testing.T) {
	provider, _ := initProvider()
	newPhone := &model.BlockedPhone{
		PhoneNumber: "+234",
		BlockType:   model.BlockTypePermanent,
		BlockUntil:  time.Date(1234, 5, 6, 7, 8, 9, 0, time.UTC),
	}
	err := provider.SetBlockedPhones(context.Background(), nil, []*model.BlockedPhone{newPhone}, nil, nil)
	require.NoError(t, err)

	blockedPhones, err := provider.GetBlockedPhones(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	newPhone.ID = "56"
	require.Equal(t, []*model.BlockedPhone{
		blockedPhones[0],
		blockedPhones[1],
		newPhone,
	}, blockedPhones)
}

func TestMySQLProvider_UpdateBlockedPhones(t *testing.T) {
	provider, _ := initProvider()
	newPhone := &model.BlockedPhone{
		ID:          "53",
		PhoneNumber: "+234",
		BlockType:   model.BlockTypePermanent,
		BlockUntil:  time.Date(1234, 5, 6, 7, 8, 9, 0, time.UTC),
	}
	err := provider.SetBlockedPhones(context.Background(), nil, nil, []*model.BlockedPhone{newPhone}, nil)
	require.Error(t, err)
	blockedPhones, err := provider.GetBlockedPhones(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, blockedPhonesList, blockedPhones)

	newPhone.ID = "54"
	err = provider.SetBlockedPhones(context.Background(), nil, nil, []*model.BlockedPhone{newPhone}, nil)
	require.NoError(t, err)
	blockedPhones, err = provider.GetBlockedPhones(context.Background(), "0", 100, nil)
	require.NoError(t, err)
	require.Equal(t, []*model.BlockedPhone{
		newPhone,
		blockedPhones[1],
	}, blockedPhones)
}

func TestMySQLProvider_prepareSelectBlockedPhonesQuery(t *testing.T) {
	query, args, err := PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.FieldFilter{
		Field:     model.BlockidAlias,
		CompareOp: filter.Equal,
		Values:    []string{"55"},
	}, DBEntitySpec{filterFields: blockedPhonesFilterFields, selectPredicate: selectBlockedPhonesPredicate, selectQueryTemplate: selectBlockedPhonesQueryTemplate, tableName: blockedphonesTableName})
	require.NoError(t, err)
	tail := strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t,
		`blockid > ? AND blockid IN (?) ORDER BY blockid LIMIT ?`, tail)
	require.EqualValues(t, []interface{}{uint64(0), "55", uint64(100)}, args)

	query, args, err = PrepareSelectInfoQuery(&limitSelectArgs{"0", 100}, &filter.LogicOpFilter{
		LogicOp: filter.LogicAnd,
		Args: []filter.FilterContainer{
			{
				Filter: &filter.FieldFilter{
					Field:     "blocktype",
					CompareOp: filter.Equal,
					Values:    []string{"permanent"},
				},
			},
			{
				Filter: &filter.FieldFilter{
					Field:     "phone",
					CompareOp: filter.StartsWith,
					Values:    []string{"+7903", "+7909"},
				},
			},
		},
	}, DBEntitySpec{filterFields: blockedPhonesFilterFields, selectPredicate: selectBlockedPhonesPredicate, selectQueryTemplate: selectBlockedPhonesQueryTemplate, tableName: blockedphonesTableName})
	require.NoError(t, err)
	tail = strings.SplitN(query, "WHERE ", 2)[1]
	require.Equal(t, `blockid > ? AND (blocktype IN (?) AND (phone LIKE ? OR phone LIKE ?)) ORDER BY blockid LIMIT ?`, tail)
	require.EqualValues(t, []interface{}{uint64(0), "permanent", "+7903%", "+7909%", uint64(100)}, args)
}

func TestMySQLProvider_GetBlockedPhones_WithFilter(t *testing.T) {
	type TestCase struct {
		blockedPhonesFilter   filter.Filter
		expectedBlockedPhones []model.EntityID
		expectedCount         uint64
		err                   string
	}

	cases := []TestCase{
		{
			blockedPhonesFilter: &filter.FieldFilter{
				Field:     "some_random_field",
				CompareOp: filter.Equal,
				Values:    []string{"some_random_value"},
			},
			err: "unexpected field 'some_random_field'",
		},
		{
			blockedPhonesFilter: &filter.FieldFilter{
				Field:     model.BlockidAlias,
				CompareOp: filter.Equal,
				Values:    []string{"55"},
			},
			expectedBlockedPhones: []model.EntityID{"55"},
			expectedCount:         1,
		},
		{
			blockedPhonesFilter: &filter.FieldFilter{
				Field:     model.PhoneAlias,
				CompareOp: filter.Contains,
				Values:    []string{"+7"},
			},
			expectedBlockedPhones: []model.EntityID{"54", "55"},
			expectedCount:         2,
		},
		{
			blockedPhonesFilter: &filter.FieldFilter{
				Field:     model.BlocktypeAlias,
				CompareOp: filter.Equal,
				Values:    []string{"permanent"},
			},
			expectedBlockedPhones: []model.EntityID{"54", "55"},
			expectedCount:         2,
		},
		{
			blockedPhonesFilter: &filter.FieldFilter{
				Field:     model.BlocktillAlias,
				CompareOp: filter.More,
				Values:    []string{"2023-12-29T16:09:48Z"},
			},
			expectedBlockedPhones: []model.EntityID{"55"},
			expectedCount:         1,
		},
	}

	provider, _ := initProvider()

	for idx, c := range cases {
		actualBlockedPhones, err := provider.GetBlockedPhones(context.Background(), "0", 200, c.blockedPhonesFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, len(c.expectedBlockedPhones), len(actualBlockedPhones), idx)
			for i := 0; i < len(actualBlockedPhones); i++ {
				require.Equal(t, c.expectedBlockedPhones[i], actualBlockedPhones[i].ID)
			}
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
		totalCount, err := provider.GetBlockedPhonesCount(context.Background(), c.blockedPhonesFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, c.expectedCount, totalCount)
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
	}
}
