package ammo

import (
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/clitypes"
	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/prospectortypes"
)

func TestGetMetaInfo(t *testing.T) {
	meta, err := getMetaInfo("/some_mega_file")
	require.NoError(t, err)
	require.Nil(t, meta)

	meta, err = getMetaInfo("/root/.bashrc")
	require.Error(t, err)
	require.Contains(t, err.Error(), "permission denied")
	require.Nil(t, meta)

	tmpFile := "./tmp.file"
	require.NoError(t, ioutil.WriteFile(tmpFile, []byte("{"), 0644))
	defer func() { _ = os.Remove(tmpFile) }()

	meta, err = getMetaInfo(tmpFile)
	require.EqualError(t, err, "failed to parse meta: ./tmp.file: unexpected end of JSON input")
	require.Nil(t, meta)

	require.NoError(t, ioutil.WriteFile(tmpFile, []byte(`{"status":"some value", "born":100500}`), 0644))

	meta, err = getMetaInfo(tmpFile)
	require.NoError(t, err)
	require.NotNil(t, meta)
	require.Equal(t, "some value", meta.Status)
	require.Equal(t, "", meta.Error)
	require.Equal(t, uint64(100500), meta.Born)
}

func TestGetHostPackInfo(t *testing.T) {
	hInfo, hostname, err := getHostPackInfo("/root/", ".bashrc")
	require.Error(t, err)
	require.Equal(t, "allowed only ammo in gz: .bashrc", err.Error())
	require.Nil(t, hInfo)
	require.Equal(t, "", hostname)

	hInfo, hostname, err = getHostPackInfo("/root/", ".bashrc.gz")
	require.Error(t, err)
	require.Contains(t, err.Error(), "permission denied")
	require.Nil(t, hInfo)
	require.Equal(t, ".bashrc", hostname)

	tmpFile := "tmp.file.gz"
	hInfo, hostname, err = getHostPackInfo(".", tmpFile)
	require.NoError(t, err)
	require.NotNil(t, hInfo)
	require.Equal(t, clitypes.AmmoInProgress.String(), hInfo.Status)
	require.Equal(t, "tmp.file", hostname)

	tmpMetaFile := "tmp.file" + prospectortypes.MetaFileSuffix
	require.NoError(t, ioutil.WriteFile(tmpMetaFile, []byte(`{"status":"some value", "born":100500, "error":"kek"}`), 0644))
	defer func() { _ = os.Remove(tmpMetaFile) }()

	hInfo, hostname, err = getHostPackInfo(".", tmpFile)
	require.NoError(t, err)
	require.NotNil(t, hInfo)
	require.Equal(t, clitypes.AmmoInvalid.String(), hInfo.Status)
	require.Equal(t, "Invalid ammo pack: ./tmp.file.meta. Status=some value. Error: kek", hInfo.Error)
	require.Equal(t, "tmp.file", hostname)

	require.NoError(t, ioutil.WriteFile(tmpMetaFile, []byte(`{"status":"oK", "born":100500}`), 0644))
	hInfo, hostname, err = getHostPackInfo(".", tmpFile)
	require.Error(t, err)
	require.Equal(t, err.Error(), "Failed to stat ammo file: ./tmp.file.gz: stat ./tmp.file.gz: no such file or directory")
	require.Nil(t, hInfo)
	require.Equal(t, "tmp.file", hostname)

	require.NoError(t, ioutil.WriteFile(tmpFile, []byte("aaaaaa"), 0644))
	defer func() { _ = os.Remove(tmpFile) }()

	hInfo, hostname, err = getHostPackInfo(".", tmpFile)
	require.NoError(t, err)
	require.NotNil(t, hInfo)
	require.Equal(t, clitypes.AmmoReady.String(), hInfo.Status)
	require.Equal(t, "", hInfo.Error)
	require.Equal(t, uint64(100500), hInfo.Born)
	require.Equal(t, uint64(6), hInfo.Size)
	require.Equal(t, "tmp.file", hostname)
}

func TestListPacks(t *testing.T) {
	tmpDir := "./tmpdir"
	err := os.Mkdir(tmpDir, os.ModePerm)
	require.NoError(t, err)
	defer func() { _ = os.RemoveAll(tmpDir) }()

	t.Run("error", func(t *testing.T) {
		_, err := listPack("/etc/passwd")
		require.Error(t, err)
	})

	t.Run("zero files", func(t *testing.T) {
		info, err := listPack(tmpDir)
		require.NoError(t, err)
		require.Equal(t, clitypes.AmmoInProgress.String(), info.Status)
	})

	t.Run("one file in progress", func(t *testing.T) {
		require.NoError(t, ioutil.WriteFile(
			tmpDir+"/host1.gz",
			[]byte(`bbbbbb`), 0644))

		info, err := listPack(tmpDir)
		require.NoError(t, err)
		require.Equal(t, clitypes.AmmoInProgress.String(), info.Status)
		require.Equal(t, 1, len(info.Hosts))
	})

	t.Run("two files", func(t *testing.T) {
		require.NoError(t, ioutil.WriteFile(
			tmpDir+"/host2.gz",
			[]byte(`aaa`), 0644))
		require.NoError(t, ioutil.WriteFile(
			tmpDir+"/host2"+prospectortypes.MetaFileSuffix,
			[]byte(`{"status":"ok", "born":100499}`), 0644))

		info, err := listPack(tmpDir)
		require.NoError(t, err)
		require.Equal(t, clitypes.AmmoInProgress.String(), info.Status)
		require.Equal(t, 2, len(info.Hosts))
		require.Equal(t, uint64(3), info.Size)
		require.Equal(t, uint64(100499), info.Born)
	})

	t.Run("two file are clitypes.AmmoReady", func(t *testing.T) {
		require.NoError(t, ioutil.WriteFile(
			tmpDir+"/host1"+prospectortypes.MetaFileSuffix,
			[]byte(`{"status":"ok", "born":100500}`), 0644))

		info, err := listPack(tmpDir)
		require.NoError(t, err)
		require.Equal(t, clitypes.AmmoReady.String(), info.Status)
		require.Equal(t, 2, len(info.Hosts))
		require.Equal(t, uint64(9), info.Size)
		require.Equal(t, uint64(100499), info.Born)
	})

	t.Run("three files", func(t *testing.T) {
		require.NoError(t, ioutil.WriteFile(
			tmpDir+"/host3.gz",
			[]byte(`cccc`), 0644))
		require.NoError(t, ioutil.WriteFile(
			tmpDir+"/host3"+prospectortypes.MetaFileSuffix,
			[]byte(`{"status":"ok", "born":100501}`), 0644))

		info, err := listPack(tmpDir)
		require.NoError(t, err)
		require.Equal(t, clitypes.AmmoReady.String(), info.Status)
		require.Equal(t, 3, len(info.Hosts))
		require.Equal(t, uint64(13), info.Size)
		require.Equal(t, uint64(100499), info.Born)
	})

	t.Run("some error", func(t *testing.T) {
		require.NoError(t, ioutil.WriteFile(
			tmpDir+"/host2"+prospectortypes.MetaFileSuffix,
			[]byte(`{"status":"errr", "error":"kek"}`), 0644))

		info, err := listPack(tmpDir)
		require.NoError(t, err)
		require.Equal(t, clitypes.AmmoInvalid.String(), info.Status)
		require.Equal(t, 3, len(info.Hosts))
		require.Equal(t, uint64(10), info.Size)
		require.Equal(t, uint64(100500), info.Born)
	})
}

func TestList(t *testing.T) {
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

	res, err := state.List()
	require.NoError(t, err)
	require.Len(t, res, 2)
	require.Contains(t, res, "pack1")
	require.Equal(t, uint64(4), (res)["pack1"].Size)
	require.Equal(t, clitypes.AmmoReady.String(), (res)["pack1"].Status)
	require.Contains(t, res, "pack2")
	require.Equal(t, uint64(7), (res)["pack2"].Size)
	require.Equal(t, clitypes.AmmoReady.String(), (res)["pack2"].Status)

	state.task = &createTask{id: "pack1"}
	res, err = state.List()
	require.NoError(t, err)
	require.Len(t, res, 2)
	require.Contains(t, res, "pack1")
	require.Equal(t, uint64(4), (res)["pack1"].Size)
	require.Equal(t, clitypes.AmmoInProgress.String(), (res)["pack1"].Status)
	require.Contains(t, res, "pack2")
	require.Equal(t, uint64(7), (res)["pack2"].Size)
	require.Equal(t, clitypes.AmmoReady.String(), (res)["pack2"].Status)
}
