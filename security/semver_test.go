package versionarium

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestVersionString(t *testing.T) {
	var cases = []struct {
		in, want string
		mustFail bool
	}{
		{"0.0.2", "0.0.2", false},
		{"0.1", "0.1.0", false},
		{"1", "1.0.0", false},
		{"1.2.3-alpha", "1.2.3-alpha", false},
		{"1.2.3-alpha+test", "1.2.3-alpha+test", false},
		{"1.2.12-beta.alpha.1.1", "1.2.12-beta.alpha.1.1", false},
		{"v0.1.1", "0.1.1", false},
		{"1.2.3-alpha:123", "", true},
		{"1.2.3.4", "", true},
		{"1.1.", "", true},
		{"1.1.1.", "", true},
		{"1.1.1.1.", "", true},
	}
	for _, tc := range cases {
		t.Run(tc.in, func(t *testing.T) {
			ver, err := newSemverVersion(tc.in, false)
			if tc.mustFail {
				require.Error(t, err)
				return
			}
			require.NoError(t, err)
			require.Equal(t, tc.want, ver.String())
		})
	}
}

func TestVersionReleaseInfo(t *testing.T) {
	var cases = []struct {
		ver, info string
	}{
		{"1.5.1", ""},
		{"1.5.1-beta", "beta"},
		{"1.5.1-alpha.1", "alpha.1"},
		{"1.5.1-beta.1.4", "beta.1.4"},
		{"1.5.1-beta.1.123456789", "beta.1.123456789"},
		{"1.5.1-beta.alpha.1", "beta.alpha.1"},
		{"1.5.1-beta.1+20130313144700", "beta.1"},
		{"1.5.1-beta.1+exp.sha.5114f85", "beta.1"},
		{"1.0.0-rc.1", "rc.1"},
	}
	for _, tc := range cases {
		t.Run(tc.ver, func(t *testing.T) {
			ver, err := newSemverVersion(tc.ver, false)
			require.NoError(t, err)
			require.Equal(t, tc.info, ver.ReleaseInfo())
		})
	}
}

func TestVersionBuildInfo(t *testing.T) {
	var cases = []struct {
		ver, info string
	}{
		{"1.5.1-alpha.1", ""},
		{"1.5.1-beta.alpha.1+123", "123"},
		{"1.5.1-beta.1+20130313144700", "20130313144700"},
		{"1.5.1-beta.1+exp.sha.5114f85", "exp.sha.5114f85"},
		{"1.5.1-beta.1+exp.sha1.5114f84", "exp.sha1.5114f84"},
		{"1.5.1-beta.1+exp.sha256", "exp.sha256"},
	}
	for _, tc := range cases {
		t.Run(tc.ver, func(t *testing.T) {
			ver, err := newSemverVersion(tc.ver, false)
			require.NoError(t, err)
			require.Equal(t, tc.info, ver.BuildInfo())
		})
	}
}

func TestVersionCompare(t *testing.T) {
	var cases = []struct {
		a, b       string
		resolution int
	}{
		{"1", "1", 0},
		{"1", "3", -1},
		{"1.5", "0.8", 1},
		{"1.5", "1.3", 1},
		{"1.2", "2.2", -1},
		{"3.0", "1.5", 1},
		{"1.5", "1.5", 0},
		{"1.0.9", "1.0.0", 1},
		{"1.0.9", "1.0.9", 0},
		{"1.1.5", "1.1.9", -1},
		{"1.2.2", "1.1.9", 1},
		{"1.2.2", "1.2.9", -1},
		{"1", "2", -1},
		{"1", "1.0.0", 0},
		{"1", "0", 1},
	}
	for _, tc := range cases {
		t.Run(tc.a, func(t *testing.T) {
			a, err := newSemverVersion(tc.a, false)
			require.NoError(t, err)
			b, err := newSemverVersion(tc.b, false)
			require.NoError(t, err)
			require.Equal(t, tc.resolution, a.Compare(b))
		})
	}
}

func TestVersionCompareWithMeta(t *testing.T) {
	var cases = []struct {
		a, b       string
		resolution int
	}{
		{"1.5.1", "1.5.1-beta", 1},
		{"1.5.1-beta", "1.5.1", -1},
		{"1.5.1-beta", "1.5.1-beta", 0},
		{"1.5.1-beta", "1.5.1-alpha", 1},
		{"1.5.1-beta.1", "1.5.1-alpha.1", 1},
		{"1.5.1-beta.1", "1.5.1-beta.0", 1},
		{"1.5.1-beta.1.5", "1.5.1-beta.1.5", 0},
		{"1.5.1-beta.1.5", "1.5.1-beta.1.4", 1},
		{"1.5.1-beta.1.0", "1.5.1-beta.1.4", -1},
		{"1.5.1-beta.1.0", "1.5.1-alpha.1.0", 1},
		{"1.5.1-beta.1.100", "1.5.1-alpha.1.99", 1},
		{"1.5.1-beta.1.123456789", "1.5.1-alpha.1.12345678", 1},
		{"1.5.1-beta.alpha.1", "1.5.1-beta.alpha.1.12345678", -1},
		{"1.5.1-beta.alpha.1", "1.5.1-beta.alpha.1+123", 0},
		{"1.5.1-beta.1+20130313144700", "1.5.1-beta.1+20120313144700", 0},
		{"1.5.1-beta.1+20130313144700", "1.5.1-beta.1+20130313144700", 0},
		{"1.5.1-beta.1+20130313144700", "1.5.1-beta.1+exp.sha.5114f85", 0},
		{"1.5.1-beta.1+exp.sha.5114f85", "1.5.1-beta.1+exp.sha.5114f84", 0},
		{"1.5.1-beta.1+exp.sha.5114f85", "1.5.1-beta.1+exp.sha1.5114f84", 0},
		{"1.5.1-beta.1+exp.sha", "1.5.1-beta.1+exp.sha256", 0},
		{"1.5.1-alpha.beta", "1.5.1-1.beta", 1},
		{"1.0.0-alpha", "1.0.0-alpha.1", -1},
		{"1.0.0-alpha.1", "1.0.0-alpha.beta", -1},
		{"1.0.0-alpha.beta", "1.0.0-beta", -1},
		{"1.0.0-beta", "1.0.0-beta.2", -1},
		//{"1.0.0-beta.2", "1.0.0-beta.11", -1}, //TODO(melkikh): oh, semver is failing here
		{"1.0.0-beta.11", "1.0.0-rc.1", -1},
		{"1.0.0-rc.1", "1.0.0", -1},
	}
	for _, tc := range cases {
		t.Run(tc.a, func(t *testing.T) {
			a, err := newSemverVersion(tc.a, false)
			require.NoError(t, err)
			b, err := newSemverVersion(tc.b, false)
			require.NoError(t, err)
			require.Equal(t, tc.resolution, a.Compare(b))
		})
	}
}

func TestRangeCheck(t *testing.T) {
	var cases = []struct {
		constraint, version string
		check               bool
	}{
		// from https://github.com/Masterminds/semver/blob/master/constraints_test.go
		{"=2.0.0", "1.2.3", false},
		{"=2.0.0", "2.0.0", true},
		{"=2.0", "1.2.3", false},
		{"=2.0", "2.0.0", true},
		{"=2.0", "2.0.1", true},
		{"4.1", "4.1.0", true},
		{"!=4.1.0", "4.1.0", false},
		{"!=4.1.0", "4.1.1", true},
		{"!=4.1", "4.1.0", false},
		{"!=4.1", "4.1.1", false},
		{"!=4.1", "5.1.0-alpha.1", false},
		//{"!=4.1-alpha", "4.1.0", true}, //TODO(melkikh): semver returns other result
		{"!=4.1", "5.1.0", true},
		//{"<11", "0.1.0", true}, //TODO(melkikh): semver returns other result
		//{"<11", "11.1.0", false}, //TODO(melkikh): semver returns other result
		//{"<1.1", "0.1.0", true}, //TODO(melkikh): semver returns other result
		//{"<1.1", "1.1.0", false}, //TODO(melkikh): semver returns other result
		//{"<1.1", "1.1.1", false}, //TODO(melkikh): semver returns other result
		{"<=11", "1.2.3", true},
		{"<=11", "12.2.3", false},
		{"<=11", "11.2.3", true},
		{"<=1.1", "1.2.3", false},
		{"<=1.1", "0.1.0", true},
		{"<=1.1", "1.1.0", true},
		{"<=1.1", "1.1.1", true},
		{">1.1", "4.1.0", true},
		{">1.1", "1.1.0", false},
		{">0", "0", false},
		{">0", "1", true},
		//{">0", "0.0.1-alpha", false}, //TODO(melkikh): semver returns other result
		//{">0.0", "0.0.1-alpha", false}, //TODO(melkikh): semver returns other result
		//{">0-0", "0.0.1-alpha", false}, //TODO(melkikh): semver returns other result
		//{">0.0-0", "0.0.1-alpha", false}, //TODO(melkikh): semver returns other result
		//{">0", "0.0.0-alpha", false}, //TODO(melkikh): semver returns other result
		//{">0-0", "0.0.0-alpha", false}, //TODO(melkikh): semver returns other result
		{">0.0.0-0", "0.0.0-alpha", true},
		{">1.2.3-alpha.1", "1.2.3-alpha.2", true},
		{">1.2.3-alpha.1", "1.3.3-alpha.2", true},
		//{">11", "11.1.0", false}, //TODO(melkikh): semver returns other result
		{">11.1", "11.1.0", false},
		//{">11.1", "11.1.1", false}, //TODO(melkikh): semver returns other result
		{">11.1", "11.2.1", true},
		{">=11", "11.1.2", true},
		{">=11.1", "11.1.2", true},
		{">=11.1", "11.0.2", false},
		{">=1.1", "4.1.0", true},
		{">=1.1", "1.1.0", true},
		{">=1.1", "0.0.9", false},
		//{">=0", "0.0.1-alpha", false}, //TODO(melkikh): semver returns other result
		//{">=0.0", "0.0.1-alpha", false}, //TODO(melkikh): semver returns other result
		{">=0-0", "0.0.1-alpha", true},
		{">=0.0-0", "0.0.1-alpha", true},
		//{">=0", "0.0.0-alpha", false}, //TODO(melkikh): semver returns other result
		{">=0-0", "0.0.0-alpha", true},
		{">=0.0.0-0", "0.0.0-alpha", true},
		{">=0.0.0-0", "1.2.3", true},
		{">=0.0.0-0", "3.4.5-beta.1", true},
		{"<0", "0.0.0-alpha", false},
		{"<0-z", "0.0.0-alpha", true},
		//{">=0", "0", true}, //TODO(melkikh): semver returns other result
		{"=0", "1", false},
		{"*", "1", true},
		{"*", "4.5.6", true},
		{"*", "1.2.3-alpha.1", false},
		{"2.*", "1", false},
		{"2.*", "3.4.5", false},
		{"2.*", "2.1.1", true},
		{"2.1.*", "2.1.1", true},
		{"2.1.*", "2.2.1", false},
		{"", "1", true},
		{"", "4.5.6", true},
		{"", "1.2.3-alpha.1", false},
		{"2", "1", false},
		{"2", "3.4.5", false},
		{"2", "2.1.1", true},
		{"2.1", "2.1.1", true},
		{"2.1", "2.2.1", false},
		{"~1.2.3", "1.2.4", true},
		{"~1.2.3", "1.3.4", false},
		{"~1.2", "1.2.4", true},
		{"~1.2", "1.3.4", false},
		{"~1", "1.2.4", true},
		{"~1", "2.3.4", false},
		{"~0.2.3", "0.2.5", true},
		{"~0.2.3", "0.3.5", false},
		{"~1.2.3-beta.2", "1.2.3-beta.4", true},

		{"~1.2.3-beta.2", "1.2.4-beta.2", true},
		{"~1.2.3-beta.2", "1.3.4-beta.2", false},
		{"^1.2.3", "1.8.9", true},
		{"^1.2.3", "2.8.9", false},
		{"^1.2.3", "1.2.1", false},
		{"^1.1.0", "2.1.0", false},
		{"^1.2.0", "2.2.1", false},
		{"^1.2.0", "1.2.1-alpha.1", false},
		{"^1.2.0-alpha.0", "1.2.1-alpha.1", true},
		{"^1.2.0-alpha.0", "1.2.1-alpha.0", true},
		{"^1.2.0-alpha.2", "1.2.0-alpha.1", false},
		{"^1.2", "1.8.9", true},
		{"^1.2", "2.8.9", false},
		{"^1", "1.8.9", true},
		{"^1", "2.8.9", false},
		{"^0.2.3", "0.2.5", true},
		{"^0.2.3", "0.5.6", false},
		{"^0.2", "0.2.5", true},
		{"^0.2", "0.5.6", false},
		{"^0.0.3", "0.0.3", true},
		{"^0.0.3", "0.0.4", false},
		//{"^0.0", "0.0.3", true}, //TODO(melkikh): semver returns other result
		{"^0.0", "0.1.4", false},
		{"^0.0", "1.0.4", false},
		//{"^0", "0.2.3", true}, //TODO(melkikh): semver returns other result
		{"^0", "1.1.4", false},
		{"^0.2.3-beta.2", "0.2.3-beta.4", true},

		{"^0.2.3-beta.2", "0.2.4-beta.2", true},
		{"^0.2.3-beta.2", "0.3.4-beta.2", false},
		{"^0.2.3-beta.2", "0.2.3-beta.2", true},
	}

	for _, tc := range cases {
		t.Run(tc.constraint, func(t *testing.T) {
			version, err := newSemverVersion(tc.version, false)
			require.NoError(t, err)

			versionRange, err := newSemverRange(tc.constraint)
			require.NoError(t, err)

			require.Equal(t, tc.check, versionRange.Check(version))
		})
	}
}
