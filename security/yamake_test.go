package yamake_test

import (
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/yamake"
)

func TestParse(t *testing.T) {
	cases := []struct {
		filename   string
		TargetType yamake.YMakeTarget
		Name       string
		Version    string
		Owners     []string
	}{
		{
			filename:   "cpp-library.make",
			TargetType: yamake.TargetGenericLibrary,
			Name:       "",
			Version:    "",
			Owners:     []string{"g:security"},
		},
		{
			filename:   "cpp-program.make",
			TargetType: yamake.TargetGenericProgram,
			Name:       "",
			Version:    "",
			Owners:     []string{"g:security"},
		},
		{
			filename:   "go-library.make",
			TargetType: yamake.TargetGoLibrary,
			Name:       "",
			Version:    "",
			Owners:     []string{"buglloc", "g:security"},
		},
		{
			filename:   "go-program.make",
			TargetType: yamake.TargetGoProgram,
			Name:       "",
			Version:    "",
			Owners:     []string{"buglloc", "g:security"},
		},
		{
			filename:   "go-program-name.make",
			TargetType: yamake.TargetGoProgram,
			Name:       "go-program-name",
			Version:    "",
			Owners:     []string{"buglloc", "g:security"},
		},
		{
			filename:   "py3-program.make",
			TargetType: yamake.TargetPyProgram,
			Name:       "",
			Version:    "",
			Owners:     []string{"buglloc", "g:security"},
		},
		{
			filename:   "py2-program.make",
			TargetType: yamake.TargetPyProgram,
			Name:       "",
			Version:    "",
			Owners:     []string{"buglloc", "g:security"},
		},
		{
			filename:   "py2-library.make",
			TargetType: yamake.TargetPyLibrary,
			Name:       "",
			Version:    "",
			Owners:     []string{"g:security"},
		},
		{
			filename:   "py-library.make",
			TargetType: yamake.TargetPyLibrary,
			Name:       "",
			Version:    "",
			Owners:     []string{"g:security"},
		},
		{
			filename:   "py3-library.make",
			TargetType: yamake.TargetPyLibrary,
			Name:       "",
			Version:    "",
			Owners:     []string{"g:security"},
		},
		{
			filename:   "py23-library.make",
			TargetType: yamake.TargetPyLibrary,
			Name:       "",
			Version:    "",
			Owners:     []string{"g:security"},
		},
		{
			filename:   "py-library-version.make",
			TargetType: yamake.TargetPyLibrary,
			Name:       "",
			Version:    "1.4.3",
			Owners:     []string{"g:python-contrib", "orivej"},
		},
		{
			filename:   "py-library-version-name.make",
			TargetType: yamake.TargetPyLibrary,
			Name:       "py-library-version-name",
			Version:    "test.version",
		},
		{
			filename:   "pycrypto-library-owners.make",
			TargetType: yamake.TargetGenericLibrary,
			Name:       "",
			Version:    "2.5",
			Owners:     []string{"g:python-contrib", "torkve"},
		},
	}

	for _, tc := range cases {
		t.Run(tc.filename, func(t *testing.T) {
			targetPath := filepath.Join("testdata", tc.filename)

			ymake, err := yamake.ParseFile(targetPath)
			require.NoError(t, err)

			assert.Equal(t, tc.Name, ymake.Name, "invalid name")
			assert.Equal(t, tc.Version, ymake.Version, "invalid version")
			assert.EqualValues(t, tc.Owners, ymake.Owners, "invalid owners")
			assert.Equal(t, tc.TargetType, ymake.TargetType, "invalid type")
		})
	}
}
