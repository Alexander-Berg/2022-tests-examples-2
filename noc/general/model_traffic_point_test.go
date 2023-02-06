package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_TrafficPoint_ok(t *testing.T) {
	tests := []struct {
		name     string
		val      []byte
		expected TrafficPoint
	}{
		{"type 100",
			[]byte(`{"connection_type":100}`),
			TrafficPoint{"", "", 100, nil, nil, nil,
				nil, nil, nil}},
		{"type str 100",
			[]byte(`{"connection_type":"100"}`),
			TrafficPoint{"", "", 100, nil, nil, nil,
				nil, nil, nil}},
		{"type 200",
			[]byte(`{"connection_type":200}`),
			TrafficPoint{"", "", 200, nil, nil, nil,
				nil, nil, nil}},
		{"type 250",
			[]byte(`{"connection_type":250}`),
			TrafficPoint{"", "", 250, nil, nil, nil,
				nil, nil, nil}},
		{"type 300",
			[]byte(`{"connection_type":300}`),
			TrafficPoint{"", "", 300, nil, nil, nil,
				nil, nil, nil}},
		{"type 350",
			[]byte(`{"connection_type":350}`),
			TrafficPoint{"", "", 350, nil, nil, nil,
				nil, nil, nil}},
		{"type 400",
			[]byte(`{"connection_type":400}`),
			TrafficPoint{"", "", 400, nil, nil, nil,
				nil, nil, nil}},
		{"type 450",
			[]byte(`{"connection_type":450}`),
			TrafficPoint{"", "", 450, nil, nil, nil,
				nil, nil, nil}},
		{"description",
			[]byte(`{"connection_type":100,"description":"text1"}`),
			TrafficPoint{"", "", 100, nil, nil, nil,
				NewNullString("text1"), nil, nil}},
		{"cl cps",
			[]byte(`{"connection_type":100,"cl":12,"cps":34}`),
			TrafficPoint{"", "", 100, NewCustom32Ref(12),
				NewCustom32Ref(34), nil, nil, nil, nil}},
		{"yav",
			[]byte(`{"connection_type":100,"yav":"secret1"}`),
			TrafficPoint{"", "", 100, nil, nil,
				NewNullString("secret1"), nil, nil, nil}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctx := NewValidationCtx()
			var v TrafficPoint
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}

func Test_TrafficPoint_err(t *testing.T) {
	var tests = []struct {
		name     string
		val      []byte
		expected string
	}{
		{"string", []byte(`{"connection_type":"err"}`),
			"EnumConnType: parsing \"err\": not a int32"},
		{"not in enum", []byte(`{"connection_type":"10"}`),
			"EnumConnType: \"10\" wrong enum value"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v TrafficPoint
			err := json.Unmarshal(test.val, &v)
			require.Error(t, err)
			require.Equal(t, test.expected, err.Error())
		})
	}
}

func Test_NewTrafficPointFromDBJson_ok(t *testing.T) {
	var tests = []struct {
		name     string
		j        string
		expected TrafficPoint
	}{
		{"nulls",
			`{"cl": null, "cps": null, "yav": null, "name": null, "type": 100,` +
				`"level":4,"child_count":0,"tags":[null],` +
				` "object_id": "12a56d2c-ee32-43b8-8f17-11cd28a64d01", "parent_object_id": "a6260416-b619-4d66-ab1c-14581773b70a"}`,
			TrafficPoint{
				ConnType:         100,
				ObjectUUID:       "12a56d2c-ee32-43b8-8f17-11cd28a64d01",
				ParentObjectUUID: "a6260416-b619-4d66-ab1c-14581773b70a",
				TreeInfo:         &TreeInfo{0, 4}}},
		{"filled",
			`{"cl": 12, "cps": 34, "yav": "secret1", "name": "desc text", "type": 250, "level": 4, "child_count": 1,` +
				`"tags":[{"id": 2,"tag": "tag1", "color": "#ff1122", "parent_id": 1, "description": "test"}],` +
				` "object_id": "12a56d2c-ee32-43b8-8f17-11cd28a64d01", "parent_object_id": "a6260416-b619-4d66-ab1c-14581773b70a"}`,
			TrafficPoint{
				ConnType:         250,
				Description:      NewNullString("desc text"),
				Cl:               NewCustom32Ref(12),
				Cps:              NewCustom32Ref(34),
				Yav:              NewNullString("secret1"),
				ObjectUUID:       "12a56d2c-ee32-43b8-8f17-11cd28a64d01",
				ParentObjectUUID: "a6260416-b619-4d66-ab1c-14581773b70a",
				Tags: []Tag{
					{
						ID:          2,
						Tag:         "tag1",
						Color:       NewNullString("#ff1122"),
						ParentID:    NewCustom32Ref(1),
						Description: NewNullString("test"),
					},
				},
				TreeInfo: &TreeInfo{1, 4}}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := NewTrafficPointFromDBJson(test.j)
			require.NoError(t, err)
			require.Equal(t, test.expected, *v)
		})
	}
}

func Test_NewTrafficPointFromDBJson_err(t *testing.T) {
	_, err := NewTrafficPointFromDBJson("")
	require.Error(t, err)
	require.Equal(t, "unexpected end of JSON input", err.Error())
}
