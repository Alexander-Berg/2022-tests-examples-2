//go:build !windows
// +build !windows

package installer_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

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

	requireSameFile(t, selfExe, filepath.Join(installDir, "skotty"))
}
