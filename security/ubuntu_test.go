package osreleases_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/libs/osreleases"
)

func TestUbuntu(t *testing.T) {
	cases := []struct {
		codename string
		release  uint16
	}{
		{
			codename: "eoan",
			release:  1910,
		},
		{
			codename: "bionic",
			release:  1804,
		},
		{
			codename: "artful",
			release:  1710,
		},
		{
			codename: "xenial",
			release:  1604,
		},
		{
			codename: "trusty",
			release:  1404,
		},
	}

	for _, tc := range cases {
		t.Run(tc.codename, func(t *testing.T) {
			ubuntu := osreleases.UbuntuFromString(tc.codename)
			require.Equal(t, osreleases.Ubuntu(tc.release), ubuntu)
			require.Equal(t, tc.codename, ubuntu.String())
		})
	}
}
