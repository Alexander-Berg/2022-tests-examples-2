package sshutil_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/ssh"

	"a.yandex-team.ru/security/skotty/skotty/pkg/sshutil"
)

func TestFingerprint(t *testing.T) {
	cases := []struct {
		filename string
		expected string
	}{
		{
			filename: "rsa.pub",
			expected: "SHA256:h1ttnBoD2JdrPvmngBfNKb5i5sfBr3EYveDHAGEo/SY",
		},
		{
			filename: "ecdsa.pub",
			expected: "SHA256:HDgRv4Tb2BblM2tNMPu1R4TibUncRg0Hhe1JGsS6ut8",
		},
		{
			filename: "ecdsa-cert.pub",
			expected: "SHA256:HCOVo9LVo7v7SqRw333XFmKUVsIuXzKTYwy+AvM+ZuA",
		},
		{
			filename: "ed25519.pub",
			expected: "SHA256:o7EigM4kZgIy6xwPSBJq7J9dd8yiPUhIWt3Z2AxzjEM",
		},
	}

	for _, tc := range cases {
		t.Run(tc.filename, func(t *testing.T) {
			in, err := os.ReadFile(filepath.Join("testdata", tc.filename))
			require.NoError(t, err)

			pubKey, _, _, _, err := ssh.ParseAuthorizedKey(in)
			require.NoError(t, err)

			actual := sshutil.Fingerprint(pubKey)
			require.Equal(t, tc.expected, actual)
		})
	}
}
