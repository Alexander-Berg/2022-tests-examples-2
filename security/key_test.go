package agentkey_test

import (
	"testing"

	"github.com/stretchr/testify/require"
	"golang.org/x/crypto/ssh"
	"golang.org/x/crypto/ssh/agent"

	"a.yandex-team.ru/security/skotty/robossh/internal/agentkey"
	"a.yandex-team.ru/security/skotty/robossh/internal/testdata"
	"a.yandex-team.ru/security/skotty/skotty/pkg/sshutil"
)

func TestKey(t *testing.T) {
	type testCase struct {
		name  string
		key   testdata.Key
		fp    string
		stale bool
		err   bool
	}

	cases := []testCase{
		{
			name: testdata.Keys["rsa-sha2-256"].Comment,
			key:  testdata.Keys["rsa-sha2-256"],
			fp:   ssh.FingerprintSHA256(testdata.Keys["rsa-sha2-256"].Signer.PublicKey()),
		},
		{
			name: "any",
			key: testdata.Key{
				Signer: nil,
				AddedKey: agent.AddedKey{
					PrivateKey: nil,
				},
			},
			err: true,
		},
		{
			name: testdata.SSHCertificates["rsa-sha2-256"].Comment,
			key:  testdata.SSHCertificates["rsa-sha2-256"],
			fp:   ssh.FingerprintSHA256(testdata.SSHCertificates["rsa-sha2-256"].Signer.PublicKey()),
		},
	}

	noCommKey := testdata.Keys["ecdsa"]
	noCommKey.AddedKey.Comment = ""
	cases = append(cases, testCase{
		name: sshutil.Fingerprint(noCommKey.Signer.PublicKey()),
		key:  noCommKey,
		fp:   ssh.FingerprintSHA256(noCommKey.Signer.PublicKey()),
	})

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			key, err := agentkey.NewKey(tc.key.AddedKey)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.name, key.Name())
			require.Equal(t, tc.fp, key.Fingerprint())
			require.False(t, key.IsStale())

			buf := []byte("kek")
			sig, err := key.Sign(buf, 0)
			require.NoError(t, err)

			err = tc.key.Signer.PublicKey().Verify(buf, sig)
			require.NoError(t, err)
		})
	}
}
