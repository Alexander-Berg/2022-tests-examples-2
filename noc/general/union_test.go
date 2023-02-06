package parser

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParseMacroItem(t *testing.T) {
	require.Equal(t, sampleMacroOneWordInfo, WithoutCache.ParseMacroItem(sampleMacroOneWord))
	require.Equal(t, sampleIPv4Info, WithoutCache.ParseMacroItem(sampleIPv4))
	require.Equal(t, sampleIPv6FullNetInfo, WithoutCache.ParseMacroItem(sampleIPv6FullNet))
	require.Equal(t, sampleProjectFastboneInfo, WithoutCache.ParseMacroItem(sampleProjectFastbone))
	require.Equal(t, sampleHostBasicInfo, WithoutCache.ParseMacroItem(sampleHostBasic))

	require.Nil(t, WithoutCache.ParseMacroItem(sampleProjectIDRangeShort))
	require.Nil(t, WithoutCache.ParseMacroItem(invalidIPv6NetTwoMasks))
}

func TestGetMacroItemType(t *testing.T) {
	require.Equal(t, MacroItem, WithoutCache.GetMacroItemType(sampleMacroOneWord))
	require.Equal(t, IPItem, WithoutCache.GetMacroItemType(sampleIPv4))
	require.Equal(t, NetItem, WithoutCache.GetMacroItemType(sampleIPv6FullNet))
	require.Equal(t, ProjectItem, WithoutCache.GetMacroItemType(sampleProjectFastbone))
	require.Equal(t, HostItem, WithoutCache.GetMacroItemType(sampleHostBasic))

	require.Equal(t, InvalidItem, WithoutCache.GetMacroItemType(sampleProjectIDRangeShort))
	require.Equal(t, InvalidItem, WithoutCache.GetMacroItemType(invalidIPv6NetTwoMasks))
}

func TestIsMacroItem(t *testing.T) {
	require.True(t, WithoutCache.IsMacroItem(sampleMacroOneWord))
	require.True(t, WithoutCache.IsMacroItem(sampleIPv4))
	require.True(t, WithoutCache.IsMacroItem(sampleIPv6FullNet))
	require.True(t, WithoutCache.IsMacroItem(sampleProjectFastbone))
	require.True(t, WithoutCache.IsMacroItem(sampleHostBasic))

	require.False(t, WithoutCache.IsMacroItem(sampleProjectIDRangeShort))
	require.False(t, WithoutCache.IsMacroItem(invalidIPv6NetTwoMasks))
}

func TestParseMacroLeaf(t *testing.T) {
	require.Equal(t, sampleIPv6Info, WithoutCache.ParseMacroLeaf(sampleIPv6))
	require.Equal(t, sampleIPv6NetInfo, WithoutCache.ParseMacroLeaf(sampleIPv6Net))
	require.Equal(t, sampleHostRealInfo, WithoutCache.ParseMacroLeaf(sampleHostReal))
	require.Equal(t, sampleProjectRangeBackboneInfo, WithoutCache.ParseMacroLeaf(sampleProjectRangeBackbone))

	require.Nil(t, WithoutCache.ParseMacroLeaf(sampleMacroOneWord))
	require.Nil(t, WithoutCache.ParseMacroLeaf(sampleProjectIDRangeLong))
	require.Nil(t, WithoutCache.ParseMacroLeaf(invalidHostNoDomain))
}

func TestGetMacroLeafType(t *testing.T) {
	require.Equal(t, IPItem, WithoutCache.GetMacroLeafType(sampleIPv6))
	require.Equal(t, NetItem, WithoutCache.GetMacroLeafType(sampleIPv6Net))
	require.Equal(t, HostItem, WithoutCache.GetMacroLeafType(sampleHostReal))
	require.Equal(t, ProjectItem, WithoutCache.GetMacroLeafType(sampleProjectRangeBackbone))

	require.Equal(t, InvalidItem, WithoutCache.GetMacroLeafType(sampleMacroOneWord))
	require.Equal(t, InvalidItem, WithoutCache.GetMacroLeafType(sampleProjectIDRangeLong))
	require.Equal(t, InvalidItem, WithoutCache.GetMacroLeafType(invalidHostNoDomain))
}

func TestIsMacroLeaf(t *testing.T) {
	require.True(t, WithoutCache.IsMacroLeaf(sampleIPv6))
	require.True(t, WithoutCache.IsMacroLeaf(sampleIPv6Net))
	require.True(t, WithoutCache.IsMacroLeaf(sampleHostReal))
	require.True(t, WithoutCache.IsMacroLeaf(sampleProjectRangeBackbone))

	require.False(t, WithoutCache.IsMacroLeaf(sampleMacroOneWord))
	require.False(t, WithoutCache.IsMacroLeaf(sampleProjectIDRangeLong))
	require.False(t, WithoutCache.IsMacroLeaf(invalidHostNoDomain))
}

func TestParseMacroChild(t *testing.T) {
	require.Equal(t, sampleMacroTwoWordsInfo, WithoutCache.ParseMacroChild(sampleMacroTwoWords))
	require.Equal(t, sampleIPv4MappedInfo, WithoutCache.ParseMacroChild(sampleIPv4Mapped))
	require.Equal(t, sampleIPv6BackboneNetInfo, WithoutCache.ParseMacroChild(sampleIPv6BackboneNet))
	require.Equal(t, sampleHostSpecialSymbolsInfo, WithoutCache.ParseMacroChild(sampleHostSpecialSymbols))

	require.Nil(t, WithoutCache.ParseMacroChild(sampleProjectIDRangeShort))
	require.Nil(t, WithoutCache.ParseMacroChild(sampleProjectFastbone))
	require.Nil(t, WithoutCache.ParseMacroChild(invalidMacroEmptyName))
	require.Nil(t, WithoutCache.ParseMacroChild(invalidProjectInvalidID))
}

func TestGetMacroChildType(t *testing.T) {
	require.Equal(t, MacroItem, WithoutCache.GetMacroChildType(sampleMacroTwoWords))
	require.Equal(t, IPItem, WithoutCache.GetMacroChildType(sampleIPv4Mapped))
	require.Equal(t, NetItem, WithoutCache.GetMacroChildType(sampleIPv6BackboneNet))
	require.Equal(t, HostItem, WithoutCache.GetMacroChildType(sampleHostSpecialSymbols))

	require.Equal(t, InvalidItem, WithoutCache.GetMacroChildType(sampleProjectIDRangeShort))
	require.Equal(t, InvalidItem, WithoutCache.GetMacroChildType(sampleProjectFastbone))
	require.Equal(t, InvalidItem, WithoutCache.GetMacroChildType(invalidMacroEmptyName))
	require.Equal(t, InvalidItem, WithoutCache.GetMacroChildType(invalidProjectInvalidID))
}

func TestIsMacroChild(t *testing.T) {
	require.True(t, WithoutCache.IsMacroChild(sampleMacroTwoWords))
	require.True(t, WithoutCache.IsMacroChild(sampleIPv4Mapped))
	require.True(t, WithoutCache.IsMacroChild(sampleIPv6BackboneNet))
	require.True(t, WithoutCache.IsMacroChild(sampleHostSpecialSymbols))

	require.False(t, WithoutCache.IsMacroChild(sampleProjectIDRangeShort))
	require.False(t, WithoutCache.IsMacroChild(sampleProjectFastbone))
	require.False(t, WithoutCache.IsMacroChild(invalidMacroEmptyName))
	require.False(t, WithoutCache.IsMacroChild(invalidProjectInvalidID))
}
