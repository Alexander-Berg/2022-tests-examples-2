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
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestCDN(t *testing.T) {

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

	location, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "spbkant"})
	require.NoError(t, err)

	dom0, err := client.Dom0s.Post(ctx, cmdbapi.Dom0In{FQDN: "spbkant01.yandex.net", LocationID: location.ID})
	require.NoError(t, err)

	container, err := client.Containers.Post(ctx, cmdbapi.ContainerIn{Dom0ID: dom0.ID, ContainerType: "strm"})
	require.NoError(t, err)

	iface, err := client.Interfaces.Post(ctx, cmdbapi.InterfaceIn{Name: "eth0", ContainerID: &container.ID})
	require.NoError(t, err)

	link, err := client.Links.Post(ctx, &cmdbapi.LinkIn{LinkID: nil, LocationID: &location.ID})
	require.NoError(t, err)

	mask, allocationIn := "255.255.255.0", cmdbapi.AllocationIn{
		InterfaceID:    iface.ID,
		IP:             "1.1.1.1",
		NetCIDR:        "1.1.1.0/24",
		LinkInternalID: &link.InternalID,
	}
	alloc, err := client.Allocations.Post(ctx, allocationIn)
	require.NoError(t, err)

	data, err := client.CDN.GetAll(ctx, cmdbclient.ArgLocations("spbkant"))
	require.NoError(t, err)

	assert.Equal(t, &apicdn.CDN{
		Locations: []*apicdn.Location{{
			ID:      location.ID,
			Name:    location.Name,
			Address: location.Address,
			Dom0s: []apicdn.Dom0{{
				ID:              dom0.ID,
				FQDN:            dom0.FQDN,
				InventoryNumber: dom0.InventoryNumber,
				LocationID:      dom0.LocationID,
				Interfaces:      []apicdn.InterfaceNested{},
				Containers: []apicdn.ContainerNested{{
					Container: apicdn.Container{
						ID:            container.ID,
						Dom0ID:        container.Dom0ID,
						ContainerType: container.ContainerType,
					},
					Interfaces: []apicdn.InterfaceNested{{
						Interface: apicdn.Interface{
							ID:          iface.ID,
							Name:        iface.Name,
							FQDN:        iface.FQDN,
							Dom0ID:      iface.Dom0ID,
							ContainerID: iface.ContainerID,
							VLAN:        iface.VLAN,
						},
						Allocations: []apicdn.Allocation{{
							ID:          alloc.ID,
							InterfaceID: alloc.InterfaceID,
							IP:          alloc.IP,
							NetCIDR:     alloc.NetCIDR,
							NetMask:     mask,
							LinkID:      alloc.LinkInternalID,
						}},
					}},
				}},
			}},
		}},
	}, data)
}
