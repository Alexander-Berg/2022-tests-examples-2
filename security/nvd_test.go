package nvd_test

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/libs/nvd"
)

func TestNVD(t *testing.T) {
	cases := map[string]struct {
		cveID         string
		willFail      bool
		description   string
		cweID         string
		score         float32
		publishedDate time.Time
	}{
		"rejected": {
			cveID:    "CVE-2021-0004",
			willFail: true,
		},
		"modified": {
			cveID:         "CVE-2021-0002",
			willFail:      false,
			description:   "modified",
			cweID:         "CWE-754",
			score:         8.1,
			publishedDate: time.Date(2021, 8, 11, 13, 15, 0, 0, time.UTC),
		},
		"recent": {
			cveID:         "CVE-2021-0003",
			willFail:      false,
			description:   "recent vuln",
			cweID:         "CWE-502",
			score:         8.4,
			publishedDate: time.Date(2021, 9, 10, 23, 15, 0, 0, time.UTC),
		},
		"normal vuln": {
			cveID:         "CVE-2021-0001",
			willFail:      false,
			description:   "normal vuln",
			cweID:         "CWE-203",
			score:         4.7,
			publishedDate: time.Date(2021, 6, 9, 20, 15, 0, 0, time.UTC),
		},
		"cvssv2": {
			cveID:         "CVE-2006-3083",
			willFail:      false,
			description:   "test cvss v2 only issue",
			cweID:         "CWE-399",
			score:         7.2,
			publishedDate: time.Date(2006, 8, 9, 10, 4, 0, 0, time.UTC),
		},
	}

	srv := httptest.NewServer(http.FileServer(http.Dir("./testdata")))
	defer srv.Close()

	nvdFeed, err := nvd.ParseNVD(srv.URL + "/index.html")
	require.NoError(t, err)

	for name, tc := range cases {
		t.Run(name+"_"+tc.cveID, func(t *testing.T) {
			item, exists := nvdFeed[tc.cveID]

			if tc.willFail {
				require.False(t, exists, "cve id %q MUST NO exists", tc.cveID)
				return
			}

			require.True(t, exists, "cve id %q MUST exists", tc.cveID)
			require.Equal(t, tc.description, item.Description)
			require.Equal(t, tc.cweID, item.CWEID)
			require.Equal(t, tc.score, item.Score)
			require.Equal(t, tc.publishedDate, item.PublishedDate)
		})
	}
}
