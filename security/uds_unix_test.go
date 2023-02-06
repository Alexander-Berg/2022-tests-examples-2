//go:build !windows
// +build !windows

package netutil_test

import (
	"context"
	"net"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/libs/netutil"
)

func TestUnixSocketCreds(t *testing.T) {
	cases := []struct {
		name   string
		listen func() (net.Listener, error)
		creds  netutil.UnixCreds
	}{
		{
			name: "uds",
			listen: func() (net.Listener, error) {
				return net.Listen("unix", "@netutil-creds-test")
			},
			creds: netutil.UnixCreds{
				PID: os.Getpid(),
				UID: os.Getuid(),
			},
		},
		{
			name: "tcp",
			listen: func() (net.Listener, error) {
				return net.Listen("tcp", ":0")
			},
			creds: netutil.UnixCreds{
				PID: -1,
				UID: -1,
			},
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			l, err := tc.listen()
			require.NoError(t, err)
			defer func() { _ = l.Close() }()

			ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
			defer cancel()

			go func(ctx context.Context) {
				conn, err := l.Accept()
				if err != nil {
					return
				}

				<-ctx.Done()
				_ = conn.Close()
			}(ctx)

			var network string
			switch l.(type) {
			case *net.UnixListener:
				network = "unix"
			case *net.TCPListener:
				network = "tcp"
			default:
				t.Fatalf("unsupported listener: %T", l)
			}

			var d net.Dialer
			conn, err := d.DialContext(ctx, network, l.Addr().String())
			require.NoError(t, err)

			creds, err := netutil.UnixSocketCreds(conn)
			require.NoError(t, err)
			require.Equal(t, tc.creds, creds)
		})
	}
}
