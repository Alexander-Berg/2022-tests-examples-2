package blacklist_test

import (
	"encoding/json"
	"io/ioutil"
	"path/filepath"
	"testing"

	"github.com/santhosh-tekuri/jsonschema/v5"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/yadi/libs/versionarium"
)

const (
	blacklistPath = "security/yadi/blacklist/blacklist.json"
	schemaPath    = "security/yadi/blacklist/blacklist.schema.json"
)

type (
	Package struct {
		Manager          string `json:"manager"`
		PackageName      string `json:"package_name"`
		AffectedVersions string `json:"affected_versions"`
		Reason           string `json:"reason"`
	}
	Blacklist struct {
		Banned map[string][]Package `json:"banned"`
	}
)

func TestJsonSchema(t *testing.T) {
	schema, err := jsonschema.Compile(testDataPath(t, schemaPath))
	require.NoError(t, err)

	var blacklist interface{}
	readBlacklist(t, &blacklist)

	err = schema.Validate(blacklist)
	require.NoError(t, err)
}

func TestVersions(t *testing.T) {
	var blacklist Blacklist
	readBlacklist(t, &blacklist)

	for language, packages := range blacklist.Banned {
		for _, pkg := range packages {
			_, err := versionarium.NewRange(language, pkg.AffectedVersions)
			require.NoError(t, err, "failed to parse versions range %s", pkg.AffectedVersions)
		}
	}
}

func readBlacklist(t *testing.T, to interface{}) {
	data, err := ioutil.ReadFile(testDataPath(t, blacklistPath))
	require.NoError(t, err)

	err = json.Unmarshal(data, to)
	require.NoError(t, err)
}

func testDataPath(t *testing.T, arcadiaPath string) string {
	targetFile, err := filepath.Abs(yatest.SourcePath(arcadiaPath))
	require.NoError(t, err)
	return targetFile
}
