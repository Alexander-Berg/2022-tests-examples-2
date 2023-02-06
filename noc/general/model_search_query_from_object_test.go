package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_SearchQueryFromObject_err(t *testing.T) {
	var tests = []struct {
		name          string
		val           []byte
		unmarshalErr  string
		validationErr string
	}{
		{
			"not string direction",
			[]byte(`{"uuid":"bad","direction":[]}`),
			"json: cannot unmarshal array into Go struct field SearchQueryFromObject.direction of type string",
			"",
		},
		{
			"wrong direction",
			[]byte(`{"uuid":"bad","direction":"foo"}`),
			"\"foo\" wrong enum value",
			"",
		},
		{
			"wrong uuid",
			[]byte(`{"uuid":"bad","direction":"up_tree"}`),
			"",
			"invalid string length",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v SearchQueryFromObject
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

func Test_SearchQueryFromObject_ok(t *testing.T) {
	var tests = []struct {
		name     string
		val      []byte
		expected SearchQueryFromObject
	}{
		{
			"valid up_tree",
			[]byte(`{"uuid":"73f4294d-269a-4c7d-a393-13d63b68cdd4","direction":"up_tree"}`),
			SearchQueryFromObject{"73f4294d-269a-4c7d-a393-13d63b68cdd4", UpTreeSearchDirection},
		},
		{
			"valid down_tree",
			[]byte(`{"uuid":"73f4294d-269a-4c7d-a393-13d63b68cdd4","direction":"down_tree"}`),
			SearchQueryFromObject{"73f4294d-269a-4c7d-a393-13d63b68cdd4", DownTreeSearchDirection},
		},
		{
			"valid all_tree",
			[]byte(`{"uuid":"73f4294d-269a-4c7d-a393-13d63b68cdd4","direction":"all_tree"}`),
			SearchQueryFromObject{"73f4294d-269a-4c7d-a393-13d63b68cdd4", AllTreeSearchDirection},
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v SearchQueryFromObject
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			ctx := NewValidationCtx()
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}

func Test_SearchDirection_2json(t *testing.T) {
	var tests = []struct {
		name     string
		val      SearchDirection
		expected []byte
	}{
		{"bad1", -1, []byte(`""`)},
		{"bad2", 3, []byte(`""`)},
		{"up_tree", UpTreeSearchDirection, []byte(`"up_tree"`)},
		{"down_tree", DownTreeSearchDirection, []byte(`"down_tree"`)},
		{"all_tree", AllTreeSearchDirection, []byte(`"all_tree"`)},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			v, err := json.Marshal(test.val)
			require.NoError(t, err)
			require.Equal(t, test.expected, v)
		})
	}
}
