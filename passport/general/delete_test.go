package ammo

import (
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/prospectortypes"
)

func TestDelete(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	pack1 := tmpDir + "/pack1"
	require.NoError(t, os.Mkdir(pack1, os.ModePerm))
	pack2 := tmpDir + "/pack2"
	require.NoError(t, os.Mkdir(pack2, os.ModePerm))

	require.NoError(t, ioutil.WriteFile(
		pack1+"/host1.gz",
		[]byte(`cccc`), 0644))
	require.NoError(t, ioutil.WriteFile(
		pack1+"/host1"+prospectortypes.MetaFileSuffix,
		[]byte(`{"status":"ok", "born":100501}`), 0644))

	require.NoError(t, ioutil.WriteFile(
		pack2+"/host1.gz",
		[]byte(`aaaaaaa`), 0644))
	require.NoError(t, ioutil.WriteFile(
		pack2+"/host1"+prospectortypes.MetaFileSuffix,
		[]byte(`{"status":"ok", "born":100499}`), 0644))

	cfg := Config{
		Dir: tmpDir,
	}
	state, err := NewAmmo(cfg)
	require.NoError(t, err)
	defer state.Stop()

	listRes, err := state.List()
	require.NoError(t, err)
	require.Len(t, listRes, 2)
	require.Contains(t, listRes, "pack1")
	require.Contains(t, listRes, "pack2")

	res, rErr, err := state.Delete("pack1")
	require.NoError(t, err)
	require.NoError(t, rErr)
	require.Contains(t, res, "status")
	require.Equal(t, "ok", res["status"])

	listRes, err = state.List()
	require.NoError(t, err)
	require.Len(t, listRes, 1)
	require.Contains(t, listRes, "pack2")

	_, rErr, err = state.Delete("pack1")
	require.NoError(t, err)
	require.EqualError(t, rErr, "ammo is absent: pack1")
}
