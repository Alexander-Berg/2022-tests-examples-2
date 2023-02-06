package parser

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/macrospb"
)

func TestCompatibleMacroType(t *testing.T) {
	require.Equal(t, macrospb.NetMacro, CompatibleMacroType(NetItem))
	require.Equal(t, macrospb.NetMacro, CompatibleMacroType(IPItem))
	require.Equal(t, macrospb.NetMacro, CompatibleMacroType(ProjectItem))
	require.Equal(t, macrospb.HostMacro, CompatibleMacroType(HostItem))
	require.Equal(t, macrospb.AnyMacro, CompatibleMacroType(MacroItem))
	require.Equal(t, macrospb.InvalidMacro, CompatibleMacroType(InvalidItem))
	require.Equal(t, macrospb.InvalidMacro, CompatibleMacroType("Invalid type"))
}

func TestUpdateMacroType(t *testing.T) {
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.InvalidMacro, InvalidItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.InvalidMacro, MacroItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.InvalidMacro, IPItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.InvalidMacro, NetItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.InvalidMacro, ProjectItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.InvalidMacro, HostItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.InvalidMacro, "Invalid type"))

	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.AnyMacro, InvalidItem))
	require.Equal(t, macrospb.AnyMacro, UpdateMacroType(macrospb.AnyMacro, MacroItem))
	require.Equal(t, macrospb.NetMacro, UpdateMacroType(macrospb.AnyMacro, IPItem))
	require.Equal(t, macrospb.NetMacro, UpdateMacroType(macrospb.AnyMacro, NetItem))
	require.Equal(t, macrospb.NetMacro, UpdateMacroType(macrospb.AnyMacro, ProjectItem))
	require.Equal(t, macrospb.HostMacro, UpdateMacroType(macrospb.AnyMacro, HostItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.AnyMacro, "Invalid type"))

	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.NetMacro, InvalidItem))
	require.Equal(t, macrospb.NetMacro, UpdateMacroType(macrospb.NetMacro, MacroItem))
	require.Equal(t, macrospb.NetMacro, UpdateMacroType(macrospb.NetMacro, IPItem))
	require.Equal(t, macrospb.NetMacro, UpdateMacroType(macrospb.NetMacro, NetItem))
	require.Equal(t, macrospb.NetMacro, UpdateMacroType(macrospb.NetMacro, ProjectItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.NetMacro, HostItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.NetMacro, "Invalid type"))

	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.HostMacro, InvalidItem))
	require.Equal(t, macrospb.HostMacro, UpdateMacroType(macrospb.HostMacro, MacroItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.HostMacro, IPItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.HostMacro, NetItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.HostMacro, ProjectItem))
	require.Equal(t, macrospb.HostMacro, UpdateMacroType(macrospb.HostMacro, HostItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.HostMacro, "Invalid type"))

	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.MixedMacro, InvalidItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.MixedMacro, MacroItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.MixedMacro, IPItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.MixedMacro, NetItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.MixedMacro, ProjectItem))
	require.Equal(t, macrospb.MixedMacro, UpdateMacroType(macrospb.MixedMacro, HostItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType(macrospb.MixedMacro, "Invalid type"))

	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType("Invalid type", InvalidItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType("Invalid type", MacroItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType("Invalid type", IPItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType("Invalid type", NetItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType("Invalid type", ProjectItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType("Invalid type", HostItem))
	require.Equal(t, macrospb.InvalidMacro, UpdateMacroType("Invalid type", "Invalid type"))
}

func TestGetMacroTypeFromChildrenCorrect(t *testing.T) {
	children := sampleNetMacroChildren
	macroType, err := WithoutCache.GetMacroTypeFromChildren(children)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)

	children = sampleHostMacroChildren
	macroType, err = WithoutCache.GetMacroTypeFromChildren(children)
	require.NoError(t, err)
	require.Equal(t, macrospb.HostMacro, macroType)

	children = sampleMixedMacroChildren
	macroType, err = WithoutCache.GetMacroTypeFromChildren(children)
	require.NoError(t, err)
	require.Equal(t, macrospb.MixedMacro, macroType)

	children = sampleAnyMacroChildren
	macroType, err = WithoutCache.GetMacroTypeFromChildren(children)
	require.NoError(t, err)
	require.Equal(t, macrospb.AnyMacro, macroType)

	children = []string{}
	macroType, err = WithoutCache.GetMacroTypeFromChildren(children)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)

	children = nil
	macroType, err = WithoutCache.GetMacroTypeFromChildren(children)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)
}

func TestGetMacroTypeFromChildrenIncorrect(t *testing.T) {
	children := invalidMacroChildrenInvalidHost
	macroType, err := WithoutCache.GetMacroTypeFromChildren(children)
	require.EqualError(t, err, ""+
		"invalid macro children: "+
		invalidHostNoDomain+" is not a valid macro child (must be one of macro, IP, net, host)")
	require.Equal(t, macrospb.InvalidMacro, macroType)

	children = invalidMacroChildrenContainProject
	macroType, err = WithoutCache.GetMacroTypeFromChildren(children)
	require.EqualError(t, err, ""+
		"invalid macro children: "+
		sampleProjectBackbone+" is not a valid macro child (must be one of macro, IP, net, host)")
	require.Equal(t, macrospb.InvalidMacro, macroType)
}

func TestGetMacroTypeFromDefinitionCorrect(t *testing.T) {
	definition := sampleNetMacroDefinition
	macroType, err := WithoutCache.GetMacroTypeFromDefinition(definition)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)

	definition = sampleHostMacroDefinition
	macroType, err = WithoutCache.GetMacroTypeFromDefinition(definition)
	require.NoError(t, err)
	require.Equal(t, macrospb.HostMacro, macroType)

	definition = sampleMixedMacroDefinition
	macroType, err = WithoutCache.GetMacroTypeFromDefinition(definition)
	require.NoError(t, err)
	require.Equal(t, macrospb.MixedMacro, macroType)

	definition = sampleAnyMacroDefinition
	macroType, err = WithoutCache.GetMacroTypeFromDefinition(definition)
	require.NoError(t, err)
	require.Equal(t, macrospb.AnyMacro, macroType)

	definition = []string{}
	macroType, err = WithoutCache.GetMacroTypeFromDefinition(definition)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)

	definition = nil
	macroType, err = WithoutCache.GetMacroTypeFromDefinition(definition)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)
}

func TestGetMacroTypeFromDefinitionIncorrect(t *testing.T) {
	definition := invalidMacroDefinitionInvalidIP
	macroType, err := WithoutCache.GetMacroTypeFromDefinition(definition)
	require.EqualError(t, err, ""+
		"invalid macro definition: "+
		invalidIPv6InvalidSymbols+" is not a valid macro item (must be one of macro, IP, net, host, project)")
	require.Equal(t, macrospb.InvalidMacro, macroType)

	definition = invalidMacroDefinitionInvalidProject
	macroType, err = WithoutCache.GetMacroTypeFromDefinition(definition)
	require.EqualError(t, err, ""+
		"invalid macro definition: "+
		invalidProjectInvalidID+" is not a valid macro item (must be one of macro, IP, net, host, project)")
	require.Equal(t, macrospb.InvalidMacro, macroType)
}

func TestGetMacroTypeFromDescriptionCorrect(t *testing.T) {
	children := sampleNetMacroChildren
	projectIDs := sampleMacroProjectIDs
	macroType, err := WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)

	children = sampleHostMacroChildren
	projectIDs = []string{}
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.NoError(t, err)
	require.Equal(t, macrospb.HostMacro, macroType)

	children = sampleMixedMacroChildren
	projectIDs = sampleMacroProjectIDs
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.NoError(t, err)
	require.Equal(t, macrospb.MixedMacro, macroType)

	children = sampleAnyMacroChildren
	projectIDs = []string{}
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.NoError(t, err)
	require.Equal(t, macrospb.AnyMacro, macroType)

	children = sampleMacroChildrenNoProjectNet
	projectIDs = []string{}
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.NoError(t, err)
	require.Equal(t, macrospb.MixedMacro, macroType)

	children = nil
	projectIDs = nil
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.NoError(t, err)
	require.Equal(t, macrospb.NetMacro, macroType)
}

func TestGetMacroTypeFromDescriptionInCorrect(t *testing.T) {
	children := sampleNetMacroChildren
	projectIDs := invalidMacroProjectIDs
	macroType, err := WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.EqualError(t, err, ""+
		"invalid macro description: "+
		"invalid project IDs: "+
		invalidProjectIDRangeTwoMasks+" is not a valid project ID")
	require.Equal(t, macrospb.InvalidMacro, macroType)

	children = invalidMacroChildrenContainProject
	projectIDs = sampleMacroProjectIDs
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.EqualError(t, err, ""+
		"invalid macro description: "+
		"invalid macro children: "+
		sampleProjectBackbone+" is not a valid macro child (must be one of macro, IP, net, host)")
	require.Equal(t, macrospb.InvalidMacro, macroType)

	children = sampleMacroChildrenNoProjectNet
	projectIDs = sampleMacroProjectIDs
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.EqualError(t, err, ""+
		"invalid macro description: "+
		"a net from [2a02:6b8:c00::/40, 2a02:6b8:fc00::/40] must appear in children when projectIDs are specified")
	require.Equal(t, macrospb.InvalidMacro, macroType)

	children = invalidMacroChildrenMultipleProjectNets
	projectIDs = sampleMacroProjectIDs
	macroType, err = WithoutCache.GetMacroTypeFromDescription(children, projectIDs)
	require.EqualError(t, err, ""+
		"invalid macro description: "+
		"it is not allowed to have more than one net from [2a02:6b8:c00::/40, 2a02:6b8:fc00::/40] in children when projectIds are specified")
	require.Equal(t, macrospb.InvalidMacro, macroType)
}
