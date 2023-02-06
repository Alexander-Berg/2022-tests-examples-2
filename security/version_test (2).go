package semver

import (
	"path"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestStrictNewVersion(t *testing.T) {
	tests := []struct {
		version string
		err     bool
	}{
		{"1.2.3", false},
		{"1.2.3-alpha.01", true},
		{"1.2.3+test.01", false},
		{"1.2.3-alpha.-1", false},
		{"v1.2.3", true},
		{"1.0", true},
		{"v1.0", true},
		{"1", true},
		{"v1", true},
		{"1.2.beta", true},
		{"v1.2.beta", true},
		{"foo", true},
		{"1.2-5", true},
		{"v1.2-5", true},
		{"1.2-beta.5", true},
		{"v1.2-beta.5", true},
		{"\n1.2", true},
		{"\nv1.2", true},
		{"1.2.0-x.Y.0+metadata", false},
		{"v1.2.0-x.Y.0+metadata", true},
		{"1.2.0-x.Y.0+metadata-width-hypen", false},
		{"v1.2.0-x.Y.0+metadata-width-hypen", true},
		{"1.2.3-rc1-with-hypen", false},
		{"v1.2.3-rc1-with-hypen", true},
		{"1.2.3.4", true},
		{"v1.2.3.4", true},
		{"1.2.2147483648", false},
		{"1.2147483648.3", false},
		{"2147483648.3.0", false},
	}

	for _, tc := range tests {
		t.Run(tc.version, func(t *testing.T) {
			_, err := StrictNewVersion(tc.version)
			if tc.err {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func TestNewVersion(t *testing.T) {
	tests := []struct {
		version string
		err     bool
	}{
		{"1.2.3", false},
		{"1.2.3-alpha.01", true},
		{"1.2.3+test.01", false},
		{"1.2.3-alpha.-1", false},
		{"v1.2.3", false},
		{"1.0", false},
		{"v1.0", false},
		{"1", false},
		{"v1", false},
		{"1.2.beta", true},
		{"v1.2.beta", true},
		{"foo", true},
		{"1.2-5", false},
		{"v1.2-5", false},
		{"1.2-beta.5", false},
		{"v1.2-beta.5", false},
		{"\n1.2", false},
		{"\nv1.2", false},
		{"1.2.0-x.Y.0+metadata", false},
		{"v1.2.0-x.Y.0+metadata", false},
		{"1.2.0-x.Y.0+metadata-width-hypen", false},
		{"v1.2.0-x.Y.0+metadata-width-hypen", false},
		{"1.2.3-rc1-with-hypen", false},
		{"v1.2.3-rc1-with-hypen", false},
		{"1.2.3.4", true},
		{"v1.2.3.4", true},
		{"1.2.2147483648", false},
		{"1.2147483648.3", false},
		{"2147483648.3.0", false},
	}

	for _, tc := range tests {
		t.Run(tc.version, func(t *testing.T) {
			_, err := NewVersion(tc.version)
			if tc.err {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func TestOriginal(t *testing.T) {
	tests := []string{
		"1.2.3",
		"v1.2.3",
		"1.0",
		"v1.0",
		"1",
		"v1",
		"1.2-5",
		"v1.2-5",
		"1.2-beta.5",
		"v1.2-beta.5",
		"1.2.0-x.Y.0+metadata",
		"v1.2.0-x.Y.0+metadata",
		"1.2.0-x.Y.0+metadata-width-hypen",
		"v1.2.0-x.Y.0+metadata-width-hypen",
		"1.2.3-rc1-with-hypen",
		"v1.2.3-rc1-with-hypen",
	}

	for _, tc := range tests {
		t.Run(tc, func(t *testing.T) {
			v, err := NewVersion(tc)
			require.NoError(t, err)

			o := v.Original
			require.Equal(t, tc, o)
		})
	}
}

func TestParts(t *testing.T) {
	v, err := NewVersion("1.2.3-beta.1+build.123")
	require.NoError(t, err)
	require.Equal(t, uint64(1), v.Major)
	require.Equal(t, uint64(2), v.Minor)
	require.Equal(t, uint64(3), v.Patch)
	require.Equal(t, "beta.1", v.Prerelease())
	require.Equal(t, "build.123", v.Metadata())
}

func TestCoerceString(t *testing.T) {
	tests := []struct {
		version  string
		expected string
	}{
		{"1.2.3", "1.2.3"},
		{"v1.2.3", "1.2.3"},
		{"1.0", "1.0.0"},
		{"v1.0", "1.0.0"},
		{"1", "1.0.0"},
		{"v1", "1.0.0"},
		{"1.2-5", "1.2.0-5"},
		{"v1.2-5", "1.2.0-5"},
		{"1.2-beta.5", "1.2.0-beta.5"},
		{"v1.2-beta.5", "1.2.0-beta.5"},
		{"1.2.0-x.Y.0+metadata", "1.2.0-x.Y.0+metadata"},
		{"v1.2.0-x.Y.0+metadata", "1.2.0-x.Y.0+metadata"},
		{"1.2.0-x.Y.0+metadata-width-hypen", "1.2.0-x.Y.0+metadata-width-hypen"},
		{"v1.2.0-x.Y.0+metadata-width-hypen", "1.2.0-x.Y.0+metadata-width-hypen"},
		{"1.2.3-rc1-with-hypen", "1.2.3-rc1-with-hypen"},
		{"v1.2.3-rc1-with-hypen", "1.2.3-rc1-with-hypen"},
	}

	for _, tc := range tests {
		t.Run(tc.version, func(t *testing.T) {
			v, err := NewVersion(tc.version)
			require.NoError(t, err)

			require.Equal(t, tc.expected, v.String())
		})
	}
}

func TestCompare(t *testing.T) {
	tests := []struct {
		v1       string
		v2       string
		expected int
	}{
		{"1.2.3", "1.5.1", -1},
		{"2.2.3", "1.5.1", 1},
		{"2.2.3", "2.2.2", 1},
		{"3.2-beta", "3.2-beta", 0},
		{"1.3", "1.1.4", 1},
		{"4.2", "4.2-beta", 1},
		{"4.2-beta", "4.2", -1},
		{"4.2-alpha", "4.2-beta", -1},
		{"4.2-alpha", "4.2-alpha", 0},
		{"4.2-beta.2", "4.2-beta.1", 1},
		{"4.2-beta2", "4.2-beta1", 1},
		{"4.2-beta", "4.2-beta.2", -1},
		{"4.2-beta", "4.2-beta.foo", -1},
		{"4.2-beta.2", "4.2-beta", 1},
		{"4.2-beta.foo", "4.2-beta", 1},
		{"1.2+bar", "1.2+baz", 0},
		{"1.0.0-beta.4", "1.0.0-beta.-2", -1},
		{"1.0.0-beta.-2", "1.0.0-beta.-3", -1},
		{"1.0.0-beta.-3", "1.0.0-beta.5", 1},
	}

	for _, tc := range tests {
		t.Run(path.Join(tc.v1, tc.v2), func(t *testing.T) {
			v1, err := NewVersion(tc.v1)
			require.NoError(t, err)

			v2, err := NewVersion(tc.v2)
			require.NoError(t, err)

			a := v1.Compare(v2)
			require.Equal(t, tc.expected, a)
		})
	}
}

func TestLessThan(t *testing.T) {
	tests := []struct {
		v1       string
		v2       string
		expected bool
	}{
		{"1.2.3", "1.5.1", true},
		{"2.2.3", "1.5.1", false},
		{"3.2-beta", "3.2-beta", false},
	}

	for _, tc := range tests {
		t.Run(path.Join(tc.v1, tc.v2), func(t *testing.T) {
			v1, err := NewVersion(tc.v1)
			require.NoError(t, err)

			v2, err := NewVersion(tc.v2)
			require.NoError(t, err)

			a := v1.LessThan(v2)
			require.Equal(t, tc.expected, a)
		})
	}
}

func TestGreaterThan(t *testing.T) {
	tests := []struct {
		v1       string
		v2       string
		expected bool
	}{
		{"1.2.3", "1.5.1", false},
		{"2.2.3", "1.5.1", true},
		{"3.2-beta", "3.2-beta", false},
		{"3.2.0-beta.1", "3.2.0-beta.5", false},
		{"3.2-beta.4", "3.2-beta.2", true},
		{"7.43.0-SNAPSHOT.99", "7.43.0-SNAPSHOT.103", false},
		{"7.43.0-SNAPSHOT.FOO", "7.43.0-SNAPSHOT.103", true},
		{"7.43-SNAPSHOT.FOO", "7.43-SNAPSHOT.103", true},
		{"7.43.0-SNAPSHOT.99", "7.43.0-SNAPSHOT.BAR", false},
	}

	for _, tc := range tests {
		t.Run(path.Join(tc.v1, tc.v2), func(t *testing.T) {
			v1, err := NewVersion(tc.v1)
			require.NoError(t, err)

			v2, err := NewVersion(tc.v2)
			require.NoError(t, err)

			a := v1.GreaterThan(v2)
			require.Equal(t, tc.expected, a)
		})
	}
}

func TestEqual(t *testing.T) {
	tests := []struct {
		v1       string
		v2       string
		expected bool
	}{
		{"1.2.3", "1.5.1", false},
		{"2.2.3", "1.5.1", false},
		{"3.2-beta", "3.2-beta", true},
		{"3.2-beta+foo", "3.2-beta+bar", true},
	}

	for _, tc := range tests {
		t.Run(path.Join(tc.v1, tc.v2), func(t *testing.T) {
			v1, err := NewVersion(tc.v1)
			require.NoError(t, err)

			v2, err := NewVersion(tc.v2)
			require.NoError(t, err)

			a := v1.Equal(v2)
			require.Equal(t, tc.expected, a)
		})
	}
}
