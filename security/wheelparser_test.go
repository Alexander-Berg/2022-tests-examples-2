package pkgparser_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/yadi/libs/pypi/pkgparser"
)

func TestWheelClassic(t *testing.T) {
	metadata, err := os.Open(filepath.Join("testdata", "whl-classic-metadata.txt"))
	if !assert.NoError(t, err) {
		return
	}
	defer func() { _ = metadata.Close() }()

	pkgInfo, err := pkgparser.ParseWheelMetadata(metadata)
	if !assert.NoError(t, err, "failed to parse whl-classic-metadata.txt") {
		return
	}

	assert.Equal(t, "test-pkg", pkgInfo.Name)
	assert.Equal(t, "1.0.0", pkgInfo.Version)
	assert.Equal(t, "Apache Software License", pkgInfo.License)
	requires := pkgInfo.Requires
	assert.Equal(t, 1, len(requires), "whl-classic-metadata.txt must have ONE requires")
	assert.Equal(t, "chardet", requires[0].Name)
	assert.Equal(t, "<3.1.0,>=3.0.2", requires[0].Versions)

	extras := pkgInfo.Extras
	securityRequires, haveSecurity := extras["security"]
	assert.True(t, haveSecurity, "whl-classic-metadata.txt must have 'security' extras")
	assert.Equal(t, 2, len(securityRequires), "whl-classic-metadata.txt must have TWO requires in 'security' extras")
	assert.Equal(t, "pyOpenSSL", securityRequires[0].Name)
	assert.Equal(t, ">=0.14", securityRequires[0].Versions)
	assert.Equal(t, "cryptography", securityRequires[1].Name)
	assert.Equal(t, ">=1.3.4", securityRequires[1].Versions)
}

func TestWheelShortest(t *testing.T) {
	metadata, err := os.Open(filepath.Join("testdata", "whl-shortest-metadata.txt"))
	if !assert.NoError(t, err) {
		return
	}
	defer func() { _ = metadata.Close() }()

	pkgInfo, err := pkgparser.ParseWheelMetadata(metadata)
	if !assert.NoError(t, err, "failed to parse whl-shortest-metadata.txt") {
		return
	}

	assert.Equal(t, "test-pkg-wo-classifiers", pkgInfo.Name)
	assert.Equal(t, "1.1.0b", pkgInfo.Version)
	assert.Equal(t, "WTFPL", pkgInfo.License)
	assert.Empty(t, pkgInfo.Requires, "whl-shortest-metadata.txt must have not any requires")
}
