package parser

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProject_GetItemType(t *testing.T) {
	require.Equal(t, InvalidItem, nilProjectInfo.GetItemType())

	require.Equal(t, ProjectItem, sampleProjectBackboneInfo.GetItemType())
	require.Equal(t, ProjectItem, sampleProjectFastboneInfo.GetItemType())
	require.Equal(t, ProjectItem, sampleProjectSecuredInfo.GetItemType())
	require.Equal(t, ProjectItem, sampleProjectRangeBackboneInfo.GetItemType())
}

func TestProject_Copy(t *testing.T) {
	require.Equal(t, nilProjectInfo, nilProjectInfo.Copy())

	require.Equal(t, sampleProjectBackboneInfo, sampleProjectBackboneInfo.Copy())
	require.Equal(t, sampleProjectFastboneInfo, sampleProjectFastboneInfo.Copy())
	require.Equal(t, sampleProjectSecuredInfo, sampleProjectSecuredInfo.Copy())
	require.Equal(t, sampleProjectRangeBackboneInfo, sampleProjectRangeBackboneInfo.Copy())
}

func TestProject_String(t *testing.T) {
	require.Empty(t, nilProjectInfo.String())

	require.Equal(t, sampleProjectBackbone, sampleProjectBackboneInfo.String())
	require.Equal(t, sampleProjectFastbone, sampleProjectFastboneInfo.String())
	require.Equal(t, sampleProjectSecured, sampleProjectSecuredInfo.String())
	require.Equal(t, sampleProjectRangeBackbone, sampleProjectRangeBackboneInfo.String())
}

func TestProject_GetWeight(t *testing.T) {
	require.Nil(t, nilProjectInfo.GetWeight())

	require.Equal(t, sampleSingleProjectWeight, sampleProjectBackboneInfo.GetWeight().String())
	require.Equal(t, sampleSingleProjectWeight, sampleProjectFastboneInfo.GetWeight().String())
	require.Equal(t, sampleSingleProjectWeight, sampleProjectSecuredInfo.GetWeight().String())
	require.Equal(t, sampleProjectRangeBackboneWeight, sampleProjectRangeBackboneInfo.GetWeight().String())
}

func TestProject_GetProjectID(t *testing.T) {
	require.Nil(t, nilProjectInfo.GetProjectID())

	require.Equal(t, sampleProjectIDShortInfo, sampleProjectBackboneInfo.GetProjectID())
	require.Equal(t, sampleProjectIDLongInfo, sampleProjectFastboneInfo.GetProjectID())
	require.Equal(t, sampleProjectIDSecuredInfo, sampleProjectSecuredInfo.GetProjectID())
	require.Equal(t, sampleProjectIDRangeLongInfo, sampleProjectRangeBackboneInfo.GetProjectID())
}

func TestProject_GetNet(t *testing.T) {
	require.Nil(t, nilProjectInfo.GetNet())

	require.Equal(t, sampleIPv6BackboneNetInfo, sampleProjectBackboneInfo.GetNet())
	require.Equal(t, sampleIPv6FastboneNetInfo, sampleProjectFastboneInfo.GetNet())
	require.Equal(t, sampleIPv6FastboneNetInfo, sampleProjectSecuredInfo.GetNet())
	require.Equal(t, sampleIPv6BackboneNetInfo, sampleProjectRangeBackboneInfo.GetNet())
}

func TestProject_IsRange(t *testing.T) {
	require.False(t, nilProjectInfo.IsRange())

	require.False(t, sampleProjectBackboneInfo.IsRange())
	require.False(t, sampleProjectFastboneInfo.IsRange())
	require.False(t, sampleProjectSecuredInfo.IsRange())

	require.True(t, sampleProjectRangeBackboneInfo.IsRange())
}

func TestProject_IsSecured(t *testing.T) {
	require.False(t, nilProjectInfo.IsSecured())

	require.False(t, sampleProjectBackboneInfo.IsSecured())
	require.False(t, sampleProjectFastboneInfo.IsSecured())
	require.False(t, sampleProjectRangeBackboneInfo.IsSecured())

	require.True(t, sampleProjectSecuredInfo.IsSecured())
}

func TestProject_GetNetType(t *testing.T) {
	require.Equal(t, InvalidProjectNet, nilProjectInfo.GetNetType())

	require.Equal(t, BackboneProjectNet, sampleProjectBackboneInfo.GetNetType())
	require.Equal(t, FastboneProjectNet, sampleProjectFastboneInfo.GetNetType())
	require.Equal(t, FastboneProjectNet, sampleProjectSecuredInfo.GetNetType())
	require.Equal(t, BackboneProjectNet, sampleProjectRangeBackboneInfo.GetNetType())

	require.Equal(t, InvalidProjectNet, invalidProjectInsufficientNetInfo.GetNetType())
}

func TestParseProject(t *testing.T) {
	projectInfo, ok := WithoutCache.ParseProject(sampleProjectBackbone)
	require.True(t, ok)
	require.Equal(t, sampleProjectBackboneInfo, projectInfo)

	projectInfo, ok = WithoutCache.ParseProject(sampleProjectFastbone)
	require.True(t, ok)
	require.Equal(t, sampleProjectFastboneInfo, projectInfo)

	projectInfo, ok = WithoutCache.ParseProject(sampleProjectRangeBackbone)
	require.True(t, ok)
	require.Equal(t, sampleProjectRangeBackboneInfo, projectInfo)

	projectInfo, ok = WithoutCache.ParseProject(invalidProjectInsufficientNet)
	require.False(t, ok)
	require.Equal(t, invalidProjectInsufficientNetInfo, projectInfo)

	projectInfo, ok = WithoutCache.ParseProject(sampleIPv4Net)
	require.False(t, ok)
	require.Nil(t, projectInfo)

	projectInfo, ok = WithoutCache.ParseProject(invalidProjectMultipleIDs)
	require.False(t, ok)
	require.Nil(t, projectInfo)

	projectInfo, ok = WithoutCache.ParseProject(invalidProjectInvalidID)
	require.False(t, ok)
	require.Nil(t, projectInfo)

	projectInfo, ok = WithoutCache.ParseProject(invalidProjectInvalidNet)
	require.False(t, ok)
	require.Nil(t, projectInfo)
}

func TestIsProject(t *testing.T) {
	require.True(t, WithoutCache.IsProject(sampleProjectBackbone))
	require.True(t, WithoutCache.IsProject(sampleProjectFastbone))
	require.True(t, WithoutCache.IsProject(sampleProjectRangeBackbone))

	require.False(t, WithoutCache.IsProject(sampleIPv4Net))
	require.False(t, WithoutCache.IsProject(invalidProjectMultipleIDs))
	require.False(t, WithoutCache.IsProject(invalidProjectInvalidID))
	require.False(t, WithoutCache.IsProject(invalidProjectInvalidNet))
	require.False(t, WithoutCache.IsProject(invalidProjectInsufficientNet))
}
