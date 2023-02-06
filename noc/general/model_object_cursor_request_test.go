package model

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/valid"
)

func Test_ObjectCursorRequest_err(t *testing.T) {
	var tests = []struct {
		name          string
		val           []byte
		unmarshalErr  string
		validationErr string
	}{
		{
			"empty string",
			[]byte(``),
			"unexpected end of JSON input",
			"",
		},
		{
			"limit less than expected (string)",
			[]byte(`{"limit":"-1"}`),
			"",
			"valid: value less than expected",
		},
		{
			"limit greater than expected",
			[]byte(`{"limit":10001}`),
			"",
			"valid: value greater than expected",
		},
		{
			"cursor less than expected",
			[]byte(`{"cursor":-1}`),
			"",
			"valid: value less than expected",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			var v ObjectCursorRequest
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
