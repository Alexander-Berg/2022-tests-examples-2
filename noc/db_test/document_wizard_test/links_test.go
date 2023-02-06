package trigger_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"gorm.io/gorm/clause"

	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbclient"
	trigger "a.yandex-team.ru/noc/cmdb/pkg/db_test/document_wizard_test"
	"a.yandex-team.ru/noc/cmdb/pkg/rtmodel"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/xptr"
	"a.yandex-team.ru/strm/common/go/pkg/xrand"
	"a.yandex-team.ru/strm/common/go/pkg/xslices"
)

func TestCMDBAPILinksGetAll(t *testing.T) {

	client, db := cmdbapitest.NewClient(t)
	ctx := context.TODO()

	contact, err := client.Contacts.Post(ctx, &cmdbapi.ContactIn{Name: "contact " + xrand.String(16)})
	require.NoError(t, err)

	range_ := trigger.Range(2)
	operators := xslices.Map(range_, func(x int) *cmdbapi.Operator {
		operator := &cmdbapi.Operator{Name: "operator " + xrand.String(16)}
		o, err := client.Operators.Post(ctx, operator)
		require.NoError(t, err)
		return o
	})
	objects := xslices.Map(range_, func(int) *rtmodel.Object {
		object := &rtmodel.Object{Name: xptr.T(types.ObjectName("object " + xrand.String(16)))}
		require.NoError(t, db.Clauses(clause.Returning{}).Create(&object).Error)
		return object
	})
	ports := xslices.Map(objects, func(obj *rtmodel.Object) *rtmodel.Port {
		port := &rtmodel.Port{ObjectID: &obj.ID, Name: xptr.T(types.PortName("port " + xrand.String(16)))}
		require.NoError(t, db.Clauses(clause.Returning{}).Create(&port).Error)
		return port
	})
	links := xslices.MapEnumerated(xslices.Zip(operators, ports), func(i int, pair xslices.Pair[*cmdbapi.Operator, *rtmodel.Port]) *cmdbapi.LinkOut {
		port := pair.B
		linkID := types.LinkID(i + 10)
		link := &cmdbapi.LinkIn{LinkID: &linkID, PortID: &port.ID}
		l, err := client.Links.Post(ctx, link)
		require.NoError(t, err)
		return l
	})
	pairs := xslices.Zip(operators, links)
	for _, pair := range pairs {
		serviceDescription := cmdbapi.ServiceDescriptionNestedIn{
			OperatorID:     pair.A.ID,
			LinkInternalID: &pair.B.InternalID,
			ContactID:      contact.ID,
		}
		_, err := client.ServiceDescriptions.Post(ctx, &serviceDescription)
		require.NoError(t, err)
	}

	for _, pair := range xslices.Zip(pairs, xslices.Zip(objects, ports)) {
		operator, link, object, port := pair.A.A, pair.A.B, pair.B.A, pair.B.B

		result, err := client.Links.GetAll(ctx, cmdbclient.OperatorID(*operator.ID))
		require.NoError(t, err)
		assert.Equal(t, []types.LinkInternalID{link.InternalID}, xslices.Map(result, LinkID))

		result, err = client.Links.GetAll(ctx, cmdbclient.ArgOperatorName(operator.Name))
		require.NoError(t, err)
		assert.Equal(t, []types.LinkInternalID{link.InternalID}, xslices.Map(result, LinkID))

		result, err = client.Links.GetAll(ctx, cmdbclient.ArgConnectionObjectID(object.ID))
		require.NoError(t, err)
		assert.Equal(t, []types.LinkInternalID{link.InternalID}, xslices.Map(result, LinkID))

		result, err = client.Links.GetAll(ctx, cmdbclient.ArgConnectionObjectName(*object.Name))
		require.NoError(t, err)
		assert.Equal(t, []types.LinkInternalID{link.InternalID}, xslices.Map(result, LinkID))

		result, err = client.Links.GetAll(ctx, cmdbclient.ArgConnectionPortID(port.ID))
		require.NoError(t, err)
		assert.Equal(t, []types.LinkInternalID{link.InternalID}, xslices.Map(result, LinkID))

		result, err = client.Links.GetAll(ctx, cmdbclient.ArgConnectionPortName(*port.Name))
		require.NoError(t, err)
		assert.Equal(t, []types.LinkInternalID{link.InternalID}, xslices.Map(result, LinkID))
	}
}

func LinkID(link *cmdbapi.LinkOutExt) types.LinkInternalID {
	return link.InternalID
}
