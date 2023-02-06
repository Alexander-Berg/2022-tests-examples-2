package stateviewer

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/stateviewertypes"
)

func TestVersion(t *testing.T) {
	sv, err := NewStateviewer()
	require.NoError(t, err)

	t.Run("initial state", func(t *testing.T) {
		require.Len(t, sv.versions, 0)
		require.Len(t, sv.versionsCmd, 0)

		v, err := sv.GetVersions()
		require.Error(t, err)
		require.Equal(t, "there is no versions info in memory", err.Error())
		require.Nil(t, v)

		v = sv.GetInstallVersionCmd()
		require.Len(t, v, 0)

		rErr, err := sv.AddInstallVersionCmd("cfg", "1.0.0")
		require.Error(t, err)
		require.Equal(t, "there is no versions info in memory", err.Error())
		require.NoError(t, rErr)

		require.Len(t, sv.versions, 0)
		require.Len(t, sv.versionsCmd, 0)
	})

	t.Run("set version", func(t *testing.T) {
		sv.SetVersions(stateviewertypes.Versions{
			"cfg": "0.5",
			"bin": "1.5",
		})
		require.Len(t, sv.versions, 2)
		require.Len(t, sv.versionsCmd, 0)

		v, err := sv.GetVersions()
		require.NoError(t, err)
		require.Contains(t, v, "cfg")
		require.Equal(t, "0.5", v["cfg"])
		require.Contains(t, v, "bin")
		require.Equal(t, "1.5", v["bin"])

		v = sv.GetInstallVersionCmd()
		require.Len(t, v, 0)
	})

	t.Run("add cmd", func(t *testing.T) {
		rErr, err := sv.AddInstallVersionCmd("cfg"+"rnd", "1.0.0")
		require.NoError(t, err)
		require.Error(t, rErr)
		require.Equal(t, "unknown package: cfgrnd", rErr.Error())
		require.Len(t, sv.versions, 2)
		require.Len(t, sv.versionsCmd, 0)

		rErr, err = sv.AddInstallVersionCmd("cfg", "1.0.0")
		require.NoError(t, err)
		require.NoError(t, rErr)
		require.Len(t, sv.versions, 2)
		require.Len(t, sv.versionsCmd, 1)

		v := sv.GetInstallVersionCmd()
		require.Len(t, v, 1)
		require.Contains(t, v, "cfg")
		require.Equal(t, "1.0.0", v["cfg"])

		rErr, err = sv.AddInstallVersionCmd("bin", "1.0.0")
		require.NoError(t, err)
		require.NoError(t, rErr)
	})

	t.Run("set same version", func(t *testing.T) {
		sv.SetVersions(stateviewertypes.Versions{
			"cfg": "0.5",
			"bin": "1.5",
		})
		require.Len(t, sv.versions, 2)
		require.Len(t, sv.versionsCmd, 2)

		v, err := sv.GetVersions()
		require.NoError(t, err)
		require.Contains(t, v, "cfg")
		require.Equal(t, "0.5", v["cfg"])
		require.Contains(t, v, "bin")
		require.Equal(t, "1.5", v["bin"])
	})

	t.Run("set new version", func(t *testing.T) {
		sv.SetVersions(stateviewertypes.Versions{
			"cfg": "1.0.0",
			"bin": "1.5",
		})
		require.Len(t, sv.versions, 2)
		require.Len(t, sv.versionsCmd, 1)

		v, err := sv.GetVersions()
		require.NoError(t, err)
		require.Contains(t, v, "cfg")
		require.Equal(t, "1.0.0", v["cfg"])
		require.Contains(t, v, "bin")
		require.Equal(t, "1.5", v["bin"])
	})
}
