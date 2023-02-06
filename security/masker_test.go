package passutil_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/internal/passutil"
)

func TestMasker(t *testing.T) {
	cases := map[string]string{
		"":          "",
		"1":         "*",
		"12":        "**",
		"123":       "***",
		"1234":      "1**4",
		"123456789": "1*******9",
		"lolkek":    "l****k",
	}

	for in, out := range cases {
		t.Run(in, func(t *testing.T) {
			require.Equal(t, out, passutil.Mask(in))
		})
	}
}
