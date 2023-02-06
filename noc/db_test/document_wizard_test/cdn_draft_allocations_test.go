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
	"a.yandex-team.ru/strm/common/go/pkg/opt"
	"a.yandex-team.ru/strm/common/go/pkg/xptr"
	"a.yandex-team.ru/strm/common/go/pkg/xslices"
)

func TestCDNDraftAllocations(t *testing.T) {

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

	location, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "mar"})
	require.NoError(t, err)

	link1, err := client.Links.Post(ctx, &cmdbapi.LinkIn{
		LinkID:     xptr.T[types.LinkID](1520),
		LocationID: &location.ID,
	})
	require.NoError(t, err)

	_, err = client.Nets.Post(ctx, cmdbapi.NetIn{
		CIDR:             "95.167.131.128/25",
		LinkInternalID:   &link1.InternalID,
		VLANID:           nil,
		Gateway:          nil,
		FirstContainerIP: opt.Some(types.IP("95.167.131.130")),
	})
	require.NoError(t, err)

	_, err = client.Nets.Post(ctx, cmdbapi.NetIn{
		CIDR:             "2a03:d000:2980:b::/64",
		LinkInternalID:   &link1.InternalID,
		VLANID:           nil,
		Gateway:          nil,
		FirstContainerIP: opt.Some(types.IP("2a03:d000:2980:b::4")),
	})
	require.NoError(t, err)

	link2, err := client.Links.Post(ctx, &cmdbapi.LinkIn{
		LinkID:     opt.Some(types.LinkID(1536)),
		LocationID: &location.ID,
	})
	require.NoError(t, err)

	_, err = client.Nets.Post(ctx, cmdbapi.NetIn{
		CIDR:             "212.30.135.0/25",
		LinkInternalID:   &link2.InternalID,
		VLANID:           nil,
		Gateway:          nil,
		FirstContainerIP: opt.Some(types.IP("212.30.135.4")),
	})
	require.NoError(t, err)

	containerType := types.ContainerType("strm")
	_, err = client.ContainerTypes.Put(ctx, &cmdbapi.ContainerTypeObj{
		Name:                       containerType,
		Domain:                     "strm.yandex.net",
		CreateInterfaceForEachLink: true,
	})
	require.NoError(t, err)

	dom01, err := client.Dom0s.Post(ctx, cmdbapi.Dom0In{FQDN: "mar01.yandex.net", LocationID: location.ID})
	require.NoError(t, err)

	_, err = client.Dom0ContainerTypes.Post(ctx, &cmdbapi.Dom0ContainerTypeIn{Dom0ID: dom01.ID, ContainerType: containerType})
	require.NoError(t, err)

	dom02, err := client.Dom0s.Post(ctx, cmdbapi.Dom0In{FQDN: "mar02.yandex.net", LocationID: location.ID})
	require.NoError(t, err)

	_, err = client.Dom0ContainerTypes.Post(ctx, &cmdbapi.Dom0ContainerTypeIn{Dom0ID: dom02.ID, ContainerType: containerType})
	require.NoError(t, err)

	_, err = client.CDN.Draft.Generate.Post(ctx, cmdbclient.ArgLocation(location.Name))
	require.NoError(t, err)

	data, err := client.CDN.GetAll(ctx, cmdbclient.ArgIncludeDraft, cmdbclient.ArgLocations("mar"))
	require.NoError(t, err)

	expected := &apicdn.CDN{
		Locations: []*apicdn.Location{{
			ID:      location.ID,
			Name:    location.Name,
			Address: location.Address,
			Dom0s: []apicdn.Dom0{{
				ID:              dom01.ID,
				FQDN:            "mar01.yandex.net",
				InventoryNumber: "",
				LocationID:      location.ID,
				Interfaces:      []apicdn.InterfaceNested{},
				Containers: []apicdn.ContainerNested{{
					Container: apicdn.Container{
						Dom0ID:        dom01.ID,
						ContainerType: containerType,
						Draft:         true,
					},
					Interfaces: []apicdn.InterfaceNested{{
						Interface: apicdn.Interface{
							Name:  "eth0",
							FQDN:  "strm-mar-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth1520",
							FQDN:  "ext-strm-mar-1520-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{{
							IP:      "95.167.131.130",
							NetCIDR: "95.167.131.128/25",
							NetMask: "255.255.255.128",
							LinkID:  opt.Some(link1.InternalID),
							Draft:   true,
						}, {
							IP:      "2a03:d000:2980:b::4",
							NetCIDR: "2a03:d000:2980:b::/64",
							NetMask: "ffff:ffff:ffff:ffff::",
							LinkID:  opt.Some(link1.InternalID),
							Draft:   true,
						}},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth1536",
							FQDN:  "ext-strm-mar-1536-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{{
							IP:      "212.30.135.4",
							NetCIDR: "212.30.135.0/25",
							NetMask: "255.255.255.128",
							LinkID:  opt.Some(link2.InternalID),
							Draft:   true,
						}},
					}},
				}},
			}, {
				ID:              dom02.ID,
				FQDN:            "mar02.yandex.net",
				InventoryNumber: "",
				LocationID:      location.ID,
				Interfaces:      []apicdn.InterfaceNested{},
				Containers: []apicdn.ContainerNested{{
					Container: apicdn.Container{
						Dom0ID:        dom02.ID,
						ContainerType: containerType,
						Draft:         true,
					},
					Interfaces: []apicdn.InterfaceNested{{
						Interface: apicdn.Interface{
							Name:  "eth0",
							FQDN:  "strm-mar-2.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth1520",
							FQDN:  "ext-strm-mar-1520-2.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{{
							IP:      "95.167.131.131",
							NetCIDR: "95.167.131.128/25",
							NetMask: "255.255.255.128",
							LinkID:  opt.Some(link1.InternalID),
							Draft:   true,
						}, {
							IP:      "2a03:d000:2980:b::5",
							NetCIDR: "2a03:d000:2980:b::/64",
							NetMask: "ffff:ffff:ffff:ffff::",
							LinkID:  opt.Some(link1.InternalID),
							Draft:   true,
						}},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth1536",
							FQDN:  "ext-strm-mar-1536-2.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{{
							IP:      "212.30.135.5",
							NetCIDR: "212.30.135.0/25",
							NetMask: "255.255.255.128",
							LinkID:  opt.Some(link2.InternalID),
							Draft:   true,
						}},
					}},
				}},
			}},
		}},
	}
	requireEqualCDN(t, expected, data)

	// post one more time
	_, err = client.CDN.Draft.Generate.Post(ctx, cmdbclient.ArgLocation(location.Name))
	require.NoError(t, err)
}

func requireEqualCDN(t *testing.T, expected *apicdn.CDN, actual *apicdn.CDN) {
	assert.Equal(t, len(expected.Locations), len(actual.Locations))
	for _, pair := range xslices.Zip(expected.Locations, actual.Locations) {
		require.Equal(t, LocationCopyIDFrom(pair.A, pair.B), pair.B)
	}
}
