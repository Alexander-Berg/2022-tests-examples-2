package readers

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
)

func TestFieldParsers(t *testing.T) {
	testCases := []struct {
		name      string
		parser    FieldParser
		goodCases map[string]interface{}
		badCases  common.StringSet
	}{
		{
			name:   "string parser",
			parser: NewStringParser(),
			goodCases: map[string]interface{}{
				`"abc"`:    "abc",
				`"cbacba"`: "cbacba",
			},
			badCases: common.NewStringSet("asd"),
		},
		{
			name:   "float64 parser",
			parser: NewFloat64Parser(),
			goodCases: map[string]interface{}{
				`1.0`:  float64(1.0),
				`-5.6`: float64(-5.6),
			},
			badCases: common.NewStringSet("asd"),
		},
		{
			name:   "color parser",
			parser: NewColorParser(),
			goodCases: map[string]interface{}{
				`"#ffddaacc"`: &Color{raw: "#ffddaacc"},
				`"#abc"`:      &Color{raw: "#abc"},
			},
			badCases: common.NewStringSet(`asd`, `"aaffdd"`, `"#"`, `"#ffddaaccbb"`),
		},
	}
	for _, testCase := range testCases {
		testCase.badCases.Add("")
		t.Run(testCase.name, func(t *testing.T) {
			for have, expect := range testCase.goodCases {
				t.Run(fmt.Sprintf("`%s` -> `%v`", have, expect), func(t *testing.T) {
					got, err := testCase.parser.ParseJSON([]byte(have))
					require.NoError(t, err)
					assert.Equal(t, expect, got)
				})
			}
			for _, have := range testCase.badCases.AsSlice() {
				t.Run(fmt.Sprintf("`%s` -> ø", have), func(t *testing.T) {
					_, err := testCase.parser.ParseJSON([]byte(have))
					require.Error(t, err)
				})
			}
		})
	}
}
