package model

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_ParnerFromDBJson_ok(t *testing.T) {
	var tests = []struct {
		name     string
		j        string
		expected Partner
	}{
		{
			name: "null description",
			j:    `{"object_id":"73f4294d-269a-4c7d-a393-13d63b68cdd4","name":"test_name","full_name":"test_full","code":"test_code","description":null}`,
			expected: Partner{
				"73f4294d-269a-4c7d-a393-13d63b68cdd4",
				"test_name",
				"test_full",
				"test_code",
				nil,
				nil,
				&TreeInfo{},
			},
		},
		{
			name: "with description",
			j:    `{"object_id":"73f4294d-269a-4c7d-a393-13d63b68cdd4","name":"test_name","full_name":"test_full","code":"test_code","description":"test_description"}`,
			expected: Partner{
				"73f4294d-269a-4c7d-a393-13d63b68cdd4",
				"test_name",
				"test_full",
				"test_code",
				NewNullString("test_description"),
				nil,
				&TreeInfo{},
			},
		},
		{
			name: "with tree info",
			j: `{"object_id":"73f4294d-269a-4c7d-a393-13d63b68cdd4","name":"test_name","full_name":"test_full",` +
				`"code":"test_code","description":"test_description","tags":[null],"child_count":2,"level":1}`,
			expected: Partner{
				"73f4294d-269a-4c7d-a393-13d63b68cdd4",
				"test_name",
				"test_full",
				"test_code",
				NewNullString("test_description"),
				nil,
				&TreeInfo{2, 1},
			},
		},
		{
			name: "with tags",
			j: `{"object_id":"73f4294d-269a-4c7d-a393-13d63b68cdd4","name":"test_name","full_name":"test_full",` +
				`"code":"test_code","description":"test_description",` +
				`"tags":[{"id": 2,"tag": "tag1", "color": "#ff1122", "parent_id": 1, "description": "test"}]}`,
			expected: Partner{
				"73f4294d-269a-4c7d-a393-13d63b68cdd4",
				"test_name",
				"test_full",
				"test_code",
				NewNullString("test_description"),
				[]Tag{
					{
						ID:          2,
						Tag:         "tag1",
						Color:       NewNullString("#ff1122"),
						ParentID:    NewCustom32Ref(1),
						Description: NewNullString("test"),
					},
				},
				&TreeInfo{0, 0},
			},
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := NewPartnerFromDBJson(test.j)
			require.NoError(t, err)
			require.Equal(t, test.expected, *v)
		})
	}
}

func Test_ParnerFromDBJson_err(t *testing.T) {
	_, err := NewPartnerFromDBJson("")
	require.Error(t, err)
	require.Equal(t, "unexpected end of JSON input", err.Error())
}
