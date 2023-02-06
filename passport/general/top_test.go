package top

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/require"
)

type testHTTPGetter struct {
	code     int
	response []byte
	err      error

	requests []string
	bodies   []string
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
		t.bodies = make([]string, 0)
	}
	t.requests = append(t.requests, path)
	t.bodies = append(t.bodies, string(body))
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
	t.Run("cmd failed", func(t *testing.T) {
		hc := &testHTTPGetter{}
		cmd := &testCmdRunner{
			err: errors.New("kek"),
		}
		tvm := &testTvm{}

		err := pushTop(hc, cmd, tvm, 100500)
		require.Error(t, err)
		require.Equal(t, "failed to run top: kek: ", err.Error())
		require.Equal(t, []string{"top -b -n2 -w 512 -c"}, cmd.commands)
	})

	t.Run("tvm failed", func(t *testing.T) {
		hc := &testHTTPGetter{}
		cmd := &testCmdRunner{
			out: []byte("kek"),
		}
		tvm := &testTvm{
			err: errors.New("lol"),
		}

		err := pushTop(hc, cmd, tvm, 100500)
		require.Error(t, err)
		require.Equal(t, "failed to get service ticket: lol", err.Error())
		require.Equal(t, []string{"top -b -n2 -w 512 -c"}, cmd.commands)
	})

	t.Run("http failed", func(t *testing.T) {
		hc := &testHTTPGetter{
			err: errors.New("lol"),
		}
		cmd := &testCmdRunner{
			out: []byte("kek"),
		}
		tvm := &testTvm{
			ticket: "serviceticket",
		}

		err := pushTop(hc, cmd, tvm, 100500)
		require.Error(t, err)
		require.Equal(t, "failed to push top: 0: : lol", err.Error())
		require.Equal(t, []string{"top -b -n2 -w 512 -c"}, cmd.commands)
		require.Equal(t, []string{"/stateviewer/top?timestamp=100500"}, hc.requests)
		require.Equal(t, []string{"BCJNGGRwuQMAAIBrZWsAAAAA9nNQvw"}, hc.bodies)
	})

	t.Run("ok", func(t *testing.T) {
		hc := &testHTTPGetter{
			code:     200,
			response: []byte("mega response"),
		}
		cmd := &testCmdRunner{
			out: []byte("kek"),
		}
		tvm := &testTvm{
			ticket: "serviceticket",
		}

		err := pushTop(hc, cmd, tvm, 100500)
		require.NoError(t, err)
		require.Equal(t, []string{"top -b -n2 -w 512 -c"}, cmd.commands)
		require.Equal(t, []string{"/stateviewer/top?timestamp=100500"}, hc.requests)
		require.Equal(t, []string{"BCJNGGRwuQMAAIBrZWsAAAAA9nNQvw"}, hc.bodies)
	})
}
