package gotest

import (
	"os"
	"os/exec"
	"syscall"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestSelfInstall_realRoot(t *testing.T) {
	test := func(t *testing.T, ok bool, args ...string) {
		err := testSelfInstall(t, func(t *testing.T, cmd *exec.Cmd) {
			cmd.Args = append(cmd.Args, args...)

			cmd.SysProcAttr = &syscall.SysProcAttr{
				Cloneflags: syscall.CLONE_NEWUSER,
				UidMappings: []syscall.SysProcIDMap{
					{
						ContainerID: 0,
						HostID:      os.Getuid(),
						Size:        1,
					},
				},
				GidMappings: []syscall.SysProcIDMap{
					{
						ContainerID: 0,
						HostID:      os.Getgid(),
						Size:        1,
					},
				},
			}
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
