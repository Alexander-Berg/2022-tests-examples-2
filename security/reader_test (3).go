package splunk

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestReader(t *testing.T) {
	cases := []struct {
		filename string
		headers  []string
		entries  []PackageEntry
		err      bool
	}{
		{
			filename: "wo_header.csv",
			err:      true,
		},
		{
			filename: "not_all_fields.csv",
			err:      true,
		},
		{
			filename: "only_required.csv",
			headers: []string{
				"os_platform",
				"os_codename",
				"pkg_name",
				"pkg_ver",
			},
			entries: []PackageEntry{
				{
					OsPlatform: "ubuntu",
					OsCodename: "xenial",
					PkgName:    "vulnerable",
					PkgVer:     "1:2.0.26-1ubuntu2",
					BaseEntry: BaseEntry{
						allFields: []string{
							"ubuntu",
							"xenial",
							"vulnerable",
							"1:2.0.26-1ubuntu2",
						},
					},
				},
				{
					OsPlatform: "debian",
					OsCodename: "buster",
					PkgName:    "not_vulnerable",
					PkgVer:     "1:2.0.26",
					BaseEntry: BaseEntry{
						allFields: []string{
							"debian",
							"buster",
							"not_vulnerable",
							"1:2.0.26",
						},
					},
				},
			},
			err: false,
		},
		{
			filename: "only_required_unsorted.csv",
			headers: []string{
				"os_codename",
				"os_platform",
				"pkg_ver",
				"pkg_name",
			},
			entries: []PackageEntry{
				{
					OsPlatform: "ubuntu",
					OsCodename: "xenial",
					PkgName:    "vulnerable",
					PkgVer:     "1:2.0.26-1ubuntu2",
					BaseEntry: BaseEntry{
						allFields: []string{
							"xenial",
							"ubuntu",
							"1:2.0.26-1ubuntu2",
							"vulnerable",
						},
					},
				},
				{
					OsPlatform: "debian",
					OsCodename: "buster",
					PkgName:    "not_vulnerable",
					PkgVer:     "1:2.0.26",
					BaseEntry: BaseEntry{
						allFields: []string{
							"buster",
							"debian",
							"1:2.0.26",
							"not_vulnerable",
						},
					},
				},
			},
			err: false,
		},
		{
			filename: "typical.csv",
			headers: []string{
				"host",
				"os_platform",
				"os_codename",
				"pkg_name",
				"time",
				"pkg_ver",
			},
			entries: []PackageEntry{
				{
					OsPlatform: "ubuntu",
					OsCodename: "xenial",
					PkgName:    "vulnerable",
					PkgVer:     "1:2.0.26-1ubuntu2",
					BaseEntry: BaseEntry{
						allFields: []string{
							"host1",
							"ubuntu",
							"xenial",
							"vulnerable",
							"12345",
							"1:2.0.26-1ubuntu2",
						},
					},
				},
				{
					OsPlatform: "debian",
					OsCodename: "buster",
					PkgName:    "not_vulnerable",
					PkgVer:     "1:2.0.26",
					BaseEntry: BaseEntry{
						allFields: []string{
							"host2",
							"debian",
							"buster",
							"not_vulnerable",
							"99999",
							"1:2.0.26",
						},
					},
				},
			},
			err: false,
		},
	}

	for _, tc := range cases {
		filename := filepath.Join("testdata", "in", tc.filename)
		t.Run(filename, func(t *testing.T) {
			f, err := os.Open(filename)
			require.NoError(t, err)
			defer func() { _ = f.Close() }()

			r := NewCSVReader(f)
			actualHeaders, err := r.Header(PackageFields...)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.headers, actualHeaders)

			idx := 0
			for r.More() {
				entry, err := r.DecodePackageEntry()
				require.NoError(t, err)

				require.Equal(t, tc.entries[idx], entry)
				idx++
			}

			require.Equal(t, idx, len(tc.entries))
		})
	}
}
