package core

import (
	"fmt"
	"math"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/valyala/fastjson"
)

func TestParseSimpleJsonValue(t *testing.T) {
	for inValue, res := range map[string]interface{}{
		"0":                    uint64(0),
		"1":                    uint64(1),
		"18446744073709551615": uint64(math.MaxUint64),
		"-9223372036854775808": int64(math.MinInt64),
		"1.2":                  1.2,
		"1e10":                 10000000000.0,
		"1E+2":                 100.0,
		"true":                 1,
		"false":                0,
		// RFC7951
		"\"123\"": uint64(123),
		//// string as is
		"\"ololo\"": "ololo",
		// looks like number
		"\"10.255.0.53\"": "10.255.0.53",
	} {
		encodedValue, err := ParseSimpleJSONValue([]byte(inValue), true)
		assert.NoError(t, err, fmt.Sprintf("string value %s", inValue))
		assert.Equal(t, encodedValue, res, fmt.Sprintf("string value %s", inValue))
	}
}

func TestParseSimpleJsonValueError(t *testing.T) {
	for _, inValue := range [][]byte{
		// juniper bug in /interfaces/interface/subinterfaces/subinterface/ipv6/addresses/address/state/prefix-length
		[]byte{128},
	} {
		encodedValue, err := ParseSimpleJSONValue(inValue, true)
		assert.Error(t, err)
		assert.Equal(t, encodedValue, nil)
	}
}

func TestParseComplexJsonValue(t *testing.T) {
	inValue := `
     {"bar": [
       {"foo": 123},
       {"bar": 0}
     ]}`
	values := map[string]interface{}{}
	err := ParseComplexJSONValue("", inValue, values, true, true)
	assert.NoError(t, err)
	assert.Equal(t, values, map[string]interface{}{"bar_bar": uint64(0), "bar_foo": uint64(123)})
}

func TestParseComplexJsonValue2(t *testing.T) {
	inValue := `{
	  "b": [
		{
		  "name": 0,
		  "c": {
			"d": 1.2,
			"e": 10042
		  }
		}
	  ]
	}`
	values := map[string]interface{}{}
	err := ParseComplexJSONValue("", inValue, values, true, true)
	assert.NoError(t, err)
	assert.Equal(t, values, map[string]interface{}{
		"b_name": uint64(0),
		"b_c_d":  float64(1.2),
		"b_c_e":  uint64(10042),
	})
}

func TestParseComplexJsonValueNotObjectInList(t *testing.T) {
	inValue := `{"a": [1, 2]}`
	values := map[string]interface{}{}
	err := ParseComplexJSONValue("", inValue, values,
		true, false)
	assert.Error(t, err)
	assert.Equal(t, values, map[string]interface{}{})
}

func TestParseNumberFromString(t *testing.T) {
	for inValue, exp := range map[string]interface{}{
		"\"1634508859295\"": uint64(1634508859295),
	} {
		var p fastjson.Parser

		v, err := p.Parse(inValue)
		assert.NoError(t, err)

		res, err := parseNumberFromString(v)

		assert.NoError(t, err)
		assert.Equal(t, res, exp, fmt.Sprintf("string value %s", inValue))
	}
}

func TestGetValueType(t *testing.T) {
	for inValue, exp := range map[string]jsonType{
		"1":           jsonValueInteger,
		"-1":          jsonValueInteger,
		"1234567890":  jsonValueInteger,
		"1.":          jsonValueString,
		"1.1":         jsonValueFloat,
		"1.123456790": jsonValueFloat,
		"1E400":       jsonValueFloat,
		"1E":          jsonValueString,
		"1E+":         jsonValueString,
		"1E+1":        jsonValueFloat,
		"-0E0":        jsonValueFloat,
		"-":           jsonValueString,
		"1.1.1":       jsonValueString,
		".1.1":        jsonValueString,
		"false":       jsonValueFalse,
		"true":        jsonValueTrue,
		" ":           jsonValueString, // juniper bug
	} {

		res := getValueType(inValue)
		assert.Equal(t, res, exp, fmt.Errorf("wrong type for %s", inValue))
	}
}
