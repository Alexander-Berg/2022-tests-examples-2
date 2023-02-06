package maven_test

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/libs/maven"
)

var (
	zeroQ, zeroMeta []string
)

func TestParseVersion(t *testing.T) {
	var cases = []struct {
		raw                 string
		major, minor, patch uint64
		qualifiers, meta    []string
	}{
		{"1", 1, 0, 0, zeroQ, zeroMeta},
		{"1.2", 1, 2, 0, zeroQ, zeroMeta},
		{"1.2.3", 1, 2, 3, zeroQ, zeroMeta},
		{"1.2.3-1", 1, 2, 3, []string{"1"}, zeroMeta},
		{"1.2.3-alpha-1", 1, 2, 3, []string{"alpha", "1"}, zeroMeta},
		{"1.2-alpha-1", 1, 2, 0, []string{"alpha", "1"}, zeroMeta},
		//{"1.2-alpha-1-20050205.060708-1", 1, 2, 0, []string{"alpha-1-20050205.060708-1"}, zeroMeta},
		{"RELEASE", 0, 0, 0, []string{"RELEASE"}, zeroMeta},
		{"2.0-1", 2, 0, 0, []string{"1"}, zeroMeta},
		//
		//// 0 at the beginning of a number has a special handling
		//{ "02", 0, 0, 0, []string{"02"}, zeroMeta },
		//{ "0.09", 0, 0, 0, 0, "0.09" },
		//{ "0.2.09", 0, 0, 0, 0, "0.2.09" },
		//{ "2.0-01", 2, 0, 0, []string{"01"}, zeroMeta },
		//
		{"1.0.1b", 1, 0, 0, []string{"1", "b"}, zeroMeta},
		{"1.0M2", 1, 0, 0, []string{"0", "M", "2"}, zeroMeta},
		{"1.0RC2", 1, 0, 0, []string{"0", "RC", "2"}, zeroMeta},
		{"1.1.2.beta1", 1, 1, 2, []string{"beta", "1"}, zeroMeta},
		{"1.7.3.0", 1, 7, 3, []string{"0"}, zeroMeta},
		//{ "1.7.3.0-1", 1, 7, 3, []string{"0", "1"}, zeroMeta }, TODO(melkikh): fixme actual: "02"
		{"PATCH-1193602", 0, 0, 0, []string{"PATCH", "1193602"}, zeroMeta},
		{"5.0.0alpha-2006020117", 5, 0, 0, []string{"0", "alpha", "2006020117"}, zeroMeta},
		{"1.0.0.-SNAPSHOT", 1, 0, 0, []string{"SNAPSHOT"}, zeroMeta},
		//{ "1..0-SNAPSHOT", 0, 0, 0, 0, "1..0-SNAPSHOT"  },
		//{ "1.0.-SNAPSHOT", 0, 0, 0, 0, "1.0.-SNAPSHOT" },
		//{ ".1.0-SNAPSHOT", 0, 0, 0, 0, ".1.0-SNAPSHOT" },
		//
		{"1.2.3.200705301630", 1, 2, 3, []string{"200705301630"}, zeroMeta},
		{"1.2.3-200705301630", 1, 2, 3, []string{"200705301630"}, zeroMeta},
	}

	for _, tc := range cases {
		t.Run(tc.raw, func(t *testing.T) {
			version, err := maven.ParseVersion(tc.raw)
			require.NoError(t, err)

			assert.Equal(t, tc.major, version.Major)
			assert.Equal(t, tc.minor, version.Minor)
			assert.Equal(t, tc.patch, version.Patch)

			assert.Len(t, version.Qualifiers, len(tc.qualifiers))

			for i := range version.Qualifiers {
				// order matter
				assert.Equal(t, tc.qualifiers[i], version.Qualifiers[i].String())
			}

			assert.Len(t, version.Build, len(tc.meta))
			for i := range version.Build {
				// order matter
				assert.Equal(t, tc.meta[i], version.Build[i])
			}
		})
	}
}

func TestVersion_Compare(t *testing.T) {
	var cases = []struct {
		left, right string
		resolution  int
	}{
		{"1.2-alpha-1-20050205.060708-1", "1.2-alpha-1-20050205.060708-1", 0},
		{"1", "1", 0},
		{"1", "2", -1},
		{"1.5", "2", -1},
		{"1", "2.5", -1},
		{"1", "1.0", 0},
		{"1", "1.0.0", 0},
		{"1.0", "1.1", -1},
		{"1.1", "1.2", -1},
		{"1.0.0", "1.1", -1},
		{"1.1", "1.2.0", -1},

		{"1.1.2.alpha1", "1.1.2", -1},
		{"1.1.2.alpha1", "1.1.2.beta1", -1},
		{"1.1.2.beta1", "1.2", -1},

		{"1.0-alpha-1", "1.0", -1},
		{"1.0-alpha-1", "1.0-alpha-2", -1},
		{"1.0-alpha-2", "1.0-alpha-15", -1},
		{"1.0-alpha-1", "1.0-beta-1", -1},

		{"1.0-beta-1", "1.0-SNAPSHOT", -1},
		{"1.0-SNAPSHOT", "1.0", -1},
		{"1.0-alpha-1-SNAPSHOT", "1.0-alpha-1", -1},

		{"1.0", "1.0-1", -1},
		{"1.0-1", "1.0-2", -1},
		{"2.0-0", "2.0", 0},
		{"2.0", "2.0-1", -1},
		{"2.0.0", "2.0-1", -1},
		{"2.0-1", "2.0.1", -1},

		{"2.0.1-klm", "2.0.1-lmn", -1},
		//{ "2.0.1", "2.0.1-xyz", -1 }, TODO(melkikh): actual: 1
		{"2.0.1-xyz-1", "2.0.1-1-xyz", -1},

		{"2.0.1", "2.0.1-123", -1},
		{"2.0.1-xyz", "2.0.1-123", -1},

		{"1.2.3-10000000000", "1.2.3-10000000001", -1},
		{"1.2.3-1", "1.2.3-10000000001", -1},
		{"2.3.0-v200706262000", "2.3.0-v200706262130", -1},

		{"2.0.0.v200706041905-7C78EK9E_EkMNfNOd2d8qq", "2.0.0.v200706041906-7C78EK9E_EkMNfNOd2d8qq", -1},

		// snapshot
		{"1-SNAPSHOT", "1-SNAPSHOT", 0},
		{"1-SNAPSHOT", "2-SNAPSHOT", -1},
		{"1.5-SNAPSHOT", "2-SNAPSHOT", -1},
		{"1-SNAPSHOT", "2.5-SNAPSHOT", -1},
		{"1-SNAPSHOT", "1.0-SNAPSHOT", 0},
		{"1-SNAPSHOT", "1.0.0-SNAPSHOT", 0},
		{"1.0-SNAPSHOT", "1.1-SNAPSHOT", -1},
		{"1.1-SNAPSHOT", "1.2-SNAPSHOT", -1},
		{"1.0.0-SNAPSHOT", "1.1-SNAPSHOT", -1},
		{"1.1-SNAPSHOT", "1.2.0-SNAPSHOT", -1},

		{"1.0-alpha-1-SNAPSHOT", "1.0-SNAPSHOT", -1},
		{"1.0-alpha-1-SNAPSHOT", "1.0-alpha-2-SNAPSHOT", -1},
		{"1.0-alpha-1-SNAPSHOT", "1.0-beta-1-SNAPSHOT", -1},

		{"1.0-beta-1-SNAPSHOT", "1.0-SNAPSHOT-SNAPSHOT", -1},
		{"1.0-SNAPSHOT-SNAPSHOT", "1.0-SNAPSHOT", -1},
		{"1.0-alpha-1-SNAPSHOT-SNAPSHOT", "1.0-alpha-1-SNAPSHOT", -1},

		{"1.0-SNAPSHOT", "1.0-1-SNAPSHOT", -1},
		{"1.0-1-SNAPSHOT", "1.0-2-SNAPSHOT", -1},
		//{"2.0-0-SNAPSHOT", "2.0-SNAPSHOT", 0},
		{"2.0-SNAPSHOT", "2.0-1-SNAPSHOT", -1},
		{"2.0.0-SNAPSHOT", "2.0-1-SNAPSHOT", -1},
		{"2.0-1-SNAPSHOT", "2.0.1-SNAPSHOT", -1},

		{"2.0.1-klm-SNAPSHOT", "2.0.1-lmn-SNAPSHOT", -1},
		{"2.0.1-xyz-SNAPSHOT", "2.0.1-SNAPSHOT", -1},
		{"2.0.1-SNAPSHOT", "2.0.1-123-SNAPSHOT", -1},
		{"2.0.1-xyz-SNAPSHOT", "2.0.1-123-SNAPSHOT", -1},
	}
	for _, tc := range cases {
		t.Run(fmt.Sprintf("%s ? %s", tc.left, tc.right), func(t *testing.T) {
			left, err := maven.ParseVersion(tc.left)
			assert.NoError(t, err)

			right, err := maven.ParseVersion(tc.right)
			assert.NoError(t, err)

			resolution := left.Compare(right)
			assert.Equal(t, tc.resolution, resolution)
		})
	}
}

func TestCompareEdgeCases(t *testing.T) {
	var cases = []struct {
		left, right maven.Version
		resolution  int
	}{
		{mustParseVersion("0.0.0"), maven.InfiniteVersion, -1},
		{maven.InfiniteVersion, mustParseVersion("9999.999.999"), +1},
		{maven.InfiniteVersion, maven.InfiniteVersion, 0},
	}

	for _, tc := range cases {
		t.Run(fmt.Sprintf("%s ? %s", tc.left, tc.right), func(t *testing.T) {
			resolution := tc.left.Compare(tc.right)
			assert.Equal(t, tc.resolution, resolution)
		})
	}
}

func mustParseVersion(s string) maven.Version {
	v, err := maven.ParseVersion(s)
	if err != nil {
		panic(`semver: ParseVersion(` + s + `): ` + err.Error())
	}
	return v
}
