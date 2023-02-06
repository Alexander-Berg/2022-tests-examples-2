package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_LogicLine_ok(t *testing.T) {
	tests := []struct {
		name     string
		val      []byte
		expected LogicLine
	}{
		{"filled int",
			[]byte(`{"racktables_object_id":321,"our_ip":"1.1.1.1","our_port":123,"their_ip":"2.2.2.2","their_port":456}`),
			LogicLine{"", "",
				321, "1.1.1.1", 123, "2.2.2.2", 456,
				nil, nil}},
		{"filled string",
			[]byte(`{"racktables_object_id":"321","our_ip":"1.1.1.1","our_port":"123","their_ip":"2.2.2.2","their_port":"456"}`),
			LogicLine{"", "",
				321, "1.1.1.1", 123, "2.2.2.2", 456,
				nil, nil}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctx := NewValidationCtx()
			var v LogicLine
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}

func Test_LogicLine_err(t *testing.T) {
	var tests = []struct {
		name      string
		val       []byte
		expectedU string
		expectedV string
	}{
		{"string", []byte(`{"racktables_object_id":"err","our_ip":"1.1.1.1","our_port":"err2","their_ip":"2.2.2.2","their_port":"err3"}`),
			`CustomInt32: parsing "err": not a int32`, ""},
		{"min", []byte(`{"racktables_object_id":-321,"our_ip":"1.1.1.1","our_port":-123,"their_ip":"2.2.2.2","their_port":-456}`),
			"", "valid: value less than expected; valid: value less than expected; valid: value less than expected"},
		{"max", []byte(`{"racktables_object_id":321,"our_ip":"1.1.1.1","our_port":65536,"their_ip":"2.2.2.2","their_port":65536}`),
			"", "valid: value greater than expected; valid: value greater than expected"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v LogicLine
			err := json.Unmarshal(test.val, &v)
			if len(test.expectedU) > 0 {
				require.Error(t, err)
				require.Equal(t, test.expectedU, err.Error())
			}
			if err == nil && len(test.expectedV) > 0 {
				ctx := NewValidationCtx()
				err = valid.Struct(ctx, v)
				require.Error(t, err)
				require.Equal(t, test.expectedV, err.Error())
			}
		})
	}
}

func Test_NewLogicLineFromDBJson_ok(t *testing.T) {
	var tests = []struct {
		name     string
		j        string
		expected LogicLine
	}{
		{"nulls", `{"tags":[null]}`, LogicLine{TreeInfo: &TreeInfo{}}},
		{"filled",
			`{"racktables_object_id": 321, "our_ip": "1.1.1.1", "our_port": 123, "their_ip": "2.2.2.2", "their_port": 345, ` +
				`"level": 4, "child_count": 0,` +
				`"tags":[{"id": 2,"tag": "tag1", "color": "#ff1122", "parent_id": 1, "description": "test"}],` +
				` "object_id": "12a56d2c-ee32-43b8-8f17-11cd28a64d01", "parent_object_id": "a6260416-b619-4d66-ab1c-14581773b70a"}`,
			LogicLine{
				RacktablesObjectID: 321,
				OurIP:              "1.1.1.1",
				OurPort:            123,
				TheirIP:            "2.2.2.2",
				TheirPort:          345,
				ObjectUUID:         "12a56d2c-ee32-43b8-8f17-11cd28a64d01",
				ParentObjectUUID:   "a6260416-b619-4d66-ab1c-14581773b70a",
				Tags: []Tag{
					{
						ID:          2,
						Tag:         "tag1",
						Color:       NewNullString("#ff1122"),
						ParentID:    NewCustom32Ref(1),
						Description: NewNullString("test"),
					},
				},
				TreeInfo: &TreeInfo{0, 4}}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := NewLogicLineFromDBJson(test.j)
			require.NoError(t, err)
			require.Equal(t, test.expected, *v)
		})
	}
}

func Test_NewLogicLineFromDBJson_err(t *testing.T) {
	_, err := NewLogicLineFromDBJson("")
	require.Error(t, err)
	require.Equal(t, "unexpected end of JSON input", err.Error())
}
