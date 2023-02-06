package prospector

import (
	"errors"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/prospectortypes"
)

type testHTTPGetter struct {
	code     int
	response []byte
	err      error

	requests []string
}

func (t *testHTTPGetter) Get(path string) (int, []byte, error) {
	if t.requests == nil {
		t.requests = make([]string, 0)
	}
	t.requests = append(t.requests, path)
	return t.code, t.response, t.err
}

type testCmdRunner struct {
	out []byte
	err error

	commands []string
}

func (t *testCmdRunner) Run(cmd string) ([]byte, error) {
	if t.commands == nil {
		t.commands = make([]string, 0)
	}
	t.commands = append(t.commands, cmd)
	return t.out, t.err
}

func TestParseTaskResponse(t *testing.T) {
	task, err := parseTaskResponse(400, []byte("kek"))
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to get task from shooter: code 400: kek")
	require.Nil(t, task)

	task, err = parseTaskResponse(200, []byte("kek"))
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to parse task from shooter: code 200: kek")
	require.Nil(t, task)

	task, err = parseTaskResponse(200, []byte(`{"id":"kek", "duration":100500}`))
	require.NoError(t, err)
	require.Equal(t, "kek", task.ID)
	require.Equal(t, uint32(100500), task.Duration)
}

func TestCleanupFiles(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	require.NoError(t, ioutil.WriteFile(
		tmpDir+"/file1",
		[]byte(`bbbbbb`), 0644))
	require.NoError(t, ioutil.WriteFile(
		tmpDir+"/"+metaFileName,
		[]byte(`bbbbbb`), 0644))

	require.NoError(t, cleanupFiles(tmpDir))

	_, err := os.Stat(tmpDir + "/" + metaFileName)
	require.NoError(t, err)

	_, err = os.Stat(tmpDir + "/file1")
	require.True(t, os.IsNotExist(err))
}

func TestGetTask(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	t.Run("http request failed", func(t *testing.T) {
		hg := &testHTTPGetter{
			err: errors.New("foo"),
		}
		_, err := getTask(tmpDir, "my.host.ru", "lol", hg)
		require.Error(t, err)
		require.Equal(t, "failed to get task from shooter: foo", err.Error())
		require.Equal(t, []string{"/prospector/task?host=my.host.ru"}, hg.requests)
	})

	t.Run("bad http code", func(t *testing.T) {
		hg := &testHTTPGetter{
			code:     403,
			response: []byte("ooo"),
		}
		_, err := getTask(tmpDir, "my.host.ru", "lol", hg)
		require.Error(t, err)
		require.Equal(t, "failed to parse task from shooter: failed to get task from shooter: code 403: ooo", err.Error())
		require.Equal(t, []string{"/prospector/task?host=my.host.ru"}, hg.requests)
	})

	t.Run("no task", func(t *testing.T) {
		hg := &testHTTPGetter{
			code:     200,
			response: []byte(`{}`),
		}
		task, err := getTask(tmpDir, "my.host.ru", "lol", hg)
		require.NoError(t, err)
		require.Equal(t, []string{"/prospector/task?host=my.host.ru"}, hg.requests)
		require.Nil(t, task)
	})

	t.Run("task already done", func(t *testing.T) {
		hg := &testHTTPGetter{
			code:     200,
			response: []byte(`{"id":"lol", "duration":100500}`),
		}
		task, err := getTask(tmpDir, "my.host.ru", "lol", hg)
		require.NoError(t, err)
		require.Equal(t, []string{"/prospector/task?host=my.host.ru"}, hg.requests)
		require.Nil(t, task)
	})

	t.Run("got common task", func(t *testing.T) {
		hg := &testHTTPGetter{
			code:     200,
			response: []byte(`{"id":"kek", "duration":100500}`),
		}
		task, err := getTask(tmpDir, "my.host.ru", "lol", hg)
		require.NoError(t, err)
		require.Equal(t, []string{"/prospector/task?host=my.host.ru"}, hg.requests)
		require.NotNil(t, task)
		require.Equal(t, "kek", task.ID)
		require.Equal(t, uint32(100500), task.Duration)
	})
}

func TestWriteMetaToDisk(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	m := Meta{ID: "qwer"}
	require.NoError(t, writeMetaToDisk(tmpDir, m))

	data, err := ioutil.ReadFile(tmpDir + "/" + metaFileName)
	require.NoError(t, err)
	require.Equal(t, []byte(`{"last_task_id":"qwer"}`), data)
}

func TestDumpRequests(t *testing.T) {
	cfg := &cfgAmmo{
		Dir:           "/var/foo",
		GorPath:       "/etc/bar",
		ListenPort:    1005,
		FileSizeLimit: 110923120932,
	}

	expectedCmd := []string{"sudo /etc/bar --input-raw :1005 --output-file /var/foo/my.host.ru --exit-after 42s --output-file-append --output-file-flush-interval 10s --output-file-max-size-limit 110923120932"}

	t.Run("with error", func(t *testing.T) {
		cr := &testCmdRunner{
			err: errors.New("kek"),
		}
		err := dumpRequests(cfg, uint32(42), "my.host.ru", cr)
		require.Error(t, err)
		require.Equal(t, "kek", err.Error())
		require.Equal(t, expectedCmd, cr.commands)
	})

	t.Run("ok", func(t *testing.T) {
		cr := &testCmdRunner{}
		err := dumpRequests(cfg, uint32(42), "my.host.ru", cr)
		require.NoError(t, err)
		require.Equal(t, expectedCmd, cr.commands)
	})
}

func TestCorrectPermissions(t *testing.T) {
	cfg := &cfgAmmo{
		Dir:       "/var/foo",
		LocalUser: "vasya",
	}

	expectedCmd := []string{"sudo chown vasya /var/foo/my.host.ru"}

	t.Run("with error", func(t *testing.T) {
		cr := &testCmdRunner{
			err: errors.New("kek"),
		}
		err := correctPermissions(cfg, "my.host.ru", cr)
		require.Error(t, err)
		require.Equal(t, "kek", err.Error())
		require.Equal(t, expectedCmd, cr.commands)
	})

	t.Run("ok", func(t *testing.T) {
		cr := &testCmdRunner{}
		err := correctPermissions(cfg, "my.host.ru", cr)
		require.NoError(t, err)
		require.Equal(t, expectedCmd, cr.commands)
	})
}

func TestCompactRequests(t *testing.T) {
	expectedCmd := []string{"gzip /var/foo/my.host.ru"}

	t.Run("with error", func(t *testing.T) {
		cr := &testCmdRunner{
			err: errors.New("kek"),
		}
		_, err := compactRequests("/var/foo", "my.host.ru", cr)
		require.Error(t, err)
		require.Equal(t, "kek", err.Error())
		require.Equal(t, expectedCmd, cr.commands)
	})

	t.Run("ok", func(t *testing.T) {
		cr := &testCmdRunner{}
		filename, err := compactRequests("/var/foo", "my.host.ru", cr)
		require.NoError(t, err)
		require.Equal(t, expectedCmd, cr.commands)
		require.Equal(t, "/var/foo/my.host.ru.gz", filename)
	})
}

func TestSendRequests(t *testing.T) {
	cfg := &cfgScp{
		RemoteUser:     "vasya",
		Host:           "my.host.ru",
		PrivateKeyPath: "/etc/bar",
		RemoteDir:      "/var/foo",
		BandwidthKbits: 100500,
	}

	expectedCmd := []string{"scp -o StrictHostKeyChecking=no -i /etc/bar -l 100500 /var/tmp/lol vasya@my.host.ru:/var/foo/qwert"}

	t.Run("with error", func(t *testing.T) {
		cr := &testCmdRunner{
			err: errors.New("kek"),
		}
		err := sendRequests(cfg, "/var/tmp/lol", "qwert", cr)
		require.Error(t, err)
		require.Equal(t, "kek", err.Error())
		require.Equal(t, expectedCmd, cr.commands)
	})

	t.Run("ok", func(t *testing.T) {
		cr := &testCmdRunner{}
		err := sendRequests(cfg, "/var/tmp/lol", "qwert", cr)
		require.NoError(t, err)
		require.Equal(t, expectedCmd, cr.commands)
	})
}

func TestSendMeta(t *testing.T) {
	cfg := &cfgScp{
		RemoteUser:     "vasya",
		Host:           "my.host.ru",
		PrivateKeyPath: "/etc/bar",
		RemoteDir:      "/var/foo",
		BandwidthKbits: 100500,
	}

	meta := prospectortypes.AmmoPackMetaInfo{
		Status: "fine",
		Born:   100400,
	}

	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	expectedCmd := []string{"scp -o StrictHostKeyChecking=no -i /etc/bar -l 100500 ./tmpdir/file1.meta vasya@my.host.ru:/var/foo/qwert"}

	t.Run("with error", func(t *testing.T) {
		cr := &testCmdRunner{
			err: errors.New("kek"),
		}
		err := sendMeta(cfg, tmpDir+"/file1", "qwert", meta, cr)
		require.Error(t, err)
		require.Equal(t, "kek", err.Error())
		require.Equal(t, expectedCmd, cr.commands)
		_, err = os.Stat(tmpDir + "/file1" + prospectortypes.MetaFileSuffix)
		require.NoError(t, err)
		require.NoError(t, os.Remove(tmpDir+"/file1"+prospectortypes.MetaFileSuffix))
	})

	t.Run("ok", func(t *testing.T) {
		cr := &testCmdRunner{}
		err := sendMeta(cfg, tmpDir+"/file1", "qwert", meta, cr)
		require.NoError(t, err)
		require.Equal(t, expectedCmd, cr.commands)
		_, err = os.Stat(tmpDir + "/file1" + prospectortypes.MetaFileSuffix)
		require.NoError(t, err)
		require.NoError(t, os.Remove(tmpDir+"/file1"+prospectortypes.MetaFileSuffix))
	})
}

func TestTrySendError(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	cfg := &Config{
		Ammo: cfgAmmo{
			Dir: tmpDir,
		},
		Scp: cfgScp{
			RemoteUser:     "vasya",
			Host:           "my.host.ru",
			PrivateKeyPath: "/etc/bar",
			RemoteDir:      "/var/foo",
			BandwidthKbits: 100500,
		},
	}

	rErr := errors.New("foo")

	expectedCmd := []string{"scp -o StrictHostKeyChecking=no -i /etc/bar -l 100500 ./tmpdir/my.host.ru.meta vasya@my.host.ru:/var/foo/qwert"}

	t.Run("with error", func(t *testing.T) {
		cr := &testCmdRunner{
			err: errors.New("kek"),
		}
		err := trySendError(cfg, "my.host.ru", rErr, "qwert", cr)
		require.Error(t, err)
		require.Equal(t, "kek", err.Error())
		require.Equal(t, expectedCmd, cr.commands)
		_, err = os.Stat(tmpDir + "/my.host.ru" + prospectortypes.MetaFileSuffix)
		require.NoError(t, err)
	})

	t.Run("ok", func(t *testing.T) {
		cr := &testCmdRunner{}
		err := trySendError(cfg, "my.host.ru", rErr, "qwert", cr)
		require.NoError(t, err)
		require.Equal(t, expectedCmd, cr.commands)
		_, err = os.Stat(tmpDir + "/my.host.ru" + prospectortypes.MetaFileSuffix)
		require.NoError(t, err)
	})
}

func TestRunTask(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	cfg := &Config{
		Ammo: cfgAmmo{
			Dir:           tmpDir,
			LocalUser:     "vasya",
			ListenPort:    1050,
			GorPath:       "/usr/bin/goooo",
			FileSizeLimit: 110923120932,
		},
		Scp: cfgScp{
			RemoteUser:     "vasya",
			Host:           "my.host.ru",
			PrivateKeyPath: "/etc/bar",
			RemoteDir:      "/var/foo",
			BandwidthKbits: 100500,
		},
	}

	task := &prospectortypes.Task{
		ID:       "qwer",
		Duration: 100500,
	}

	t.Run("common", func(t *testing.T) {
		cr := &testCmdRunner{}
		err := runTask(cfg, "my.host.ru", task, cr)
		require.NoError(t, err)

		expectedCmd := []string{
			"sudo /usr/bin/goooo --input-raw :1050 --output-file ./tmpdir/my.host.ru --exit-after 100500s --output-file-append --output-file-flush-interval 10s --output-file-max-size-limit 110923120932",
			"sudo chown vasya ./tmpdir/my.host.ru",
			"gzip ./tmpdir/my.host.ru",
			"scp -o StrictHostKeyChecking=no -i /etc/bar -l 100500 ./tmpdir/my.host.ru.gz vasya@my.host.ru:/var/foo/qwer",
			"scp -o StrictHostKeyChecking=no -i /etc/bar -l 100500 ./tmpdir/my.host.ru.meta vasya@my.host.ru:/var/foo/qwer",
		}
		require.Equal(t, expectedCmd, cr.commands)

		_, err = os.Stat(tmpDir + "/my.host.ru" + prospectortypes.MetaFileSuffix)
		require.NoError(t, err)
	})
}
