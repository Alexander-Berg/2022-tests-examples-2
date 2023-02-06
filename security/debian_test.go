package osreleases_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/libs/osreleases"
)

func TestDebian(t *testing.T) {
	cases := []struct {
		codename string
		release  uint16
	}{
		{
			codename: "etch",
			release:  4,
		},
		{
			codename: "lenny",
			release:  5,
		},
		{
			codename: "squeeze",
			release:  6,
		},
		{
			codename: "wheezy",
			release:  7,
		},
		{
			codename: "jessie",
			release:  8,
		},
		{
			codename: "stretch",
			release:  9,
		},
		{
			codename: "buster",
			release:  10,
		},
		{
			codename: "bullseye",
			release:  11,
		},
		{
			codename: "bookworm",
			release:  12,
		},
	}

	for _, tc := range cases {
		t.Run(tc.codename, func(t *testing.T) {
			debian := osreleases.DebianFromString(tc.codename)
			require.Equal(t, osreleases.Debian(tc.release), debian)
			require.Equal(t, tc.codename, debian.String())
		})
	}
}
