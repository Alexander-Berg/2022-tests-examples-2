package trigger

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
)

func TestLocations(t *testing.T) {
	client, _ := cmdbapitest.NewClient(t)
	ctx := context.TODO()
	_, err := client.Locations.Post(ctx, &cmdbapi.LocationIn{Name: "m9"})
	require.NoError(t, err)
	locations, err := client.Locations.GetAll(ctx)
	require.NoError(t, err)
	require.Greater(t, len(locations), 0)
}

func TestLinkWizardLocations(t *testing.T) {
	client, _ := cmdbapitest.NewClient(t)
	ctx := context.TODO()
	link1, err := client.LinkWizard.Post(ctx, &cmdbapi.LinkWizardIn{
		LinkNestedIn: cmdbapi.LinkNestedIn{
			LinkID: nil,
			Location: &cmdbapi.LocationIn{
				Name:    "mskmar",
				Address: "address 1",
			},
		},
	})
	require.NoError(t, err)
	location1, err := client.Locations.Get(ctx, *link1.LocationID)
	require.NoError(t, err)
	require.Equal(t, &cmdbapi.LocationOut{
		ID:      *link1.LocationID,
		Name:    "mskmar",
		Address: "address 1",
	}, location1)

	link2, err := client.LinkWizard.Post(ctx, &cmdbapi.LinkWizardIn{
		LinkNestedIn: cmdbapi.LinkNestedIn{
			LinkID: nil,
			Location: &cmdbapi.LocationIn{
				ID:   link1.LocationID,
				Name: "mskmar",
			},
		},
	})
	require.NoError(t, err)
	require.Equal(t, link1.LocationID, link2.LocationID)

	_, err = client.LinkWizard.Post(ctx, &cmdbapi.LinkWizardIn{
		LinkNestedIn: cmdbapi.LinkNestedIn{
			LinkID: nil,
			Location: &cmdbapi.LocationIn{
				Name: "mskmar",
			},
		},
	})
	require.Error(t, err)
}
