package sfx_test

import (
	"os"
	"os/exec"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/libs/go/sfx"
)

func TestZip(t *testing.T) {
	target, err := os.CreateTemp("", "")
	require.NoError(t, err)
	t.Logf("target: %s\n", target.Name())
	defer func() {
		_ = os.Remove(target.Name())
	}()

	_, err = target.WriteString("lol kek cheburek")
	require.NoError(t, err)
	require.NoError(t, target.Close())

	contentDir, err := os.MkdirTemp("", "")
	require.NoError(t, err)
	t.Logf("content dir: %s\n", contentDir)
	defer func() {
		_ = os.RemoveAll(contentDir)
	}()

	err = os.MkdirAll(filepath.Join(contentDir, "lol"), 0777)
	require.NoError(t, err)
	err = os.WriteFile(filepath.Join(contentDir, "lol", "kek.txt"), []byte("kek"), 0777)
	require.NoError(t, err)
	stat, err := os.Stat(filepath.Join(contentDir, "lol", "kek.txt"))
	require.NoError(t, err)
	expectedPerm := stat.Mode().Perm()

	err = sfx.Zip(target.Name(), []string{contentDir})
	require.NoError(t, err)

	require.True(t, sfx.IsZip(target.Name()))

	list, err := sfx.List(target.Name())
	require.NoError(t, err)
	require.Len(t, list, 1)

	extractDir, err := os.MkdirTemp("", "")
	require.NoError(t, err)
	t.Logf("extract dir: %s\n", extractDir)
	defer func() {
		_ = os.RemoveAll(extractDir)
	}()

	err = sfx.Unzip(target.Name(), extractDir)
	require.NoError(t, err)

	info, err := os.Stat(filepath.Join(extractDir, "lol", "kek.txt"))
	require.NoError(t, err)

	require.Equal(t, expectedPerm, info.Mode().Perm())
	actualContent, err := os.ReadFile(filepath.Join(extractDir, "lol", "kek.txt"))
	require.NoError(t, err)
	require.Equal(t, []byte("kek"), actualContent)
}

func TestSfx(t *testing.T) {
	sfxBin, err := yatest.BinaryPath("security/libs/go/sfx/cmd/sfx/sfx")
	require.NoError(t, err)

	runSfx := func(args ...string) error {
		cmd := exec.Command(sfxBin, args...)
		return cmd.Run()
	}

	target, err := os.CreateTemp("", "")
	require.NoError(t, err)
	t.Logf("target: %s\n", target.Name())
	defer func() {
		_ = os.Remove(target.Name())
	}()

	_, err = target.WriteString("lol kek cheburek")
	require.NoError(t, err)
	require.NoError(t, target.Close())

	contentDir, err := os.MkdirTemp("", "")
	require.NoError(t, err)
	t.Logf("content dir: %s\n", contentDir)
	defer func() {
		_ = os.RemoveAll(contentDir)
	}()

	err = os.WriteFile(filepath.Join(contentDir, "kek.txt"), []byte("kek"), 0777)
	require.NoError(t, err)
	stat, err := os.Stat(filepath.Join(contentDir, "kek.txt"))
	require.NoError(t, err)
	expectedPerm := stat.Mode().Perm()

	err = runSfx("create", target.Name(), contentDir)
	require.NoError(t, err)

	require.True(t, sfx.IsZip(target.Name()))

	list, err := sfx.List(target.Name())
	require.NoError(t, err)
	require.Len(t, list, 1)

	extractDir, err := os.MkdirTemp("", "")
	require.NoError(t, err)
	t.Logf("extract dir: %s\n", extractDir)
	defer func() {
		_ = os.RemoveAll(extractDir)
	}()

	err = runSfx("extract", target.Name(), extractDir)
	require.NoError(t, err)

	info, err := os.Stat(filepath.Join(extractDir, "kek.txt"))
	require.NoError(t, err)

	require.Equal(t, expectedPerm, info.Mode().Perm())
	actualContent, err := os.ReadFile(filepath.Join(extractDir, "kek.txt"))
	require.NoError(t, err)
	require.Equal(t, []byte("kek"), actualContent)
}
