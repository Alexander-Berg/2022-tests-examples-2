package parser

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestHost_GetItemType(t *testing.T) {
	require.Equal(t, InvalidItem, nilHostInfo.GetItemType())

	require.Equal(t, HostItem, sampleHostBasicInfo.GetItemType())
	require.Equal(t, HostItem, sampleHostSpecialSymbolsInfo.GetItemType())
	require.Equal(t, HostItem, sampleHostRealInfo.GetItemType())
}

func TestHost_Copy(t *testing.T) {
	require.Equal(t, nilHostInfo, nilHostInfo.Copy())

	require.Equal(t, sampleHostBasicInfo, sampleHostBasicInfo.Copy())
	require.Equal(t, sampleHostSpecialSymbolsInfo, sampleHostSpecialSymbolsInfo.Copy())
	require.Equal(t, sampleHostRealInfo, sampleHostRealInfo.Copy())
}

func TestHost_String(t *testing.T) {
	require.Empty(t, nilHostInfo.String())

	require.Equal(t, sampleHostBasic, sampleHostBasicInfo.String())
	require.Equal(t, sampleHostSpecialSymbols, sampleHostSpecialSymbolsInfo.String())
	require.Equal(t, sampleHostReal, sampleHostRealInfo.String())
}

func TestHost_GetWeight(t *testing.T) {
	require.Nil(t, nilHostInfo.GetWeight())

	require.Equal(t, hostWeight, sampleHostBasicInfo.GetWeight().String())
	require.Equal(t, hostWeight, sampleHostSpecialSymbolsInfo.GetWeight().String())
	require.Equal(t, hostWeight, sampleHostRealInfo.GetWeight().String())
}

func TestParseHost(t *testing.T) {
	require.Equal(t, sampleHostBasicInfo, WithoutCache.ParseHost(sampleHostBasic))
	require.Equal(t, sampleHostSpecialSymbolsInfo, WithoutCache.ParseHost(sampleHostSpecialSymbols))
	require.Equal(t, sampleHostRealInfo, WithoutCache.ParseHost(sampleHostReal))

	require.Nil(t, WithoutCache.ParseHost(sampleIPv4))
	require.Nil(t, WithoutCache.ParseHost(invalidHostInvalidURL))
	require.Nil(t, WithoutCache.ParseHost(invalidHostNoDomain))
	require.Nil(t, WithoutCache.ParseHost(invalidHostIsRelPath))
	require.Nil(t, WithoutCache.ParseHost(invalidHostHasSchema))
	require.Nil(t, WithoutCache.ParseHost(invalidHostHasRelPath))
	require.Nil(t, WithoutCache.ParseHost(invalidHostHasParams))
	require.Nil(t, WithoutCache.ParseHost(invalidHostHasHash))
}

func TestIsHost(t *testing.T) {
	require.True(t, WithoutCache.IsHost(sampleHostBasic))
	require.True(t, WithoutCache.IsHost(sampleHostSpecialSymbols))
	require.True(t, WithoutCache.IsHost(sampleHostReal))

	require.False(t, WithoutCache.IsHost(sampleIPv4))
	require.False(t, WithoutCache.IsHost(invalidHostInvalidURL))
	require.False(t, WithoutCache.IsHost(invalidHostNoDomain))
	require.False(t, WithoutCache.IsHost(invalidHostIsRelPath))
	require.False(t, WithoutCache.IsHost(invalidHostHasSchema))
	require.False(t, WithoutCache.IsHost(invalidHostHasRelPath))
	require.False(t, WithoutCache.IsHost(invalidHostHasParams))
	require.False(t, WithoutCache.IsHost(invalidHostHasHash))
}
