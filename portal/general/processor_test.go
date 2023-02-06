package httpprocessor

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"strings"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/experiments/conditions"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

func Test_Processor_deserializeFlags(t *testing.T) {
	type args struct {
		raw     json.RawMessage
		handler string
	}

	tests := []struct {
		name string
		args args
		want experimentFlagsBatch
	}{
		{
			name: "empty",
			args: args{
				raw:     json.RawMessage(`[]`),
				handler: "MORDA",
			},
			want: experimentFlagsBatch{},
		},
		{
			name: "small",
			args: args{
				raw: json.RawMessage(`[
					  {
						"HANDLER": "VH",
						"CONTEXT": {
						  "VH": {
							"flags": [
							  "enable_vod_hls_packager=1"
							],
							"testid": [
							  "356537"
							]
						  }
						}
					  }
					]`),
				handler: "VH",
			},
			want: experimentFlagsBatch{
				flagsDataItem{
					Condition: "",
					Context: map[string]flagsDataItemContextValue{
						"VH": {
							Flags: []string{
								"enable_vod_hls_packager=1",
							},
							TestIDs: []string{"356537"},
						},
					},
					Handler: "VH",
				},
			},
		},
		{
			name: "big, extract flag for MORDA handler",
			args: args{
				raw: json.RawMessage(`[
					  {
						"HANDLER": "MORDA",
						"CONTEXT": {
						  "MORDA": {
							"flags": [
							  "_slice_name=more-extra100-related_exp2",
							  "topnews_extra=1",
							  "topnews_extra_gray=1"
							],
							"testid": [
							  "348841"
							]
						  }
						},
						"CONDITION": "(device.OSFamily eq \"Android\" && device.OSVersion ge \"6\") || (device.OSFamily eq \"iOS\" && device.OSVersion ge \"11\")"
					  },
					  {
						"HANDLER": "NEWS_SPORT",
						"CONTEXT": {
						  "NEWS_SPORT": {
							"testid": [
							  "348841"
							]
						  }
						}
					  },
					  {
						"HANDLER": "NEWS_MORDA_API",
						"CONTEXT": {
						  "NEWS_MORDA_API": {
							"flags": [
							  "yxnews_extra_stories_russian_top=1",
							  "yxnews_extra_stories_max_top_size=3",
							  "yxnews_extra_stories_min_top_size=1",
							  "yxnews_extra_stories_worst_position=100",
							  "yxnews_extra_stories_expire_hours=24",
							  "yxnews_extra_stories_min_docs=2"
							]
						  }
						},
						"TESTID": [
						  "348841"
						]
					  }
					]`),
				handler: "MORDA",
			},
			want: experimentFlagsBatch{
				flagsDataItem{
					Condition: "(device.OSFamily eq \"Android\" && device.OSVersion ge \"6\") || (device.OSFamily eq \"iOS\" && device.OSVersion ge \"11\")",
					Context: map[string]flagsDataItemContextValue{
						"MORDA": {
							Flags: []string{
								"_slice_name=more-extra100-related_exp2",
								"topnews_extra=1",
								"topnews_extra_gray=1",
							},
							TestIDs: []string{"348841"},
						},
					},
					Handler: "MORDA",
				},
			},
		},
		{
			name: "big, extract flag for NEWS_MORDA_API handler",
			args: args{
				raw: json.RawMessage(`[
					  {
						"HANDLER": "MORDA",
						"CONTEXT": {
						  "MORDA": {
							"flags": [
							  "_slice_name=more-extra100-related_exp2",
							  "topnews_extra=1",
							  "topnews_extra_gray=1"
							],
							"testid": [
							  "348841"
							]
						  }
						},
						"CONDITION": "(device.OSFamily eq \"Android\" && device.OSVersion ge \"6\") || (device.OSFamily eq \"iOS\" && device.OSVersion ge \"11\")"
					  },
					  {
						"HANDLER": "NEWS_SPORT",
						"CONTEXT": {
						  "NEWS_SPORT": {
							"testid": [
							  "348841"
							]
						  }
						}
					  },
					  {
						"HANDLER": "NEWS_MORDA_API",
						"CONTEXT": {
						  "NEWS_MORDA_API": {
							"flags": [
							  "yxnews_extra_stories_russian_top=1",
							  "yxnews_extra_stories_max_top_size=3",
							  "yxnews_extra_stories_min_top_size=1",
							  "yxnews_extra_stories_worst_position=100",
							  "yxnews_extra_stories_expire_hours=24",
							  "yxnews_extra_stories_min_docs=2"
							]
						  }
						},
						"TESTID": [
						  "348841"
						]
					  }
					]`),
				handler: "NEWS_MORDA_API",
			},
			want: experimentFlagsBatch{
				flagsDataItem{
					Condition: "",
					Context: map[string]flagsDataItemContextValue{
						"NEWS_MORDA_API": {
							Flags: []string{
								"yxnews_extra_stories_russian_top=1",
								"yxnews_extra_stories_max_top_size=3",
								"yxnews_extra_stories_min_top_size=1",
								"yxnews_extra_stories_worst_position=100",
								"yxnews_extra_stories_expire_hours=24",
								"yxnews_extra_stories_min_docs=2",
							},
							TestIDs: nil,
						},
					},
					Handler: "NEWS_MORDA_API",
				},
			},
		},
		{
			name: "unsupported flag format for VH handler",
			args: args{
				raw: json.RawMessage(`[
					  {
						"HANDLER": "VH",
						"CONTEXT": {
						  "VH": {
							"flags": [
							  "enable_vod_hls_packager=1"
							],
							"testid": [
							  "356537"
							]
						  }
						}
					  }
					]`),
				handler: "MORDA",
			},
			want: experimentFlagsBatch{},
		},
	}

	p := New(log3.NewLoggerStub(), nil, nil, nil)
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			actual, err := p.deserializeFlags(base64.StdEncoding.EncodeToString(test.args.raw), test.args.handler)

			require.NoError(t, err)
			assert.Equal(t, test.want, actual)
		})
	}
}

func Test_Processor_parseExpFlagsHeader(t *testing.T) {
	type args struct {
		base64  string
		handler string
	}

	tests := []struct {
		name string
		args args
		want []experimentFlagsBatch
	}{
		{
			name: "empty batches",
			args: args{
				base64:  "W10=,W10=,W10=",
				handler: "MORDA",
			},
			want: []experimentFlagsBatch{},
		},
		{
			name: "several batches",
			args: args{
				base64:  "W10=,W3siSEFORExFUiI6IlZIIiwiQ09OVEVYVCI6eyJWSCI6eyJmbGFncyI6WyJlbmFibGVfdm9kX2hsc19wYWNrYWdlcj0xIl0sInRlc3RpZCI6WyIzNTY1MzciXX19fV0=,W10=,W3siSEFORExFUiI6IlZIIiwiQ09OVEVYVCI6eyJWSCI6eyJmbGFncyI6WyJlbmFibGVfdm9kX2hsc19wYWNrYWdlcj0xIl0sInRlc3RpZCI6WyIzNTY1MzciXX19fV0=",
				handler: "VH",
			},
			want: []experimentFlagsBatch{
				{
					flagsDataItem{
						Condition: "",
						Context: map[string]flagsDataItemContextValue{
							"VH": {
								Flags: []string{
									"enable_vod_hls_packager=1",
								},
								TestIDs: []string{"356537"},
							},
						},
						Handler: "VH",
					},
				},
				{
					flagsDataItem{
						Condition: "",
						Context: map[string]flagsDataItemContextValue{
							"VH": {
								Flags: []string{
									"enable_vod_hls_packager=1",
								},
								TestIDs: []string{"356537"},
							},
						},
						Handler: "VH",
					},
				},
			},
		},
		{
			name: "invalid raw",
			args: args{
				base64:  "W10:=,W10=",
				handler: "MORDA",
			},
			want: []experimentFlagsBatch{},
		},
	}

	p := New(log3.NewLoggerStub(), nil, nil, nil)
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			actual, err := p.parseExpFlagsHeader(test.args.base64, test.args.handler)

			require.NoError(t, err)
			assert.Equal(t, test.want, actual)
		})
	}
}

func Test_Processor_parseABFlag(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		want    abFlag
		wantErr string
	}{
		{
			name:  "regular",
			input: "key=value",
			want:  abFlag{"key", "value"},
		},
		{
			name:  "spaces around equal sign",
			input: "key = value",
			want:  abFlag{"key", "value"},
		},
		{
			name:  "trailing spaces",
			input: "  key=value  ",
			want:  abFlag{"key", "value"},
		},
		{
			name:  "newline at the begin",
			input: "\nkey=value",
			want:  abFlag{"key", "value"},
		},
		{
			name:  "newline at the end",
			input: "key=value\n",
			want:  abFlag{"key", "value"},
		},
		{
			name:  "value with =",
			input: "key=subkey=value",
			want:  abFlag{"key", "subkey=value"},
		},
		{
			name:    "empty value",
			input:   "key=",
			want:    abFlag{"key", ""},
			wantErr: "empty AB-flag value",
		},
		{
			name:    "empty value with spaces",
			input:   "key=   ",
			want:    abFlag{"key", ""},
			wantErr: "empty AB-flag value",
		},
		{
			name:    "empty key",
			input:   "=value",
			want:    abFlag{"", "value"},
			wantErr: "empty AB-flag key",
		},
		{
			name:    "empty key with spaces",
			input:   "   =value",
			want:    abFlag{"", "value"},
			wantErr: "empty AB-flag key",
		},
		{
			name:    "no separator",
			input:   "keyvalue",
			want:    abFlag{},
			wantErr: "invalid AB-flag format",
		},
	}

	p := New(log3.NewLoggerStub(), nil, nil, nil)
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			actual, err := p.parseABFlag(test.input)

			if test.wantErr == "" {
				require.NoError(t, err)
				assert.Equal(t, test.want, actual)
			} else {
				require.Error(t, err)
				assert.Equal(t, test.want, actual)
				assert.EqualError(t, err, test.wantErr)
			}
		})
	}
}

func Test_Processor_ParseExperimentBoxes(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  []ExperimentBox
	}{
		{
			name:  "empty string",
			input: "",
			want:  nil,
		},
		{
			name:  "single test id",
			input: "111222,0,1",
			want: []ExperimentBox{
				{111222, 1},
			},
		},
		{
			name:  "single test id with trail semicolon",
			input: "111222,0,1;",
			want: []ExperimentBox{
				{111222, 1},
			},
		},
		{
			name:  "several test ids",
			input: "111222,0,1;333444,0,42",
			want: []ExperimentBox{
				{111222, 1},
				{333444, 42},
			},
		},
		{
			name:  "duplicate test ids with different boxes",
			input: "111222,0,1;111222,0,42",
			want: []ExperimentBox{
				{111222, 1},
				{111222, 42},
			},
		},
		{
			name:  "duplicate test ids with same boxes",
			input: "111222,0,42;111222,0,42",
			want: []ExperimentBox{
				{111222, 42},
			},
		},
	}

	p := New(log3.NewLoggerStub(), nil, nil, nil)
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			actual, err := p.ParseExperimentBoxes(test.input)

			require.NoError(t, err)
			assert.ElementsMatch(t, test.want, actual)
		})
	}
}

func Test_Processor_processBatchItem(t *testing.T) {
	type args struct {
		item        flagsDataItem
		expBoxesSet common.IntSet
		handler     string
	}

	var tests = []struct {
		name string
		args args
		want models.ABFlags
	}{
		{
			name: "MORDA handler",
			args: args{
				item: flagsDataItem{
					Context: map[string]flagsDataItemContextValue{
						"MORDA": {
							Flags: []string{
								"_slice_name=more-extra100-related_exp2",
								"topnews_extra=1",
								"topnews_extra_gray=1",
							},
							TestIDs: []string{"348841"},
						},
						"APPSEARCH": {
							Flags:   []string{},
							TestIDs: []string{"654321"},
						},
					},
					Handler: "MORDA",
				},
				expBoxesSet: common.NewIntSet(348841),
				handler:     "MORDA",
			},
			want: models.ABFlags{
				Flags: map[string]string{
					"topnews_extra":      "1",
					"topnews_extra_gray": "1",
				},
				SliceNames: []string{"more-extra100-related_exp2"},
			},
		},
		{
			name: "MORDA handler with condition",
			args: args{
				item: flagsDataItem{
					Condition: "(device.OSFamily eq \"Android\" && device.OSVersion ge \"6\") || (device.OSFamily eq \"iOS\" && device.OSVersion ge \"11\")",
					Context: map[string]flagsDataItemContextValue{
						"MORDA": {
							Flags: []string{
								"_slice_name=more-extra100-related_exp2",
								"topnews_extra=1",
								"topnews_extra_gray=1",
							},
							TestIDs: []string{"348841"},
						},
						"APPSEARCH": {
							Flags:   []string{},
							TestIDs: []string{"654321"},
						},
					},
					Handler: "MORDA",
				},
				expBoxesSet: common.NewIntSet(348841),
				handler:     "MORDA",
			},
			want: models.ABFlags{
				Flags: map[string]string{
					"topnews_extra":      "1",
					"topnews_extra_gray": "1",
				},
				SliceNames: []string{"more-extra100-related_exp2"},
			},
		},
		{
			name: "failed condition evaluation",
			args: args{
				item: flagsDataItem{
					Condition: "(device.OSFamily eq \"Android\" && device.OSVersion ge \"10\") || (device.OSFamily eq \"iOS\" && device.OSVersion ge \"11\")",
					Context: map[string]flagsDataItemContextValue{
						"MORDA": {
							Flags:   []string{},
							TestIDs: []string{"348841"},
						},
					},
					Handler: "MORDA",
				},
				expBoxesSet: common.NewIntSet(348841),
				handler:     "MORDA",
			},
			want: models.ABFlags{
				Flags:      map[string]string{},
				SliceNames: []string{},
			},
		},
		{
			name: "invalid test id",
			args: args{
				item: flagsDataItem{
					Context: map[string]flagsDataItemContextValue{
						"MORDA": {
							Flags:   []string{},
							TestIDs: []string{"123456"},
						},
					},
					Handler: "MORDA",
				},
				expBoxesSet: common.NewIntSet(348841),
				handler:     "MORDA",
			},
			want: models.ABFlags{
				Flags:      map[string]string{},
				SliceNames: []string{},
			},
		},
		{
			name: "invalid handler",
			args: args{
				item: flagsDataItem{
					Context: map[string]flagsDataItemContextValue{
						"MORDA": {
							Flags:   []string{},
							TestIDs: []string{"348841"},
						},
					},
					Handler: "MORDA",
				},
				expBoxesSet: common.NewIntSet(348841),
				handler:     "APPSEARCH",
			},
			want: models.ABFlags{
				Flags:      map[string]string{},
				SliceNames: []string{},
			},
		},
		{
			name: "some invalid ab flags",
			args: args{
				item: flagsDataItem{
					Context: map[string]flagsDataItemContextValue{
						"MORDA": {
							Flags: []string{
								"_slice_name=more-extra100-related_exp2",
								"_slice_name=",
								"topnews_extra=1",
								"topnews_invalid=",
								"topnews_extra_gray=1",
							},
							TestIDs: []string{"348841"},
						},
					},
					Handler: "MORDA",
				},
				expBoxesSet: common.NewIntSet(348841),
				handler:     "MORDA",
			},
			want: models.ABFlags{
				Flags: map[string]string{
					"topnews_extra":      "1",
					"topnews_extra_gray": "1",
				},
				SliceNames: []string{"more-extra100-related_exp2"},
			},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			ctxStub := NewMocktrackedInputContext(ctrl)
			ctxStub.EXPECT().HasKey(gomock.Any()).Return(true).AnyTimes()
			ctxStub.EXPECT().GetString("device.OSFamily").Return("Android").AnyTimes()
			ctxStub.EXPECT().GetString("device.OSVersion").Return("6").AnyTimes()
			ctxStub.EXPECT().GetMissedKeys().Return(nil).MaxTimes(1)
			p := New(log3.NewLoggerStub(), ctxStub, conditions.NewABFlagsConditionsParser(), nil)

			err := p.processBatchItem(test.args.item, test.args.expBoxesSet, test.args.handler)

			require.NoError(t, err)
			assert.Equal(t, test.want.Flags, p.abFlags.Flags, "check AB flags")
			assert.Equal(t, test.want.SliceNames, p.abFlags.SliceNames, "check slice names")
		})
	}
}

func Test_Processor_Process(t *testing.T) {
	type args struct {
		expBoxesHeader string
		flagsHeader    []flagsHeaderTest
		handler        string
	}

	var tests = []struct {
		name string
		args args
		want models.ABFlags
	}{
		{
			name: "MORDA single flag",
			args: args{
				expBoxesHeader: "123456,0,1;222222,0,42",
				flagsHeader: []flagsHeaderTest{
					{
						name:   "MORDA",
						flags:  `"topnews_extra=1","_slice_name=slice1"`,
						testID: 123456,
					},
					{
						name:   "APPSEARCH",
						flags:  `"topnews_extra=2","_slice_name=slice2"`,
						testID: 654321,
					},
				},
				handler: "MORDA",
			},
			want: models.ABFlags{
				Flags: map[string]string{
					"topnews_extra": "1",
				},
				TestIDs: common.NewIntSet(123456, 222222),
				TestIDsBuckets: map[int][]int{
					123456: {1},
					222222: {42},
				},
				SliceNames: []string{"slice1"},
			},
		},
		{
			name: "MORDA several flags",
			args: args{
				expBoxesHeader: "123456,0,1;222222,0,42",
				flagsHeader: []flagsHeaderTest{
					{
						name:   "MORDA",
						flags:  `"topnews_extra=1","_slice_name=slice1"`,
						testID: 123456,
					},
					{
						name:   "MORDA",
						flags:  `"topnews_extra_gray=1","_slice_name=slice2"`,
						testID: 222222,
					},
				},
				handler: "MORDA",
			},
			want: models.ABFlags{
				Flags: map[string]string{
					"topnews_extra":      "1",
					"topnews_extra_gray": "1",
				},
				TestIDs: common.NewIntSet(123456, 222222),
				TestIDsBuckets: map[int][]int{
					123456: {1},
					222222: {42},
				},
				SliceNames: []string{"slice1", "slice2"},
			},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctrl := gomock.NewController(t)
			ctxStub := NewMocktrackedInputContext(ctrl)
			ctxStub.EXPECT().GetMissedKeys().Return(nil).MaxTimes(2)
			p := New(log3.NewLoggerStub(), ctxStub, conditions.NewABFlagsConditionsParser(), nil)

			actual, err := p.Process(test.args.expBoxesHeader, flagsJSONBase64(test.args.flagsHeader), test.args.handler)

			require.NoError(t, err)
			assert.Equal(t, test.want, actual)
		})
	}
}

func benchmarkParseExpFlagsHeader(b *testing.B) {
	header := "W3siSEFORExFUiI6Ik1PUkRBIiwiQ09OVEVYVCI6eyJNT1JEQSI6eyJmbGFncyI6WyJfc2xpY2VfbmFtZT1tb3JlLWV4dHJhMTAwLXJlbGF0ZWRfZXhwMiIsInRvcG5ld3NfZXh0cmE9MSIsInRvcG5ld3NfZXh0cmFfZ3JheT0xIl0sInRlc3RpZCI6WyIzNDg4NDEiXX19LCJDT05ESVRJT04iOiIoZGV2aWNlLk9TRmFtaWx5IGVxIFwiQW5kcm9pZFwiICYmIGRldmljZS5PU1ZlcnNpb24gZ2UgXCI2XCIpIHx8IChkZXZpY2UuT1NGYW1pbHkgZXEgXCJpT1NcIiAmJiBkZXZpY2UuT1NWZXJzaW9uIGdlIFwiMTFcIikifSx7IkhBTkRMRVIiOiJORVdTX1NQT1JUIiwiQ09OVEVYVCI6eyJORVdTX1NQT1JUIjp7InRlc3RpZCI6WyIzNDg4NDEiXX19fSx7IkhBTkRMRVIiOiJORVdTX01PUkRBX0FQSSIsIkNPTlRFWFQiOnsiTkVXU19NT1JEQV9BUEkiOnsiZmxhZ3MiOlsieXhuZXdzX2V4dHJhX3N0b3JpZXNfcnVzc2lhbl90b3A9MSIsInl4bmV3c19leHRyYV9zdG9yaWVzX21heF90b3Bfc2l6ZT0zIiwieXhuZXdzX2V4dHJhX3N0b3JpZXNfbWluX3RvcF9zaXplPTEiLCJ5eG5ld3NfZXh0cmFfc3Rvcmllc193b3JzdF9wb3NpdGlvbj0xMDAiLCJ5eG5ld3NfZXh0cmFfc3Rvcmllc19leHBpcmVfaG91cnM9MjQiLCJ5eG5ld3NfZXh0cmFfc3Rvcmllc19taW5fZG9jcz0yIl19fSwiVEVTVElEIjpbIjM0ODg0MSJdfV0="
	processor := processor{}
	_, err := processor.parseExpFlagsHeader(header, "MORDA")
	assert.NoError(b, err)
}

func BenchmarkParseExpFlagsHeaderSeq(b *testing.B) {
	for i := 0; i < b.N; i++ {
		benchmarkParseExpFlagsHeader(b)
	}
}

func BenchmarkParseExpFlagsHeaderParallel(b *testing.B) {
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			benchmarkParseExpFlagsHeader(b)
		}
	})
}

type flagsHeaderTest struct {
	name   string
	flags  string
	testID int
}

func flagsJSONBase64(hh []flagsHeaderTest) string {
	str := fmt.Sprintf("[%s]", flagsHeaderTestString(hh))
	return base64.StdEncoding.EncodeToString([]byte(str))
}

func flagsHeaderTestString(hh []flagsHeaderTest) string {
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
			h.name,
			h.name,
			h.flags,
			h.testID)
	}
	return strings.Join(res, ",")
}
