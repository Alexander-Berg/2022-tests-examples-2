package sshclient

import (
	"testing"

	"github.com/blang/semver/v4"
	"github.com/stretchr/testify/require"
)

func TestParseSSHVersion(t *testing.T) {
	mustParseVersion := func(in string) semver.Version {
		v, err := semver.ParseTolerant(in)
		require.NoError(t, err)
		return v
	}

	cases := []struct {
		clientName string
		in         string
		ver        semver.Version
		err        bool
	}{
		{
			clientName: "OpenSSH",
			in:         "OpenSSH_8.1",
			ver:        mustParseVersion("8.1"),
		},
		{
			clientName: "OpenSSH",
			in:         "OpenSSH_8.1p1",
			ver:        mustParseVersion("8.1"),
		},
		{
			clientName: "OpenSSH",
			in:         "OpenSSH_8.1p1\n",
			ver:        mustParseVersion("8.1"),
		},
		{
			clientName: "OpenSSH",
			in:         "OpenSSH_8.1p1, LibreSSL 2.7.3",
			ver:        mustParseVersion("8.1"),
		},
		{
			clientName: "OpenSSH",
			in:         "OpenSSH_8.2p1 Ubuntu-4ubuntu0.1, OpenSSL 1.1.1f  31 Mar 2020",
			ver:        mustParseVersion("8.2"),
		},
		{
			clientName: "OpenSSH",
			in:         "OpenSSH_8.2p1 Ubuntu-4ubuntu0.1, OpenSSL 1.1.1f  31 Mar 2020\n\nlala",
			ver:        mustParseVersion("8.2"),
		},
		{
			clientName: "OpenSSH_for_Windows",
			in:         "OpenSSH_for_Windows_8.6p1, LibreSSL 3.3.3",
			ver:        mustParseVersion("8.6"),
		},
		{
			clientName: "OpenSSH",
			in:         "OpenSSH_for_Windows_8.6p1, LibreSSL 3.3.3",
			err:        true,
		},
		{
			clientName: "kek",
			in:         "OpenSSH_8.2p1 Ubuntu-4ubuntu0.1, OpenSSL 1.1.1f  31 Mar 2020",
			err:        true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.in, func(t *testing.T) {
			ver, err := parseSSHVersion(tc.clientName, tc.in)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.ver.String(), ver.String())
		})
	}
}
