package unittest

import (
	"io/fs"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/tirole/internal/model"
)

func TestReadMapping(t *testing.T) {
	dir := "./"
	filename := dir + mappingFileName
	cleanup := func() {
		_ = os.Remove(filename)
	}
	cleanup()
	defer cleanup()

	_, err := readMapping(dir)
	require.ErrorContains(t, err, "failed to read file body './mapping.yaml'")

	require.NoError(t, ioutil.WriteFile(filename, []byte("kek"), fs.ModePerm))
	_, err = readMapping(dir)
	require.ErrorContains(t, err, "failed to parse file './mapping.yaml'")

	yamlConfig := `
slugs:
  some_slug_1:
    tvmid:
      - 42
  some_slug_2:
    tvmid:
      - 43
      - 44
`
	require.NoError(t, ioutil.WriteFile(filename, []byte(yamlConfig), fs.ModePerm))

	actual, err := readMapping(dir)
	require.NoError(t, err)
	require.EqualValues(t,
		map[string]model.Mapping{
			"some_slug_1": {42: nil},
			"some_slug_2": {43: nil, 44: nil},
		},
		actual,
	)
}
