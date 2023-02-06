package splunk

import (
	"bytes"
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestWriter(t *testing.T) {
	cases := []string{
		"typical.csv",
		"only_required.csv",
		"all_fields.csv",
	}

	for _, tc := range cases {
		t.Run(tc, func(t *testing.T) {
			inF, err := os.Open(filepath.Join("testdata", "in", tc))
			require.NoError(t, err)
			defer func() { _ = inF.Close() }()

			r := NewCSVReader(inF)
			headers, err := r.Header(PackageFields...)
			require.NoError(t, err)

			var out bytes.Buffer
			w := NewCSVWriter(&out, headers)

			for r.More() {
				entry, err := r.DecodePackageEntry()
				require.NoError(t, err)

				if entry.PkgName == "vulnerable" {
					entry.Issues = []Issue{
						{
							ID:               "YADI-LINUX-UBUNTU-KEK-1337",
							AffectedVersions: "<1.0.0",
							Summary:          "kek",
							Reference:        "https://yadi.yandex-team.ru/vulns/vuln/YADI-LINUX-UBUNTU-KEK-1337",
							CVSSScore:        9.2,
						},
						{
							ID:               "YADI-LINUX-UBUNTU-LOL-1332",
							AffectedVersions: "<1.0.0",
							Summary:          "lol",
							Reference:        "https://yadi.yandex-team.ru/vulns/vuln/YADI-LINUX-UBUNTU-LOL-1332",
							CVSSScore:        1.2,
						},
					}
				}

				err = w.Write(entry.BaseEntry)
				require.NoError(t, err)
			}

			require.NoError(t, w.Close())
			expected, err := ioutil.ReadFile(filepath.Join("testdata", "out", tc))
			require.NoError(t, err)
			require.Equal(t, string(expected), out.String())
		})
	}
}
