package dbsync_test

import (
	"reflect"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/dbsync"
	"a.yandex-team.ru/noc/cmdb/pkg/rtmodel"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
)

func TestDiff_Objects(t *testing.T) {
	before := []rtmodel.Object{{
		ID:   8916,
		Name: (*types.ObjectName)(ptr.String("m9-s5")),
		FQDN: ptr.String("m9-s5.yndx.net"),
		Type: ptr.String("Network switch"),
	}, {
		ID:   12705,
		Name: (*types.ObjectName)(ptr.String("jansson")),
		FQDN: ptr.String("jansson.yndx.net"),
		Type: ptr.String("Router"),
	}, {
		ID:   40059,
		Name: (*types.ObjectName)(ptr.String("spb4-s1")),
		FQDN: ptr.String("spb4-s1.yndx.net"),
		Type: ptr.String("Network switch"),
	}}
	after := []rtmodel.Object{{
		ID:   12705,
		Name: (*types.ObjectName)(ptr.String("jansson")),
		FQDN: ptr.String("jansson.yndx.net"),
		Type: ptr.String("Router"),
	}, {
		ID:   40059,
		Name: (*types.ObjectName)(ptr.String("spb4-s11")),
		FQDN: ptr.String("spb4-s11.yndx.net"),
		Type: ptr.String("Network switch"),
	}, {
		ID:   63389,
		Name: (*types.ObjectName)(ptr.String("vla-cpb2")),
		FQDN: ptr.String("vla-cpb2.yndx.net"),
		Type: ptr.String("Router"),
	}}
	created, deleted, modified, err := dbsync.Diff{}.RowsDiff(before, after)
	require.NoError(t, err)
	assert.Equal(t, []rtmodel.Object{{
		ID:   63389,
		Name: (*types.ObjectName)(ptr.String("vla-cpb2")),
		FQDN: ptr.String("vla-cpb2.yndx.net"),
		Type: ptr.String("Router"),
	}}, created.([]rtmodel.Object))
	assert.Equal(t, []rtmodel.Object{{
		ID:   8916,
		Name: (*types.ObjectName)(ptr.String("m9-s5")),
		FQDN: ptr.String("m9-s5.yndx.net"),
		Type: ptr.String("Network switch"),
	}}, deleted.([]rtmodel.Object))
	assert.Equal(t, [2][]rtmodel.Object{{{
		ID:   40059,
		Name: (*types.ObjectName)(ptr.String("spb4-s1")),
		FQDN: ptr.String("spb4-s1.yndx.net"),
		Type: ptr.String("Network switch"),
	}}, {{
		ID:   40059,
		Name: (*types.ObjectName)(ptr.String("spb4-s11")),
		FQDN: ptr.String("spb4-s11.yndx.net"),
		Type: ptr.String("Network switch"),
	}}}, [2][]rtmodel.Object{
		modified[0].([]rtmodel.Object),
		modified[1].([]rtmodel.Object),
	})
}

func TestDiff_Diff(t *testing.T) {
	models := FillModels(1)
	require.Equal(t, 1, len(models.Objects))
	_, err := dbsync.Diff{}.Diff(*models, *models)
	assert.NoError(t, err)
}

func FillModels(count int) *dbsync.Models {
	fieldValues := make([]interface{}, 0)
	for _, field := range dbsync.MustListFields(new(dbsync.Models)) {
		ty := reflect.TypeOf(field)
		arr := reflect.MakeSlice(ty, 0, 0)
		itemPtr := reflect.New(ty.Elem())
		for i := 0; i < count; i++ {
			arr = reflect.Append(arr, itemPtr.Elem())
		}
		fieldValues = append(fieldValues, arr.Interface())
	}

	models := dbsync.NewModels(fieldValues)
	return models
}
