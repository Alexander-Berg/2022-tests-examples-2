package pipeproxy_test

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/gofrs/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/skotty/wsl2proxy/internal/pipeproxy"
)

func startServer(t *testing.T) (sockPath string, close func()) {
	sockUUID, err := uuid.NewV4()
	require.NoError(t, err)

	sockPath = filepath.Join(os.TempDir(), fmt.Sprintf("pipesrv-%s.sock", sockUUID))
	l, err := net.Listen("unix", sockPath)
	require.NoError(t, err)

	processConn := func(c net.Conn) {
		defer func() { _ = c.Close() }()

		buf := make([]byte, 3)
		if _, err := c.Read(buf); err != nil {
			t.Logf("unable to read from conn: %v\n", err)
			return
		}

		if _, err := c.Write(buf); err != nil {
			t.Logf("unable to write to conn: %v\n", err)
			return
		}
	}

	go func() {
		for {
			conn, err := l.Accept()
			if err != nil {
				if errors.Is(err, net.ErrClosed) {
					return
				}
				t.Logf("unable to accept connect: %v\n", err)
				continue
			}

			processConn(conn)
		}
	}()

	return fmt.Sprintf("unix:%s", sockPath), func() {
		_ = os.Remove(sockPath)
		assert.NoError(t, l.Close())
	}
}

func TestPipeProxy(t *testing.T) {
	binaryPath, err := yatest.BinaryPath("security/skotty/wsl2proxy/cmd/wsl2proxy/wsl2proxy")
	require.NoError(t, err)

	proxy := pipeproxy.NewPipeProxy(binaryPath, "forward")
	srvPath, srvClose := startServer(t)
	defer srvClose()

	sess, err := proxy.Start(context.Background(), srvPath)
	require.NoError(t, err)
	defer func() {
		assert.NoError(t, sess.Close())
	}()

	stream, err := sess.OpenStream()
	require.NoError(t, err)
	defer func() {
		assert.NoError(t, stream.Close())
	}()

	buf := []byte{'k', 'e', 'k'}
	n, err := stream.Write(buf)
	require.NoError(t, err)
	require.Equal(t, 3, n)

	n, err = stream.Read(buf)
	require.NoError(t, err)
	require.Equal(t, 3, n)
	require.Equal(t, []byte{'k', 'e', 'k'}, buf)
}

func TestPipeProxy_invalid(t *testing.T) {
	binaryPath, err := yatest.BinaryPath("security/skotty/wsl2proxy/cmd/wsl2proxy/wsl2proxy")
	require.NoError(t, err)

	cases := []struct {
		name string
		path string
	}{
		{
			name: "invalid_schema",
			path: "kek",
		},
		{
			name: "no_socket",
			path: "unix:/kek.sock",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			proxy := pipeproxy.NewPipeProxy(binaryPath, "forward")
			sess, err := proxy.Start(context.Background(), tc.path)
			require.NoError(t, err)
			defer func() {
				assert.NoError(t, sess.Close())
			}()

			stream, err := sess.OpenStream()
			require.NoError(t, err)
			defer func() {
				assert.NoError(t, stream.Close())
			}()

			buf := []byte{'k', 'e', 'k'}
			n, err := stream.Write(buf)
			require.NoError(t, err)
			require.Equal(t, 3, n)

			n, err = stream.Read(buf)
			require.ErrorIs(t, err, io.EOF)
			require.Equal(t, 0, n)
		})
	}
}

func TestPipeProxy_cancelProxy(t *testing.T) {
	binaryPath, err := yatest.BinaryPath("security/skotty/wsl2proxy/cmd/wsl2proxy/wsl2proxy")
	require.NoError(t, err)

	proxy := pipeproxy.NewPipeProxy(binaryPath, "forward")
	srvPath, srvClose := startServer(t)
	defer srvClose()

	ctx, cancel := context.WithCancel(context.Background())
	sess, err := proxy.Start(ctx, srvPath)
	require.NoError(t, err)
	defer func() {
		assert.NoError(t, sess.Close())
	}()

	cancel()
	//TODO(buglloc): do smth better please
	time.Sleep(1 * time.Second)

	stream, err := sess.OpenStream()
	require.Error(t, err)
	require.Nil(t, stream)
	require.False(t, sess.IsAlive())
}

func TestPipeProxy_cancelSess(t *testing.T) {
	binaryPath, err := yatest.BinaryPath("security/skotty/wsl2proxy/cmd/wsl2proxy/wsl2proxy")
	require.NoError(t, err)

	proxy := pipeproxy.NewPipeProxy(binaryPath, "forward")
	srvPath, srvClose := startServer(t)
	defer srvClose()

	ctx, cancel := context.WithCancel(context.Background())
	sess, err := proxy.Start(ctx, srvPath)
	require.NoError(t, err)
	defer func() {
		assert.NoError(t, sess.Close())
	}()

	stream, err := sess.OpenStream()
	require.NoError(t, err)
	defer func() {
		assert.NoError(t, stream.Close())
	}()

	cancel()
	//TODO(buglloc): do smth better please
	time.Sleep(1 * time.Second)

	buf := []byte{'k', 'e', 'k'}
	_, err = stream.Write(buf)
	require.Error(t, err)

	_, err = stream.Read(buf)
	require.Error(t, err)

	require.False(t, sess.IsAlive())
}
