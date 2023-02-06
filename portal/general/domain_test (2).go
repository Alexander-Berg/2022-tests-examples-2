package madmtypes

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNewDomainSet(t *testing.T) {
	for _, tc := range domains {
		require.Equal(t, tc.Set, NewDomainSet(tc.Repr))
	}
}

func TestDomainSet_ParseMADM(t *testing.T) {
	var d DomainSet
	for _, tc := range domains {
		require.NoError(t, d.ParseMADM([]byte(tc.Repr)))
		require.Equal(t, tc.Set, d)
	}
}

func TestDomainSet_Contains(t *testing.T) {
	require.True(t, RU.Contains(RU))
	require.True(t, UA.Contains(UA))
	require.True(t, AllDomains.Contains(RU))
	require.True(t, Kubru.Contains(RU))
	require.True(t, Kubru.Contains(KUB))
	require.False(t, KubrMinusUA.Contains(UA))
	require.False(t, Undefined.Contains(RU))
}

var domains = []struct {
	Repr string
	Set  DomainSet
}{
	{
		Repr: "ru",
		Set:  RU,
	},
	{
		Repr: "ua",
		Set:  UA,
	},
	{
		Repr: "kubru",
		Set:  Kubru,
	},
	{
		Repr: "foobar",
		Set:  Undefined,
	},
	{
		Repr: "",
		Set:  Undefined,
	},
	{
		Repr: "all",
		Set:  AllDomains,
	},
}
