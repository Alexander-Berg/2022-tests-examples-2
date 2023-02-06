package jobsutils

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/pkg/macros/mctests"
)

func TestGetExpansionsWeight(t *testing.T) {
	expansions := map[string]map[string]struct{}{
		macroOne: {
			sampleProject:   {},
			sampleHostOne:   {},
			sampleNetOneIP:  {},
			sampleCommonNet: {},
		},
		macroTwo: {
			sampleHostOne:   {},
			sampleIPv6:      {},
			sampleIPv4:      {},
			sampleCommonNet: {},
		},
		macroThree: {
			sampleProject: {},
		},
		// this is an important case because there used to a bug
		// when macroThree and macroFour would've been different
		macroFour: {
			sampleProject: {},
		},
	}
	weights := getExpansionsWeight(expansions)
	require.Equal(t, "72339069014638594", weights[macroOne].String())
	require.Equal(t, "281474976710659", weights[macroTwo].String())
	require.Equal(t, "72057594037927936", weights[macroThree].String())
	require.Equal(t, weights[macroFour].String(), weights[macroThree].String())

	expansions = map[string]map[string]struct{}{
		macroOne: {
			sampleHostOne:      {},
			sampleNetOneIP:     {},
			sampleProjectRange: {},
		},
		macroTwo: {
			sampleHostOne:   {},
			sampleProject:   {},
			sampleIPv4:      {},
			sampleCommonNet: {},
		},
		macroThree: {},
	}
	weights = getExpansionsWeight(expansions)
	require.Equal(t, "36893488147419103234", weights[macroOne].String())
	require.Equal(t, "72339069014638594", weights[macroTwo].String())
	require.Equal(t, "0", weights[macroThree].String())
}

func TestGetMostSpecificMacros(t *testing.T) {
	expansions := map[string]map[string]struct{}{}
	dependencies := map[string]map[string]struct{}{}
	specMacros, err := GetMostSpecificMacros(expansions, dependencies)
	require.NoError(t, err)
	require.Equal(t, map[string]string{}, specMacros)

	expansions = nil
	dependencies = nil
	specMacros, err = GetMostSpecificMacros(expansions, dependencies)
	require.NoError(t, err)
	require.Nil(t, specMacros)

	expansions = map[string]map[string]struct{}{}
	dependencies = nil
	specMacros, err = GetMostSpecificMacros(expansions, dependencies)
	require.NoError(t, err)
	require.Nil(t, specMacros)

	expansions = nil
	dependencies = map[string]map[string]struct{}{}
	specMacros, err = GetMostSpecificMacros(expansions, dependencies)
	require.NoError(t, err)
	require.Nil(t, specMacros)

	expansions = map[string]map[string]struct{}{
		macroOne: {
			sampleHostOne:      {},
			sampleCommonNet:    {},
			sampleIPv6:         {},
			sampleProjectRange: {},
		},
		macroTwo: {
			sampleHostOne:      {},
			sampleProjectRange: {},
		},
		macroThree: {
			sampleHostOne:   {},
			sampleCommonNet: {},
			sampleIPv6:      {},
		},
		macroFour: {
			sampleHostTwo:      {},
			sampleProjectRange: {},
			sampleHostOne:      {},
		},
		macroFive: {
			sampleHostOne: {},
		},
		macroSix: {
			sampleHostOne:   {},
			sampleCommonNet: {},
			sampleIPv6:      {},
		},
		macroSeven: {
			sampleProject:   {},
			sampleHostOne:   {},
			sampleCommonNet: {},
			sampleIPv6:      {},
		},
		skipMacroForMostSpecific: {
			sampleProject:   {},
			sampleHostOne:   {},
			sampleCommonNet: {},
			sampleIPv6:      {},
		},
	}
	dependencies = map[string]map[string]struct{}{
		macroOne: {
			macroTwo:   {},
			macroThree: {},
		},
		macroTwo: {},
		// macroThree is consciously omitted to test such a case
		macroFour: {
			macroTwo: {},
		},
		macroFive: {},
		macroSix: {
			macroThree: {},
		},
		macroSeven: {
			macroThree: {},
		},
		skipMacroForMostSpecific: {
			macroThree: {},
		},
	}
	specMacros, err = GetMostSpecificMacros(expansions, dependencies)
	require.NoError(t, err)
	require.Equal(t, macroTwo, specMacros[sampleProjectRange])
	require.Equal(t, macroThree, specMacros[sampleCommonNet])
	require.Equal(t, macroThree, specMacros[sampleIPv6])
	require.Equal(t, macroSeven, specMacros[sampleProject])

	expansions = map[string]map[string]struct{}{
		macroOne: {
			sampleCommonNet: {},
		},
		macroTwo: {
			sampleCommonNet: {},
		},
	}
	dependencies = map[string]map[string]struct{}{}
	specMacros, err = GetMostSpecificMacros(expansions, dependencies)
	require.Nil(t, specMacros)
	require.Error(t, err)
	require.Contains(t,
		[]string{"most specific macros for " + sampleCommonNet + " is ambiguous: " + macroOne + " or " + macroTwo,
			"most specific macros for " + sampleCommonNet + " is ambiguous: " + macroTwo + " or " + macroOne}, err.Error())
}

func TestGetProjectIDToMacro(t *testing.T) {
	mostSpecific := map[string]string{}
	require.Equal(t, map[string]string{}, GetProjectIDToMacro(mostSpecific))

	mostSpecific = nil
	require.Equal(t, map[string]string{}, GetProjectIDToMacro(mostSpecific))

	mostSpecific = map[string]string{
		sampleIPv6:         macroOne,
		sampleProject:      macroTwo,
		sampleCommonNet:    macroTwo,
		sampleHostOne:      macroThree,
		sampleProjectRange: macroFour,
	}
	require.Equal(t, map[string]string{
		"10b9936": macroTwo,
		"f800/23": macroFour,
	}, GetProjectIDToMacro(mostSpecific))
}

func BenchmarkGetMostSpecificMacros(b *testing.B) {
	b.StopTimer()

	defMapOfSet := mctests.ReadMapOfArraysToMapOfSets(mctests.FlatMacrosFilename)
	depMapOfSet := mctests.ReadMapOfArraysToMapOfSets(mctests.DependenciesFilename)

	// to fill out parser cache (which will usually be the case during server run)
	_, _ = GetMostSpecificMacros(defMapOfSet, depMapOfSet)

	b.StartTimer()
	for i := 0; i < b.N; i++ {
		_, _ = GetMostSpecificMacros(defMapOfSet, depMapOfSet)
	}
}
