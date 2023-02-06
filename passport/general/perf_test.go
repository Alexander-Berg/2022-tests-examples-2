package perf

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/stateviewertypes"
)

type testHTTPGetter struct {
	code     int
	response []byte
	err      error

	requests []string
	bodies   [][]byte
}

func (t *testHTTPGetter) Get(path string, headers map[string]string) (int, []byte, error) {
	if t.requests == nil {
		t.requests = make([]string, 0)
	}
	t.requests = append(t.requests, path)
	return t.code, t.response, t.err
}

func (t *testHTTPGetter) Post(path string, body []byte, headers map[string]string) (int, []byte, error) {
	if t.requests == nil {
		t.requests = make([]string, 0)
		t.bodies = make([][]byte, 0)
	}
	t.requests = append(t.requests, path)
	t.bodies = append(t.bodies, body)
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

type testTvm struct {
	ticket string
	err    error

	aliases []string
}

func (t *testTvm) GetServiceTicket(alias string) (string, error) {
	if t.aliases == nil {
		t.aliases = make([]string, 0)
	}
	t.aliases = append(t.aliases, alias)

	return t.ticket, t.err
}

func TestPush(t *testing.T) {
	cfg := Config{
		Dir:     "/some/dir",
		PidFile: "/some/exe",
	}

	t.Run("tvm failed", func(t *testing.T) {
		hc := &testHTTPGetter{}
		cmd := &testCmdRunner{}
		tvm := &testTvm{
			err: errors.New("kek"),
		}

		err := run(cfg, hc, cmd, tvm, 100500)
		require.Error(t, err)
		require.Equal(t, "failed to get service ticket: kek", err.Error())
		require.Nil(t, hc.requests)
		require.Nil(t, cmd.commands)
	})

	t.Run("get failed", func(t *testing.T) {
		hc := &testHTTPGetter{
			err: errors.New("kek")}
		cmd := &testCmdRunner{}
		tvm := &testTvm{
			ticket: "serviceticket",
		}

		err := run(cfg, hc, cmd, tvm, 100500)
		require.Error(t, err)
		require.Equal(t, "failed to get task: 0: : kek", err.Error())
		require.Equal(t, []string{"/stateviewer/perf"}, hc.requests)
		require.Nil(t, cmd.commands)
	})

	t.Run("parse failed", func(t *testing.T) {
		hc := &testHTTPGetter{
			code:     200,
			response: []byte("{"),
		}
		cmd := &testCmdRunner{}
		tvm := &testTvm{
			ticket: "serviceticket",
		}

		err := run(cfg, hc, cmd, tvm, 100500)
		require.Error(t, err)
		require.Equal(t, "failed to parse task: 200: {: unexpected end of JSON input", err.Error())
		require.Equal(t, []string{"/stateviewer/perf"}, hc.requests)
		require.Nil(t, cmd.commands)
	})

	t.Run("no task", func(t *testing.T) {
		hc := &testHTTPGetter{
			code:     200,
			response: []byte(`{"need_create":false}`),
		}
		cmd := &testCmdRunner{}
		tvm := &testTvm{
			ticket: "serviceticket",
		}

		err := run(cfg, hc, cmd, tvm, 100500)
		require.NoError(t, err)
		require.Equal(t, []string{"/stateviewer/perf"}, hc.requests)
		require.Nil(t, cmd.commands)
	})

	t.Run("no task", func(t *testing.T) {
		hc := &testHTTPGetter{
			code:     200,
			response: []byte(`{"need_create":false}`),
		}
		cmd := &testCmdRunner{}
		tvm := &testTvm{
			ticket: "serviceticket",
		}

		err := run(cfg, hc, cmd, tvm, 100500)
		require.NoError(t, err)
		require.Equal(t, []string{"/stateviewer/perf"}, hc.requests)
		require.Nil(t, cmd.commands)
	})

	t.Run("task succeed", func(t *testing.T) {
		hc := &testHTTPGetter{
			code:     200,
			response: []byte(`{"need_create":true}`),
		}
		cmd := &testCmdRunner{
			out: []byte("qwerty"),
		}
		tvm := &testTvm{
			ticket: "serviceticket",
		}

		err := run(cfg, hc, cmd, tvm, 100500)
		require.NoError(t, err)
		require.Equal(t, []string{"/stateviewer/perf", "/stateviewer/perf?timestamp=100500"}, hc.requests)
		require.Equal(t,
			[]string{
				"sudo perf record -o /some/dir/some.perf.data -p $(cat /some/exe) -F 0 -a -g -- sleep 0",
				"sudo perf script -i /some/dir/some.perf.data",
			},
			cmd.commands)
	})
}

func TestPerformTask(t *testing.T) {
	cfg := Config{
		Dir:     "/some/dir",
		PidFile: "/some/exe",
	}

	t.Run("perf failed", func(t *testing.T) {
		hc := &testHTTPGetter{
			code:     200,
			response: []byte(`{"need_create":true}`),
		}
		cmd := &testCmdRunner{
			err: errors.New("kek"),
		}
		task := &stateviewertypes.PerfCmd{
			Frequency: 999,
			Sleep:     1000,
		}

		err := performTask(cfg, hc, cmd, 100500, task, nil)
		require.Error(t, err)
		require.Equal(t, []string{"sudo perf record -o /some/dir/some.perf.data -p $(cat /some/exe) -F 999 -a -g -- sleep 1000"}, cmd.commands)
		require.Nil(t, hc.requests)
	})

	t.Run("post failed", func(t *testing.T) {
		hc := &testHTTPGetter{
			code:     300,
			response: []byte(`lol`),
		}
		cmd := &testCmdRunner{}
		task := &stateviewertypes.PerfCmd{
			Frequency: 999,
			Sleep:     1000,
		}

		err := performTask(cfg, hc, cmd, 100500, task, nil)
		require.Error(t, err)
		require.Equal(t,
			[]string{
				"sudo perf record -o /some/dir/some.perf.data -p $(cat /some/exe) -F 999 -a -g -- sleep 1000",
				"sudo perf script -i /some/dir/some.perf.data",
			},
			cmd.commands)
		require.Equal(t, []string{"/stateviewer/perf?timestamp=100500"}, hc.requests)
	})
}
