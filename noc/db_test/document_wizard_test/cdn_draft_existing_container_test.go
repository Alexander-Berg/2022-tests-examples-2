package trigger

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi/apicdn"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbclient"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
	"a.yandex-team.ru/strm/common/go/pkg/xptr"
)

func TestCDNDraftExistingContainers(t *testing.T) {

	dbURI := cmdbapitest.DBURI()

	lg, _ := zap.New(zap.ConsoleConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)

	ctx := context.TODO()
	_, client, _ := cmdbapitest.NewRouter(t, db, logger)

	location, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "pink"})
	require.NoError(t, err)

	link1In := &cmdbapi.LinkIn{
		LinkID:     xptr.T[types.LinkID](147),
		LocationID: &location.ID,
	}
	_, err = client.Links.Post(ctx, link1In)
	require.NoError(t, err)

	containerType := types.ContainerType("strm")
	_, err = client.ContainerTypes.Put(ctx, &cmdbapi.ContainerTypeObj{
		Name:                       containerType,
		Domain:                     "strm.yandex.net",
		CreateInterfaceForEachLink: true,
	})
	require.NoError(t, err)

	dom01, err := client.Dom0s.Post(ctx, cmdbapi.Dom0In{FQDN: "pink01.yandex.net", LocationID: location.ID})
	require.NoError(t, err)

	_, err = client.Dom0ContainerTypes.Post(ctx, &cmdbapi.Dom0ContainerTypeIn{Dom0ID: dom01.ID, ContainerType: containerType})
	require.NoError(t, err)

	_, err = client.Containers.Post(ctx, cmdbapi.ContainerIn{Dom0ID: dom01.ID, ContainerType: containerType})
	require.NoError(t, err)

	_, err = client.CDN.Draft.Generate.Post(ctx, cmdbclient.ArgLocation(location.Name))
	require.NoError(t, err)

	data, err := client.CDN.GetAll(ctx, cmdbclient.ArgIncludeDraft, cmdbclient.ArgLocations("pink"))
	require.NoError(t, err)

	expected := &apicdn.CDN{
		Locations: []*apicdn.Location{{
			ID:      location.ID,
			Name:    location.Name,
			Address: location.Address,
			Dom0s: []apicdn.Dom0{{
				ID:              dom01.ID,
				FQDN:            "pink01.yandex.net",
				InventoryNumber: "",
				LocationID:      location.ID,
				Interfaces:      []apicdn.InterfaceNested{},
				Containers: []apicdn.ContainerNested{{
					Container: apicdn.Container{
						Dom0ID:        dom01.ID,
						ContainerType: containerType,
						Draft:         false,
					},
					Interfaces: []apicdn.InterfaceNested{{
						Interface: apicdn.Interface{
							Name:  "eth0",
							FQDN:  "strm-pink-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth147",
							FQDN:  "ext-strm-pink-147-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}},
				}},
			}},
		}},
	}
	assert.Equal(t, CDNCopyIDFrom(expected, data), data)
}
