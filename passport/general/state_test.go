package shooter

import (
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/internal/ammo"
	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/internal/locker"
	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/internal/shooting"
	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/prospectortypes"
)

type testCmdCreatorImpl struct {
	cmds []string
}

type testCmd struct {
	runOutput   []byte
	runError    error
	pid         int
	signalError error

	stop chan bool
}

func (t *testCmdCreatorImpl) Create(command string) shooting.Cmd {
	if t.cmds == nil {
		t.cmds = make([]string, 0)
	}
	t.cmds = append(t.cmds, command)

	return &testCmd{
		stop: make(chan bool),
	}
}

func (c *testCmd) Run() ([]byte, error) {
	<-c.stop
	return c.runOutput, c.runError
}

func (c *testCmd) GetPid() int {
	return c.pid
}

func (c *testCmd) Signal(sig os.Signal) error {
	close(c.stop)
	return c.signalError
}

func TestState(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	cfg := Config{
		Shooting: shooting.Config{
			GorPath: "/usr/bin/lol",
			Target:  "my.host.ru",
		},
		Ammo: ammo.Config{
			Dir: tmpDir,
		},
	}
	lock, err := locker.NewLocker(cfg.Lock)
	require.NoError(t, err)

	st, err := NewState(cfg, lock)
	require.NoError(t, err)
	cr := &testCmdCreatorImpl{}

	ammoID := "kekekekeke"

	t.Run("invalid schema", func(t *testing.T) {
		params := shooting.Params{}
		res, rErr, err := st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "schema is unknown: ", rErr.Error())
		require.Nil(t, res)

		params.Schema = "asdasdjkn"
		res, rErr, err = st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "schema is unknown: asdasdjkn", rErr.Error())
		require.Nil(t, res)
	})

	t.Run("invalid instances", func(t *testing.T) {
		params := shooting.Params{
			Schema: "http",
		}
		res, rErr, err := st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "instances cannot be 0", rErr.Error())
		require.Nil(t, res)
	})

	t.Run("invalid duration", func(t *testing.T) {
		params := shooting.Params{
			Schema:    "https",
			Instances: 3,
			Duration:  shooting.MaxDuration + 1,
		}
		res, rErr, err := st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "shooting duration is too longer then 1 hour: 3601 seconds", rErr.Error())
		require.Nil(t, res)
	})

	t.Run("invalid ammo", func(t *testing.T) {
		params := shooting.Params{
			Schema:    "https",
			Instances: 3,
		}
		res, rErr, err := st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "missing ammo pack: ", rErr.Error())
		require.Nil(t, res)

		params.AmmoID = ammoID
		res, rErr, err = st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "missing ammo pack: kekekekeke", rErr.Error())
		require.Nil(t, res)
	})

	require.NoError(t, os.Mkdir(tmpDir+"/"+ammoID, os.ModePerm))
	t.Run("ammo is not ready", func(t *testing.T) {
		params := shooting.Params{
			Schema:    "https",
			Instances: 3,
			AmmoID:    ammoID,
		}
		res, rErr, err := st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "ammo pack is not ready: InProgress", rErr.Error())
		require.Nil(t, res)
	})

	require.NoError(t, ioutil.WriteFile(
		tmpDir+"/"+ammoID+"/host1.gz",
		[]byte(`aaaaaaa`), 0644))
	require.NoError(t, ioutil.WriteFile(
		tmpDir+"/"+ammoID+"/host1"+prospectortypes.MetaFileSuffix,
		[]byte(`{"status":"ok", "born":100499}`), 0644))
	t.Run("ok: start", func(t *testing.T) {
		params := shooting.Params{
			Schema:    "https",
			Instances: 3,
			AmmoID:    ammoID,
		}
		res, rErr, err := st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.NoError(t, rErr)
		require.Equal(t, shooting.StartResult{"status": "ok"}, res)
	})

	t.Run("double start", func(t *testing.T) {
		params := shooting.Params{
			Schema:    "https",
			Instances: 3,
			AmmoID:    ammoID,
		}
		res, rErr, err := st.ShootingStart(params, cr)
		require.NoError(t, err)
		require.Equal(t, "shooting is already running", rErr.Error())
		require.Nil(t, res)
	})

	t.Run("ok: stop", func(t *testing.T) {
		res, rErr, err := st.ShootingStop()
		require.NoError(t, err)
		require.NoError(t, rErr)
		require.Equal(t, shooting.StopResult{"status": "ok"}, res)
	})

	t.Run("double stop", func(t *testing.T) {
		res, rErr, err := st.ShootingStop()
		require.NoError(t, err)
		require.Equal(t, "nothing to stop", rErr.Error())
		require.Nil(t, res)
	})
}
