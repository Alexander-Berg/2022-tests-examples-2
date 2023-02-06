package signer

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParseCertificateInfo(t *testing.T) {
	cases := []struct {
		Name     string
		HavePriv bool
	}{
		{
			Name:     "insecure_prev",
			HavePriv: true,
		},
		{
			Name:     "insecure_cur",
			HavePriv: true,
		},
		{
			Name:     "insecure_next",
			HavePriv: false,
		},
	}

	for _, tc := range cases {
		t.Run(tc.Name, func(t *testing.T) {
			cert, err := parseCertificateInfo(fmt.Sprintf("./testdata/%s.json", tc.Name))
			require.NoError(t, err)
			require.NotEmpty(t, cert.PublicBytes)
			require.NotEmpty(t, cert.Public)
			require.NotEmpty(t, cert.SSHPublicBytes)
			require.NotEmpty(t, cert.SSHFingerprint)
			if tc.HavePriv {
				require.NotEmpty(t, cert.Private)
				require.NotEmpty(t, cert.SSHSigner)
			} else {
				require.Empty(t, cert.Private)
				require.Empty(t, cert.SSHSigner)
			}
		})
	}
}
