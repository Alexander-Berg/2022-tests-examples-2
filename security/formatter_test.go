package shellutil_test

import (
	"fmt"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/wsl2proxy/internal/listener"
	"a.yandex-team.ru/security/skotty/wsl2proxy/internal/shellutil"
)

func TestListeners(t *testing.T) {
	type shellCase struct {
		shell    string
		expected string
	}
	cases := []struct {
		spec   listener.Spec
		shells []shellCase
	}{
		{
			spec: listener.Spec{},
			shells: []shellCase{
				{
					shell:    "/bin/not-a-fish",
					expected: "\n",
				},
				{
					shell:    "/bin/fish",
					expected: "\n",
				},
				{
					shell:    "/bin/bash",
					expected: "\n",
				},
			},
		},
		{
			spec: listener.Spec{
				Pairs: []listener.ListenPair{
					{
						Name: "KEK",
						Src:  "/kek.sock",
						Dst:  "unix:/cheburek",
					},
					{
						Name: "LOL",
						Src:  "/lol.sock",
						Dst:  "unix:/cheburek",
					},
				},
			},
			shells: []shellCase{
				{
					shell:    "/bin/not-a-fish",
					expected: "KEK=\"/kek.sock\"; export KEK\nLOL=\"/lol.sock\"; export LOL\n",
				},
				{
					shell:    "/bin/fish",
					expected: "set -gx KEK \"/kek.sock\"\nset -gx LOL \"/lol.sock\"\n",
				},
				{
					shell:    "/bin/bash",
					expected: "KEK=\"/kek.sock\"; export KEK\nLOL=\"/lol.sock\"; export LOL\n",
				},
				{
					shell:    "/bin/csh",
					expected: "setenv KEK \"/kek.sock\";\nsetenv LOL \"/lol.sock\";\n",
				},
			},
		},
	}

	setEnv := func(k, v string) {
		if v == "" {
			_ = os.Unsetenv(k)
			return
		}

		_ = os.Setenv(k, v)
	}

	for i, tc := range cases {
		t.Run(fmt.Sprint(i), func(t *testing.T) {
			for _, shellTc := range tc.shells {
				t.Run(shellTc.shell, func(t *testing.T) {
					originalShell := os.Getenv("SHELL")

					setEnv("SHELL", shellTc.shell)
					defer setEnv("SHELL", originalShell)

					actual := shellutil.Listeners(tc.spec)
					require.Equal(t, shellTc.expected, string(actual))
				})
			}
		})
	}
}
