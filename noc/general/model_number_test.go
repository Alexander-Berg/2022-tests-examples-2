package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_Number_Ok(t *testing.T) {
	tests := []struct {
		name     string
		val      []byte
		expected Number
	}{
		{"number", []byte(`{"number":"123456789"}`), Number{Number: "123456789"}},
		{"internal", []byte(`{"number":"123456789","internal_number":"123"}`),
			Number{Number: "123456789", InternalNumber: NewNullString("123")}},
		{"holder", []byte(`{"number":"123456789","holder":"123"}`),
			Number{Number: "123456789", Holder: NewCustom32Ref(123)}},
		{"priority", []byte(`{"number":"123456789","priority":"1"}`),
			Number{Number: "123456789", Priority: 1}},
		{"city", []byte(`{"number":"123456789","city":"1"}`),
			Number{Number: "123456789", City: 1}},
		{"description", []byte(`{"number":"123456789","description":"text"}`),
			Number{Number: "123456789", Description: NewNullString("text")}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctx := NewValidationCtx()
			var v Number
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}

func Test_NumberFromDBJson_ok(t *testing.T) {
	var tests = []struct {
		name     string
		j        string
		expected Number
	}{
		{
			"nulls",
			`{"object_id": "004bf157-3554-4a0b-a368-30fdffed9964", "parent_object_id": "c3d96dbb-95d7-40fd-8ac1-1679e07dacde",` +
				`"level": 5,"child_count": 0,"tags":[null],` +
				`"city": 0, "holder": null, "number": "74999999999", "priority": 0, "description": null, "internal_number": null}`,
			Number{
				ObjectUUID:       "004bf157-3554-4a0b-a368-30fdffed9964",
				ParentObjectUUID: "c3d96dbb-95d7-40fd-8ac1-1679e07dacde",
				Number:           "74999999999",
				TreeInfo:         &TreeInfo{ChildCount: 0, Level: 5},
			},
		},
		{
			"filled",
			`{"object_id": "004bf157-3554-4a0b-a368-30fdffed9964", "parent_object_id": "c3d96dbb-95d7-40fd-8ac1-1679e07dacde",` +
				`"level": 5, "child_count": 0, ` +
				`"tags":[{"id": 2,"tag": "tag1", "color": "#ff1122", "parent_id": 1, "description": "test"}],` +
				`"city": 15, "holder": 42, "number": "74999999999", "priority": 2, "description": "text1", "internal_number": "8765"}`,
			Number{
				ObjectUUID:       "004bf157-3554-4a0b-a368-30fdffed9964",
				ParentObjectUUID: "c3d96dbb-95d7-40fd-8ac1-1679e07dacde",
				Number:           "74999999999",
				InternalNumber:   NewNullString("8765"),
				Holder:           NewCustom32Ref(42),
				Description:      NewNullString("text1"),
				Priority:         2,
				City:             15,
				Tags: []Tag{
					{
						ID:          2,
						Tag:         "tag1",
						Color:       NewNullString("#ff1122"),
						ParentID:    NewCustom32Ref(1),
						Description: NewNullString("test"),
					},
				},
				TreeInfo: &TreeInfo{ChildCount: 0, Level: 5},
			},
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := NewNumberFromDBJson(test.j)
			require.NoError(t, err)
			require.Equal(t, test.expected, *v)
		})
	}
}

func Test_NumberFromDBJson_err(t *testing.T) {
	_, err := NewNumberFromDBJson("")
	require.Error(t, err)
	require.Equal(t, "unexpected end of JSON input", err.Error())
}
