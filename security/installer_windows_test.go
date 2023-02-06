//go:build windows
// +build windows

package installer_test

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"
	"golang.org/x/sys/windows/registry"

	"a.yandex-team.ru/security/skotty/launcher/internal/installer"
)

func TestInstall(t *testing.T) {
	selfExe, err := os.Executable()
	require.NoError(t, err)

	tmpDir, err := os.MkdirTemp("", "skotty-launcher-*")
	require.NoError(t, err)
	defer func() { _ = os.RemoveAll(tmpDir) }()

	installDir := filepath.Join(tmpDir, "skotty", "launcher", "test")
	err = installer.Install(installDir)
	require.NoError(t, err)

	requireSameFile(t, selfExe, filepath.Join(installDir, "skotty.exe"))
	require.Truef(t, inPathEnv(t, installDir), "%q not found in the HKCU\\Environment[PATH]", installDir)
}

func inPathEnv(t *testing.T, target string) bool {
	getRegEnv := func(key string) (string, error) {
		k, err := registry.OpenKey(registry.CURRENT_USER, "Environment", registry.QUERY_VALUE)
		if err != nil {
			return "", err
		}
		defer func() { _ = k.Close() }()

		s, _, err := k.GetStringValue(key)
		return s, err
	}

	pathEnv, err := getRegEnv("PATH")
	require.NoError(t, err)

	const envDelim = string(os.PathListSeparator)
	paths := strings.Split(pathEnv, envDelim)
	for _, p := range paths {
		if p == target {
			return true
		}
	}

	return false
}
