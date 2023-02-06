package parser

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"github.com/valyala/fastjson"
)

type testType struct {
	B   bool           `madm:"b"`
	S   string         `madm:"s"`
	BS  []byte         `madm:"bs"`
	I   int            `madm:"i"`
	I32 int32          `madm:"i32"`
	I64 int64          `madm:"i64"`
	U   uint           `madm:"u"`
	U32 uint32         `madm:"u32"`
	U64 uint64         `madm:"u64"`
	T   time.Time      `madm:"t"`
	P   fakeMadmParser `madm:"p"`
	SP  *string        `madm:"sp"`
	L   []int          `madm:"l"`
}

var (
	fullTestCase = `{
	"b": "true",
	"s": "str",
	"bs": "bstr",
	"i": "42",
	"i32": "-43",
	"i64": "44",
	"u": "45",
	"u32": "46",
	"u64": "47",
	"t": "2022-01-11 22:05",
	"p": "foo",
	"sp": "bar",
    "l": "1,2; 3"
}`
)

func TestParseMADM(t *testing.T) {
	j, err := fastjson.Parse(fullTestCase)
	require.NoError(t, err)
	var obj testType
	require.NoError(t, ParseMADM(j, &obj))
	require.True(t, obj.B)
	require.Equal(t, "str", obj.S)
	require.Equal(t, []byte("bstr"), obj.BS)
	require.Equal(t, 42, obj.I)
	require.Equal(t, int32(-43), obj.I32)
	require.Equal(t, int64(44), obj.I64)
	require.Equal(t, uint(45), obj.U)
	require.Equal(t, uint32(46), obj.U32)
	require.Equal(t, uint64(47), obj.U64)
	require.Equal(t, 2022, obj.T.Year())
	require.NotZero(t, obj.P.CallsCount)
	require.NotNil(t, obj.SP)
	require.Equal(t, "bar", *obj.SP)
	require.Len(t, obj.L, 3)
	require.Equal(t, 1, obj.L[0])
	require.Equal(t, 2, obj.L[1])
	require.Equal(t, 3, obj.L[2])

	obj = testType{
		U: 42,
	}
	j, err = fastjson.Parse("{}")
	require.NoError(t, err)
	require.NoError(t, ParseMADM(j, &obj))
	require.False(t, obj.B)
	require.Zero(t, obj.I)
	require.Equal(t, uint(42), obj.U)
	require.Zero(t, obj.P.CallsCount)
	require.Nil(t, obj.SP)
}

func Test_parseTime(t *testing.T) {
	var (
		supportedLayouts = []string{
			"2006-01-02 15:04:05", "2006-01-02 15:04", "2006-01-02",
		}
		invalidCases = []string{
			"", "now", "15:04",
		}
	)
	now := time.Now()

	for _, layout := range supportedLayouts {
		strRepresentation := now.Format(layout)
		expected, err := time.Parse(layout, strRepresentation)
		require.NoError(t, err)
		parsed, err := parseTime(strRepresentation)
		require.NoError(t, err)
		require.Equal(t, expected, parsed)
	}

	for _, testCase := range invalidCases {
		_, err := parseTime(testCase)
		require.Error(t, err)
	}
}

type fakeMadmParser struct {
	CallsCount int
}

func (p *fakeMadmParser) ParseMADM([]byte) error {
	p.CallsCount += 1
	return nil
}
