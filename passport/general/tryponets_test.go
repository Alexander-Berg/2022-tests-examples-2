package grantnets

import (
	"net"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProjectID(t *testing.T) {
	toPtr := func(val uint32) *uint32 {
		return &val
	}

	cases := []struct {
		ip string
		id *uint32
	}{
		{ip: "8.8.8.8", id: nil},
		{ip: "6.5.4.1", id: nil},
		{ip: "::ffff:ffff:ffff:ffff", id: toPtr(0xffffffff)},
		{ip: "2a02:6b8:b010:1d::7f", id: toPtr(0)},
		{ip: "2a02:6b8:c00:103b:0:604:9:2224", id: toPtr(0x604)},
	}

	for idx, c := range cases {
		ip := net.ParseIP(c.ip)
		require.NotNil(t, ip, idx)
		id := GetProjectID(ip)
		if c.id == nil {
			require.Nil(t, id, idx)
		} else {
			require.Equal(t, *c.id, *GetProjectID(ip), idx)
		}
	}
}

func TestTrypoNetworkLooks(t *testing.T) {
	require.True(t, LooksLikeTrypoNetwork("@"))
	require.True(t, LooksLikeTrypoNetwork("@@@@"))
	require.True(t, LooksLikeTrypoNetwork("10df426@2a02:6b8:c00::/40"))

	require.False(t, LooksLikeTrypoNetwork("213.180.205.169"))
	require.False(t, LooksLikeTrypoNetwork("2a02:6b8:c00::/40"))
}

func TestTrypoNetworkParse(t *testing.T) {
	cases := []struct {
		s   string
		err string
	}{
		{s: "8.8.8.8", err: "malformed: bad @"},
		{s: "2a02:6b8:b010:1d::7f", err: "malformed: bad @"},
		{s: "2a02:6b8:c00::/40", err: "malformed: bad @"},
		{s: "10d@f426@2a02:6b8:c00::/40", err: "malformed: bad @"},
		{s: "qweasd@2a02:6b8:c00::/40", err: "invalid project id: 'qweasd'"},
		{s: "10df426@2a02:6b8:c00::/40"},
	}

	for idx, c := range cases {
		_, err := ParseTrypoNetwork(c.s)
		if c.err == "" {
			require.NoError(t, err, idx)
		} else {
			require.EqualError(t, err, c.err, idx)
		}
	}

	_, err := ParseTrypoNetwork("10df426@2a02:6b8:c00::")
	require.Error(t, err)
}

func TestTrypoNetworkContains(t *testing.T) {
	cases := []struct {
		s   string
		val bool
	}{
		{s: "8.8.8.8", val: false},
		{s: "2a02:6b8:b010:1d::7f", val: false},
		{s: "2a02:6b8:c00:0:10d:f426::", val: true},  // #1
		{s: "2a02:6b8:c00:0:10d:f426::1", val: true}, // #1
		{s: "2a02:7b8:c00:0:10d:f426::1", val: true}, // #2
		{s: "2a02:6b8:c00:0:20d:f426::1", val: true}, // #3
		{s: "2a02:6b8:c00:0:30d:f426::1", val: false},
		{s: "2a02:8b8:c00:0:10d:f426::1", val: false},
	}

	networks := make(TrypoNetworks)

	//#1
	n, err := ParseTrypoNetwork("10df426@2a02:6b8:c00::/40")
	require.NoError(t, err)
	networks.Add(n)

	//#2
	n, err = ParseTrypoNetwork("10df426@2a02:7b8:c00::/40")
	require.NoError(t, err)
	networks.Add(n)

	//#3
	n, err = ParseTrypoNetwork("20df426@2a02:6b8:c00::/40")
	require.NoError(t, err)
	networks.Add(n)

	for idx, c := range cases {
		ip := net.ParseIP(c.s)
		require.NotNil(t, ip)
		require.Equal(t, c.val, networks.Contains(ip), idx)
	}
}
