package softattest_test

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/x509"
	"crypto/x509/pkix"
	"fmt"
	"math/big"
	"strconv"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/pkg/softattest"
)

func genCert(serial int64) ([]byte, []byte, error) {
	privKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to generate private key: %w", err)
	}
	csr := &x509.Certificate{
		SerialNumber: big.NewInt(serial),
		Subject: pkix.Name{
			CommonName:         "tst",
			Country:            []string{"RU"},
			Province:           []string{"Moscow"},
			Locality:           []string{"Moscow"},
			Organization:       []string{"Yandex"},
			OrganizationalUnit: []string{"Infra"},
		},
		PublicKey:             &privKey.PublicKey,
		NotBefore:             time.Now(),
		NotAfter:              time.Now().AddDate(25, 0, 0),
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageClientAuth},
		KeyUsage:              x509.KeyUsageDigitalSignature | x509.KeyUsageCertSign,
		BasicConstraintsValid: true,
	}

	privKeyBytes, err := x509.MarshalECPrivateKey(privKey)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to marshal private key: %w", err)
	}

	pubKeyBytes, err := x509.CreateCertificate(rand.Reader, csr, csr, csr.PublicKey, privKey)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to generate certificate: %w", err)
	}

	return privKeyBytes, pubKeyBytes, nil
}

func TestVerify(t *testing.T) {
	_, pubKey, err := genCert(1)
	require.NoError(t, err)

	cert, err := x509.ParseCertificate(pubKey)
	require.NoError(t, err)

	attestCert, err := softattest.SharedAttestator().Certificate()
	require.NoError(t, err)

	serial, err := softattest.SharedAttestator().TokenSerial()
	require.NoError(t, err)

	cases := []struct {
		pinPolicy   softattest.PINPolicy
		touchPolicy softattest.TouchPolicy
	}{
		{
			pinPolicy:   softattest.PINPolicyOnce,
			touchPolicy: softattest.TouchPolicyNever,
		},
		{
			pinPolicy:   softattest.PINPolicyAlways,
			touchPolicy: softattest.TouchPolicyCached,
		},
	}

	for i, tc := range cases {
		t.Run(strconv.Itoa(i), func(t *testing.T) {
			slotAttestCert, err := softattest.SharedAttestator().Attest(cert, tc.pinPolicy, tc.touchPolicy)
			require.NoError(t, err)
			require.NotNil(t, attestCert)

			attest, err := softattest.Verify(attestCert, slotAttestCert)
			require.NoError(t, err)
			require.NotNil(t, attest)
			require.Equal(t, serial, attest.Serial)
			require.Equal(t, tc.pinPolicy, attest.PINPolicy)
			require.Equal(t, tc.touchPolicy, attest.TouchPolicy)
		})
	}
}
