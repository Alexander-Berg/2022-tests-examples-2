package packages_test

import (
	"encoding/json"
	"io/ioutil"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/pkg/cfgvalid"
)

type PkgJSON struct {
	Meta struct {
		Name        string `json:"name"`
		Maintainer  string `json:"maintainer"`
		Description string `json:"description"`
		Homepage    string `json:"homepage"`
		Version     string `json:"version"`
	} `json:"meta"`

	Build struct {
		Targets         []string `json:"targets"`
		BuildType       string   `json:"build_type"`
		TargetPlatforms []string `json:"target-platforms"`
	} `json:"build"`

	Data []struct {
		Source struct {
			Type string `json:"type"`
			Path string `json:"path"`
		} `json:"source"`

		Destination struct {
			Path string `json:"path"`
		} `json:"destination"`
	} `json:"data"`
}

type Pkg struct {
	Name          string
	PkgJSONPath   string
	GideonCfgPath string
}

var pkgs = []Pkg{
	{
		Name:          "yandex-gideon",
		PkgJSONPath:   "yandex-gideon/pkg.json",
		GideonCfgPath: "yandex-gideon/conf.d",
	},
	{
		Name:          "yandex-gideon-systemd",
		PkgJSONPath:   "yandex-gideon-systemd/pkg.json",
		GideonCfgPath: "yandex-gideon-systemd/etc/gideon",
	},
	{
		Name:          "yandex-gideon-bundle",
		PkgJSONPath:   "yandex-gideon-bundle/pkg.json",
		GideonCfgPath: "yandex-gideon-bundle/etc/gideon",
	},
	{
		Name:          "yandex-gideon-mdb-bundle",
		PkgJSONPath:   "yandex-gideon-mdb-bundle/pkg.json",
		GideonCfgPath: "yandex-gideon-mdb-bundle/etc/gideon",
	},
	{
		Name:          "yandex-gideon-mds-bundle",
		PkgJSONPath:   "yandex-gideon-mds-bundle/pkg.json",
		GideonCfgPath: "yandex-gideon-mds-bundle/etc/gideon",
	},
	{
		Name:          "yandex-gideon-ydb-bundle",
		PkgJSONPath:   "yandex-gideon-ydb-bundle/pkg.json",
		GideonCfgPath: "yandex-gideon-ydb-bundle/etc/gideon",
	},
}

func TestPkgs(t *testing.T) {
	for _, pkg := range pkgs {
		t.Run(pkg.Name, func(t *testing.T) {
			require.NotEmpty(t, pkg.Name)
			require.NotEmpty(t, pkg.PkgJSONPath)
			require.NotEmpty(t, pkg.GideonCfgPath)
		})
	}
}

func TestPkgJSON(t *testing.T) {
	for _, pkg := range pkgs {
		t.Run(pkg.Name, func(t *testing.T) {
			rawPkgJSON, err := ioutil.ReadFile(pkg.PkgJSONPath)
			require.NoError(t, err)

			var pkgJSON PkgJSON
			err = json.Unmarshal(rawPkgJSON, &pkgJSON)
			require.NoError(t, err)

			require.NotEmpty(t, pkgJSON.Meta.Name, "name")
			require.NotEmpty(t, pkgJSON.Meta.Version, "version")
			require.NotEmpty(t, pkgJSON.Meta.Maintainer, "maintainer")

			require.NotEmpty(t, pkgJSON.Data, "data")
		})
	}
}

func TestConfigs(t *testing.T) {
	for _, pkg := range pkgs {
		t.Run(pkg.Name, func(t *testing.T) {
			matches, err := filepath.Glob(filepath.Join(pkg.GideonCfgPath, "*.yaml"))
			require.NoError(t, err)
			require.NotEmpty(t, matches)

			for _, match := range matches {
				t.Run(match, func(t *testing.T) {
					err := cfgvalid.ValidateConfig(match)
					require.NoError(t, err)
				})
			}
		})
	}
}
