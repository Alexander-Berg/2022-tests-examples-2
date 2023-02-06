package askpass_test

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/skotty/libs/askpass"
	"a.yandex-team.ru/security/skotty/libs/askpass/fakepass/fakepass"
)

func TestAskPassDisabled(t *testing.T) {
	_ = os.Setenv("SSH_ASKPASS_REQUIRE", "never")
	defer func() { _ = os.Unsetenv("SSH_ASKPASS_REQUIRE") }()

	ask := askpass.NewClient(askpass.WithProgram("/bin/true"))
	ok, err := ask.Confirm("tst")
	require.Error(t, err)
	require.False(t, ok)
}

func TestAskPassConfirm(t *testing.T) {
	cases := []struct {
		output   string
		exitCode int
		ok       bool
		err      bool
	}{
		{
			output: "yes",
			ok:     true,
		},
		{
			output: "",
			ok:     true,
		},
		{
			output: "no",
			ok:     false,
		},
		{
			output: "nope",
			ok:     false,
		},
		{
			output:   "yes",
			exitCode: 1,
			ok:       false,
		},
	}

	fakePass, err := yatest.BinaryPath("security/skotty/libs/askpass/fakepass/cmd/fakepass/fakepass")
	require.NoError(t, err)

	for i, tc := range cases {
		t.Run(fmt.Sprint(i), func(t *testing.T) {
			rawMsg, err := json.Marshal(fakepass.Opts{
				Output:         tc.output,
				ExitCode:       tc.exitCode,
				ExpectedPrompt: "confirm",
			})
			require.NoError(t, err)

			ask := askpass.NewClient(askpass.WithProgram(fakePass))
			ok, err := ask.Confirm(base64.RawStdEncoding.EncodeToString(rawMsg))
			if tc.err {
				require.Error(t, err)
				require.False(t, ok)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.ok, ok)
		})
	}
}

func TestAskPassConfirm_err(t *testing.T) {
	ask := askpass.NewClient(askpass.WithProgram("something-terrible"))
	ok, err := ask.Confirm("tst")
	require.False(t, ok)
	require.Error(t, err)
}
