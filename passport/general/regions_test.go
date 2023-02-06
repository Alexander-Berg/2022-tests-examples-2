package mysql

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/filter"
	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

// from sms.sql
var regionsList = []*model.Region{
	{
		ID:     "1",
		Prefix: "+",
		Name:   "Other",
		EntityCommon: model.EntityCommon{
			AuditCreate: model.EventInfo{ChangeID: "", TS: 0},
			AuditModify: model.EventInfo{ChangeID: "", TS: 0},
		},
	},
	{
		ID:     "2",
		Prefix: "+7",
		Name:   "Russia",
		EntityCommon: model.EntityCommon{
			AuditCreate: model.EventInfo{ChangeID: "", TS: 0},
			AuditModify: model.EventInfo{ChangeID: "", TS: 0},
		},
	},
	{
		ID:     "3",
		Prefix: "+735190",
		Name:   "Chelyabinsk region",
		EntityCommon: model.EntityCommon{
			AuditCreate: model.EventInfo{ChangeID: "", TS: 0},
			AuditModify: model.EventInfo{ChangeID: "", TS: 0},
		},
	},
	{
		ID:     "4",
		Prefix: "+225",
		Name:   "Côte d'Ivoire",
		EntityCommon: model.EntityCommon{
			AuditCreate: model.EventInfo{ChangeID: "", TS: 0},
			AuditModify: model.EventInfo{ChangeID: "", TS: 0},
		},
	},
	{
		ID:     "5",
		Prefix: "+99833",
		Name:   "Uzbekistan",
		EntityCommon: model.EntityCommon{
			AuditCreate: model.EventInfo{ChangeID: "", TS: 0},
			AuditModify: model.EventInfo{ChangeID: "", TS: 0},
		},
	},
}

type TestRegionsStoreSchemaType int

const (
	PrefixAsKey TestRegionsStoreSchemaType = iota
	IDAsKey
)

func TestMySQLProvider_GetRegions_All(t *testing.T) {
	provider, _ := initProvider()
	regions, err := provider.GetRegions(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, regionsList, regions)
}

func checkDeletedRegions(t *testing.T, provider *Provider, schemaType TestRegionsStoreSchemaType, toDelete []model.EntityID, toRemain []model.EntityID, affected bool) {
	err := provider.SetRegions(context.Background(), toDelete, nil, nil, nil)

	if !affected {
		require.Error(t, err)
	} else {
		require.NoError(t, err)
	}
	regions, err := provider.GetRegions(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, len(toRemain), len(regions))
	for i := range regions {
		require.Equal(t, toRemain[i], regions[i].ID)
	}
}

func TestMySQLProvider_DeleteRegionsSome(t *testing.T) {
	provider, _ := initProvider()
	// there is a check: number of affected rows should be equal to expected rows number
	checkDeletedRegions(t, provider, IDAsKey, []model.EntityID{"33", "2"}, []model.EntityID{"1", "2", "3", "4", "5"}, false)
	checkDeletedRegions(t, provider, IDAsKey, []model.EntityID{"2"}, []model.EntityID{"1", "3", "4", "5"}, true)
	checkDeletedRegions(t, provider, IDAsKey, []model.EntityID{"2"}, []model.EntityID{"1", "3", "4", "5"}, false)
}

func TestMySQLProvider_DeleteRegionsByIdAll(t *testing.T) {
	provider, _ := initProvider()
	err := provider.SetRegions(context.Background(), []model.EntityID{"1", "2", "3", "4", "5"}, nil, nil, nil)
	require.Error(t, err)
}

func TestMySQLProvider_CreateRegions(t *testing.T) {
	provider, _ := initProvider()
	newRegion := &model.Region{
		Prefix: "+7495",
		Name:   "Moscow",
	}
	newRegionWithAudit := &model.Region{
		ID:     "6",
		Prefix: newRegion.Prefix,
		Name:   newRegion.Name,
		EntityCommon: model.EntityCommon{
			AuditModify: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
			AuditCreate: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
		},
	}

	err := provider.SetRegions(context.Background(), nil, []*model.Region{newRegion}, nil, nil)
	require.NoError(t, err)

	regions, err := provider.GetRegions(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Region{
		regions[0],
		regions[1],
		regions[2],
		regions[3],
		regions[4],
		newRegionWithAudit,
	}, regions)
}

func TestMySQLProvider_UpdateRegions(t *testing.T) {
	provider, _ := initProvider()
	newRegion := &model.Region{
		ID:     "55",
		Name:   "Moscow",
		Prefix: "+735190",
	}
	newRegionWithAudit := &model.Region{
		Prefix: newRegion.Prefix,
		Name:   newRegion.Name,
		EntityCommon: model.EntityCommon{
			AuditModify: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
			AuditCreate: model.EventInfo{
				ChangeID: "",
				TS:       0,
			},
		},
	}
	err := provider.SetRegions(context.Background(), nil, nil, []*model.Region{newRegion}, nil)
	require.Error(t, err)
	regions, err := provider.GetRegions(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, regionsList, regions)

	newRegion.ID = "3"
	newRegionWithAudit.ID = "3"
	err = provider.SetRegions(context.Background(), nil, nil, []*model.Region{newRegion}, nil)
	require.NoError(t, err)
	regions, err = provider.GetRegions(context.Background(), nil)
	require.NoError(t, err)
	require.Equal(t, []*model.Region{
		regions[0],
		regions[1],
		newRegionWithAudit,
		regions[3],
		regions[4],
	}, regions)
}

func TestMySQLProvider_GetRegions_WithFilter(t *testing.T) {
	type TestCase struct {
		regionsFilter   filter.Filter
		expectedRegions []model.EntityID
		err             string
	}

	cases := []TestCase{
		{
			regionsFilter: &filter.FieldFilter{
				Field:     "some_random_field",
				CompareOp: filter.Equal,
				Values:    []string{"some_random_value"},
			},
			err: "unexpected field 'some_random_field'",
		},
		{
			regionsFilter: &filter.FieldFilter{
				Field:     model.NameFieldAlias,
				CompareOp: filter.Equal,
				Values:    []string{"Russia"},
			},
			expectedRegions: []model.EntityID{"2"},
		},
		{
			regionsFilter: &filter.FieldFilter{
				Field:     model.NameFieldAlias,
				CompareOp: filter.StartsWith,
				Values:    []string{"Rus"},
			},
			expectedRegions: []model.EntityID{"2"},
		},
		{
			regionsFilter: &filter.FieldFilter{
				Field:     model.PrefixFieldAlias,
				CompareOp: filter.Contains,
				Values:    []string{"98"},
			},
			expectedRegions: []model.EntityID{"5"},
		},
	}

	provider, _ := initProvider()

	for idx, c := range cases {
		actualRegions, err := provider.GetRegions(context.Background(), c.regionsFilter)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, len(c.expectedRegions), len(actualRegions), idx)
			for i := 0; i < len(actualRegions); i++ {
				require.Equal(t, c.expectedRegions[i], actualRegions[i].ID)
			}
		} else {
			require.Error(t, err)
			require.Contains(t, err.Error(), c.err)
		}
	}
}
