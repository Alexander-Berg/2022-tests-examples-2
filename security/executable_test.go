package launcher_test

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/sectools"
	"a.yandex-team.ru/security/skotty/launcher/internal/updater"
	"a.yandex-team.ru/security/skotty/launcher/pkg/launcher"
)

var home string

func TestMain(m *testing.M) {
	var err error
	home, err = os.MkdirTemp("", "updater-test-*")
	if err != nil {
		panic(fmt.Sprintf("create temporary home: %v", err))
	}

	oldHome := os.Getenv("HOME")
	err = os.Setenv("HOME", home)
	if err != nil {
		panic(fmt.Sprintf("update home: %v", err))
	}

	exitVal := m.Run()
	_ = os.Setenv("HOME", oldHome)
	os.Exit(exitVal)
}

func TestLatestExecutable(t *testing.T) {
	relPath, err := updater.ReleasesPath()
	require.NoError(t, err)

	err = os.MkdirAll(relPath, 0o755)
	require.NoError(t, err)

	writeReleaseInfo := func(t *testing.T, ri updater.ReleaseInfo) {
		targetPath := filepath.Join(relPath, "current.json")

		releaseBytes, err := json.Marshal(ri)
		require.NoError(t, err)

		err = os.WriteFile(targetPath, releaseBytes, 0o644)
		require.NoError(t, err)
	}

	cases := []struct {
		name      string
		expected  string
		err       bool
		bootstrap func(t *testing.T)
	}{
		{
			name: "missing",
			err:  true,
			bootstrap: func(t *testing.T) {
				_ = os.RemoveAll(filepath.Join(relPath, "current.json"))
			},
		},
		{
			name: "invalid",
			err:  true,
			bootstrap: func(t *testing.T) {
				writeReleaseInfo(t, updater.ReleaseInfo{
					Version: "0.0.0",
				})
			},
		},
		{
			name:     "ok",
			expected: filepath.Join(home, ".skotty", "releases", "1.2.3", "skotty"),
			bootstrap: func(t *testing.T) {
				writeReleaseInfo(t, updater.ReleaseInfo{
					Version: "1.2.3",
					Channel: sectools.ChannelTesting,
				})
			},
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.bootstrap(t)
			actual, err := launcher.LatestExecutable()
			if tc.err {
				require.Error(t, err)
				return
			}

			require.Equal(t, tc.expected, actual)
		})
	}
}
