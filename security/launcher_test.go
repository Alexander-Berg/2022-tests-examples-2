package launcher_test

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/libs/go/ioatomic"
	"a.yandex-team.ru/security/skotty/launcher/internal/launcher"
	"a.yandex-team.ru/security/skotty/launcher/internal/updater"
	"a.yandex-team.ru/security/skotty/launcher/internal/version"
	"a.yandex-team.ru/security/skotty/launcher/tools/fake-skotty/runinfo"
)

func TestLaunch(t *testing.T) {
	home, err := os.MkdirTemp("", "launcher-home-*")
	require.NoError(t, err)

	oldHome := os.Getenv("HOME")
	defer func() { _ = os.Setenv("HOME", oldHome) }()

	err = os.Setenv("HOME", home)
	require.NoError(t, err)

	selfExe, err := os.Executable()
	require.NoError(t, err)

	relPath, err := updater.ReleasesPath()
	require.NoError(t, err)

	skottyPath, err := yatest.BinaryPath("security/skotty/launcher/tools/fake-skotty/fake-skotty")
	require.NoError(t, err)

	err = os.MkdirAll(filepath.Join(relPath, "1.1.1"), 0o700)
	require.NoError(t, err)

	err = ioatomic.CopyFile(skottyPath, filepath.Join(relPath, "1.1.1", "skotty"))
	require.NoError(t, err)

	err = os.WriteFile(filepath.Join(relPath, "current.json"), []byte(`{"Version":"1.1.1","Channel":"channel"}`), 0o644)
	require.NoError(t, err)
	defer func() { _ = os.RemoveAll(filepath.Join(relPath, "current.json")) }()

	for _, exitCode := range []int{0, 1, 2} {
		t.Run(fmt.Sprint(exitCode), func(t *testing.T) {
			f, err := os.CreateTemp("", "fake-skotty-out-*")
			require.NoError(t, err)
			_ = f.Close()
			defer func() { _ = os.RemoveAll(f.Name()) }()

			args := []string{
				"--out", f.Name(),
				"--exit-code", fmt.Sprint(exitCode),
			}
			actualCode, err := launcher.Launch(args...)
			require.NoError(t, err)
			require.Equal(t, exitCode, actualCode)

			infoBytes, err := os.ReadFile(f.Name())
			require.NoError(t, err)

			var actualInfo runinfo.RunInfo
			err = json.Unmarshal(infoBytes, &actualInfo)
			require.NoError(t, err)

			expectedInfo := runinfo.RunInfo{
				Args: args,
				Env: map[string]string{
					"UNDER_LAUNCHER":          "yes",
					"SKOTTY_LAUNCHER_PATH":    selfExe,
					"SKOTTY_LAUNCHER_VERSION": version.Full(),
					"SKOTTY_CHANNEL":          "channel",
				},
			}

			require.EqualValues(t, expectedInfo, actualInfo)
		})
	}
}
