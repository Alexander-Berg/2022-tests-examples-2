package trigger_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/bw"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbclient"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/diff"
	"a.yandex-team.ru/noc/cmdb/pkg/diffmodel"
	"a.yandex-team.ru/noc/cmdb/pkg/rtmodel"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
	"a.yandex-team.ru/strm/common/go/pkg/xptr"
)

func TestDiff(t *testing.T) {

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

	location, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "kiv"})
	require.NoError(t, err)

	require.NoError(t, db.Create(&rtmodel.Object{ID: 23778, Name: (*types.ObjectName)(ptr.String("dante"))}).Error)
	link1, err := client.LinkWizard.Post(ctx, NewLinkWizard{
		LinkID:   1530,
		NetCIDR:  "1.1.3.0/24",
		IP:       "1.1.3.1",
		Location: cmdbapitest.NewLocationIn(location),
	}.NewLinkWizard())
	require.NoError(t, err)

	_, err = client.DocumentWizard.Post(ctx, cmdbapi.DocumentWizardIn{
		Operator: cmdbapi.Operator{Name: "MTS"},
		Contact:  cmdbapi.ContactIn{Name: "MTS"},
		ServiceDescription: cmdbapi.ServiceDescriptionTruncated{
			LinkInternalID: &link1.InternalID,
		},
	})
	require.NoError(t, err)

	link2, err := client.LinkWizard.Post(ctx, NewLinkWizard{
		LinkID:   1531,
		NetCIDR:  "1.1.2.0/24",
		IP:       "1.1.2.1",
		Location: cmdbapitest.NewLocationIn(location),
	}.NewLinkWizard())
	require.NoError(t, err)

	_, err = client.DocumentWizard.Post(ctx, cmdbapi.DocumentWizardIn{
		Operator: cmdbapi.Operator{Name: "Avantel"},
		Contact:  cmdbapi.ContactIn{Name: "Avantel"},
		ServiceDescription: cmdbapi.ServiceDescriptionTruncated{
			LinkInternalID: &link2.InternalID,
		},
	})
	require.NoError(t, err)

	response, err := client.Diff.GetAll(ctx, cmdbclient.ArgLocation(location.Name))
	require.NoError(t, err)
	expected := cmdbapi.DiffResponse{
		link1.InternalID: &cmdbapi.LinkDiffResponse{
			Diff: &cmdbapi.Diff{
				Allocations: &diff.AllocationsDiff{
					Create: []diffmodel.DiffAllocation{{
						ObjectID:   23778,
						ObjectName: "dante",
						IP:         "1.1.3.1",
						Type:       "connected",
						OSIf:       "ae0",
						NetCIDR:    "1.1.3.0/24",
						Comment:    "%peer% 1530",
					}},
				},
				Nets: &diff.NetsDiff{
					Create: []diffmodel.Net{{
						Name: "MTS 1GE@KIV %cdn%",
						CIDR: "1.1.3.0/24",
					}},
				},
			},
		},
		link2.InternalID: &cmdbapi.LinkDiffResponse{
			Diff: &cmdbapi.Diff{
				Allocations: &diff.AllocationsDiff{
					Create: []diffmodel.DiffAllocation{{
						ObjectID:   23778,
						ObjectName: "dante",
						IP:         "1.1.2.1",
						Type:       "connected",
						OSIf:       "ae0",
						NetCIDR:    "1.1.2.0/24",
						Comment:    "%peer% 1531",
					}},
				},
				Nets: &diff.NetsDiff{
					Create: []diffmodel.Net{{
						Name: "Avantel 1GE@KIV %cdn%",
						CIDR: "1.1.2.0/24",
					}},
				},
			},
		},
	}
	for _, diff := range response {
		require.NotEmpty(t, diff.Text)
		diff.Text = "" // do not check text
	}
	require.Equal(t, expected, response)
}

func TestDiffCommit(t *testing.T) {

	dbURI := cmdbapitest.DBURI()

	lg, _ := zap.New(zap.ConsoleConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)

	server, _, _ := cmdbapitest.NewRouter(t, db, logger)
	d := cmdbapi.Diff{
		Allocations: &diff.AllocationsDiff{
			Create: []diffmodel.DiffAllocation{{
				ObjectID:   23778,
				ObjectName: "dante",
				IP:         "1.1.3.1",
				Type:       "connected",
				OSIf:       "ae0",
				NetCIDR:    "1.1.3.0/24",
				Comment:    "%peer% 1530",
			}, {
				ObjectID:   23778,
				ObjectName: "dante",
				IP:         "1.1.3.1",
				Type:       "connected",
				OSIf:       "ae0",
				NetCIDR:    "1.1.3.0/24",
				Comment:    "%peer% 1531",
			}},
		},
		Nets: &diff.NetsDiff{
			Create: []diffmodel.Net{{
				Name: "[operator_name] 1GE@KIV %cdn%",
				CIDR: "1.1.3.0/24",
			}, {
				Name: "[operator_name] 1GE@KIV %cdn%",
				CIDR: "1.1.3.0/24",
			}},
		},
	}
	server.Post(t, server.URL+"/api/diff/commit", d)
}

type NewLinkWizard struct {
	LinkID   types.LinkID
	NetCIDR  types.NetCIDR
	IP       types.IP
	Location *cmdbapi.LocationIn
}

func (n NewLinkWizard) NewLinkWizard() *cmdbapi.LinkWizardIn {
	return &cmdbapi.LinkWizardIn{
		LinkNestedIn: cmdbapi.LinkNestedIn{
			LinkID:    &n.LinkID,
			Location:  n.Location,
			LinkType:  "cdn",
			Bandwidth: xptr.T[bw.BandwidthString]("1g"),
		},
		Allocations: []cmdbapi.ObjectAllocationIn{{
			ObjectID:  23778,
			IP:        n.IP,
			Interface: "ae0",
			Type:      "peer",
			NetCIDR:   n.NetCIDR,
		}},
		Nets: []cmdbapi.NetIn{
			{CIDR: n.NetCIDR},
		},
		Objects: []cmdbapi.LinkObject{
			{ObjectID: 23778, TerminatesBGPSession: true},
		},
	}
}
