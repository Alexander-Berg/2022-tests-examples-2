package sectools_test

import (
	"bytes"
	"context"
	"fmt"
	"runtime"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/sectools"
	"a.yandex-team.ru/security/libs/go/sectools/mocktools"
)

func TestClient(t *testing.T) {
	srv, err := mocktools.NewSrv(
		mocktools.WithTool("kek", "stable", "1.0.0", "./testdata/kek.txt"),
		mocktools.WithTool("kek", "0.0.9", "0.0.9", "./testdata/kek.txt"),
	)
	require.NoError(t, err)

	type version struct {
		versionErr  bool
		version     string
		isLatest    bool
		contentErr  bool
		contentHash string
		content     []byte
	}

	cases := []struct {
		name     string
		toolName string
		channel  sectools.Channel
		os       string
		arch     string
		versions []version
	}{
		{
			name:     "valid",
			toolName: "kek",
			channel:  sectools.ChannelStable,
			os:       runtime.GOOS,
			arch:     runtime.GOARCH,
			versions: []version{
				{
					version:    "0.0.8",
					versionErr: false,
					contentErr: true,
				},
				{
					version:     "0.0.9",
					versionErr:  false,
					content:     []byte("kek\n"),
					contentHash: "b2s:39cd1fad07b342f54a45c61def043775b29fc5d52a129b151d7d503b9f67b224",
				},
				{
					version:     "1.0.0",
					isLatest:    true,
					content:     []byte("kek\n"),
					contentHash: "b2s:39cd1fad07b342f54a45c61def043775b29fc5d52a129b151d7d503b9f67b224",
				},
			},
		},
		{
			name:     "invalid-channel",
			toolName: "kek",
			channel:  sectools.ChannelPrestable,
			os:       runtime.GOOS,
			arch:     runtime.GOARCH,
			versions: []version{
				{
					version:    "0.0.9",
					versionErr: true,
				},
				{
					version:    "1.0.0",
					versionErr: true,
				},
			},
		},
		{
			name:     "invalid-tool-name",
			toolName: "not-kek",
			channel:  sectools.ChannelStable,
			os:       runtime.GOOS,
			arch:     runtime.GOARCH,
			versions: []version{
				{
					version:    "0.0.9",
					versionErr: true,
				},
				{
					version:    "1.0.0",
					versionErr: true,
				},
			},
		},
		{
			name:     "invalid-os",
			toolName: "kek",
			channel:  sectools.ChannelStable,
			os:       "kek",
			arch:     runtime.GOARCH,
			versions: []version{
				{
					version:    "0.0.8",
					contentErr: true,
				},
				{
					version:    "0.0.9",
					contentErr: true,
				},
				{
					version:    "1.0.0",
					isLatest:   true,
					contentErr: true,
				},
			},
		},
		{
			name:     "invalid-arch",
			toolName: "kek",
			channel:  sectools.ChannelStable,
			os:       runtime.GOOS,
			arch:     "kek",
			versions: []version{
				{
					version:    "0.0.9",
					contentErr: true,
				},
				{
					version:    "1.0.0",
					isLatest:   true,
					contentErr: true,
				},
			},
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			sc := sectools.NewClient(tc.toolName,
				sectools.WithChannel(tc.channel),
				sectools.WithArch(tc.arch),
				sectools.WithOS(tc.os),
				sectools.WithUpstream(srv.URL),
			)

			for _, lc := range tc.versions {
				t.Run(fmt.Sprintf("latest_%s", lc.version), func(t *testing.T) {
					isLatest, actualVersion, err := sc.IsLatestVersion(context.Background(), lc.version)
					if lc.versionErr {
						require.Error(t, err)
						return
					}

					t.Run(fmt.Sprintf("content_%s", lc.version), func(t *testing.T) {
						var out bytes.Buffer
						err := sc.DownloadVersion(context.Background(), lc.version, &out)
						if lc.contentErr {
							require.Error(t, err)
							return
						}

						require.NoError(t, err)
						require.Equal(t, lc.content, out.Bytes())
					})

					require.NoError(t, err)
					require.Equal(t, lc.isLatest, isLatest)
					if !isLatest {
						require.NotEqual(t, lc.version, actualVersion)
						return
					}

					require.Equal(t, lc.version, actualVersion)

					actualManifest, err := sc.LatestManifest(context.Background())
					require.NoError(t, err)
					require.Equal(t, lc.version, actualManifest.Version)
					require.Equal(t, lc.contentHash, actualManifest.Binaries[tc.os][tc.arch].Hash)

					actualVersion, err = sc.LatestVersion(context.Background())
					require.NoError(t, err)
					require.Equal(t, lc.version, actualVersion)

					t.Run("content_latest", func(t *testing.T) {
						var out bytes.Buffer
						err := sc.DownloadLatestVersion(context.Background(), &out)
						if lc.contentErr {
							require.Error(t, err)
							return
						}

						require.NoError(t, err)
						require.Equal(t, lc.content, out.Bytes())
					})

					t.Run("content_channel", func(t *testing.T) {
						var out bytes.Buffer
						err := sc.DownloadVersion(context.Background(), string(tc.channel), &out)
						if lc.contentErr {
							require.Error(t, err)
							return
						}

						require.NoError(t, err)
						require.Equal(t, lc.content, out.Bytes())
					})
				})
			}
		})
	}
}
