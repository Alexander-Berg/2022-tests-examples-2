package crash_test

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/skotty/skotty/internal/crash"
)

func crashTstExec() (string, error) {
	return yatest.BinaryPath("security/skotty/skotty/internal/crash/crashtst/cmd/crash-handler/crash-handler")
}

func TestCrashNoRestarts(t *testing.T) {
	exitCodes := []int{0x0, 0x1}
	if runtime.GOOS == "windows" {
		exitCodes = append(exitCodes, 0x40010004)
	}

	for _, exitCode := range exitCodes {
		t.Run(fmt.Sprint(exitCode), func(t *testing.T) {
			tmpDir := os.TempDir()
			defer func() { _ = os.RemoveAll(tmpDir) }()

			var stderr bytes.Buffer
			s := crash.NewSaver(tmpDir,
				crash.WithName("crash-handler"),
				crash.WithExecutableFinder(crashTstExec),
				crash.WithArgs("-exit-code", fmt.Sprint(exitCode), "-time-to-exit", "0"),
				crash.WithStderr(&stderr),
				crash.WithRestartHandler(func() bool {
					t.Fatal("crasher restarted, but must not")
					return false
				}),
			)
			require.True(t, s.IsParent())
			actualCode, err := s.StartChild()
			require.NoError(t, err)
			require.Equal(t, exitCode, actualCode)
			require.Equal(t, "crash-handler started\nunder saver: yes\n", stderr.String())
		})
	}
}

func TestCrashRestarts(t *testing.T) {
	for _, exitCode := range []int{0x2, 0x8b} {
		t.Run(fmt.Sprint(exitCode), func(t *testing.T) {
			tmpDir := os.TempDir()
			defer func() { _ = os.RemoveAll(tmpDir) }()

			var restarts int
			var stderr bytes.Buffer
			s := crash.NewSaver(tmpDir,
				crash.WithName("crash-handler"),
				crash.WithExecutableFinder(crashTstExec),
				crash.WithArgs("-exit-code", fmt.Sprint(exitCode), "-time-to-exit", "0"),
				crash.WithStderr(&stderr),
				crash.WithRestartHandler(func() bool {
					restarts++
					return restarts < 2
				}),
			)

			actualCode, err := s.StartChild()
			require.NoError(t, err)
			require.Equal(t, exitCode, actualCode)
			require.Equal(t, 2, restarts)
			require.Equal(t, "crash-handler started\nunder saver: yes\ncrash-handler started\nunder saver: yes\n", stderr.String())

			files, err := filepath.Glob(filepath.Join(tmpDir, "crash.*.stderr"))
			require.NoError(t, err)
			require.Len(t, files, 2)
		})
	}
}

func TestCrashArgs(t *testing.T) {
	exe, err := yatest.BinaryPath("security/skotty/skotty/internal/crash/crashtst/cmd/self-crash/self-crash")
	require.NoError(t, err)

	var stdout bytes.Buffer
	expectedArgs := []string{
		"-lol", "kek", "--", "cheburek",
	}
	cmd := exec.Command(exe, expectedArgs...)
	cmd.Stdout = &stdout
	err = cmd.Run()
	require.NoError(t, err)

	var actualArgs []string
	err = json.Unmarshal(stdout.Bytes(), &actualArgs)
	require.NoError(t, err)
	require.ElementsMatch(t, expectedArgs, actualArgs)
}

func TestCrashNeedRestarts(t *testing.T) {
	tmpDir := os.TempDir()
	defer func() { _ = os.RemoveAll(tmpDir) }()

	crashExe, err := crashTstExec()
	require.NoError(t, err)

	holeExe, err := yatest.BinaryPath("security/skotty/skotty/internal/crash/crashtst/cmd/blackhole/blackhole")
	require.NoError(t, err)

	exe := crashExe
	var stderr bytes.Buffer
	var restarts int
	s := crash.NewSaver(tmpDir,
		crash.WithName("crash-handler"),
		crash.WithExecutableFinder(func() (string, error) {
			return exe, nil
		}),
		crash.WithArgs("-exit-code", fmt.Sprint(crash.NeedRestartExitCode), "-time-to-exit", "0"),
		crash.WithStderr(&stderr),
		crash.WithRestartHandler(func() bool {
			exe = holeExe
			restarts++
			return true
		}),
	)

	actualCode, err := s.StartChild()
	require.NoError(t, err)
	require.Equal(t, 0, actualCode)
	require.Equal(t, 1, restarts)
	require.Equal(t, "crash-handler started\nunder saver: yes\n", stderr.String())
}
