package gotest

import (
	"bytes"
	"crypto/sha256"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
)

func isExecAll(mode os.FileMode) bool {
	return mode&0111 == 0111
}

func hashFile(t *testing.T, filePath string) string {
	f, err := os.Open(filePath)
	require.NoError(t, err)
	defer func() { _ = f.Close() }()

	h := sha256.New()
	_, err = io.Copy(h, f)
	require.NoError(t, err)

	return fmt.Sprintf("%x", h.Sum(nil))
}

func testIsLauncher(t *testing.T, filePath string) {
	cmd := exec.Command(filePath, "--is-launcher")
	cmd.Env = []string{}
	var b bytes.Buffer
	cmd.Stdout = &b
	require.NoError(t, cmd.Run())

	require.Equal(t, "yep", string(bytes.TrimSpace(b.Bytes())))
}

func testSelfInstall(t *testing.T, patcher func(t *testing.T, cmd *exec.Cmd)) error {
	launcherPath, err := yatest.BinaryPath("security/skotty/launcher/cmd/launcher/launcher")
	require.NoError(t, err)

	runtimeDir, err := os.MkdirTemp("", "")
	require.NoError(t, err)

	defer func() {
		_ = os.RemoveAll(runtimeDir)
	}()

	installDir := filepath.Join(runtimeDir, "install_here")

	cmd := exec.Command(launcherPath, "--self-install")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Env = []string{
		"HOME=" + runtimeDir,
		"SKOTTY_INSTALL_DIR=" + installDir,
	}
	if patcher != nil {
		patcher(t, cmd)
	}

	if err := cmd.Run(); err != nil {
		return err
	}

	installerPath := filepath.Join(installDir, "skotty")
	if runtime.GOOS == "windows" {
		installerPath += ".exe"
	}

	fi, err := os.Stat(installerPath)
	require.NoError(t, err)

	require.True(t, isExecAll(fi.Mode()))
	require.True(t, fi.Mode().IsRegular())
	require.Equal(t, hashFile(t, launcherPath), hashFile(t, installerPath))

	testIsLauncher(t, installerPath)
	return nil
}

func TestSelfInstall(t *testing.T) {
	err := testSelfInstall(t, nil)
	require.NoError(t, err)
}

func TestSelfInstall_autocheckRoot(t *testing.T) {
	if val, ok := yatest.BuildFlag("AUTOCHECK"); !ok || val != "yes" {
		t.Skip("supported ONLY under CI")
		return
	}

	test := func(t *testing.T, ok bool, args ...string) {
		err := testSelfInstall(t, func(t *testing.T, cmd *exec.Cmd) {
			cmd.Args = append(cmd.Args, args...)
			cmd.Env = append(cmd.Env, "TRUST_ME_IAM_ROOT=yes")
		})

		if ok {
			require.NoError(t, err)
		} else {
			require.Error(t, err)
		}
	}

	t.Run("with_allow_root", func(t *testing.T) {
		test(t, true, "--allow-root")
	})

	t.Run("without_allow_root", func(t *testing.T) {
		test(t, false)
	})
}
