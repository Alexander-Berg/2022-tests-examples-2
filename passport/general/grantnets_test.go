package grantnets

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNets(t *testing.T) {
	nets := NewNets()

	for _, s := range []string{
		"10df426@2a02:6b8:c00::/40",
		"213.180.205.169",
		"2a02:6b8:0:1402::/64",
		"2a02:6b8:0:1402::11e",
		"2a02:6b8:0:1402::121",
		"2a02:6b8:0:1402::181",
		"2a02:6b8:0:1402::182",
		"2a02:6b8:0:1402::6",
		"2a02:6b8:0:1465::/64",
		"2a02:6b8:0:1465::110",
		"2a02:6b8:0:1465::1c6",
		"2a02:6b8:0:1465::1c7",
		"2a02:6b8:0:1465::1c8",
		"2a02:6b8:0:1465::1c9",
		"2a02:6b8:0:1465::c7",
		"2a02:6b8:0:1472:2741:0:8b6:212",
		"2a02:6b8:0:1472:2741:0:8b7:111",
		"2a02:6b8:0:1472:2741:0:8b7:112",
		"2a02:6b8:0:1472:2741:0:8b7:113",
		"2a02:6b8:0:1472:2741:0:8b7:114",
		"2a02:6b8:0:1472:2741:0:8b7:115",
		"2a02:6b8:0:1472::/64",
		"2a02:6b8:0:1619::/64",
	} {
		require.NoError(t, nets.Add(s))
	}

	cases := []struct {
		s   string
		val bool
	}{
		{s: "123.45.67.89", val: false},
		{s: "2a02:6b8:0:1401::182", val: false},
		{s: "2a02:6b8:0:1402::182", val: true},           // host
		{s: "2a02:6b8:0:1472:2741:0:8b6:212", val: true}, // host
		{s: "2a02:6b8:0:1472::1", val: true},             // classic
		{s: "2a02:6b8:c00:0:10d:f426::", val: true},      // trypo
	}

	for idx, c := range cases {
		require.Equal(t, c.val, nets.Contains(c.s), idx)
	}
}

func TestNetsErrors(t *testing.T) {
	nets := NewNets()
	require.EqualError(t,
		nets.Add("0d@f426@2a02:6b8:c00::/40"),
		"failed to parse trypo network '0d@f426@2a02:6b8:c00::/40': malformed: bad @")
	require.Error(t, nets.Add("2a02:6b8:c00::/146"))
	require.EqualError(t,
		nets.Add("qwerter"),
		"failed to parse single host 'qwerter': invalid IP")
}
