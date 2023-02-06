package conditions

import (
	"fmt"
	"math/rand"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/devices"
)

func TestParseCondition(t *testing.T) {
	testCases := []struct {
		expression string
		expected   Expression
		caseName   string
		valid      bool
	}{
		{
			expression: "cgi.app_version >= 21020300 && cgi.app_id eq 'ru.yandex.searchplugin'",
			expected: logicalExpression{
				left: numberComparisonExpression{
					field:               "cgi.app_version",
					comparisonOperation: comparisonGreaterOrEqual,
					value:               21020300,
				},
				logicalOperation: logicalAnd,
				right: stringComparisonExpression{
					field:               "cgi.app_id",
					comparisonOperation: comparisonEqual,
					value:               "ru.yandex.searchplugin",
				},
			},
			caseName: "from production",
			valid:    true,
		},
		{
			expression: "cgi.app_version >= 73000000 && cgi.app_id eq 'ru.yandex.mobile'  && !(cgi.pzdCoin eq 0) && !(cgi.pzdCoin eq 1)",
			expected: logicalExpression{
				left: logicalExpression{
					left: logicalExpression{
						left: numberComparisonExpression{
							field:               "cgi.app_version",
							comparisonOperation: comparisonGreaterOrEqual,
							value:               73000000,
						},
						logicalOperation: logicalAnd,
						right: stringComparisonExpression{
							field:               "cgi.app_id",
							comparisonOperation: comparisonEqual,
							value:               "ru.yandex.mobile",
						},
					},
					logicalOperation: logicalAnd,
					right: negationLogicalExpression{
						Expression: stringComparisonExpression{
							field:               "cgi.pzdCoin",
							comparisonOperation: comparisonEqual,
							value:               "0",
						},
					},
				},
				logicalOperation: logicalAnd,
				right: negationLogicalExpression{
					Expression: stringComparisonExpression{
						field:               "cgi.pzdCoin",
						comparisonOperation: comparisonEqual,
						value:               "1",
					},
				},
			},
			caseName: "another from production HOME-72136",
			valid:    true,
		},
		{
			expression: "version == 42 || version == 45 || version == 48",
			expected: logicalExpression{
				left: logicalExpression{
					left: numberComparisonExpression{
						field:               "version",
						comparisonOperation: comparisonEqual,
						value:               42,
					},
					logicalOperation: logicalOr,
					right: numberComparisonExpression{
						field:               "version",
						comparisonOperation: comparisonEqual,
						value:               45,
					},
				},
				logicalOperation: logicalOr,
				right: numberComparisonExpression{
					field:               "version",
					comparisonOperation: comparisonEqual,
					value:               48,
				},
			},
			caseName: "several boolean operands",
			valid:    true,
		},
		{
			expression: "version == \"1.2.3\"",
			expected: versionComparisonExpression{
				field:               "version",
				comparisonOperation: comparisonEqual,
				value:               devices.NewVersion("1.2.3"),
			},
			caseName: "version comparsion using numeric comparsion operator and quoted version",
			valid:    true,
		},
		{
			expression: "version == \"123\"",
			expected: numberComparisonExpression{
				field:               "version",
				comparisonOperation: comparisonEqual,
				value:               123,
			},
			caseName: "number comparsion using numeric comparsion operator and quoted number",
			valid:    true,
		},
		{
			expression: "a == 3 || b == 5 && c == 7",
			expected: logicalExpression{
				left: numberComparisonExpression{
					field:               "a",
					comparisonOperation: comparisonEqual,
					value:               3,
				},
				logicalOperation: logicalOr,
				right: logicalExpression{
					left: numberComparisonExpression{
						field:               "b",
						comparisonOperation: comparisonEqual,
						value:               5,
					},
					logicalOperation: logicalAnd,
					right: numberComparisonExpression{
						field:               "c",
						comparisonOperation: comparisonEqual,
						value:               7,
					},
				},
			},
			caseName: "logical operations priority",
			valid:    true,
		},
		{
			expression: "(a == 3 || a == 5) && (b == 7 || b == 9)",
			expected: logicalExpression{
				left: logicalExpression{
					left: numberComparisonExpression{
						field:               "a",
						value:               3,
						comparisonOperation: comparisonEqual,
					},
					right: numberComparisonExpression{
						field:               "a",
						value:               5,
						comparisonOperation: comparisonEqual,
					},
					logicalOperation: logicalOr,
				},
				right: logicalExpression{
					left: numberComparisonExpression{
						field:               "b",
						value:               7,
						comparisonOperation: comparisonEqual,
					},
					right: numberComparisonExpression{
						field:               "b",
						value:               9,
						comparisonOperation: comparisonEqual,
					},
					logicalOperation: logicalOr,
				},
				logicalOperation: logicalAnd,
			},
			caseName: "parenthesis",
			valid:    true,
		},
		{
			expression: "(((field == 42)))",
			expected: numberComparisonExpression{
				field:               "field",
				comparisonOperation: comparisonEqual,
				value:               42,
			},
			caseName: "nested parenthesis",
			valid:    true,
		},
		{
			expression: "!apple",
			expected: negationLogicalExpression{
				Expression: fieldCheckExpression{
					field: "apple",
				},
			},
			caseName: "field negation",
			valid:    true,
		},
		{
			expression: "field eq 42",
			expected: stringComparisonExpression{
				field:               "field",
				comparisonOperation: comparisonEqual,
				value:               "42",
			},
			caseName: "number in string expression",
			valid:    true,
		},
		{
			expression: "field < '42'",
			expected: numberComparisonExpression{
				field:               "field",
				comparisonOperation: comparisonLess,
				value:               42,
			},
			caseName: "string in number expression",
			valid:    true,
		},
		{
			expression: "!(a == 42)",
			expected: negationLogicalExpression{
				Expression: numberComparisonExpression{
					field:               "a",
					comparisonOperation: comparisonEqual,
					value:               42,
				},
			},
			caseName: "number expression negation",
			valid:    true,
		},
		{
			expression: "!(b eq 'value')",
			expected: negationLogicalExpression{
				Expression: stringComparisonExpression{
					field:               "b",
					comparisonOperation: comparisonEqual,
					value:               "value",
				},
			},
			caseName: "string expression negation",
			valid:    true,
		},
		{
			expression: "!(a == 42 && b eq 'value')",
			expected: negationLogicalExpression{
				Expression: logicalExpression{
					left: numberComparisonExpression{
						field:               "a",
						comparisonOperation: comparisonEqual,
						value:               42,
					},
					logicalOperation: logicalAnd,
					right: stringComparisonExpression{
						field:               "b",
						comparisonOperation: comparisonEqual,
						value:               "value",
					},
				},
			},
			caseName: "expression negation 2",
			valid:    true,
		},
		{
			expression: "field1 || field2 eq 'value'",
			expected: logicalExpression{
				left: fieldCheckExpression{
					field: "field1",
				},
				logicalOperation: logicalOr,
				right: stringComparisonExpression{
					field:               "field2",
					comparisonOperation: comparisonEqual,
					value:               "value",
				},
			},
			caseName: "field check expression",
			valid:    true,
		},
		{
			expression: "f1 eq 'single_quoted_value'",
			expected: stringComparisonExpression{
				field:               "f1",
				comparisonOperation: comparisonEqual,
				value:               "single_quoted_value",
			},
			caseName: "single quoted value",
			valid:    true,
		},
		{
			expression: "f1 eq \"double_quoted_value\"",
			expected: stringComparisonExpression{
				field:               "f1",
				comparisonOperation: comparisonEqual,
				value:               "double_quoted_value",
			},
			caseName: "double quoted value",
			valid:    true,
		},
		{
			expression: "   field!=42   ",
			expected: numberComparisonExpression{
				field:               "field",
				comparisonOperation: comparisonNotEqual,
				value:               42,
			},
			caseName: "trailing whitespace",
			valid:    true,
		},
		{
			expression: "content:big || tld:all-com.tr",
			expected: logicalExpression{
				left: stringComparisonExpression{
					field:               "content",
					comparisonOperation: comparisonEqual,
					value:               "big",
				},
				logicalOperation: logicalOr,
				right: stringComparisonExpression{
					field:               "tld",
					comparisonOperation: comparisonEqual,
					value:               "all-com.tr",
				},
			},
			caseName: "variable with colon",
			valid:    true,
		},
		{
			expression: "((device.OSName) eq ('Windows XP'))",
			expected: stringComparisonExpression{
				field:               "device.OSName",
				comparisonOperation: comparisonEqual,
				value:               "Windows XP",
			},
			caseName: "encased ids and strings",
			valid:    true,
		},
		{
			expression: "0",
			expected: numberCheckExpression{
				number: 0,
			},
			caseName: "number as expression",
			valid:    true,
		},
		{
			expression: "abc >= 0.0.1",
			expected: versionComparisonExpression{
				field:               "abc",
				comparisonOperation: comparisonGreaterOrEqual,
				value:               devices.Version{0, 0, 1},
			},
			valid: true,
		},
		{
			expression: "",
			expected:   nil,
			caseName:   "empty string",
			valid:      true,
		},
		{
			expression: "    ",
			expected:   nil,
			caseName:   "whitespace string",
			valid:      true,
		},
		{
			expression: "1abc eq 'value'",
			caseName:   "invalid identifier",
		},
		{
			expression: "(a == 42 && b == 15",
			caseName:   "unbalanced parenthesis",
		},
		{
			expression: "a = 42",
			caseName:   "invalid operator",
		},
		{
			expression: `cgi.app_version > 21110700 &&  cgi.app_id eq \u2018ru.yandex.searchplugin.beta\u2019`,
			caseName:   "strange quotes",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			actual, err := parseCondition(testCase.expression)
			if testCase.valid {
				assert.NoError(t, err)
				assert.Equal(t, testCase.expected, actual)
			} else {
				assert.Error(t, err)
				assert.Nil(t, actual)
			}
		})
	}
}

func TestEvaluateStringComparisonEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal string",
			data:     inputContextData{"fruit": "apple"},
			expected: true,
		},
		{
			caseName: "not equal string",
			data:     inputContextData{"fruit": "banana"},
			expected: false,
		},
		{
			caseName: "not equal number",
			data:     inputContextData{"fruit": "42"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"vegetable": "cucumber"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "fruit",
		comparisonOperation: comparisonEqual,
		value:               "apple",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringComparisonNotEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"fruit": "apple"},
			expected: false,
		},
		{
			caseName: "not equal string",
			data:     inputContextData{"fruit": "banana"},
			expected: true,
		},
		{
			caseName: "not equal number",
			data:     inputContextData{"fruit": "42"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"vegetable": "cucumber"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "fruit",
		comparisonOperation: comparisonNotEqual,
		value:               "apple",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringComparisonLess(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"fruit": "aaaapple"},
			expected: true,
		},
		{
			caseName: "equal",
			data:     inputContextData{"fruit": "apple"},
			expected: false,
		},
		{
			caseName: "greater",
			data:     inputContextData{"fruit": "banana"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"vegetable": "cucumber"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "fruit",
		comparisonOperation: comparisonLess,
		value:               "apple",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringComparisonGreater(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"fruit": "aaaapple"},
			expected: false,
		},
		{
			caseName: "equal",
			data:     inputContextData{"fruit": "apple"},
			expected: false,
		},
		{
			caseName: "greater",
			data:     inputContextData{"fruit": "banana"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"vegetable": "cucumber"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "fruit",
		comparisonOperation: comparisonGreater,
		value:               "apple",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringComparisonLessOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"fruit": "aaaapple"},
			expected: true,
		},
		{
			caseName: "equal",
			data:     inputContextData{"fruit": "apple"},
			expected: true,
		},
		{
			caseName: "greater",
			data:     inputContextData{"fruit": "banana"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"vegetable": "cucumber"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "fruit",
		comparisonOperation: comparisonLessOrEqual,
		value:               "apple",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringComparisonGreaterOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"fruit": "aaaapple"},
			expected: false,
		},
		{
			caseName: "equal",
			data:     inputContextData{"fruit": "apple"},
			expected: true,
		},
		{
			caseName: "greater",
			data:     inputContextData{"fruit": "banana"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"vegetable": "cucumber"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "fruit",
		comparisonOperation: comparisonGreaterOrEqual,
		value:               "apple",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringVersionComparisonEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal a.b",
			data:     inputContextData{"field": "1.42"},
			expected: true,
		},
		{
			caseName: "not equal a.b",
			data:     inputContextData{"field": "1.43"},
			expected: false,
		},
		{
			caseName: "equal a.b.0",
			data:     inputContextData{"field": "1.42.0"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1.42"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonEqual,
		value:               "1.42",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestStringVersionComparisonNotEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "not equal a",
			data:     inputContextData{"field": "1"},
			expected: true,
		},
		{
			caseName: "not equal a.b",
			data:     inputContextData{"field": "1.43"},
			expected: true,
		},
		{
			caseName: "equal a.b",
			data:     inputContextData{"field": "1.42"},
			expected: false,
		},
		{
			caseName: "equal a.b.0",
			data:     inputContextData{"field": "1.42.0"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonNotEqual,
		value:               "1.42",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringVersionComparisonLess(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "1.41"},
			expected: true,
		},
		{
			caseName: "equal a.b",
			data:     inputContextData{"field": "1.420"},
			expected: false,
		},
		{
			caseName: "greater a.b",
			data:     inputContextData{"field": "11.41"},
			expected: false,
		},
		{
			caseName: "less 0a.b",
			data:     inputContextData{"field": "01.41"},
			expected: true,
		},
		{
			caseName: "equal a.b",
			data:     inputContextData{"field": "1.42"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonLess,
		value:               "1.42",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringVersionComparisonGreater(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "1.41"},
			expected: false,
		},
		{
			caseName: "equal a.b",
			data:     inputContextData{"field": "1.42"},
			expected: false,
		},
		{
			caseName: "greater a.b",
			data:     inputContextData{"field": "1.420"},
			expected: true,
		},
		{
			caseName: "greater a.b",
			data:     inputContextData{"field": "11.41"},
			expected: true,
		},
		{
			caseName: "less 0a.b",
			data:     inputContextData{"field": "01.41"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonGreater,
		value:               "1.42",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringVersionComparisonLessOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: true,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: true,
		},
		{
			caseName: "less a",
			data:     inputContextData{"field": "41"},
			expected: true,
		},
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "41.1"},
			expected: true,
		},
		{
			caseName: "less a.b.c.d",
			data:     inputContextData{"field": "4.3.2.1"},
			expected: true,
		},
		{
			caseName: "greater a",
			data:     inputContextData{"field": "43"},
			expected: false,
		},
		{
			caseName: "greater a.b.c",
			data:     inputContextData{"field": "45.1.3"},
			expected: false,
		},
		{
			caseName: "greater a.0.0",
			data:     inputContextData{"field": "143.0.0"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonLessOrEqual,
		value:               "42",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateStringVersionComparisonGreaterOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: true,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: true,
		},

		{
			caseName: "less a.b",
			data:     inputContextData{"field": "41.1"},
			expected: false,
		},
		{
			caseName: "less a.b.c.d",
			data:     inputContextData{"field": "4.3.2.1"},
			expected: false,
		},
		{
			caseName: "greater a",
			data:     inputContextData{"field": "43"},
			expected: true,
		},
		{
			caseName: "greater a.b.c",
			data:     inputContextData{"field": "45.1.3"},
			expected: true,
		},
		{
			caseName: "greater a.0.0",
			data:     inputContextData{"field": "143.0.0"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := stringComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonGreaterOrEqual,
		value:               "42",
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestNumberComparisonEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"answer": "41"},
			expected: false,
		},
		{
			caseName: "equal",
			data:     inputContextData{"answer": "42"},
			expected: true,
		},
		{
			caseName: "greater",
			data:     inputContextData{"answer": "43"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"magic_number": "15111992"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "answer",
		comparisonOperation: comparisonEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestNumberComparisonNotEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"answer": "41"},
			expected: true,
		},
		{
			caseName: "equal",
			data:     inputContextData{"answer": "42"},
			expected: false,
		},
		{
			caseName: "greater",
			data:     inputContextData{"answer": "43"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"magic_number": "15111992"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "answer",
		comparisonOperation: comparisonNotEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestNumberComparisonLess(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"answer": "41"},
			expected: true,
		},
		{
			caseName: "equal",
			data:     inputContextData{"answer": "42"},
			expected: false,
		},
		{
			caseName: "greater",
			data:     inputContextData{"answer": "43"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"magic_number": "15111992"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "answer",
		comparisonOperation: comparisonLess,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestNumberComparisonGreater(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"answer": "41"},
			expected: false,
		},
		{
			caseName: "equal",
			data:     inputContextData{"answer": "42"},
			expected: false,
		},
		{
			caseName: "greater",
			data:     inputContextData{"answer": "43"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"magic_number": "15111992"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "answer",
		comparisonOperation: comparisonGreater,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestNumberComparisonLessOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"answer": "41"},
			expected: true,
		},
		{
			caseName: "equal",
			data:     inputContextData{"answer": "42"},
			expected: true,
		},
		{
			caseName: "greater",
			data:     inputContextData{"answer": "43"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"magic_number": "15111992"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "answer",
		comparisonOperation: comparisonLessOrEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestNumberComparisonGreaterOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "less",
			data:     inputContextData{"answer": "41"},
			expected: false,
		},
		{
			caseName: "equal",
			data:     inputContextData{"answer": "42"},
			expected: true,
		},
		{
			caseName: "greater",
			data:     inputContextData{"answer": "43"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"magic_number": "15111992"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "answer",
		comparisonOperation: comparisonGreaterOrEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateNumberVersionComparisonEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: true,
		},
		{
			caseName: "equal a.0",
			data:     inputContextData{"field": "42.0"},
			expected: true,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: true,
		},
		{
			caseName: "less a",
			data:     inputContextData{"field": "41"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateNumberVersionComparisonNotEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: false,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: false,
		},
		{
			caseName: "less a",
			data:     inputContextData{"field": "41"},
			expected: true,
		},
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "41.1"},
			expected: true,
		},
		{
			caseName: "less a.b.c.d",
			data:     inputContextData{"field": "4.3.2.1"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonNotEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateNumberVersionComparisonLess(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: false,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: false,
		},
		{
			caseName: "less a",
			data:     inputContextData{"field": "41"},
			expected: true,
		},
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "41.1"},
			expected: true,
		},
		{
			caseName: "less a.b.c.d",
			data:     inputContextData{"field": "4.3.2.1"},
			expected: true,
		},
		{
			caseName: "greater a",
			data:     inputContextData{"field": "43"},
			expected: false,
		},
		{
			caseName: "greater a.b.c",
			data:     inputContextData{"field": "43.1.3"},
			expected: false,
		},
		{
			caseName: "greater a.0.0",
			data:     inputContextData{"field": "143.0.0"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonLess,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateNumberVersionComparisonGreater(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: false,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: false,
		},
		{
			caseName: "less a",
			data:     inputContextData{"field": "41"},
			expected: false,
		},
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "41.1"},
			expected: false,
		},
		{
			caseName: "less a.b.c.d",
			data:     inputContextData{"field": "4.3.2.1"},
			expected: false,
		},
		{
			caseName: "greater a",
			data:     inputContextData{"field": "43"},
			expected: true,
		},
		{
			caseName: "greater a.b.c",
			data:     inputContextData{"field": "43.1.3"},
			expected: true,
		},
		{
			caseName: "greater a.0.0",
			data:     inputContextData{"field": "143.0.0"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonGreater,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateNumberVersionComparisonLessOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: true,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: true,
		},
		{
			caseName: "less a",
			data:     inputContextData{"field": "41"},
			expected: true,
		},
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "41.1"},
			expected: true,
		},
		{
			caseName: "less a.b.c.d",
			data:     inputContextData{"field": "4.3.2.1"},
			expected: true,
		},
		{
			caseName: "greater a",
			data:     inputContextData{"field": "43"},
			expected: false,
		},
		{
			caseName: "greater a.b.c",
			data:     inputContextData{"field": "43.1.3"},
			expected: false,
		},
		{
			caseName: "greater a.0.0",
			data:     inputContextData{"field": "143.0.0"},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonLessOrEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateNumberVersionComparisonGreaterOrEqual(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal",
			data:     inputContextData{"field": "42"},
			expected: true,
		},
		{
			caseName: "equal a.0.0.0",
			data:     inputContextData{"field": "42.0.0.0"},
			expected: true,
		},
		{
			caseName: "less a",
			data:     inputContextData{"field": "41"},
			expected: false,
		},
		{
			caseName: "less a.b",
			data:     inputContextData{"field": "41.1"},
			expected: false,
		},
		{
			caseName: "less a.b.c.d",
			data:     inputContextData{"field": "4.3.2.1"},
			expected: false,
		},
		{
			caseName: "greater a",
			data:     inputContextData{"field": "43"},
			expected: true,
		},
		{
			caseName: "greater a.b.c",
			data:     inputContextData{"field": "43.1.3"},
			expected: true,
		},
		{
			caseName: "greater a.0.0",
			data:     inputContextData{"field": "143.0.0"},
			expected: true,
		},
		{
			caseName: "no key",
			data:     inputContextData{"another_field": "1"},
			expected: false,
		},
	}

	tree := numberComparisonExpression{
		field:               "field",
		comparisonOperation: comparisonGreaterOrEqual,
		value:               42,
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateFieldCheck(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "number 1",
			data:     inputContextData{"isTouch": "1"},
			expected: true,
		},
		{
			caseName: "string yes",
			data:     inputContextData{"isTouch": "yes"},
			expected: true,
		},
		{
			caseName: "number 0",
			data:     inputContextData{"isTouch": "0"},
			expected: false,
		},
		{
			caseName: "empty string",
			data:     inputContextData{"isTouch": ""},
			expected: false,
		},
		{
			caseName: "no key",
			data:     inputContextData{"isDesktop": "yes"},
			expected: false,
		},
	}

	tree := fieldCheckExpression{field: "isTouch"}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateLogicalOperationAnd(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal string and equal number",
			data:     inputContextData{"fruit": "apple", "answer": "42"},
			expected: true,
		},
		{
			caseName: "not equal string and equal number",
			data:     inputContextData{"fruit": "banana", "answer": "42"},
			expected: false,
		},
		{
			caseName: "equal string and not equal number",
			data:     inputContextData{"fruit": "apple", "answer": "99"},
			expected: false,
		},
		{
			caseName: "not equal string and not equal number",
			data:     inputContextData{"fruit": "banana", "answer": "99"},
			expected: false,
		},
		{
			caseName: "equal string and no key number",
			data:     inputContextData{"fruit": "apple", "somevalue": "42"},
			expected: false,
		},
		{
			caseName: "no key string and equal number",
			data:     inputContextData{"vegetable": "tomato", "answer": "42"},
			expected: false,
		},
	}

	tree := logicalExpression{
		left: stringComparisonExpression{
			field:               "fruit",
			comparisonOperation: comparisonEqual,
			value:               "apple",
		},
		logicalOperation: logicalAnd,
		right: numberComparisonExpression{
			field:               "answer",
			comparisonOperation: comparisonEqual,
			value:               42,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateLogicalOperationOr(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal string and equal number",
			data:     inputContextData{"fruit": "apple", "answer": "42"},
			expected: true,
		},
		{
			caseName: "not equal string and equal number",
			data:     inputContextData{"fruit": "banana", "answer": "42"},
			expected: true,
		},
		{
			caseName: "equal string and not equal number",
			data:     inputContextData{"fruit": "apple", "answer": "99"},
			expected: true,
		},
		{
			caseName: "not equal string and not equal number",
			data:     inputContextData{"fruit": "banana", "answer": "99"},
			expected: false,
		},
		{
			caseName: "equal string and no key number",
			data:     inputContextData{"fruit": "apple", "somevalue": "42"},
			expected: true,
		},
		{
			caseName: "no key string and equal number",
			data:     inputContextData{"vegetable": "tomato", "answer": "42"},
			expected: true,
		},
		{
			caseName: "no key string and no key number",
			data:     inputContextData{"vegetable": "tomato", "somevalue": "42"},
			expected: false,
		},
	}

	tree := logicalExpression{
		left: stringComparisonExpression{
			field:               "fruit",
			comparisonOperation: comparisonEqual,
			value:               "apple",
		},
		logicalOperation: logicalOr,
		right: numberComparisonExpression{
			field:               "answer",
			comparisonOperation: comparisonEqual,
			value:               42,
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func TestEvaluateLogicalOperationNot(t *testing.T) {
	testCases := []struct {
		caseName string
		data     inputContextData
		expected bool
	}{
		{
			caseName: "equal string and equal number",
			data:     inputContextData{"fruit": "apple", "answer": "42"},
			expected: false,
		},
		{
			caseName: "not equal string and equal number",
			data:     inputContextData{"fruit": "banana", "answer": "42"},
			expected: false,
		},
		{
			caseName: "equal string and not equal number",
			data:     inputContextData{"fruit": "apple", "answer": "99"},
			expected: false,
		},
		{
			caseName: "not equal string and not equal number",
			data:     inputContextData{"fruit": "banana", "answer": "99"},
			expected: true,
		},
		{
			caseName: "equal string and no key number",
			data:     inputContextData{"fruit": "apple", "somevalue": "42"},
			expected: false,
		},
		{
			caseName: "no key string and equal number",
			data:     inputContextData{"vegetable": "tomato", "answer": "42"},
			expected: false,
		},
		{
			caseName: "no key string and no key number",
			data:     inputContextData{"vegetable": "tomato", "somevalue": "42"},
			expected: true,
		},
	}

	tree := negationLogicalExpression{
		Expression: logicalExpression{
			left: stringComparisonExpression{
				field:               "fruit",
				comparisonOperation: comparisonEqual,
				value:               "apple",
			},
			logicalOperation: logicalOr,
			right: numberComparisonExpression{
				field:               "answer",
				comparisonOperation: comparisonEqual,
				value:               42,
			},
		},
	}
	for _, testCase := range testCases {
		t.Run(testCase.caseName, func(t *testing.T) {
			assert.Equal(t, testCase.expected, tree.Evaluate(&inputContext{
				data:       testCase.data,
				missedKeys: make(common.StringSet),
			}))
		})
	}
}

func createConditionStringForBenchmark(i int) string {
	return fmt.Sprintf("cgi.app_version >= %d && cgi.app_id eq 'ru.yandex.mobile' && !(cgi.pzdCoin eq 0) && !(cgi.pzdCoin eq 1)", i)
}

func benchmarkParserSeq(b *testing.B, parser ABFlagsConditionsParser, randSeed int64, differentExpressionsCount int) {
	rand.Seed(randSeed)
	for i := 0; i < b.N; i++ {
		conditionString := createConditionStringForBenchmark(rand.Intn(differentExpressionsCount))
		_, err := parser.Parse(conditionString)
		assert.NoError(b, err)
	}
}

func benchmarkParserParallel(b *testing.B, parser ABFlagsConditionsParser, randSeed int64, differentExpressionsCount int) {
	rand.Seed(randSeed)
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			conditionString := createConditionStringForBenchmark(rand.Intn(differentExpressionsCount))
			_, err := parser.Parse(conditionString)
			assert.NoError(b, err)
		}
	})
}

func BenchmarkDefaultABFlagsConditionsParser(b *testing.B) {
	parser := &defaultABFlagsConditionsParser{}
	benchmarkParserSeq(b, parser, 15_11_1992, 1000)
}

func BenchmarkDefaultABFlagsConditionsParserParallel(b *testing.B) {
	parser := &defaultABFlagsConditionsParser{}
	benchmarkParserParallel(b, parser, 15_11_1992, 1000)
}

func BenchmarkCachedABFlagsConditionsParser(b *testing.B) {
	parser := newCachedABFlagsConditionsParser()
	benchmarkParserSeq(b, parser, 15_11_1992, 1000)
}

func BenchmarkCachedABFlagsConditionsParserParallel(b *testing.B) {
	parser := newCachedABFlagsConditionsParser()
	benchmarkParserParallel(b, parser, 15_11_1992, 1000)
}

func Test_parseCondition(t *testing.T) {
	type args struct {
		s string
	}
	tests := []struct {
		name    string
		args    args
		want    Expression
		wantErr bool
	}{
		{
			name: "example from prod; ios quotes",
			args: args{
				s: "cgi.app_version > 21110700 && cgi.app_id eq ‘ru.yandex.searchplugin.beta\u2019",
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "empty string",
			args: args{
				s: "",
			},
			want:    nil,
			wantErr: false,
		},
		{
			name: "not equal symbol",
			args: args{
				s: "cgi.app_version ≠ 34",
			},
			want:    nil,
			wantErr: true,
		},
		{
			name: "several boolean operands",
			args: args{
				s: "version == 42 || version == 45 || version == 48",
			},
			want: logicalExpression{
				logicalExpression{
					numberComparisonExpression{"version", comparisonEqual, 42},
					logicalOr,
					numberComparisonExpression{"version", comparisonEqual, 45},
				},
				logicalOr,
				numberComparisonExpression{"version", comparisonEqual, 48},
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := parseCondition(tt.args.s)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}
