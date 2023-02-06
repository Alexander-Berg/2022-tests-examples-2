package readers

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/fs"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/libs/utils/runtimeconfig/v2"
)

func TestSettingsParser(t *testing.T) {
	fileInfo := fs.NewVirtualFileInfo("/opt/www/bases/madm/testing_ready/testFile.json", time.Now())
	fileContentsAsString := `{
		"All": [
			{
				"StringField": "abc",
				"float64Field": -4.5,
				"ColorField": "#aaffeecc",
				"extraField": 123
			},
			{
				"stringField": "cba",
				"disabled": "1"
			}
		]
}`
	fileContents := []byte(fileContentsAsString)
	file := fs.NewVirtualFile(fileContents, fileInfo)
	vfs, err := fs.NewVirtualFileSystem(file)
	require.NoError(t, err)
	type testType struct {
		StringField       string
		Float64FieldByTag float64 `madm:"float64Field"`
		ColorField        Color
		MissingField      string
		MissingFieldByPtr *string
	}
	expectedValue := testType{
		StringField:       "abc",
		Float64FieldByTag: -4.5,
		ColorField:        Color{"#aaffeecc"},
	}
	values := []*testType{}
	pointerToData, err := NewPointerToData(&values)
	require.NoError(t, err)

	logger := log3.NewLoggerStub()
	fileWatcher, err := runtimeconfig.NewFileWatcher(vfs, logger, nil, nil)
	require.NoError(t, err)

	settingsGetter, err := NewSettingsGetter("testFile", "", common.Development, pointerToData, NewDisabledFilter(), logger, fileWatcher)
	require.NoError(t, err)
	settingsGetter.WaitForInit()

	require.NotEmpty(t, values)
	assert.Len(t, values, 1)
	assert.Equal(t, expectedValue, *values[0])
}
