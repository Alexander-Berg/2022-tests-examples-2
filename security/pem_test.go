package certutil_test

import (
	"math/big"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/libs/certutil"
)

func TestPemToCert(t *testing.T) {
	cases := []struct {
		filename string
		serial   string
		cn       string
		err      bool
	}{
		{
			filename: "tst.pub",
			serial:   "2021",
			cn:       "tst",
			err:      false,
		},
		{
			filename: "tst",
			err:      true,
		},
		{
			filename: "broken.pub",
			err:      true,
		},
		{
			filename: "garbage",
			err:      true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.filename, func(t *testing.T) {
			data, err := os.ReadFile(filepath.Join("testdata", tc.filename))
			require.NoError(t, err)

			cert, err := certutil.PemToCert(data)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.serial, cert.SerialNumber.String())
			require.Equal(t, tc.cn, cert.Subject.CommonName)

			require.Equal(t, data, certutil.CertToPem(cert))
		})
	}
}

func TestPemToECPriv(t *testing.T) {
	cases := []struct {
		filename string
		d        *big.Int
		err      bool
	}{
		{
			filename: "tst",
			d: func() *big.Int {
				var out big.Int
				_, _ = out.SetString("96483988973850764762690171404940454293892390722372724676902375326058119164460", 10)
				return &out
			}(),
			err: false,
		},
		{
			filename: "tst.pub",
			err:      true,
		},
		{
			filename: "broken",
			err:      true,
		},

		{
			filename: "garbage",
			err:      true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.filename, func(t *testing.T) {
			data, err := os.ReadFile(filepath.Join("testdata", tc.filename))
			require.NoError(t, err)

			priv, err := certutil.PemToECPriv(data)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.d, priv.D)
		})
	}
}
