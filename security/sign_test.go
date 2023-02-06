package certutil_test

import (
	"crypto"
	"crypto/x509"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/libs/certutil"
)

func TestSign(t *testing.T) {
	pub := func() *x509.Certificate {
		data, err := os.ReadFile(filepath.Join("testdata", "tst.pub"))
		require.NoError(t, err)

		out, err := certutil.PemToCert(data)
		require.NoError(t, err)

		return out
	}()

	priv := func() crypto.Signer {
		data, err := os.ReadFile(filepath.Join("testdata", "tst"))
		require.NoError(t, err)

		out, err := certutil.PemToECPriv(data)
		require.NoError(t, err)

		return out
	}()

	sign, err := certutil.Sign(priv, []byte("kek"))
	require.NoError(t, err)

	ok, err := certutil.Verify(pub, []byte("kek"), sign)
	require.NoError(t, err)
	require.True(t, ok)
}
