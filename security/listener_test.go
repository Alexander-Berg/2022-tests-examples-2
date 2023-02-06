package listener_test

import (
	"context"
	"errors"
	"fmt"
	"io/fs"
	"net"
	"os"
	"path/filepath"
	"sync"
	"testing"

	"github.com/gofrs/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/skotty/wsl2proxy/internal/listener"
)

func startTargetServer(t *testing.T) (sockPath string, close func()) {
	sockUUID, err := uuid.NewV4()
	require.NoError(t, err)

	sockPath = filepath.Join(os.TempDir(), fmt.Sprintf("lisTarget-%s.sock", sockUUID))
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

func startListenerServer(t *testing.T, spec listener.Spec) func() {
	binaryPath, err := yatest.BinaryPath("security/skotty/wsl2proxy/cmd/wsl2proxy/wsl2proxy")
	require.NoError(t, err)

	var wg sync.WaitGroup
	wg.Add(1)

	l, err := listener.NewListener(
		listener.WithProxyBinary(binaryPath, "forward"),
		listener.WithOnListen(func(_ listener.Spec) {
			wg.Done()
		}),
	)
	require.NoError(t, err)

	go func() {
		err = l.ListenAndServe(context.Background(), spec)
		assert.NoError(t, err)
	}()

	wg.Wait()
	return l.Close
}

func TestLala(t *testing.T) {
	srvPath, srvClose := startTargetServer(t)
	defer srvClose()

	sockUUID, err := uuid.NewV4()
	require.NoError(t, err)

	sockPath := filepath.Join(os.TempDir(), fmt.Sprintf("listen-%s.sock", sockUUID))
	spec := listener.Spec{
		Pairs: []listener.ListenPair{
			{
				Name: "tst",
				Src:  sockPath,
				Dst:  srvPath,
			},
		},
	}
	listenerClose := startListenerServer(t, spec)
	defer listenerClose()

	conn, err := net.Dial("unix", sockPath)
	require.NoError(t, err)

	buf := []byte{'k', 'e', 'k'}
	n, err := conn.Write(buf)
	require.NoError(t, err)
	require.Equal(t, 3, n)

	n, err = conn.Read(buf)
	require.NoError(t, err)
	require.Equal(t, 3, n)
	require.Equal(t, []byte{'k', 'e', 'k'}, buf)

	require.NoError(t, conn.Close())

	stat, err := os.Stat(sockPath)
	require.NoError(t, err)
	require.True(t, stat.Mode()&fs.ModeSocket != 0, "not a socket")
	listenerClose()

	_, err = os.Stat(sockPath)
	require.Error(t, err)
}
