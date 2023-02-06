package reqs

import (
	"encoding/json"
	"errors"
	"testing"

	"github.com/santhosh-tekuri/jsonschema/v5"
	"github.com/stretchr/testify/require"
)

func TestValidateScheme(t *testing.T) {
	cases := []struct {
		Name string
		Body string
		Err  string
	}{
		{
			Name: "system_slug: missing",
			Body: `{"some_field":123}`,
			Err:  "system_slug",
		},
		{
			Name: "roles: missing",
			Body: `{"system_slug":123}`,
			Err:  "roles",
		},
		{
			Name: "system_slug: type",
			Body: `{"system_slug":123,"roles":456}`,
			Err:  "system_slug",
		},
		{
			Name: "system_slug: length",
			Body: `{"system_slug":"","roles":{}}`,
			Err:  "system_slug",
		},
		{
			Name: "revision: missing",
			Body: `{"system_slug":"123","roles":{}}`,
			Err:  "revision",
		},
		{
			Name: "born_date: missing",
			Body: `{"system_slug":"123","roles":{"revision": false}}`,
			Err:  "born_date",
		},
		{
			Name: "revision: type",
			Body: `{"system_slug":"123","roles":{"revision": false, "born_date": false}}`,
			Err:  "revision",
		},
		{
			Name: "revision: min value",
			Body: `{"system_slug":"123","roles":{"revision": 0, "born_date": false}}`,
			Err:  "revision",
		},
		{
			Name: "born_date: type",
			Body: `{"system_slug":"123","roles":{"revision": 16, "born_date": false}}`,
			Err:  "born_date",
		},
		{
			Name: "born_date: min value",
			Body: `{"system_slug":"123","roles":{"revision": 16, "born_date": 0}}`,
			Err:  "born_date",
		},
		{
			Name: "OK",
			Body: `{"system_slug":"123","roles":{"revision": 16, "born_date": 16}}`,
		},
		// TODO: cover rest part of schema
		// {
		// 	Body: `{"system_slug":"foo","roles":{"revision": 161,"born_date": 161,"tvm":{"1":{"kek":[]}}}}`,
		// },
	}

	for _, c := range cases {
		var v interface{}
		err := json.Unmarshal([]byte(c.Body), &v)
		require.NoError(t, err, c.Name)

		err = UploadRolesSchema.Validate(v)
		if c.Err != "" {
			var verr *jsonschema.ValidationError
			require.True(t, errors.As(err, &verr))

			require.NotEmpty(t, verr.Causes, c.Name)
			errs := ""
			for _, e := range verr.Causes {
				errs += e.Error() + "; "
			}
			require.Contains(t, errs, c.Err, c.Name)
		} else {
			require.NoError(t, err, c.Name)
		}
	}
}
