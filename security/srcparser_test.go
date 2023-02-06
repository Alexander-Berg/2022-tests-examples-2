package pkgparser_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/yadi/libs/pypi/pkgparser"
)

func TestSrcClassic(t *testing.T) {
	metadata, err := os.Open(filepath.Join("testdata", "src-classic-pkginfo.txt"))
	if !assert.NoError(t, err) {
		return
	}
	defer func() { _ = metadata.Close() }()

	pkgInfo := new(pkgparser.PkgInfo)
	err = pkgparser.ParseSrcPkgInfo(metadata, pkgInfo)
	if !assert.NoError(t, err, "failed to parse src-classic-pkginfo.txt") {
		return
	}

	assert.Equal(t, "test-pkg", pkgInfo.Name)
	assert.Equal(t, "2.1.1", pkgInfo.Version)
	assert.Equal(t, "Eiffel Forum License", pkgInfo.License)
}

func TestShortestClassic(t *testing.T) {
	metadata, err := os.Open(filepath.Join("testdata", "src-shortest-pkginfo.txt"))
	if !assert.NoError(t, err) {
		return
	}
	defer func() { _ = metadata.Close() }()

	pkgInfo := new(pkgparser.PkgInfo)
	err = pkgparser.ParseSrcPkgInfo(metadata, pkgInfo)
	if !assert.NoError(t, err, "failed to parse src-shortest-pkginfo.txt") {
		return
	}

	assert.Equal(t, "test-pkg-shortest", pkgInfo.Name)
	assert.Equal(t, "2.1.1-dev", pkgInfo.Version)
	assert.Equal(t, "Apache 1.0", pkgInfo.License)
}
