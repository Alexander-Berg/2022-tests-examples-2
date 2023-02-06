package trigger

import (
	"context"
	"testing"

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
	"a.yandex-team.ru/strm/common/go/pkg/xslices"
)

func TestCDNDraftNewContainers(t *testing.T) {

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

	location, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "maroff"})
	require.NoError(t, err)

	link1In := &cmdbapi.LinkIn{
		LinkID:     xptr.T[types.LinkID](1357),
		LocationID: &location.ID,
	}
	_, err = client.Links.Post(ctx, link1In)
	require.NoError(t, err)

	link2In := &cmdbapi.LinkIn{
		LinkID:     xptr.T[types.LinkID](2468),
		LocationID: &location.ID,
	}
	_, err = client.Links.Post(ctx, link2In)
	require.NoError(t, err)

	containerType := types.ContainerType("strm")
	_, err = client.ContainerTypes.Put(ctx, &cmdbapi.ContainerTypeObj{
		Name:                       containerType,
		Domain:                     "strm.yandex.net",
		CreateInterfaceForEachLink: true,
	})
	require.NoError(t, err)

	dom01, err := client.Dom0s.Post(ctx, cmdbapi.Dom0In{FQDN: "maroff01.yandex.net", LocationID: location.ID})
	require.NoError(t, err)

	_, err = client.Dom0ContainerTypes.Post(ctx, &cmdbapi.Dom0ContainerTypeIn{Dom0ID: dom01.ID, ContainerType: containerType})
	require.NoError(t, err)

	dom02, err := client.Dom0s.Post(ctx, cmdbapi.Dom0In{FQDN: "maroff02.yandex.net", LocationID: location.ID})
	require.NoError(t, err)

	_, err = client.Dom0ContainerTypes.Post(ctx, &cmdbapi.Dom0ContainerTypeIn{Dom0ID: dom02.ID, ContainerType: containerType})
	require.NoError(t, err)

	_, err = client.CDN.Draft.Generate.Post(ctx, cmdbclient.ArgLocation(location.Name))
	require.NoError(t, err)

	data, err := client.CDN.GetAll(ctx, cmdbclient.ArgIncludeDraft, cmdbclient.ArgLocations("maroff"))
	require.NoError(t, err)

	expected := &apicdn.CDN{
		Locations: []*apicdn.Location{{
			ID:      location.ID,
			Name:    location.Name,
			Address: location.Address,
			Dom0s: []apicdn.Dom0{{
				ID:              dom01.ID,
				FQDN:            "maroff01.yandex.net",
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
							FQDN:  "strm-maroff-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth1357",
							FQDN:  "ext-strm-maroff-1357-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth2468",
							FQDN:  "ext-strm-maroff-2468-1.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}},
				}},
			}, {
				ID:              dom02.ID,
				FQDN:            "maroff02.yandex.net",
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
							FQDN:  "strm-maroff-2.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth1357",
							FQDN:  "ext-strm-maroff-1357-2.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}, {
						Interface: apicdn.Interface{
							Name:  "eth2468",
							FQDN:  "ext-strm-maroff-2468-2.strm.yandex.net",
							Draft: true,
						},
						Allocations: []apicdn.Allocation{},
					}},
				}},
			}},
		}},
	}
	require.Equal(t, CDNCopyIDFrom(expected, data), data)

	// post one more time
	_, err = client.CDN.Draft.Generate.Post(ctx, cmdbclient.ArgLocation(location.Name))
	require.NoError(t, err)
}

func CDNCopyIDFrom(expected *apicdn.CDN, actual *apicdn.CDN) *apicdn.CDN {
	for _, location := range xslices.Zip(expected.Locations, actual.Locations) {
		expectedLocation := location.A
		actualLocation := location.B
		LocationCopyIDFrom(expectedLocation, actualLocation)
	}
	return expected
}

func LocationCopyIDFrom(expected *apicdn.Location, actual *apicdn.Location) *apicdn.Location {
	for id, dom0 := range xslices.Zip(expected.Dom0s, actual.Dom0s) {
		for ic, container := range xslices.Zip(dom0.A.Containers, dom0.B.Containers) {
			expected.Dom0s[id].Containers[ic].ID = actual.Dom0s[id].Containers[ic].ID
			for ii, iface := range xslices.Zip(container.A.Interfaces, container.B.Interfaces) {
				expected.Dom0s[id].Containers[ic].Interfaces[ii].ID = actual.Dom0s[id].Containers[ic].Interfaces[ii].ID
				expected.Dom0s[id].Containers[ic].Interfaces[ii].ContainerID = actual.Dom0s[id].Containers[ic].Interfaces[ii].ContainerID
				for ia := range xslices.Zip(iface.A.Allocations, iface.B.Allocations) {
					expected.Dom0s[id].Containers[ic].Interfaces[ii].Allocations[ia].ID = actual.Dom0s[id].Containers[ic].Interfaces[ii].Allocations[ia].ID
					expected.Dom0s[id].Containers[ic].Interfaces[ii].Allocations[ia].InterfaceID = actual.Dom0s[id].Containers[ic].Interfaces[ii].Allocations[ia].InterfaceID
				}
			}
		}
	}
	return expected
}
