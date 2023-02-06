package experiments

import (
	"encoding/base64"
	"fmt"
	"strings"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/experiments/madmprocessor"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/staticparams"
)

type flagTestCase struct {
	flag                 string
	expectedValue        string
	expectedPresenceFlag bool
	expectedBoolValue    bool
}

func Test_parser_parse(t *testing.T) {
	type fields struct {
		abHandlerName     ABHandlerName
		env               common.Environment
		handlers          []handlerTest
		xYandexExpBoxes   string
		isInternalRequest bool
		cgiABFlags        map[string]string
		httpProcessor     models.ABFlags
		madmGetFlags      map[string][]madmprocessor.ABFlagsParameters
	}

	type args struct {
		ignoreBalancerExps bool
	}

	type want struct {
		testIDs []int
		abFlags []flagTestCase
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   want
	}{
		{
			name: "MORDA single flag",
			fields: fields{
				abHandlerName: MORDA,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"fruit=apple"`,
						testID: 123456,
					},
					{
						name:   APPSEARCH,
						flags:  `"fruit=banana"`,
						testID: 654321,
					},
				},
				xYandexExpBoxes: "123456,0,1;222222,0,42",
				httpProcessor: models.ABFlags{
					Flags:          map[string]string{"fruit": "apple"},
					TestIDs:        common.NewIntSet(123456),
					TestIDsBuckets: map[int][]int{123456: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{123456},
				abFlags: []flagTestCase{
					{
						flag:                 "fruit",
						expectedValue:        "apple",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
				},
			},
		},
		{
			name: "APPSEARCH single flag",
			fields: fields{
				abHandlerName: APPSEARCH,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"fruit=apple"`,
						testID: 123456,
					},
					{
						name:   APPSEARCH,
						flags:  `"fruit=banana"`,
						testID: 654321,
					},
				},
				xYandexExpBoxes: "654321,0,1;222222,0,42",
				httpProcessor: models.ABFlags{
					Flags:          map[string]string{"fruit": "banana"},
					TestIDs:        common.NewIntSet(654321),
					TestIDsBuckets: map[int][]int{654321: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{654321},
				abFlags: []flagTestCase{
					{
						flag:                 "fruit",
						expectedValue:        "banana",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
				},
			},
		},
		{
			name: "MORDA use flag as boolean",
			fields: fields{
				abHandlerName: MORDA,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"alpha=0","bravo=1","charlie=2","delta=false","echo=true"`,
						testID: 123456,
					},
					{
						name:   APPSEARCH,
						flags:  `"alpha=2","bravo=1","charlie=0","delta=true","echo=false"`,
						testID: 654321,
					},
				},
				xYandexExpBoxes: "123456,0,1;222222,0,42",
				httpProcessor: models.ABFlags{
					Flags: map[string]string{
						"alpha":   "0",
						"bravo":   "1",
						"charlie": "2",
						"delta":   "false",
						"echo":    "true",
					},
					TestIDs:        common.NewIntSet(123456),
					TestIDsBuckets: map[int][]int{123456: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{123456},
				abFlags: []flagTestCase{
					{flag: "alpha", expectedValue: "0", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "bravo", expectedValue: "1", expectedBoolValue: true, expectedPresenceFlag: true},
					{flag: "charlie", expectedValue: "2", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "delta", expectedValue: "false", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "echo", expectedValue: "true", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "zulu", expectedValue: "", expectedBoolValue: false, expectedPresenceFlag: false},
				},
			},
		},
		{
			name: "APPSEARCH use flag as boolean",
			fields: fields{
				abHandlerName: APPSEARCH,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"alpha=0","bravo=1","charlie=2","delta=false","echo=true"`,
						testID: 123456,
					},
					{
						name:   APPSEARCH,
						flags:  `"alpha=2","bravo=1","charlie=0","delta=true","echo=false"`,
						testID: 654321,
					},
				},
				xYandexExpBoxes: "654321,0,1;222222,0,42",
				httpProcessor: models.ABFlags{
					Flags: map[string]string{
						"alpha":   "2",
						"bravo":   "1",
						"charlie": "0",
						"delta":   "true",
						"echo":    "false",
					},
					TestIDs:        common.NewIntSet(654321),
					TestIDsBuckets: map[int][]int{654321: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{654321},
				abFlags: []flagTestCase{
					{flag: "alpha", expectedValue: "2", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "bravo", expectedValue: "1", expectedBoolValue: true, expectedPresenceFlag: true},
					{flag: "charlie", expectedValue: "0", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "delta", expectedValue: "true", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "echo", expectedValue: "false", expectedBoolValue: false, expectedPresenceFlag: true},
					{flag: "zulu", expectedValue: "", expectedBoolValue: false, expectedPresenceFlag: false},
				},
			},
		},
		{
			name: "overriding flags from CGI Testing env",
			fields: fields{
				abHandlerName: MORDA,
				env:           common.Testing,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"fruit": "apple"`,
						testID: 123456,
					},
				},
				xYandexExpBoxes: "123456,0,1;222222,0,42",
				cgiABFlags: map[string]string{
					"fruit":  "banana",
					"number": "42",
					"town":   "1",
				},
				httpProcessor: models.ABFlags{
					Flags:          map[string]string{"fruit": "apple"},
					TestIDs:        common.NewIntSet(123456),
					TestIDsBuckets: map[int][]int{123456: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{123456},
				abFlags: []flagTestCase{
					{
						flag:                 "fruit",
						expectedValue:        "banana",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
					{
						flag:                 "vegetable",
						expectedValue:        "",
						expectedPresenceFlag: false,
						expectedBoolValue:    false,
					},
					{
						flag:                 "town",
						expectedValue:        "1",
						expectedPresenceFlag: true,
						expectedBoolValue:    true,
					},
					{
						flag:                 "number",
						expectedValue:        "42",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
				},
			},
		},
		{
			name: "overriding flags from CGI internal request",
			fields: fields{
				abHandlerName: MORDA,
				env:           common.Production,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"fruit": "apple"`,
						testID: 123456,
					},
				},
				xYandexExpBoxes:   "123456,0,1;222222,0,42",
				isInternalRequest: true,
				cgiABFlags: map[string]string{
					"fruit":  "banana",
					"number": "42",
					"town":   "1",
				},
				httpProcessor: models.ABFlags{
					Flags:          map[string]string{"fruit": "apple"},
					TestIDs:        common.NewIntSet(123456),
					TestIDsBuckets: map[int][]int{123456: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{123456},
				abFlags: []flagTestCase{
					{
						flag:                 "fruit",
						expectedValue:        "banana",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
					{
						flag:                 "vegetable",
						expectedValue:        "",
						expectedPresenceFlag: false,
						expectedBoolValue:    false,
					},
					{
						flag:                 "town",
						expectedValue:        "1",
						expectedPresenceFlag: true,
						expectedBoolValue:    true,
					},
					{
						flag:                 "number",
						expectedValue:        "42",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
				},
			},
		},
		{
			name: "overriding flags from CGI Production env",
			fields: fields{
				abHandlerName: MORDA,
				env:           common.Production,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"fruit": "apple"`,
						testID: 123456,
					},
				},
				xYandexExpBoxes: "123456,0,1;222222,0,42",
				cgiABFlags: map[string]string{
					"fruit":  "banana",
					"number": "42",
					"town":   "1",
				},
				httpProcessor: models.ABFlags{
					Flags:          map[string]string{"fruit": "apple"},
					TestIDs:        common.NewIntSet(123456),
					TestIDsBuckets: map[int][]int{123456: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{123456},
				abFlags: []flagTestCase{
					{
						flag:                 "fruit",
						expectedValue:        "apple",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
					{
						flag:                 "vegetable",
						expectedValue:        "",
						expectedPresenceFlag: false,
						expectedBoolValue:    false,
					},
					{
						flag:                 "town",
						expectedValue:        "",
						expectedPresenceFlag: false,
						expectedBoolValue:    false,
					},
					{
						flag:                 "number",
						expectedValue:        "",
						expectedPresenceFlag: false,
						expectedBoolValue:    false,
					},
				},
			},
		},
		{
			name: "ignore balancer headers Development env",
			fields: fields{
				abHandlerName: MORDA,
				env:           common.Development,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"fruit": "apple"`,
						testID: 123456,
					},
				},
				xYandexExpBoxes: "123456,0,1;222222,0,42",
				cgiABFlags: map[string]string{
					"number": "42",
					"town":   "moscow",
				},
				httpProcessor: models.ABFlags{},
			},
			args: args{ignoreBalancerExps: true},
			want: want{
				testIDs: []int{},
				abFlags: []flagTestCase{
					{flag: "fruit", expectedValue: "", expectedPresenceFlag: false, expectedBoolValue: false},
					{flag: "number", expectedValue: "42", expectedPresenceFlag: true, expectedBoolValue: false},
					{flag: "town", expectedValue: "moscow", expectedPresenceFlag: true, expectedBoolValue: false},
				},
			},
		},
		{
			name: "adding flags from madm Production env",
			fields: fields{
				abHandlerName: MORDA,
				env:           common.Development,
				handlers: []handlerTest{
					{
						name:   MORDA,
						flags:  `"fruit": "apple",`,
						testID: 123456,
					},
				},
				xYandexExpBoxes: "123456,0,1;222222,0,42",
				cgiABFlags: map[string]string{
					"fruit": "banana",
					"town":  "moscow",
				},
				madmGetFlags: map[string][]madmprocessor.ABFlagsParameters{
					"berry": {{}},
					"meal":  {{}},
					"fruit": {{}},
				},
				httpProcessor: models.ABFlags{
					Flags:          map[string]string{"fruit": "apple"},
					TestIDs:        common.NewIntSet(123456),
					TestIDsBuckets: map[int][]int{123456: {1}},
					SliceNames:     make([]string, 0),
				},
			},
			want: want{
				testIDs: []int{123456},
				abFlags: []flagTestCase{
					{
						flag:                 "fruit",
						expectedValue:        "banana",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
					{
						flag:                 "vegetable",
						expectedValue:        "",
						expectedPresenceFlag: false,
						expectedBoolValue:    false,
					},
					{
						flag:                 "town",
						expectedValue:        "moscow",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
					{
						flag:                 "berry",
						expectedValue:        "strawberry",
						expectedPresenceFlag: true,
						expectedBoolValue:    false,
					},
				},
			},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)

			staticParamsMock := NewMockstaticParamsGetter(ctrl)
			staticParamsMock.EXPECT().Location().Return(staticparams.Location("")).MaxTimes(2)
			staticParamsMock.EXPECT().Env().Return(test.fields.env).MaxTimes(1)

			madmProcessorMock := NewMockmadmFlagsProcessor(ctrl)
			madmProcessorMock.EXPECT().GetFlags().Return(test.fields.madmGetFlags, nil).Times(1)
			madmProcessorMock.EXPECT().Process("berry").Return("strawberry", true, nil).MaxTimes(1)
			madmProcessorMock.EXPECT().Process("meal").Return("meal", false, nil).MaxTimes(1)
			madmProcessorMock.EXPECT().Process("fruit").Return("orange", true, nil).MaxTimes(0)

			httpWrapperMock := NewMockhttpWrapper(ctrl)
			httpWrapperMock.EXPECT().IsInternalRequest().Return(test.fields.isInternalRequest).MaxTimes(1)
			httpWrapperMock.EXPECT().GetExpBoxes(gomock.Any()).Return(test.fields.xYandexExpBoxes).MaxTimes(1)
			httpWrapperMock.EXPECT().GetExpFlags(gomock.Any()).Return(flagsJSONBase64(test.fields.handlers)).MaxTimes(1)
			httpWrapperMock.EXPECT().GetOverridingABFlags().Return(test.fields.cgiABFlags).MaxTimes(1)

			httpProcessorMock := NewMockhttpFlagsProcessor(ctrl)
			httpProcessorMock.EXPECT().
				Process(test.fields.xYandexExpBoxes, flagsJSONBase64(test.fields.handlers), test.fields.abHandlerName.String()).
				Return(test.fields.httpProcessor, nil).
				MaxTimes(1)

			parser := NewParser(log3.NewLoggerStub(), staticParamsMock, test.fields.abHandlerName,
				madmProcessorMock, httpProcessorMock, httpWrapperMock)

			abFlags, err := parser.parse(test.args.ignoreBalancerExps)
			require.NoError(t, err)

			assertABFlags(t, abFlags, test.want.abFlags)
			assert.Equal(t, common.NewIntSet(test.want.testIDs...), abFlags.TestIDs)
		})
	}
}

type handlerTest struct {
	name   ABHandlerName
	flags  string
	testID int
}

func flagsJSONBase64(hh []handlerTest) string {
	str := fmt.Sprintf("[%s]", handlerTestString(hh))
	return base64.StdEncoding.EncodeToString([]byte(str))
}

func handlerTestString(hh []handlerTest) string {
	res := make([]string, len(hh))
	for i, h := range hh {
		res[i] = fmt.Sprintf(`{
				"HANDLER": "%s",
				"CONTEXT": {
					"%s": {
						"flags": [%s],
						"testid": ["%d"]
					}
				},
				"CONDITION": ""
			}`,
			h.name.String(),
			h.name.String(),
			h.flags,
			h.testID)
	}
	return strings.Join(res, ",")
}

func assertABFlags(t *testing.T, abFlags models.ABFlags, cases []flagTestCase) {
	for _, flagCase := range cases {
		t.Run(flagCase.flag, func(t *testing.T) {
			v, ok := abFlags.Get(flagCase.flag)
			assert.Equal(t, flagCase.expectedValue, v, "check flag value")
			assert.Equal(t, flagCase.expectedPresenceFlag, ok, "check ok flag")
			assert.Equal(t, flagCase.expectedBoolValue, abFlags.GetBool(flagCase.flag), "check flag value as bool")
		})
	}
}
