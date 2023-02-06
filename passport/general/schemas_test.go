package yasmsinternal

import (
	"testing"

	"github.com/santhosh-tekuri/jsonschema/v5"
	"github.com/stretchr/testify/require"
)

type TestValidateCase struct {
	body   []byte
	schema *jsonschema.Schema
	err    string
}

func (c *TestValidateCase) run(t *testing.T, idx int) {
	err := validate(c.schema, c.body)
	if c.err == "" {
		require.NoError(t, err, idx)
	} else {
		require.Error(t, err, idx)
		require.Contains(t, err.Error(), c.err, idx)
	}
}

func TestValidate_ChangeInfo(t *testing.T) {
	cases := []TestValidateCase{
		{
			body:   []byte(`{"issue": ["PASSP-1", "PASSP-23455"], "comment": "update routes"}`),
			schema: changeInfoSchema,
		},
		{
			body:   []byte(`{"issue": "PASSP-1", "comment": "update routes"}`),
			schema: changeInfoSchema,
			err:    "expected array, but got string",
		},
		{
			body:   []byte(`{"issue": ["111-1", "PASSP-2"], "comment": "update routes"}`),
			schema: changeInfoSchema,
			err:    "does not match pattern",
		},
		{
			body:   []byte(`{"issue": ["PASSP-1234", "PASSP2"], "comment": "update routes"}`),
			schema: changeInfoSchema,
			err:    "does not match pattern",
		},
	}

	for idx, c := range cases {
		c.run(t, idx)
	}
}
