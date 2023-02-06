package parser

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestIP_GetItemType(t *testing.T) {
	require.Equal(t, InvalidItem, nilIPInfo.GetItemType())

	require.Equal(t, IPItem, sampleIPv4Info.GetItemType())
	require.Equal(t, IPItem, sampleIPv4MappedInfo.GetItemType())
	require.Equal(t, IPItem, sampleBackboneIPv6Info.GetItemType())
	require.Equal(t, IPItem, sampleFastboneIPv6Info.GetItemType())
	require.Equal(t, IPItem, sampleIPv6Info.GetItemType())
	require.Equal(t, IPItem, sampleIPv6FullInfo.GetItemType())
}

func TestIP_Copy(t *testing.T) {
	require.Equal(t, nilIPInfo, nilIPInfo.Copy())

	require.Equal(t, sampleIPv4Info, sampleIPv4Info.Copy())
	require.Equal(t, sampleIPv4MappedInfo, sampleIPv4MappedInfo.Copy())
	require.Equal(t, sampleBackboneIPv6Info, sampleBackboneIPv6Info.Copy())
	require.Equal(t, sampleFastboneIPv6Info, sampleFastboneIPv6Info.Copy())
	require.Equal(t, sampleIPv6Info, sampleIPv6Info.Copy())
	require.Equal(t, sampleIPv6FullInfo, sampleIPv6FullInfo.Copy())
}

func TestIP_String(t *testing.T) {
	require.Empty(t, nilIPInfo.String())

	require.Equal(t, sampleIPv4, sampleIPv4Info.String())
	require.Equal(t, sampleIPv4Mapped, sampleIPv4MappedInfo.String())
	require.Equal(t, sampleBackboneIPv6, sampleBackboneIPv6Info.String())
	require.Equal(t, sampleFastboneIPv6, sampleFastboneIPv6Info.String())
	require.Equal(t, sampleIPv6, sampleIPv6Info.String())
	require.Equal(t, sampleIPv6Full, sampleIPv6FullInfo.String())
}

func TestIP_GetWeight(t *testing.T) {
	require.Nil(t, nilIPInfo.GetWeight())

	require.Equal(t, ipWeight, sampleIPv4Info.GetWeight().String())
	require.Equal(t, ipWeight, sampleIPv4MappedInfo.GetWeight().String())
	require.Equal(t, ipWeight, sampleBackboneIPv6Info.GetWeight().String())
	require.Equal(t, ipWeight, sampleFastboneIPv6Info.GetWeight().String())
	require.Equal(t, ipWeight, sampleIPv6Info.GetWeight().String())
	require.Equal(t, ipWeight, sampleIPv6FullInfo.GetWeight().String())
}

func TestIP_GetType(t *testing.T) {
	require.Equal(t, InvalidIP, nilIPInfo.GetType())
	require.Equal(t, IPv4, sampleIPv4Info.GetType())
	require.Equal(t, IPv4Mapped, sampleIPv4MappedInfo.GetType())
	require.Equal(t, IPv6, sampleBackboneIPv6Info.GetType())
	require.Equal(t, IPv6, sampleFastboneIPv6Info.GetType())
	require.Equal(t, IPv6, sampleIPv6Info.GetType())
	require.Equal(t, IPv6, sampleIPv6FullInfo.GetType())
}

func TestParseIP(t *testing.T) {
	require.Equal(t, sampleIPv4Info, WithoutCache.ParseIP(sampleIPv4))
	require.Equal(t, sampleIPv4MappedInfo, WithoutCache.ParseIP(sampleIPv4Mapped))
	require.Equal(t, sampleBackboneIPv6Info, WithoutCache.ParseIP(sampleBackboneIPv6))
	require.Equal(t, sampleFastboneIPv6Info, WithoutCache.ParseIP(sampleFastboneIPv6))
	require.Equal(t, sampleIPv6Info, WithoutCache.ParseIP(sampleIPv6))
	require.Equal(t, sampleIPv6FullInfo, WithoutCache.ParseIP(sampleIPv6Full))

	require.Nil(t, WithoutCache.ParseIP(sampleIPv6BackboneNet))
	require.Nil(t, WithoutCache.ParseIP(invalidIPv6TooSmall))
	require.Nil(t, WithoutCache.ParseIP(invalidIPv6InvalidSymbols))
	require.Nil(t, WithoutCache.ParseIP(invalidIPv4Mapped))
}

func TestIsIP(t *testing.T) {
	require.True(t, WithoutCache.IsIP(sampleIPv4))
	require.True(t, WithoutCache.IsIP(sampleIPv4Mapped))
	require.True(t, WithoutCache.IsIP(sampleBackboneIPv6))
	require.True(t, WithoutCache.IsIP(sampleFastboneIPv6))
	require.True(t, WithoutCache.IsIP(sampleIPv6))
	require.True(t, WithoutCache.IsIP(sampleIPv6Full))

	require.False(t, WithoutCache.IsIP(sampleIPv6BackboneNet))
	require.False(t, WithoutCache.IsIP(invalidIPv6TooSmall))
	require.False(t, WithoutCache.IsIP(invalidIPv6InvalidSymbols))
	require.False(t, WithoutCache.IsIP(invalidIPv4Mapped))
}
