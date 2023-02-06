package sshutil_test

import (
	"fmt"
	"net"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/pkg/sshutil"
)

func TestSSHAgentScript(t *testing.T) {
	cases := []struct {
		sock     string
		pid      int
		expected string
		env      map[string]string
	}{
		{
			sock:     "",
			pid:      31337,
			expected: "\n",
			env: map[string]string{
				"SHELL": "/bin/not-a-fish",
			},
		},
		{
			sock:     "not-a-fish",
			pid:      31337,
			expected: "SSH_AGENT_LAUNCHER='skotty'; export SSH_AGENT_LAUNCHER;\nSSH_AUTH_SOCK=\"not-a-fish\"; export SSH_AUTH_SOCK;\nSSH_AGENT_PID=31337; export SSH_AGENT_PID;\n",
			env: map[string]string{
				"SHELL": "/bin/not-a-fish",
			},
		},
		{
			sock:     `"fishkek"`,
			pid:      31337,
			expected: "set -gx SSH_AGENT_LAUNCHER 'skotty';\nset -gx SSH_AUTH_SOCK \"\\\"fishkek\\\"\";\nset -gx SSH_AGENT_PID 31337;\n",
			env: map[string]string{
				"SHELL": "/bin/fish",
			},
		},
		{
			sock:     "cshkek",
			pid:      31337,
			expected: "setenv SSH_AGENT_LAUNCHER 'skotty';\nsetenv SSH_AUTH_SOCK \"cshkek\";\nsetenv SSH_AGENT_PID 31337;\n",
			env: map[string]string{
				"SHELL": "/bin/csh",
			},
		},
		{
			sock:     "kek",
			pid:      31337,
			expected: "SSH_AGENT_LAUNCHER='skotty'; export SSH_AGENT_LAUNCHER;\nSSH_AUTH_SOCK=\"kek\"; export SSH_AUTH_SOCK;\nSSH_AGENT_PID=31337; export SSH_AGENT_PID;\n",
			env: map[string]string{
				"SHELL": "/bin/zsh",
			},
		},
		{
			sock:     `"kek"`,
			pid:      31337,
			expected: "SSH_AGENT_LAUNCHER='skotty'; export SSH_AGENT_LAUNCHER;\nSSH_AUTH_SOCK=\"\\\"kek\\\"\"; export SSH_AUTH_SOCK;\nSSH_AGENT_PID=31337; export SSH_AGENT_PID;\n",
			env: map[string]string{
				"SHELL": "/bin/bash",
			},
		},
	}

	setEnvs := func(envs map[string]string) {
		for k, v := range envs {
			if v == "" {
				_ = os.Unsetenv(k)
				continue
			}

			_ = os.Setenv(k, v)
		}
	}

	for _, tc := range cases {
		t.Run(tc.sock, func(t *testing.T) {
			originalEnv := make(map[string]string)
			for name := range tc.env {
				originalEnv[name] = os.Getenv(name)
			}

			setEnvs(tc.env)
			defer setEnvs(originalEnv)

			actual := sshutil.SSHAgentScript(tc.sock, tc.pid)
			require.Equal(t, tc.expected, string(actual))
		})
	}
}

func TestReplaceAuthSock_noSock(t *testing.T) {
	if env, ok := os.LookupEnv("SSH_AUTH_SOCK"); ok {
		defer func() { _ = os.Setenv("SSH_AUTH_SOCK", env) }()
	}

	_ = os.Unsetenv("SSH_AUTH_SOCK")
	replaced, err := sshutil.ReplaceAuthSock("/some-sock")
	require.NoError(t, err)
	require.False(t, replaced)
}

func TestReplaceAuthSock_invalid(t *testing.T) {
	cases := []func(t *testing.T, newPath string) string{
		func(t *testing.T, _ string) string {
			out, err := os.MkdirTemp("", "TestReplaceAuthSock_invalid")
			require.NoError(t, err)
			return out
		},
		func(t *testing.T, _ string) string {
			out, err := os.CreateTemp("", "TestReplaceAuthSock_invalid")
			require.NoError(t, err)
			_ = out.Close()
			return out.Name()
		},
		func(t *testing.T, newPath string) string {
			curPath := filepath.Join(os.TempDir(), "TestReplaceAuthSock_invalid_same_symlink")

			err := os.Symlink(curPath, newPath)
			require.NoError(t, err)
			return curPath
		},
		func(_ *testing.T, _ string) string {
			return "/not/existst"
		},
	}

	for i, tc := range cases {
		t.Run(fmt.Sprint(i), func(t *testing.T) {
			if env, ok := os.LookupEnv("SSH_AUTH_SOCK"); ok {
				defer func() { _ = os.Setenv("SSH_AUTH_SOCK", env) }()
			} else {
				defer func() { _ = os.Unsetenv("SSH_AUTH_SOCK") }()
			}

			newPath := filepath.Join(os.TempDir(), "TestReplaceAuthSock_invalid_new_path")
			curSock := tc(t, newPath)
			defer func() { _ = os.RemoveAll(curSock) }()

			_ = os.Setenv("SSH_AUTH_SOCK", curSock)
			replaced, err := sshutil.ReplaceAuthSock(newPath)
			require.NoError(t, err)
			require.False(t, replaced)
		})
	}
}

func TestReplaceAuthSock_ok(t *testing.T) {
	if env, ok := os.LookupEnv("SSH_AUTH_SOCK"); ok {
		defer func() { _ = os.Setenv("SSH_AUTH_SOCK", env) }()
	} else {
		defer func() { _ = os.Unsetenv("SSH_AUTH_SOCK") }()
	}

	newSock := filepath.Join(os.TempDir(), "TestReplaceAuthSock_ok_newPath")
	curSock := filepath.Join(os.TempDir(), "TestReplaceAuthSock_ok")
	_ = os.RemoveAll(curSock)
	l, err := net.Listen("unix", curSock)
	require.NoError(t, err)
	defer func() { _ = l.Close() }()

	_ = os.Setenv("SSH_AUTH_SOCK", curSock)
	replaced, err := sshutil.ReplaceAuthSock(newSock)
	require.NoError(t, err)
	require.True(t, replaced)

	actualSock, err := os.Readlink(curSock)
	require.NoError(t, err)
	require.Equal(t, newSock, actualSock)
}
