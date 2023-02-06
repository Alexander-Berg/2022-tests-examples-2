package softattest_test

import (
	_ "embed"
	"errors"
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/libs/certutil"
	"a.yandex-team.ru/security/skotty/skotty/pkg/softattest"
)

//go:embed skotty-soft.priv
var privKeyBytes []byte

//go:embed skotty-soft.pub
var pubKeyBytes []byte

func TestSharedAttestator(t *testing.T) {
	attest := softattest.SharedAttestator()
	require.NotNil(t, attest)

	serial, err := attest.TokenSerial()
	require.NoError(t, err)

	rootPub, err := certutil.PemToCert(pubKeyBytes)
	require.NoError(t, err)
	require.Equal(t, rootPub, attest.Public)

	cert, err := attest.Certificate()
	require.NoError(t, err)
	require.Equal(t, fmt.Sprintf("Skotty Self Attest for %s", serial), cert.Subject.CommonName)
	require.Equal(t, rootPub.Subject, cert.Issuer)
	require.Equal(t, true, cert.IsCA)
	require.LessOrEqual(t, time.Now().Add(time.Hour).UnixNano(), cert.NotAfter.UnixNano())
}

func TestTokenSerial(t *testing.T) {
	cases := []struct {
		userName    string
		machineID   string
		tokenSerial string
	}{
		{
			userName:    "buglloc",
			machineID:   "lol",
			tokenSerial: "5a8867fb3977151ff1fc328edae2924c",
		},
		{
			userName:    "buglloc",
			machineID:   "kek",
			tokenSerial: "001ad9fd243293d19417b9db802a44cb",
		},
		{
			userName:    "buglloc",
			machineID:   "lolkek",
			tokenSerial: "1af421d2cc0136b2c3d55a7b7f9fbd3b",
		},
		{
			userName:    "anton-k",
			machineID:   "lolkekcheburek",
			tokenSerial: "65d418bf4086b1d33cfe5553b9ea9d05",
		},
	}

	t.Run("success", func(t *testing.T) {
		for _, tc := range cases {
			t.Run(tc.tokenSerial, func(t *testing.T) {
				usernameFn := func() (string, error) {
					return tc.userName, nil
				}

				machineIDFn := func() (string, error) {
					return tc.machineID, nil
				}

				attest := softattest.NewAttestator(privKeyBytes, pubKeyBytes, usernameFn, machineIDFn)
				serial, err := attest.TokenSerial()
				require.NoError(t, err)
				require.Equal(t, tc.tokenSerial, serial)
			})
		}
	})

	t.Run("fail_username", func(t *testing.T) {
		for _, tc := range cases {
			t.Run(tc.tokenSerial, func(t *testing.T) {
				usernameFn := func() (string, error) {
					return tc.userName, errors.New("err")
				}

				machineIDFn := func() (string, error) {
					return tc.machineID, nil
				}

				attest := softattest.NewAttestator(privKeyBytes, pubKeyBytes, usernameFn, machineIDFn)
				serial, err := attest.TokenSerial()
				require.Error(t, err)
				require.Empty(t, serial)
			})
		}
	})

	t.Run("fail_username", func(t *testing.T) {
		for _, tc := range cases {
			t.Run(tc.tokenSerial, func(t *testing.T) {
				usernameFn := func() (string, error) {
					return tc.userName, nil
				}

				machineIDFn := func() (string, error) {
					return tc.machineID, errors.New("err")
				}

				attest := softattest.NewAttestator(privKeyBytes, pubKeyBytes, usernameFn, machineIDFn)
				serial, err := attest.TokenSerial()
				require.Error(t, err)
				require.Empty(t, serial)
			})
		}
	})
}
