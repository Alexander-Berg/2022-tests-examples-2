package kernel_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/internal/kernel"
)

func TestVersion(t *testing.T) {
	cases := []struct {
		Version           *kernel.Version
		VersionString     string
		HasRawTracePoints bool
	}{
		{
			Version: &kernel.Version{
				Major: 3,
				Minor: 16,
				Patch: 92,
			},
			VersionString:     "3.16.92",
			HasRawTracePoints: false,
		},
		{
			Version: &kernel.Version{
				Major: 4,
				Minor: 13,
				Patch: 0,
			},
			VersionString:     "4.13.0",
			HasRawTracePoints: false,
		},
		{
			Version: &kernel.Version{
				Major: 4,
				Minor: 17,
				Patch: 0,
			},
			VersionString:     "4.17.0",
			HasRawTracePoints: true,
		},
		{
			Version: &kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 83,
			},
			VersionString:     "4.19.83",
			HasRawTracePoints: true,
		},
		{
			Version: &kernel.Version{
				Major: 5,
				Minor: 4,
				Patch: 18,
			},
			VersionString:     "5.4.18",
			HasRawTracePoints: true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.Version.String(), func(t *testing.T) {
			require.Equal(t, tc.VersionString, tc.Version.String())
			if tc.HasRawTracePoints {
				require.Truef(t, tc.Version.HasRawTracePoints(), "kernel version %q must support raw tracepoints", tc.Version)
			} else {
				require.Falsef(t, tc.Version.HasRawTracePoints(), "kernel version %q must NOT support raw tracepoints", tc.Version)
			}
		})
	}
}
