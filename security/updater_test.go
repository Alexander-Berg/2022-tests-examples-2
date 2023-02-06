package updater

import (
	"context"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"
	"google.golang.org/grpc"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/libs/go/sectools"
	"a.yandex-team.ru/security/libs/go/sectools/mocktools"
	"a.yandex-team.ru/security/skotty/launcher/tools/fake-skotty/runinfo"
	"a.yandex-team.ru/security/skotty/skotty/pkg/skottyctl/skottyrpc"
)

var home string

func TestMain(m *testing.M) {
	var err error
	home, err = os.MkdirTemp("", "updater-test-*")
	if err != nil {
		panic(fmt.Sprintf("create temporary home: %v", err))
	}

	oldHome := os.Getenv("HOME")
	err = os.Setenv("HOME", home)
	if err != nil {
		panic(fmt.Sprintf("update home: %v", err))
	}

	err = os.MkdirAll(filepath.Join(home, ".skotty", "releases"), 0o700)
	if err != nil {
		panic(fmt.Sprintf("create releases dir: %v", err))
	}

	exitVal := m.Run()
	_ = os.Setenv("HOME", oldHome)
	os.Exit(exitVal)
}

func TestReleasesPath(t *testing.T) {
	relPath, err := ReleasesPath()
	require.NoError(t, err)
	require.Equal(t, filepath.Join(home, ".skotty", "releases"), relPath)
}

func TestInReleasesPath(t *testing.T) {
	cases := [][]string{
		{},
		{"lol"},
		{"lol", "kek", "cheburek"},
	}
	for _, tc := range cases {
		t.Run(strings.Join(tc, "_"), func(t *testing.T) {
			actual, err := InReleasesPath(tc...)
			require.NoError(t, err)
			expected := filepath.Join(append([]string{home, ".skotty", "releases"}, tc...)...)
			require.Equal(t, expected, actual)
		})
	}
}

func TestReadReleaseInfo(t *testing.T) {
	infoPath, err := InReleasesPath("current.json")
	require.NoError(t, err)
	defer func() { _ = os.RemoveAll(infoPath) }()

	writeReleaseInfo := func(t *testing.T, ri ReleaseInfo) {
		releaseBytes, err := json.Marshal(ri)
		require.NoError(t, err)

		err = os.WriteFile(infoPath, releaseBytes, 0o644)
		require.NoError(t, err)
	}

	cases := []struct {
		name      string
		expected  ReleaseInfo
		err       bool
		bootstrap func(t *testing.T)
	}{
		{
			name: "missing",
			err:  true,
			expected: ReleaseInfo{
				Version: DefaultVersion,
				Channel: DefaultChannel,
			},
			bootstrap: func(t *testing.T) {
				_ = os.RemoveAll(infoPath)
			},
		},
		{
			name: "empty",
			err:  true,
			expected: ReleaseInfo{
				Version: DefaultVersion,
				Channel: DefaultChannel,
			},
			bootstrap: func(t *testing.T) {
				f, err := os.Create(infoPath)
				require.NoError(t, err)
				_ = f.Close()
			},
		},
		{
			name: "empty1",
			err:  true,
			expected: ReleaseInfo{
				Version: DefaultVersion,
				Channel: DefaultChannel,
			},
			bootstrap: func(t *testing.T) {
				err := os.WriteFile(infoPath, []byte{'{', '}'}, 0o644)
				require.NoError(t, err)
			},
		},
		{
			name: "empty2",
			err:  true,
			expected: ReleaseInfo{
				Version: DefaultVersion,
				Channel: DefaultChannel,
			},
			bootstrap: func(t *testing.T) {
				err := os.WriteFile(infoPath, []byte(`{"Version":""}`), 0o644)
				require.NoError(t, err)
			},
		},
		{
			name: "invalid",
			err:  true,
			expected: ReleaseInfo{
				Version: DefaultVersion,
				Channel: DefaultChannel,
			},
			bootstrap: func(t *testing.T) {
				err := os.WriteFile(infoPath, []byte{'{'}, 0o644)
				require.NoError(t, err)
			},
		},
		{
			name: "normal",
			expected: ReleaseInfo{
				Version: "1.2.3",
				Channel: sectools.ChannelStable,
			},
			bootstrap: func(t *testing.T) {
				writeReleaseInfo(t, ReleaseInfo{
					Version: "1.2.3",
					Channel: sectools.ChannelStable,
				})
			},
		},
		{
			name: "no_channel",
			expected: ReleaseInfo{
				Version: "1.2.4",
				Channel: sectools.ChannelStable,
			},
			bootstrap: func(t *testing.T) {
				writeReleaseInfo(t, ReleaseInfo{
					Version: "1.2.4",
				})
			},
		},
		{
			name: "prestable",
			expected: ReleaseInfo{
				Version: "1.2.4",
				Channel: sectools.ChannelPrestable,
			},
			bootstrap: func(t *testing.T) {
				writeReleaseInfo(t, ReleaseInfo{
					Version: "1.2.4",
					Channel: sectools.ChannelPrestable,
				})
			},
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			tc.bootstrap(t)
			actual, err := ReadReleaseInfo()
			if tc.err {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}

			require.Equal(t, tc.expected, actual)
		})
	}
}

func TestWriteChannel(t *testing.T) {
	infoPath, err := InReleasesPath("current.json")
	require.NoError(t, err)
	defer func() { _ = os.RemoveAll(infoPath) }()

	err = os.WriteFile(infoPath, []byte(`{"version":"1.1.1"}`), 0o644)
	require.NoError(t, err)

	for _, tc := range []sectools.Channel{sectools.ChannelStable, sectools.ChannelTesting, sectools.ChannelPrestable} {
		t.Run(fmt.Sprint(tc), func(t *testing.T) {
			err := WriteChannel(tc)
			require.NoError(t, err)

			ri, err := ReadReleaseInfo()
			require.NoError(t, err)

			require.Equal(t, ri.Channel, tc)
		})
	}
}

func TestWriteReleaseInfo(t *testing.T) {
	infoPath, err := InReleasesPath("current.json")
	require.NoError(t, err)
	defer func() { _ = os.RemoveAll(infoPath) }()

	cases := []struct {
		ri  ReleaseInfo
		err bool
	}{
		{
			err: true,
		},
		{
			ri: ReleaseInfo{
				Version: "1.1.1",
				Channel: sectools.ChannelStable,
			},
		},
		{
			ri: ReleaseInfo{
				Version: "1.1.3",
				Channel: sectools.ChannelPrestable,
			},
		},
		{
			ri: ReleaseInfo{
				Version: "1.1.4",
				Channel: sectools.ChannelTesting,
			},
		},
	}

	for _, tc := range cases {
		t.Run(fmt.Sprint(tc.ri), func(t *testing.T) {
			expected := tc.ri
			err := writeReleaseInfo(expected)
			if tc.err {
				require.Error(t, err)
				expected = ReleaseInfo{
					Version: DefaultVersion,
					Channel: DefaultChannel,
				}
			} else {
				require.NoError(t, err)
			}

			actual, err := ReadReleaseInfo()
			if tc.err {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
			}

			require.Equal(t, actual, expected)
		})
	}
}

func TestUpdate(t *testing.T) {
	skottyPath, err := yatest.BinaryPath("security/skotty/launcher/tools/fake-skotty/fake-skotty")
	require.NoError(t, err)

	srv, err := mocktools.NewSrv(
		mocktools.WithTool("skotty", "stable", "1.0.0", skottyPath),
		mocktools.WithTool("skotty", "prestable", "1.1.0", skottyPath),
		mocktools.WithTool("skotty", "testing", "1.2.0", skottyPath),
	)
	require.NoError(t, err)

	sectoolsOpts = []sectools.Option{
		sectools.WithUpstream(srv.URL),
	}

	skottyCtl := newFakeSupervisor(filepath.Join(home, ".skotty", "ctl.sock"))
	go func() {
		_ = skottyCtl.ListenAndServe()
	}()
	defer skottyCtl.Shutdown()

	tmpF, err := os.CreateTemp("", "")
	require.NoError(t, err)
	_ = tmpF.Close()
	outPath := tmpF.Name()

	err = os.Setenv("FAKE_SKOTTY_OUTPUT", outPath)
	require.NoError(t, err)
	defer func() { _ = os.Unsetenv("FAKE_SKOTTY_OUTPUT") }()

	releasePath, err := ReleasesPath()
	require.NoError(t, err)
	_ = os.RemoveAll(releasePath)

	collectReleases := func(t *testing.T) []string {
		entries, err := os.ReadDir(releasePath)
		require.NoError(t, err)

		var out []string
		for _, de := range entries {
			if !de.IsDir() {
				continue
			}

			out = append(out, de.Name())
		}
		return out
	}

	checkReleaseInfo := func(t *testing.T, ri ReleaseInfo) {
		actual, err := ReadReleaseInfo()
		require.NoError(t, err)

		require.Equal(t, ri, actual)
	}

	_ = os.MkdirAll(filepath.Join(releasePath, "0.0.1"), 0o755)
	require.ElementsMatch(t, []string{"0.0.1"}, collectReleases(t))

	curVersion, err := Update()
	require.NoError(t, err)
	require.Equal(t, "1.0.0", curVersion)
	require.ElementsMatch(t, []string{"1.0.0", "0.0.1"}, collectReleases(t))
	checkNotifyInstallOut(t, outPath)
	checkReleaseInfo(t, ReleaseInfo{
		Version: "1.0.0",
		Channel: sectools.ChannelStable,
	})
	err = os.RemoveAll(outPath)
	require.NoError(t, err)

	curVersion, err = Update()
	require.ErrorIs(t, err, ErrNoUpdates)
	require.Equal(t, "1.0.0", curVersion)
	require.ElementsMatch(t, []string{"1.0.0", "0.0.1"}, collectReleases(t))
	checkReleaseInfo(t, ReleaseInfo{
		Version: "1.0.0",
		Channel: sectools.ChannelStable,
	})

	err = WriteChannel(sectools.ChannelPrestable)
	require.NoError(t, err)
	checkReleaseInfo(t, ReleaseInfo{
		Version: "1.0.0",
		Channel: sectools.ChannelPrestable,
	})

	curVersion, err = Update()
	require.NoError(t, err)
	require.Equal(t, "1.1.0", curVersion)
	require.ElementsMatch(t, []string{"1.1.0", "1.0.0", "0.0.1"}, collectReleases(t))
	checkNotifyInstallOut(t, outPath)
	checkReleaseInfo(t, ReleaseInfo{
		Version: "1.1.0",
		Channel: sectools.ChannelPrestable,
	})

	curVersion, err = Update()
	require.ErrorIs(t, err, ErrNoUpdates)
	require.Equal(t, "1.1.0", curVersion)
	require.ElementsMatch(t, []string{"1.1.0", "1.0.0", "0.0.1"}, collectReleases(t))
	checkReleaseInfo(t, ReleaseInfo{
		Version: "1.1.0",
		Channel: sectools.ChannelPrestable,
	})

	err = WriteChannel(sectools.ChannelTesting)
	require.NoError(t, err)
	checkReleaseInfo(t, ReleaseInfo{
		Version: "1.1.0",
		Channel: sectools.ChannelTesting,
	})

	curVersion, err = Update()
	require.NoError(t, err)
	require.Equal(t, "1.2.0", curVersion)
	require.ElementsMatch(t, []string{"1.2.0", "1.1.0", "0.0.1"}, collectReleases(t))
	checkNotifyInstallOut(t, outPath)
	checkReleaseInfo(t, ReleaseInfo{
		Version: "1.2.0",
		Channel: sectools.ChannelTesting,
	})

	err = writeReleaseInfo(ReleaseInfo{
		Version: "0.0.9",
		Channel: "kek",
	})
	require.NoError(t, err)
	curVersion, err = Update()
	require.Error(t, err)
	require.Equal(t, "", curVersion)
	require.ElementsMatch(t, []string{"1.2.0", "1.1.0", "0.0.1"}, collectReleases(t))
	checkReleaseInfo(t, ReleaseInfo{
		Version: "0.0.9",
		Channel: "kek",
	})
}

func TestDownloadVersion(t *testing.T) {
	skottyPath, err := yatest.BinaryPath("security/skotty/launcher/tools/fake-skotty/fake-skotty")
	require.NoError(t, err)

	srv, err := mocktools.NewSrv(
		mocktools.WithTool("skotty", "stable", "1.0.0", skottyPath),
	)
	require.NoError(t, err)

	sectoolsOpts = []sectools.Option{
		sectools.WithUpstream(srv.URL),
	}

	tmpF, err := os.CreateTemp("", "")
	require.NoError(t, err)
	_ = tmpF.Close()
	outPath := tmpF.Name()

	err = os.Setenv("FAKE_SKOTTY_OUTPUT", outPath)
	require.NoError(t, err)
	defer func() { _ = os.Unsetenv("FAKE_SKOTTY_OUTPUT") }()

	for i, ver := range []string{"stable", "1.0.0", "0.0.1"} {
		t.Run(ver, func(t *testing.T) {
			downloadedPath, err := DownloadVersion(ver)
			if i == 2 {
				require.Error(t, err)
				require.Empty(t, downloadedPath)

				_, err := os.Stat(filepath.Join(home, ".skotty", "releases", ver))
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, filepath.Join(home, ".skotty", "releases", ver, BinaryName), downloadedPath)

			checkNotifyInstallOut(t, outPath)
		})
	}
}

func checkNotifyInstallOut(t *testing.T, outPath string) {
	runInfoBytes, err := os.ReadFile(outPath)
	require.NoError(t, err)

	var runInfo runinfo.RunInfo
	err = json.Unmarshal(runInfoBytes, &runInfo)
	require.NoError(t, err)

	require.Equal(t,
		runinfo.RunInfo{
			Args: []string{"notify", "install"},
			Env: map[string]string{
				"UNDER_LAUNCHER": "yes",
			},
		},
		runInfo,
	)
}

type fakeSupervisor struct {
	skottyrpc.SupervisorServer
	addr string
	grpc *grpc.Server
}

func newFakeSupervisor(addr string) *fakeSupervisor {
	return &fakeSupervisor{
		addr: addr,
		grpc: grpc.NewServer(),
	}
}

func (s *fakeSupervisor) ListenAndServe() error {
	_ = os.Remove(s.addr)

	listener, err := net.Listen("unix", s.addr)
	if err != nil {
		return fmt.Errorf("listen fail: %w", err)
	}

	defer func() {
		_ = listener.Close()
	}()

	skottyrpc.RegisterSupervisorServer(s.grpc, s)

	return s.grpc.Serve(listener)
}

func (s *fakeSupervisor) Shutdown() {
	s.grpc.GracefulStop()
}

func (s *fakeSupervisor) Status(_ context.Context, _ *skottyrpc.StatusRequest) (*skottyrpc.StatusReply, error) {
	return &skottyrpc.StatusReply{
		Pid:     int32(os.Getpid()),
		Version: "0.0.1",
	}, nil
}
