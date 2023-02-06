package cgroup_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
	"golang.org/x/sys/unix"

	"a.yandex-team.ru/security/gideon/gideon/internal/cgroup"
	"a.yandex-team.ru/security/gideon/gideon/internal/cgroup/internal"
)

const (
	freezerCGroupRoot = "/feeezer_cgroup"
)

func TestGetCgroupID(t *testing.T) {
	cases := map[string]struct {
		path         string
		createCGroup bool
		err          bool
	}{
		"first_level": {
			path:         "kek",
			createCGroup: true,
			err:          false,
		},
		"second_level": {
			path:         "lol/kek",
			createCGroup: true,
			err:          false,
		},
		"non_cgroup": {
			path:         "cheburek",
			createCGroup: false,
			err:          true,
		},
	}

	mountFreezer(t)
	defer umountFreezer(t)
	for name, tc := range cases {
		t.Run(name, func(t *testing.T) {
			path := filepath.Join(freezerCGroupRoot, tc.path)
			var expectedID uint64
			if tc.createCGroup {
				expectedID = createFreezer(t, path)
				defer removeFreezer(t, path)
			}

			actualID, err := cgroup.GetCgroupID(path)
			if tc.err {
				require.Error(t, err)
				require.Zero(t, actualID)
			} else {
				require.NoError(t, err)
				require.Equal(t, expectedID, actualID)
			}
		})
	}
}

func mountFreezer(t *testing.T) {
	err := os.MkdirAll(freezerCGroupRoot, 0777)
	require.NoError(t, err)

	err = unix.Mount("none", freezerCGroupRoot, "cgroup", 0, "freezer")
	require.NoError(t, err, "mount fail")
}

func umountFreezer(t *testing.T) {
	err := unix.Unmount(freezerCGroupRoot, unix.MNT_FORCE)
	require.NoError(t, err, "umount fail")
	_ = os.RemoveAll(freezerCGroupRoot)
}

func createFreezer(t *testing.T, path string) uint64 {
	err := os.MkdirAll(path, 0777)
	require.NoError(t, err)

	id, err := internal.GetCgroupIDCGO(path)
	require.NoError(t, err)
	return id
}

func removeFreezer(t *testing.T, path string) {
	err := os.RemoveAll(path)
	require.NoError(t, err)
}
