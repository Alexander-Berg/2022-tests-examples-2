package parser

import (
	"math"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProjectID_GetItemType(t *testing.T) {
	require.Equal(t, InvalidItem, nilProjectIDInfo.GetItemType())

	require.Equal(t, ProjectIDItem, sampleProjectIDShortInfo.GetItemType())
	require.Equal(t, ProjectIDItem, sampleProjectIDLongInfo.GetItemType())
	require.Equal(t, ProjectIDItem, sampleProjectIDSecuredInfo.GetItemType())
	require.Equal(t, ProjectIDItem, sampleProjectIDRangeShortInfo.GetItemType())
	require.Equal(t, ProjectIDItem, sampleProjectIDRangeLongInfo.GetItemType())
	require.Equal(t, ProjectIDItem, sampleProjectIDRangeLowerNotBaseInfo.GetItemType())
}

func TestProjectID_Copy(t *testing.T) {
	require.Equal(t, nilProjectIDInfo, nilProjectIDInfo.Copy())

	require.Equal(t, sampleProjectIDShortInfo, sampleProjectIDShortInfo.Copy())
	require.Equal(t, sampleProjectIDLongInfo, sampleProjectIDLongInfo.Copy())
	require.Equal(t, sampleProjectIDSecuredInfo, sampleProjectIDSecuredInfo.Copy())
	require.Equal(t, sampleProjectIDRangeShortInfo, sampleProjectIDRangeShortInfo.Copy())
	require.Equal(t, sampleProjectIDRangeLongInfo, sampleProjectIDRangeLongInfo.Copy())
	require.Equal(t, sampleProjectIDRangeLowerNotBaseInfo, sampleProjectIDRangeLowerNotBaseInfo.Copy())
}

func TestProjectID_String(t *testing.T) {
	require.Empty(t, nilProjectIDInfo.String())

	require.Equal(t, sampleProjectIDShort, sampleProjectIDShortInfo.String())
	require.Equal(t, sampleProjectIDLong, sampleProjectIDLongInfo.String())
	require.Equal(t, sampleProjectIDSecured, sampleProjectIDSecuredInfo.String())
	require.Equal(t, sampleProjectIDRangeShort, sampleProjectIDRangeShortInfo.String())
	require.Equal(t, sampleProjectIDRangeLong, sampleProjectIDRangeLongInfo.String())
	require.Equal(t, "f000/20", sampleProjectIDRangeLowerNotBaseInfo.String())

}

func TestProjectID_GetWeight(t *testing.T) {
	require.Nil(t, nilProjectIDInfo.GetWeight())

	require.Equal(t, singleProjectIDWeight, sampleProjectIDShortInfo.GetWeight().String())
	require.Equal(t, singleProjectIDWeight, sampleProjectIDLongInfo.GetWeight().String())
	require.Equal(t, singleProjectIDWeight, sampleProjectIDSecuredInfo.GetWeight().String())
	require.Equal(t, sampleProjectIDRangeShortWeight, sampleProjectIDRangeShortInfo.GetWeight().String())
	require.Equal(t, sampleProjectIDRangeLongWeight, sampleProjectIDRangeLongInfo.GetWeight().String())
	require.Equal(t, sampleProjectIDRangeLowerNotBaseWeight, sampleProjectIDRangeLowerNotBaseInfo.GetWeight().String())
}

func TestProjectID_GetMaskSize(t *testing.T) {
	require.Zero(t, nilProjectIDInfo.GetMaskSize())

	require.Equal(t, -1, sampleProjectIDShortInfo.GetMaskSize())
	require.Equal(t, -1, sampleProjectIDLongInfo.GetMaskSize())
	require.Equal(t, -1, sampleProjectIDSecuredInfo.GetMaskSize())
	require.Equal(t, 23, sampleProjectIDRangeShortInfo.GetMaskSize())
	require.Equal(t, 16, sampleProjectIDRangeLongInfo.GetMaskSize())
	require.Equal(t, 20, sampleProjectIDRangeLowerNotBaseInfo.GetMaskSize())
}

func TestProjectID_IsRange(t *testing.T) {
	require.False(t, nilProjectIDInfo.IsRange())

	require.False(t, sampleProjectIDShortInfo.IsRange())
	require.False(t, sampleProjectIDLongInfo.IsRange())
	require.False(t, sampleProjectIDSecuredInfo.IsRange())

	require.True(t, sampleProjectIDRangeShortInfo.IsRange())
	require.True(t, sampleProjectIDRangeLongInfo.IsRange())
	require.True(t, sampleProjectIDRangeLowerNotBaseInfo.IsRange())
}

func TestProjectID_IsSecured(t *testing.T) {
	require.False(t, nilProjectIDInfo.IsSecured())

	require.False(t, sampleProjectIDShortInfo.IsSecured())
	require.False(t, sampleProjectIDLongInfo.IsSecured())
	require.False(t, sampleProjectIDRangeShortInfo.IsSecured())
	require.False(t, sampleProjectIDRangeLongInfo.IsSecured())
	require.False(t, sampleProjectIDRangeLowerNotBaseInfo.IsSecured())

	require.True(t, sampleProjectIDSecuredInfo.IsSecured())
}

func TestProjectID_Uint(t *testing.T) {
	require.Equal(t, uint32(math.MaxUint32), nilProjectIDInfo.Uint())

	require.Equal(t, sampleProjectIDShortInfo.baseID, sampleProjectIDShortInfo.Uint())
	require.Equal(t, sampleProjectIDLongInfo.baseID, sampleProjectIDLongInfo.Uint())
	require.Equal(t, sampleProjectIDSecuredInfo.baseID, sampleProjectIDSecuredInfo.Uint())

	require.Equal(t, uint32(math.MaxUint32), sampleProjectIDRangeShortInfo.Uint())
	require.Equal(t, uint32(math.MaxUint32), sampleProjectIDRangeLongInfo.Uint())
	require.Equal(t, uint32(math.MaxUint32), sampleProjectIDRangeLowerNotBaseInfo.Uint())
}

func TestProjectID_GetLower(t *testing.T) {
	require.Nil(t, nilProjectIDInfo.GetLower())

	require.Equal(t, sampleProjectIDShortInfo, sampleProjectIDShortInfo.GetLower())
	require.Equal(t, sampleProjectIDLongInfo, sampleProjectIDLongInfo.GetLower())
	require.Equal(t, sampleProjectIDSecuredInfo, sampleProjectIDSecuredInfo.GetLower())

	require.Equal(t, sampleProjectIDRangeShortLowerInfo, sampleProjectIDRangeShortInfo.GetLower())
	require.Equal(t, sampleProjectIDRangeLongLowerInfo, sampleProjectIDRangeLongInfo.GetLower())
	require.Equal(t, sampleProjectIDRangeLowerNotBaseLowerInfo, sampleProjectIDRangeLowerNotBaseInfo.GetLower())
}

func TestProjectID_GetLowerUint(t *testing.T) {
	require.Equal(t, uint32(math.MaxUint32), nilProjectIDInfo.GetLowerUint())

	require.Equal(t, sampleProjectIDShortInfo.Uint(), sampleProjectIDShortInfo.GetLowerUint())
	require.Equal(t, sampleProjectIDLongInfo.Uint(), sampleProjectIDLongInfo.GetLowerUint())
	require.Equal(t, sampleProjectIDSecuredInfo.Uint(), sampleProjectIDSecuredInfo.GetLowerUint())

	require.Equal(t, sampleProjectIDRangeShortLowerInfo.Uint(), sampleProjectIDRangeShortInfo.GetLowerUint())
	require.Equal(t, sampleProjectIDRangeLongLowerInfo.Uint(), sampleProjectIDRangeLongInfo.GetLowerUint())
	require.Equal(t, sampleProjectIDRangeLowerNotBaseLowerInfo.Uint(), sampleProjectIDRangeLowerNotBaseInfo.GetLowerUint())
}

func TestProjectID_GetUpper(t *testing.T) {
	require.Nil(t, nilProjectIDInfo.GetUpper())

	require.Equal(t, sampleProjectIDShortInfo, sampleProjectIDShortInfo.GetUpper())
	require.Equal(t, sampleProjectIDLongInfo, sampleProjectIDLongInfo.GetUpper())
	require.Equal(t, sampleProjectIDSecuredInfo, sampleProjectIDSecuredInfo.GetUpper())

	require.Equal(t, sampleProjectIDRangeShortUpperInfo, sampleProjectIDRangeShortInfo.GetUpper())
	require.Equal(t, sampleProjectIDRangeLongUpperInfo, sampleProjectIDRangeLongInfo.GetUpper())
	require.Equal(t, sampleProjectIDRangeLowerNotBaseUpperInfo, sampleProjectIDRangeLowerNotBaseInfo.GetUpper())
}

func TestProjectID_GetUpperUint(t *testing.T) {
	require.Equal(t, uint32(math.MaxUint32), nilProjectIDInfo.GetUpperUint())

	require.Equal(t, sampleProjectIDShortInfo.Uint(), sampleProjectIDShortInfo.GetUpperUint())
	require.Equal(t, sampleProjectIDLongInfo.Uint(), sampleProjectIDLongInfo.GetUpperUint())
	require.Equal(t, sampleProjectIDSecuredInfo.Uint(), sampleProjectIDSecuredInfo.GetUpperUint())

	require.Equal(t, sampleProjectIDRangeShortUpperInfo.Uint(), sampleProjectIDRangeShortInfo.GetUpperUint())
	require.Equal(t, sampleProjectIDRangeLongUpperInfo.Uint(), sampleProjectIDRangeLongInfo.GetUpperUint())
	require.Equal(t, sampleProjectIDRangeLowerNotBaseUpperInfo.Uint(), sampleProjectIDRangeLowerNotBaseInfo.GetUpperUint())
}

func TestProjectID_Contains(t *testing.T) {
	// nil
	require.True(t, nilProjectIDInfo.Contains(nilProjectIDInfo))
	require.False(t, nilProjectIDInfo.Contains(sampleProjectIDLongInfo))
	require.False(t, sampleBiggestProjectIDRange.Contains(nilProjectIDInfo))

	// contains itself
	require.True(t, sampleProjectIDLongInfo.Contains(sampleProjectIDLongInfo))
	require.True(t, sampleProjectIDRangeLowerNotBaseInfo.Contains(sampleProjectIDRangeLowerNotBaseInfo))

	// the biggest one contains all
	require.True(t, sampleBiggestProjectIDRange.Contains(sampleProjectIDShortInfo))
	require.True(t, sampleBiggestProjectIDRange.Contains(sampleProjectIDRangeLongInfo))

	// nothing contains the biggest (but itself)
	require.False(t, sampleProjectIDSecuredInfo.Contains(sampleBiggestProjectIDRange))
	require.False(t, sampleProjectIDRangeShortInfo.Contains(sampleBiggestProjectIDRange))

	// general case
	require.True(t, sampleOuterProjectIDRange.Contains(sampleInnerProjectIDRange))
	require.False(t, sampleInnerProjectIDRange.Contains(sampleOuterProjectIDRange))
}

func TestProjectID_Intersect(t *testing.T) {
	// nil
	start, finish, ok := nilProjectIDInfo.Intersect(nilProjectIDInfo)
	require.Zero(t, start)
	require.Zero(t, finish)
	require.False(t, ok)

	start, finish, ok = sampleBiggestProjectIDRange.Intersect(nilProjectIDInfo)
	require.Zero(t, start)
	require.Zero(t, finish)
	require.False(t, ok)

	start, finish, ok = nilProjectIDInfo.Intersect(sampleBiggestProjectIDRange)
	require.Zero(t, start)
	require.Zero(t, finish)
	require.False(t, ok)

	// intersect with itself is itself

	start, finish, ok = sampleProjectIDLongInfo.Intersect(sampleProjectIDLongInfo)
	require.Equal(t, sampleProjectIDLongInfo.GetLowerUint(), start)
	require.Equal(t, sampleProjectIDLongInfo.GetUpperUint(), finish)
	require.True(t, ok)

	start, finish, ok = sampleProjectIDRangeLongInfo.Intersect(sampleProjectIDRangeLongInfo)
	require.Equal(t, sampleProjectIDRangeLongInfo.GetLowerUint(), start)
	require.Equal(t, sampleProjectIDRangeLongInfo.GetUpperUint(), finish)
	require.True(t, ok)

	// intersect with the biggest is itself (no matter the order)

	start, finish, ok = sampleBiggestProjectIDRange.Intersect(sampleProjectIDLongInfo)
	require.Equal(t, sampleProjectIDLongInfo.GetLowerUint(), start)
	require.Equal(t, sampleProjectIDLongInfo.GetUpperUint(), finish)
	require.True(t, ok)

	start, finish, ok = sampleBiggestProjectIDRange.Intersect(sampleProjectIDRangeShortInfo)
	require.Equal(t, sampleProjectIDRangeShortInfo.GetLowerUint(), start)
	require.Equal(t, sampleProjectIDRangeShortInfo.GetUpperUint(), finish)
	require.True(t, ok)

	start, finish, ok = sampleProjectIDRangeLongInfo.Intersect(sampleBiggestProjectIDRange)
	require.Equal(t, sampleProjectIDRangeLongInfo.GetLowerUint(), start)
	require.Equal(t, sampleProjectIDRangeLongInfo.GetUpperUint(), finish)
	require.True(t, ok)

	start, finish, ok = sampleProjectIDShortInfo.Intersect(sampleBiggestProjectIDRange)
	require.Equal(t, sampleProjectIDShortInfo.GetLowerUint(), start)
	require.Equal(t, sampleProjectIDShortInfo.GetUpperUint(), finish)
	require.True(t, ok)

	// intersect with outer is itself (no matter the order)

	start, finish, ok = sampleOuterProjectIDRange.Intersect(sampleInnerProjectIDRange)
	require.Equal(t, sampleInnerProjectIDRange.GetLowerUint(), start)
	require.Equal(t, sampleInnerProjectIDRange.GetUpperUint(), finish)
	require.True(t, ok)

	start, finish, ok = sampleInnerProjectIDRange.Intersect(sampleOuterProjectIDRange)
	require.Equal(t, sampleInnerProjectIDRange.GetLowerUint(), start)
	require.Equal(t, sampleInnerProjectIDRange.GetUpperUint(), finish)
	require.True(t, ok)

	// no intersection

	start, finish, ok = sampleNoIntersectProjectIDRange.Intersect(sampleInnerProjectIDRange)
	require.Zero(t, start)
	require.Zero(t, finish)
	require.False(t, ok)

	start, finish, ok = sampleOuterProjectIDRange.Intersect(sampleNoIntersectProjectIDRange)
	require.Zero(t, start)
	require.Zero(t, finish)
	require.False(t, ok)

	// partial intersect is impossible in our model since ranges
	// are defined using masks and not as an arbitrary segment of project IDs
}

func TestParseProjectID(t *testing.T) {
	require.Equal(t, sampleProjectIDShortInfo, WithoutCache.ParseProjectID(sampleProjectIDShort))
	require.Equal(t, sampleProjectIDLongInfo, WithoutCache.ParseProjectID(sampleProjectIDLong))
	require.Equal(t, sampleProjectIDSecuredInfo, WithoutCache.ParseProjectID(sampleProjectIDSecured))
	require.Equal(t, sampleProjectIDRangeShortInfo, WithoutCache.ParseProjectID(sampleProjectIDRangeShort))
	require.Equal(t, sampleProjectIDRangeLongInfo, WithoutCache.ParseProjectID(sampleProjectIDRangeLong))
	require.Equal(t, sampleProjectIDRangeLowerNotBaseInfo, WithoutCache.ParseProjectID(sampleProjectIDRangeLowerNotBase))

	require.Nil(t, WithoutCache.ParseProjectID(invalidProjectIDIPLike))
	require.Nil(t, WithoutCache.ParseProjectID(invalidProjectIDEndFF))
	require.Nil(t, WithoutCache.ParseProjectID(invalidProjectIDTooBig))
	require.Nil(t, WithoutCache.ParseProjectID(invalidProjectIDRangeTwoMasks))
	require.Nil(t, WithoutCache.ParseProjectID(invalidProjectIDRangeMaskNegative))
	require.Nil(t, WithoutCache.ParseProjectID(invalidProjectIDRangeMaskTooBig))
	require.Nil(t, WithoutCache.ParseProjectID(invalidProjectIDRangeMaskNotInt))
}

func TestIsProjectID(t *testing.T) {
	require.True(t, WithoutCache.IsProjectID(sampleProjectIDShort))
	require.True(t, WithoutCache.IsProjectID(sampleProjectIDLong))
	require.True(t, WithoutCache.IsProjectID(sampleProjectIDSecured))
	require.True(t, WithoutCache.IsProjectID(sampleProjectIDRangeShort))
	require.True(t, WithoutCache.IsProjectID(sampleProjectIDRangeLong))
	require.True(t, WithoutCache.IsProjectID(sampleProjectIDRangeLowerNotBase))

	require.False(t, WithoutCache.IsProjectID(invalidProjectIDIPLike))
	require.False(t, WithoutCache.IsProjectID(invalidProjectIDEndFF))
	require.False(t, WithoutCache.IsProjectID(invalidProjectIDTooBig))
	require.False(t, WithoutCache.IsProjectID(invalidProjectIDRangeTwoMasks))
	require.False(t, WithoutCache.IsProjectID(invalidProjectIDRangeMaskNegative))
	require.False(t, WithoutCache.IsProjectID(invalidProjectIDRangeMaskTooBig))
	require.False(t, WithoutCache.IsProjectID(invalidProjectIDRangeMaskNotInt))
}

func TestCheckProjectIDs(t *testing.T) {
	require.NoError(t, WithoutCache.CheckProjectIDs(nil))
	require.NoError(t, WithoutCache.CheckProjectIDs([]string{}))

	projectIDs := []string{
		sampleProjectIDShort,
		sampleProjectIDLong,
		sampleProjectIDRangeShort,
		sampleProjectIDRangeLong,
	}
	require.NoError(t, WithoutCache.CheckProjectIDs(projectIDs))

	projectIDs = []string{
		sampleProjectIDShort,
		sampleProjectIDLong,
		invalidProjectIDIPLike,
		sampleProjectIDRangeLong,
	}
	err := WithoutCache.CheckProjectIDs(projectIDs)
	require.EqualError(t, err, ""+
		"invalid project IDs: "+
		invalidProjectIDIPLike+" is not a valid project ID")

	projectIDs = []string{
		sampleProjectIDShort,
		sampleProjectIDLong,
		sampleProjectIDRangeShort,
		invalidProjectIDRangeMaskTooBig,
		sampleProjectIDRangeLong,
		invalidProjectIDRangeMaskNotInt,
	}
	err = WithoutCache.CheckProjectIDs(projectIDs)
	require.EqualError(t, err, ""+
		"invalid project IDs: "+
		invalidProjectIDRangeMaskTooBig+" is not a valid project ID")
}
