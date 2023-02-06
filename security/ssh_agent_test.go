package sshutil_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/pkg/sshutil"
)

func TestSSHAgentScript(t *testing.T) {
	cases := []struct {
		sock     string
		pid      int
		expected string
	}{
		{
			sock:     "kek",
			pid:      31337,
			expected: "SSH_AGENT_LAUNCHER='skotty'; export SSH_AGENT_LAUNCHER;\nSSH_AUTH_SOCK=\"kek\"; export SSH_AUTH_SOCK;\nSSH_AGENT_PID=31337; export SSH_AGENT_PID;\n",
		},
		{
			sock:     `"kek"`,
			pid:      31337,
			expected: "SSH_AGENT_LAUNCHER='skotty'; export SSH_AGENT_LAUNCHER;\nSSH_AUTH_SOCK=\"\\\"kek\\\"\"; export SSH_AUTH_SOCK;\nSSH_AGENT_PID=31337; export SSH_AGENT_PID;\n",
		},
	}

	for _, tc := range cases {
		t.Run(tc.sock, func(t *testing.T) {
			actual := sshutil.SSHAgentScript(tc.sock, tc.pid)
			require.Equal(t, tc.expected, string(actual))
		})
	}
}
