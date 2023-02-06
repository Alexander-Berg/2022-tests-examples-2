package model

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProvider_GetRegion(t *testing.T) {
	regions := Regions{
		"+": &Region{
			Name: "Default",
		},
		"+7": &Region{
			Name: "Russia",
		},
		"+374": &Region{
			Name: "Armenia",
		},
		"+372": &Region{
			Name: "Estonia",
		},
	}

	region, err := regions.GetRegion("+7")
	require.NoError(t, err)
	require.Equal(t, Region{
		Name: "Russia",
	}, *region)

	region, err = regions.GetRegion("+3721236")
	require.NoError(t, err)
	require.Equal(t, Region{
		Name: "Estonia",
	}, *region)

	region, err = regions.GetRegion("+3741")
	require.NoError(t, err)
	require.Equal(t, Region{
		Name: "Armenia",
	}, *region)

	region, err = regions.GetRegion("+4954")
	require.NoError(t, err)
	require.Equal(t, Region{
		Name: "Default",
	}, *region)
}
