package grantnets

import (
	"net"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestHostParse(t *testing.T) {
	_, err := ParseHost("987.123.asa.3")
	require.Error(t, err)

	cases := []struct {
		s    string
		high uint64
		low  uint64
	}{
		{s: "123.45.67.89", high: 0, low: 0xffff7b2d4359},
		{s: "2a02:6b8:0:1402::182", high: 0x2a0206b800001402, low: 0x182},
		{s: "2a02:6b8:0:1472:2741:0:8b6:212", high: 0x2a0206b800001472, low: 0x2741000008b60212},
	}
	h, err := ParseHost("123.45.67.89")
	require.NoError(t, err)
	require.Equal(t, uint64(0), h.high)
	require.Equal(t, uint64(0xffff7b2d4359), h.low)

	for idx, c := range cases {
		ip := net.ParseIP(c.s)
		require.NotNil(t, ip)

		h = HostFromIP(ip)
		require.Equal(t, c.high, h.high, idx)
		require.Equal(t, c.low, h.low, idx)
	}
}

func TestHostContains(t *testing.T) {
	hosts := make(Hosts)
	hosts.Add(HostFromIP(net.IPv4(127, 0, 0, 1)))
	ip := net.ParseIP("2a02:6b8:0:1472:2741:0:8b6:212")
	require.NotNil(t, ip)
	hosts.Add(HostFromIP(ip))

	require.True(t, hosts.Contains(net.IPv4(127, 0, 0, 1)))
	require.True(t, hosts.Contains(ip))

	ip = net.ParseIP("2a02:6b8:0:1472:2741:0:8b6:210")
	require.NotNil(t, ip)
	require.False(t, hosts.Contains(ip))
}
