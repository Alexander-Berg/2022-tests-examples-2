package expander

import (
	"context"
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/go/macro"
	"a.yandex-team.ru/noc/macros/pkg/macros/marshaller"
	"a.yandex-team.ru/noc/macros/pkg/macros/mctests"
	"a.yandex-team.ru/noc/macros/pkg/macros/mcutils"
)

// do all tests in cycle so that we don't depend on map traversing order
const iterNum = 100

func TestExpandCorrect(t *testing.T) {
	definitions := map[string][]string{
		"_1_":       {"_1_A_", "2a02:5180::1509:185:71:76:17", "_1_B_"},
		"_1_A_":     {"_1_B_B_B_", "192.0.2.1/12"},
		"_1_B_":     {"4b14@2a02:6b8:c00::/40", "_1_B_A_", "exa!mple.net", "_1_B_B_"},
		"_1_B_A_":   {"2a02:06b8:0c00:0000:0000:0000:0000:0000/40"},
		"_1_B_B_":   {"_1_B_B_A_", "_1_B_B_B_", "_1_B_B_C_", "_1_B_B_D_"},
		"_1_B_B_A_": {"_1_A_"},
		"_1_B_B_B_": {"hyperion-db01h.market.yandex.net", "example.net"},
		"_1_B_B_C_": {"10b9936/24@2a02:6b8:fc00::/40", "::ffff:192.0.2.1/80"},
		"_1_B_B_D_": {"::ffff:192.0.2.1/80", "hyperion-db01h.market.yandex.net", "_1_B_A_"},
		"_2_":       {"_2_A_", "_2_B_"},
		"_2_A_":     {"_1_B_", "mk8s-master-catcfrjupce9sq1np9fp.ycp.cloud.yandex.net"},
		"_2_B_":     {"_1_B_B_D_", "10b9936@2a02:6b8:c00::/40"},
		"_3_":       {"_3_A_"},
		"_3_A_":     {"2a02:6b8:c00::/40"},
	}

	dependenciesMap := map[string]map[string]struct{}{
		"_1_": {
			"_1_A_":     {},
			"_1_B_":     {},
			"_1_B_A_":   {},
			"_1_B_B_":   {},
			"_1_B_B_A_": {},
			"_1_B_B_B_": {},
			"_1_B_B_C_": {},
			"_1_B_B_D_": {},
		},
		"_1_A_": {
			"_1_B_B_B_": {},
		},
		"_1_B_": {
			"_1_A_":     {},
			"_1_B_A_":   {},
			"_1_B_B_":   {},
			"_1_B_B_A_": {},
			"_1_B_B_B_": {},
			"_1_B_B_C_": {},
			"_1_B_B_D_": {},
		},
		"_1_B_A_": {},
		"_1_B_B_": {
			"_1_A_":     {},
			"_1_B_A_":   {},
			"_1_B_B_A_": {},
			"_1_B_B_B_": {},
			"_1_B_B_C_": {},
			"_1_B_B_D_": {},
		},
		"_1_B_B_A_": {
			"_1_A_":     {},
			"_1_B_B_B_": {},
		},
		"_1_B_B_B_": {},
		"_1_B_B_C_": {},
		"_1_B_B_D_": {
			"_1_B_A_": {},
		},
		"_2_": {
			"_2_A_":     {},
			"_2_B_":     {},
			"_1_A_":     {},
			"_1_B_":     {},
			"_1_B_A_":   {},
			"_1_B_B_":   {},
			"_1_B_B_A_": {},
			"_1_B_B_B_": {},
			"_1_B_B_C_": {},
			"_1_B_B_D_": {},
		},
		"_2_A_": {
			"_1_A_":     {},
			"_1_B_":     {},
			"_1_B_A_":   {},
			"_1_B_B_":   {},
			"_1_B_B_A_": {},
			"_1_B_B_B_": {},
			"_1_B_B_C_": {},
			"_1_B_B_D_": {},
		},
		"_2_B_": {
			"_1_B_B_D_": {},
			"_1_B_A_":   {},
		},
		"_3_": {
			"_3_A_": {},
		},
		"_3_A_": {},
	}

	expandedMap := map[string]map[string]struct{}{
		"_1_": {
			"2a02:5180::1509:185:71:76:17":               {},
			"4b14@2a02:6b8:c00::/40":                     {},
			"exa!mple.net":                               {},
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40": {},
			"192.0.2.1/12":                               {},
			"example.net":                                {},
			"10b9936/24@2a02:6b8:fc00::/40":              {},
			"::ffff:192.0.2.1/80":                        {},
			"hyperion-db01h.market.yandex.net":           {},
		},
		"_1_A_": {
			"192.0.2.1/12":                     {},
			"hyperion-db01h.market.yandex.net": {},
			"example.net":                      {},
		},
		"_1_B_": {
			"4b14@2a02:6b8:c00::/40":                     {},
			"exa!mple.net":                               {},
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40": {},
			"192.0.2.1/12":                               {},
			"example.net":                                {},
			"10b9936/24@2a02:6b8:fc00::/40":              {},
			"::ffff:192.0.2.1/80":                        {},
			"hyperion-db01h.market.yandex.net":           {},
		},
		"_1_B_A_": {
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40": {},
		},
		"_1_B_B_": {
			"192.0.2.1/12":                               {},
			"example.net":                                {},
			"10b9936/24@2a02:6b8:fc00::/40":              {},
			"::ffff:192.0.2.1/80":                        {},
			"hyperion-db01h.market.yandex.net":           {},
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40": {},
		},
		"_1_B_B_A_": {
			"192.0.2.1/12":                     {},
			"hyperion-db01h.market.yandex.net": {},
			"example.net":                      {},
		},
		"_1_B_B_B_": {
			"hyperion-db01h.market.yandex.net": {},
			"example.net":                      {},
		},
		"_1_B_B_C_": {
			"10b9936/24@2a02:6b8:fc00::/40": {},
			"::ffff:192.0.2.1/80":           {},
		},
		"_1_B_B_D_": {
			"::ffff:192.0.2.1/80":                        {},
			"hyperion-db01h.market.yandex.net":           {},
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40": {},
		},
		"_2_": {
			"mk8s-master-catcfrjupce9sq1np9fp.ycp.cloud.yandex.net": {},
			"4b14@2a02:6b8:c00::/40":                                {},
			"exa!mple.net":                                          {},
			"192.0.2.1/12":                                          {},
			"example.net":                                           {},
			"10b9936/24@2a02:6b8:fc00::/40":                         {},
			"10b9936@2a02:6b8:c00::/40":                             {},
			"::ffff:192.0.2.1/80":                                   {},
			"hyperion-db01h.market.yandex.net":                      {},
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40":            {},
		},
		"_2_A_": {
			"mk8s-master-catcfrjupce9sq1np9fp.ycp.cloud.yandex.net": {},
			"4b14@2a02:6b8:c00::/40":                                {},
			"exa!mple.net":                                          {},
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40":            {},
			"192.0.2.1/12":                                          {},
			"example.net":                                           {},
			"10b9936/24@2a02:6b8:fc00::/40":                         {},
			"::ffff:192.0.2.1/80":                                   {},
			"hyperion-db01h.market.yandex.net":                      {},
		},
		"_2_B_": {
			"10b9936@2a02:6b8:c00::/40":                  {},
			"::ffff:192.0.2.1/80":                        {},
			"hyperion-db01h.market.yandex.net":           {},
			"2a02:06b8:0c00:0000:0000:0000:0000:0000/40": {},
		},
		"_3_": {
			"2a02:6b8:c00::/40": {},
		},
		"_3_A_": {
			"2a02:6b8:c00::/40": {},
		},
	}

	for i := 0; i < iterNum; i++ {
		exp, deps, err := ExpandMacro("_1_", definitions)
		require.NoError(t, err)
		require.Equal(t, expandedMap["_1_"], exp)
		require.Equal(t, dependenciesMap["_1_"], deps)

		expMap, dependencies, err := ExpandAll(definitions)
		require.NoError(t, err)
		require.Equal(t, dependenciesMap, dependencies)
		require.Equal(t, expandedMap, expMap)
	}
}

func TestExpandInvalidItem(t *testing.T) {
	definitions := map[string][]string{
		"_1_":       {"_1_A_", "2a02:5180::1509:185:71:76:17", "_1_B_"},
		"_1_A_":     {"_1_B_B_B_", "192.0.2.1/12"},
		"_1_B_":     {"4b14@2a02:6b8:c00::/40", "_1_B_A_", "exa!mple.net", "_1_B_B_"},
		"_1_B_A_":   {"2a02:06b8:0c00:0000:0000:0000:0000:0000/40"},
		"_1_B_B_":   {"_1_B_B_A_", "_1_B_B_B_", "_1_B_B_C_", "_1_B_B_D_"},
		"_1_B_B_A_": {"_1_A_"},
		"_1_B_B_B_": {"hyperion-db01h.market.yandex.net", "example.net"},
		"_1_B_B_C_": {"10b9936/24@2a02:6b8:fc00::/40", "::ffff:192.0.2.1/80"},
		"_1_B_B_D_": {"::ffff:192.0.2.1/80", "hyperion-db01h.market.yandex.net", "_1_B_A_"},
		"_2_":       {"_2_A_", "_2_B_"},
		"_2_A_":     {"_1_B_", "mk8s-master-catcfrjupce9sq1np9fp.ycp.cloud.yandex.net"},
		"_2_B_":     {"_1_B_B_D_", "10b9936@2a02:6b8:c00::/40"},
		"_3_":       {"_3_A"},
		"_3_A":      {"2a02:6b8:c00::/40"},
	}

	for i := 0; i < iterNum; i++ {
		exp, deps, err := ExpandMacro("_3_", definitions)
		require.Nil(t, exp)
		require.Nil(t, deps)
		require.EqualError(t, err, "_3_A is not a valid macro")

		allM, allDeps, err := ExpandAll(definitions)
		require.Nil(t, allM)
		require.Nil(t, allDeps)
		require.Error(t, err)
		require.Contains(t, []string{
			"failed to expand all macros: " +
				"failed to expand macro _3_: " +
				"_3_A is not a valid macro",
			"failed to expand all macros: " +
				"failed to expand macro _3_A: " +
				"_3_A is not a valid macro",
		}, err.Error())
	}
}

func TestExpandUnknownMacro(t *testing.T) {
	definitions := map[string][]string{
		"_1_":       {"_1_A_", "2a02:5180::1509:185:71:76:17", "_1_B_"},
		"_1_A_":     {"_1_B_B_B_", "192.0.2.1/12"},
		"_1_B_":     {"4b14@2a02:6b8:c00::/40", "_1_B_A_", "exa!mple.net", "_1_B_B_"},
		"_1_B_A_":   {"2a02:06b8:0c00:0000:0000:0000:0000:0000/40"},
		"_1_B_B_":   {"_1_B_B_A_", "_1_B_B_B_", "_1_B_B_C_", "_1_B_B_D_"},
		"_1_B_B_A_": {"_1_A_"},
		"_1_B_B_B_": {"hyperion-db01h.market.yandex.net", "example.net"},
		"_1_B_B_C_": {"10b9936/24@2a02:6b8:fc00::/40", "::ffff:192.0.2.1/80"},
		"_1_B_B_D_": {"::ffff:192.0.2.1/80", "hyperion-db01h.market.yandex.net", "_1_B_A_"},
		"_2_":       {"_2_A_", "_2_B_"},
		"_2_A_":     {"_1_B_", "mk8s-master-catcfrjupce9sq1np9fp.ycp.cloud.yandex.net"},
		"_2_B_":     {"_1_B_B_D_", "10b9936@2a02:6b8:c00::/40"},
		"_3_":       {"_3_A_", "_3_C_"},
		"_3_A_":     {"2a02:6b8:c00::/40"},
	}

	for i := 0; i < iterNum; i++ {
		exp, deps, err := ExpandMacro("_3_", definitions)
		require.Nil(t, exp)
		require.Nil(t, deps)
		require.EqualError(t, err, "macro _3_C_ is not a key in macro definitions")

		allM, allDeps, err := ExpandAll(definitions)
		require.Nil(t, allM)
		require.Nil(t, allDeps)
		require.Error(t, err)
		require.Contains(t, []string{
			"failed to expand all macros: " +
				"failed to expand macro _3_: " +
				"macro _3_C_ is not a key in macro definitions",
			"failed to expand all macros: " +
				"failed to expand macro _3_C_: " +
				"macro _3_C_ is not a key in macro definitions",
		}, err.Error())
	}
}

func TestExpandCycle(t *testing.T) {
	definitions := map[string][]string{
		"_1_":       {"_1_A_", "2a02:5180::1509:185:71:76:17", "_1_B_"},
		"_1_A_":     {"_1_B_B_B_", "192.0.2.1/12"},
		"_1_B_":     {"4b14@2a02:6b8:c00::/40", "_1_B_A_", "exa!mple.net", "_1_B_B_"},
		"_1_B_A_":   {"2a02:06b8:0c00:0000:0000:0000:0000:0000/40"},
		"_1_B_B_":   {"_1_B_B_A_", "_1_B_B_B_", "_1_B_B_C_", "_1_B_B_D_"},
		"_1_B_B_A_": {"_1_A_"},
		"_1_B_B_B_": {"hyperion-db01h.market.yandex.net", "example.net"},
		"_1_B_B_C_": {"10b9936/24@2a02:6b8:fc00::/40", "::ffff:192.0.2.1/80"},
		"_1_B_B_D_": {"::ffff:192.0.2.1/80", "hyperion-db01h.market.yandex.net", "_1_B_A_"},
		"_2_":       {"_2_A_", "_2_B_"},
		"_2_A_":     {"_1_B_", "mk8s-master-catcfrjupce9sq1np9fp.ycp.cloud.yandex.net"},
		"_2_B_":     {"_1_B_B_D_", "10b9936@2a02:6b8:c00::/40"},
		"_3_":       {"_3_A_"},
		"_3_A_":     {"2a02:6b8:c00::/40", "_3_"},
	}

	for i := 0; i < iterNum; i++ {
		exp, deps, err := ExpandMacro("_3_", definitions)
		require.Nil(t, exp)
		require.Nil(t, deps)
		require.EqualError(t, err, "a cycle with macro _3_ has occurred")

		allM, allDeps, err := ExpandAll(definitions)
		require.Nil(t, allM)
		require.Nil(t, allDeps)
		require.Error(t, err)
		require.Contains(t, []string{
			"failed to expand all macros: " +
				"failed to expand macro _3_: " +
				"a cycle with macro _3_ has occurred",
			"failed to expand all macros: " +
				"failed to expand macro _3_A_: " +
				"a cycle with macro _3_A_ has occurred",
		}, err.Error())
	}
}

func TestExpandPersistence(t *testing.T) {
	dir := mctests.GetSrcDir()

	ctx := context.Background()

	t.Setenv("PATH", fmt.Sprintf("%s:%s", dir+"/m4-mac", dir+"/m4-linux"))

	origMacros, err := macro.ExpandMacrosInc(ctx, dir+"/macros-inc-test.m4",
		macro.WithTrypoSupport(), macro.WithTrypoRangeSupport(), macro.WithFastBone())
	require.NoError(t, err)

	oldMacros, _, err := ExpandAll(origMacros)
	require.NoError(t, err)

	err = marshaller.Export(marshaller.MarshalM4(mcutils.MakeAllArrFromAllSet(oldMacros)), dir+"/macros-inc-new.m4")
	require.NoError(t, err)

	macros, err := macro.ExpandMacrosInc(ctx, dir+"/macros-inc-new.m4",
		macro.WithTrypoSupport(), macro.WithTrypoRangeSupport(), macro.WithFastBone())
	require.NoError(t, err)

	newMacros, _, err := ExpandAll(macros)
	require.NoError(t, err)

	for macr, exp := range oldMacros {
		require.Equal(t, exp, newMacros[macr])
	}
}

func benchmarkExpandMacros(b *testing.B, filename string) {
	b.Helper()
	b.StopTimer()

	defMapOfArr := mctests.ReadMapOfArrays(filename)

	// to fill out parser cache (which will usually be the case during server run)
	_, _, _ = ExpandAll(defMapOfArr)

	b.StartTimer()
	for i := 0; i < b.N; i++ {
		_, _, _ = ExpandAll(defMapOfArr)
	}
}

func BenchmarkExpandMacroFlat(b *testing.B) {
	benchmarkExpandMacros(b, mctests.FlatMacrosFilename)
}

func BenchmarkExpandMacroOrig(b *testing.B) {
	benchmarkExpandMacros(b, mctests.OriginalMacrosFilename)
}
