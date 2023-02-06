package lineage_test

import (
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/lineage"
)

func TestAlpineRelease(t *testing.T) {
	detected := lineage.ParseAlpineRelease(filepath.Join("testdata", "alpine-release"))
	if !assert.NotNil(t, detected) {
		return
	}

	assert.Equal(t, lineage.Alpine, detected.Family)
	assert.Equal(t, "3.7.0", detected.Release)
	assert.Equal(t, "v3.7", detected.Codename)
}

func TestDebianVersion(t *testing.T) {
	type testCase struct {
		VersionFile string
		Family      string
		Release     string
		Codename    string
	}

	testCases := []testCase{
		{
			VersionFile: "debian_version-stretch",
			Family:      lineage.Debian,
			Release:     "9.9",
			Codename:    "stretch",
		},
		{
			VersionFile: "debian_version-sid",
			Family:      lineage.Debian,
			Release:     "bullseye/sid",
			Codename:    "sid",
		},
	}

	for _, tc := range testCases {
		detected := lineage.ParseDebianVersion(filepath.Join("testdata", tc.VersionFile))
		require.NotNil(t, detected, "failed to parse: %s", tc.VersionFile)
		require.Equal(t, tc.Family, detected.Family, "parse family for %s", tc.VersionFile)
		require.Equal(t, tc.Release, detected.Release, "parse release for %s", tc.VersionFile)
		require.Equal(t, tc.Codename, detected.Codename, "parse codename for %s", tc.VersionFile)
	}
}

func TestLsbRelease(t *testing.T) {
	type testCase struct {
		ReleaseFile string
		Family      string
		Release     string
		Codename    string
	}

	testCases := []testCase{
		{
			ReleaseFile: "lsb-release-arch",
			Family:      lineage.ArchLinux,
			Release:     "rolling",
		},
		{
			ReleaseFile: "lsb-release-cosmic",
			Family:      lineage.Ubuntu,
			Release:     "18.10",
			Codename:    "cosmic",
		},
		{
			ReleaseFile: "lsb-release-bionic",
			Family:      lineage.Ubuntu,
			Release:     "18.04",
			Codename:    "bionic",
		},
		{
			ReleaseFile: "lsb-release-precise",
			Family:      lineage.Ubuntu,
			Release:     "12.04",
			Codename:    "precise",
		},
	}

	for _, tc := range testCases {
		detected := lineage.ParseLsbRelease(filepath.Join("testdata", tc.ReleaseFile))
		require.NotNil(t, detected, "failed to parse: %s", tc.ReleaseFile)
		require.Equal(t, tc.Family, detected.Family, "parse family for %s", tc.ReleaseFile)
		require.Equal(t, tc.Release, detected.Release, "parse release for %s", tc.ReleaseFile)
		require.Equal(t, tc.Codename, detected.Codename, "parse codename for %s", tc.ReleaseFile)
	}
}

func TestOsRelease(t *testing.T) {
	type testCase struct {
		ReleaseFile string
		Family      string
		Release     string
		Codename    string
	}

	testCases := []testCase{
		{
			ReleaseFile: "os-release-arch",
			Family:      lineage.ArchLinux,
		},
		{
			ReleaseFile: "os-release-alpine-3.7",
			Family:      lineage.Alpine,
			Release:     "3.7.0",
			Codename:    "v3.7",
		},
		{
			ReleaseFile: "os-release-alpine-3.11.3",
			Family:      lineage.Alpine,
			Release:     "3.11.3",
			Codename:    "v3.11",
		},
		{
			ReleaseFile: "os-release-centos",
			Family:      lineage.CentOS,
			Release:     "7",
		},
		{
			ReleaseFile: "os-release-debian",
			Family:      lineage.Debian,
			Release:     "10",
			Codename:    "buster",
		},
		{
			ReleaseFile: "os-release-debian-no-codename",
			Family:      lineage.Debian,
			Release:     "9",
			Codename:    "stretch",
		},
		{
			ReleaseFile: "os-release-ubuntu",
			Family:      lineage.Ubuntu,
			Release:     "18.10",
			Codename:    "cosmic",
		},
		{
			ReleaseFile: "os-release-ubuntu-no-codename",
			Family:      lineage.Ubuntu,
			Release:     "16.04.6",
			Codename:    "xenial",
		},
	}

	for _, tc := range testCases {
		detected := lineage.ParseOsRelease(filepath.Join("testdata", tc.ReleaseFile))
		require.NotNil(t, detected, "failed to parse: %s", tc.ReleaseFile)
		require.Equal(t, tc.Family, detected.Family, "parse family for %s", tc.ReleaseFile)
		require.Equal(t, tc.Release, detected.Release, "parse release for %s", tc.ReleaseFile)
		require.Equal(t, tc.Codename, detected.Codename, "parse codename for %s", tc.ReleaseFile)
	}
}
