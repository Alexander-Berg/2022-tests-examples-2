package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_Contact_Ok(t *testing.T) {
	tests := []struct {
		name     string
		val      []byte
		expected Contact
	}{
		{"type slug fio", []byte(`{"type_slug":"tech","full_name":"FIO1"}`),
			Contact{TypeSlug: "tech", FullName: "FIO1"}},
		{"contacts", []byte(`{"type_slug":"tech","full_name":"FIO1","contacts":[` +
			`{"info_type":"staff","data":"DATA1","description":"DESC1"},` +
			`{"info_type":"phone","data":"DATA2","description":"DESC2"},` +
			`{"info_type":"e-mail","data":"DATA3","description":"DESC3"},` +
			`{"info_type":"telegram","data":"DATA4","description":"DESC4"},` +
			`{"info_type":"skype","data":"DATA5","description":"DESC5"},` +
			`{"info_type":"whatsapp","data":"DATA6","description":"DESC6"}]}`),
			Contact{TypeSlug: "tech", FullName: "FIO1", Contacts: []ContactInfo{
				{InfoType: "staff", Data: "DATA1", Description: NewNullString("DESC1")},
				{InfoType: "phone", Data: "DATA2", Description: NewNullString("DESC2")},
				{InfoType: "e-mail", Data: "DATA3", Description: NewNullString("DESC3")},
				{InfoType: "telegram", Data: "DATA4", Description: NewNullString("DESC4")},
				{InfoType: "skype", Data: "DATA5", Description: NewNullString("DESC5")},
				{InfoType: "whatsapp", Data: "DATA6", Description: NewNullString("DESC6")},
			}}},
		{"data", []byte(`{"type_slug":"tech","full_name":"FIO1","data":"DATA1"}`),
			Contact{TypeSlug: "tech", FullName: "FIO1", Data: NewNullString("DATA1")}},
		{"uuid", []byte(`{"object_uuid":"e75d3cfb-2c0f-4bea-8473-f19047a85e7c",` +
			`"parent_object_uuid":"0fae6f76-1afb-4b1f-9a83-d41a19df5741","type_slug":"tech","full_name":"FIO1"}`),
			Contact{
				ObjectUUID:       "e75d3cfb-2c0f-4bea-8473-f19047a85e7c",
				ParentObjectUUID: "0fae6f76-1afb-4b1f-9a83-d41a19df5741",
				TypeSlug:         "tech",
				FullName:         "FIO1"}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			ctx := NewValidationCtx()
			var v Contact
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}

func Test_ContactFromDBJson_ok(t *testing.T) {
	var tests = []struct {
		name     string
		j        string
		expected Contact
	}{
		{"nulls",
			`{"tags":[null]}`,
			Contact{
				Contacts: []ContactInfo{},
				TreeInfo: &TreeInfo{},
			},
		},
		{"filled",
			`{"data": "data1", "type": 3, "object_id": "d5925831-c6b2-4761-8133-efc5e40fcbb1", ` +
				`"type_slug": "our_manager", "full_name": "Test Test FIO", ` +
				`"contacts": [{"data": "staff-login", "info_type": "staff", "description": "contact info desc"}], ` +
				`"level": 2, "child_count": 0, "parent_object_id": "5fdbd3ea-3541-4bca-8a42-f0092140cdcb",` +
				`"tags":[{"id": 2,"tag": "tag1", "color": "#ff1122", "parent_id": 1, "description": "test"}]}`,
			Contact{
				ObjectUUID:       "d5925831-c6b2-4761-8133-efc5e40fcbb1",
				ParentObjectUUID: "5fdbd3ea-3541-4bca-8a42-f0092140cdcb",
				TypeSlug:         "our_manager",
				FullName:         "Test Test FIO",
				Contacts: []ContactInfo{
					{
						InfoType:    "staff",
						Data:        "staff-login",
						Description: NewNullString("contact info desc"),
					},
				},
				Data: NewNullString("data1"),
				Tags: []Tag{
					{
						ID:          2,
						Tag:         "tag1",
						Color:       NewNullString("#ff1122"),
						ParentID:    NewCustom32Ref(1),
						Description: NewNullString("test"),
					},
				},
				TreeInfo: &TreeInfo{
					ChildCount: 0,
					Level:      2,
				},
			}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := NewContactFromDBJson(test.j)
			require.NoError(t, err)
			require.Equal(t, test.expected, *v)
		})
	}
}

func Test_ContactFromDBJson_err(t *testing.T) {
	_, err := NewContactFromDBJson("")
	require.Error(t, err)
	require.Equal(t, "unexpected end of JSON input", err.Error())
}
