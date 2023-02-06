package grantnets

import (
	"net"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestClassicNetworkLooks(t *testing.T) {
	require.True(t, LooksLikeClassicNetwork("///"))
	require.True(t, LooksLikeClassicNetwork("/"))
	require.True(t, LooksLikeClassicNetwork("8.8.8.0/24"))

	require.False(t, LooksLikeClassicNetwork("8.8.8.8"))
	require.False(t, LooksLikeClassicNetwork("::1"))
}

func TestClassicNetworkParse(t *testing.T) {
	_, err := ParseClassicNetwork("///")
	require.Error(t, err)

	_, err = ParseClassicNetwork("8.8.8.8")
	require.Error(t, err)

	c, err := ParseClassicNetwork("8.8.8.0/24")
	require.NoError(t, err)

	require.True(t, c.Contains(net.IPv4(8, 8, 8, 8)))
	require.False(t, c.Contains(net.IPv4(8, 8, 7, 8)))

	_, err = ParseClassicNetwork("2a02:6b8:0:1465::/64")
	require.NoError(t, err)
}
