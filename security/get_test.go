package integration

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/kirby/integration/testutil"
)

func TestGoGet(t *testing.T) {
	cases := []string{
		"gopkg.in/resty.v1@latest",
		"github.com/go-resty/resty/v2@latest",
		"github.com/go-resty/resty/v2",
		"github.com/go-resty/resty/v2@v2.3.0",
		"github.com/go-resty/resty/v2@b87f65ce5ed58bfbc2eb455f353b56be54bdf07f",
	}

	run := func(name string, req string, env ...string) {
		t.Run(name, func(t *testing.T) {
			testutil.SetupGoMod(t)
			goEnv := append(testutil.GoEnv(t, kirbyURL), env...)
			_, err := testutil.GoGet(req, goEnv)
			require.NoError(t, err)
		})
	}

	for _, tc := range cases {
		run(tc+"-nosumdb", tc, "GOSUMDB=off")
		run(tc+"-sumdb", tc)
	}
}
