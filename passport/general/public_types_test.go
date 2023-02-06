package tvmtypes

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCheckTiroleFeature(t *testing.T) {
	config := Config{
		Clients: map[string]Client{
			"bar": {},
		},
	}
	require.NoError(t, config.CheckTiroleFeature(false))
	require.NoError(t, config.CheckTiroleFeature(true))

	config = Config{
		Clients: map[string]Client{
			"bar": {
				IdmSlug: "kek",
			},
		},
	}
	require.EqualError(t,
		config.CheckTiroleFeature(false),
		"'roles_for_idm_slug'='kek' is specified in config but disk cache is not configured")
	require.EqualError(t,
		config.CheckTiroleFeature(true),
		"'roles_for_idm_slug'='kek' is configured for client 'bar' but secret is empty")

	config = Config{
		Clients: map[string]Client{
			"bar": {
				Secret:  "lol",
				IdmSlug: "kek",
			},
		},
	}
	require.EqualError(t,
		config.CheckTiroleFeature(false),
		"'roles_for_idm_slug'='kek' is specified in config but disk cache is not configured")
	require.NoError(t, config.CheckTiroleFeature(true))
}
