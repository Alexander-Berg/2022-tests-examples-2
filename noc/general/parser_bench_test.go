package parser

import (
	"testing"

	"a.yandex-team.ru/noc/macros/pkg/macros/mctests"
)

func benchmarkParseAll(b *testing.B, parserInstance *Parser) {
	b.Helper()
	b.StopTimer()

	defMapOfArr := mctests.ReadMapOfArrays(mctests.FlatMacrosFilename)

	parseAllIteration := func() {
		for _, exp := range defMapOfArr {
			for _, elem := range exp {
				_ = parserInstance.GetMacroItemType(elem)
			}
		}
	}

	// to fill cache if such is present
	parseAllIteration()

	b.StartTimer()
	for i := 0; i < b.N; i++ {
		parseAllIteration()
	}
}

func BenchmarkNoCacheParseAll(b *testing.B) {
	benchmarkParseAll(b, WithoutCache)
}

func BenchmarkCacheParseAll(b *testing.B) {
	benchmarkParseAll(b, WithCache)
}
