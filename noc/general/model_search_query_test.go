package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_SearchQuery_err(t *testing.T) {
	var tests = []struct {
		name          string
		val           []byte
		unmarshalErr  string
		validationErr string
	}{
		{
			"empty value",
			[]byte(`{"value":""}`),
			"",
			"given string too short",
		},
		{
			"short value",
			[]byte(`{"value":"12"}`),
			"",
			"given string too short",
		},
		{
			"wrong type",
			[]byte(`{"object_types":["partner","test"]}`),
			"\"test\" wrong enum value",
			"",
		},
		{
			"null type",
			[]byte(`{"object_types":["partner",null]}`),
			"null wrong enum value",
			"",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v SearchQuery
			err := json.Unmarshal(test.val, &v)
			if test.unmarshalErr != "" {
				require.Error(t, err)
				require.Equal(t, test.unmarshalErr, err.Error())
			} else {
				require.NoError(t, err)
				ctx := NewValidationCtx()
				err = valid.Struct(ctx, v)
				require.Error(t, err)
				require.Equal(t, test.validationErr, err.Error())
			}
		})
	}
}

func Test_SearchQuery_ok(t *testing.T) {
	var tests = []struct {
		name     string
		val      []byte
		expected SearchQuery
	}{
		{
			"value",
			[]byte(`{"value":"1234567"}`),
			SearchQuery{Value: NewNullString("1234567")},
		},
		{
			"with empty type",
			[]byte(`{"value":"1234567","object_types":[]}`),
			SearchQuery{Value: NewNullString("1234567"), ObjectTypes: []SearchQueryObjectType{}},
		},
		{
			"with type",
			[]byte(`{"value":"1234567","object_types":["partner"]}`),
			SearchQuery{Value: NewNullString("1234567"), ObjectTypes: []SearchQueryObjectType{PartnerObjectType}},
		},
		{
			"with from_object",
			[]byte(`{"from_object":{"uuid":"73f4294d-269a-4c7d-a393-13d63b68cdd4","direction":"all_tree"}}`),
			SearchQuery{
				FromObject: &SearchQueryFromObject{
					UUID:      "73f4294d-269a-4c7d-a393-13d63b68cdd4",
					Direction: AllTreeSearchDirection,
				},
			},
		},
		{
			"with tags",
			[]byte(`{"with_tags":["tag1","tag2"]}`),
			SearchQuery{
				WithTags: []string{"tag1", "tag2"},
			},
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v SearchQuery
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			ctx := NewValidationCtx()
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}
