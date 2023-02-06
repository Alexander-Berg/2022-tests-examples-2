package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

type testSearchQueryObjectType = struct {
	TestType SearchQueryObjectType `json:"test_type"`
}

func Test_SearchQueryObjectType_err(t *testing.T) {
	var tests = []struct {
		name         string
		val          []byte
		unmarshalErr string
	}{
		{
			"not string value",
			[]byte(`[]`),
			"json: cannot unmarshal array into Go value of type string",
		},
		{
			"bad value",
			[]byte(`"foo"`),
			"\"foo\" wrong enum value",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v SearchQueryObjectType
			err := json.Unmarshal(test.val, &v)
			require.Error(t, err)
			require.Equal(t, test.unmarshalErr, err.Error())
		})
	}
}

func Test_SearchQueryObjectType_ok(t *testing.T) {
	var tests = []struct {
		name     string
		val      []byte
		expected testSearchQueryObjectType
	}{
		{"partner", []byte(`{"test_type":"partner"}`), testSearchQueryObjectType{PartnerObjectType}},
		{"contract", []byte(`{"test_type":"contract"}`), testSearchQueryObjectType{ContractObjectType}},
		{"traffic_point", []byte(`{"test_type":"traffic_point"}`), testSearchQueryObjectType{TrafficPointObjectType}},
		{"logic_line", []byte(`{"test_type":"logic_line"}`), testSearchQueryObjectType{LogicLineObjectType}},
		{"sip_end_point", []byte(`{"test_type":"sip_end_point"}`), testSearchQueryObjectType{SIPEndPointObjectType}},
		{"number", []byte(`{"test_type":"number"}`), testSearchQueryObjectType{NumberObjectType}},
		{"contact", []byte(`{"test_type":"contact"}`), testSearchQueryObjectType{ContactObjectType}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v testSearchQueryObjectType
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			ctx := NewValidationCtx()
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}

func Test_SearchQueryObjectType_2json(t *testing.T) {
	var tests = []struct {
		name     string
		val      SearchQueryObjectType
		expected []byte
	}{
		{"bad1", -1, []byte(`""`)},
		{"bad2", 7, []byte(`""`)},
		{"partner", PartnerObjectType, []byte(`"partner"`)},
		{"contract", ContractObjectType, []byte(`"contract"`)},
		{"traffic_point", TrafficPointObjectType, []byte(`"traffic_point"`)},
		{"logic_line", LogicLineObjectType, []byte(`"logic_line"`)},
		{"sip_end_point", SIPEndPointObjectType, []byte(`"sip_end_point"`)},
		{"number", NumberObjectType, []byte(`"number"`)},
		{"contact", ContactObjectType, []byte(`"contact"`)},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := json.Marshal(test.val)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}
