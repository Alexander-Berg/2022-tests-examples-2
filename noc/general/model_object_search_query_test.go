package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_ObjectSearchQuery_ok(t *testing.T) {
	var tests = []struct {
		name string
		val  []byte
	}{
		{"empty", []byte(`{}`)},
		{"only type", []byte(`{"object_type":"partner"}`)},
		{
			"with from object",
			[]byte(`{"from_object":{"uuid":"73f4294d-269a-4c7d-a393-13d63b68cdd4","direction":"all_tree"}}`),
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v ObjectSearchQuery
			err := json.Unmarshal(test.val, &v)
			require.NoError(t, err)
			ctx := NewValidationCtx()
			err = valid.Struct(ctx, v)
			require.NoError(t, err)
		})
	}
}
