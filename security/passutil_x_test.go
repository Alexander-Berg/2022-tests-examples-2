package passutil_test

import (
	"math/rand"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/internal/passutil"
)

func TestXPassword(t *testing.T) {
	cases := []struct {
		len  int
		pass string
	}{
		{
			len:  1,
			pass: "h",
		},
		{
			len:  6,
			pass: "ehwu7Z",
		},
		{
			len:  18,
			pass: "GXyQSroCrRTVOOk3GI",
		},
	}

	rand.Seed(0)
	for _, tc := range cases {
		t.Run(tc.pass, func(t *testing.T) {
			pass, err := passutil.Password(tc.len)
			require.NoError(t, err)
			require.NotEqual(t, tc.pass, pass)
		})
	}
}
