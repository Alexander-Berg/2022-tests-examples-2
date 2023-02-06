package integration

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/kirby/integration/testutil"
)

func TestGoDownload(t *testing.T) {
	type testCase struct {
		Req     string
		PkgName string
		Version string
	}

	cases := []testCase{
		{
			Req:     "gopkg.in/resty.v1@latest",
			PkgName: "gopkg.in/resty.v1",
		},
		{
			Req:     "github.com/go-resty/resty/v2@latest",
			PkgName: "github.com/go-resty/resty/v2",
		},
		{
			Req:     "github.com/go-resty/resty/v2@v2.3.0",
			PkgName: "github.com/go-resty/resty/v2",
			Version: "v2.3.0",
		},
		{
			Req:     "github.com/go-resty/resty/v2@b87f65ce5ed58bfbc2eb455f353b56be54bdf07f",
			PkgName: "github.com/go-resty/resty/v2",
			Version: "v2.3.1-0.20200619075926-b87f65ce5ed5",
		},
	}

	run := func(name string, tc testCase, env ...string) {
		t.Run(name, func(t *testing.T) {
			testutil.SetupGoMod(t)
			goEnv := append(testutil.GoEnv(t, kirbyURL), env...)
			m, err := testutil.GoDownload(tc.Req, goEnv)
			require.NoError(t, err)

			require.Equal(t, tc.PkgName, m.Path)
			require.NotEmpty(t, m.Dir)
			require.NotEmpty(t, m.Info)
			require.NotEmpty(t, m.Zip)
			require.NotEmpty(t, m.GoMod)
			require.NotEmpty(t, m.Version)
			if tc.Version != "" {
				require.Equal(t, tc.Version, m.Version)
			}
		})
	}

	for _, tc := range cases {
		run(tc.Req+"-nosumdb", tc, "GOSUMDB=off")
		run(tc.Req+"-sumdb", tc)
	}
}
