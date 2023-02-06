package piv_test

import (
	"encoding/base64"
	"testing"

	"github.com/google/go-cmp/cmp"
	"github.com/google/go-cmp/cmp/cmpopts"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/piv"
)

func TestMetadata_unmarshal(t *testing.T) {
	cases := []struct {
		name string
		in   string
		err  bool
		out  piv.Metadata
	}{
		{
			name: "yc-yubikey-cli",
			in:   "gAOBAQI=",
			out: piv.Metadata{
				Flags: 2,
			},
		},
		{
			name: "salt",
			in:   "gAiBAQGCA2tlaw==",
			out: piv.Metadata{
				Flags: 1,
				Salt:  []byte("kek"),
			},
		},
		{
			name: "empty",
			in:   "gAOBAQA=",
			out:  piv.Metadata{},
		},
		{
			name: "invalid-tag",
			in:   "iQOBAQI=",
			err:  true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			var m piv.Metadata
			data, err := base64.StdEncoding.DecodeString(tc.in)
			require.NoError(t, err)

			err = m.Unmarshal(data)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			equalMetadata(t, tc.out, m)
		})
	}
}

func TestMetadata_marshal(t *testing.T) {
	cases := []struct {
		name string
		in   piv.Metadata
		out  string
	}{
		{
			name: "yc-yubikey-cli",
			in: piv.Metadata{
				Flags: 2,
			},
			out: "gAOBAQI=",
		},
		{
			name: "salt",
			in: piv.Metadata{
				Flags: 1,
				Salt:  []byte("kek"),
			},
			out: "gAiBAQGCA2tlaw==",
		},
		{
			name: "empty",
			in:   piv.Metadata{},
			out:  "gAOBAQA=",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			expected, err := base64.StdEncoding.DecodeString(tc.out)
			require.NoError(t, err)

			actual, err := tc.in.Marshal()
			require.NoError(t, err)

			require.Equal(t, expected, actual)
		})
	}
}

func TestMetadata_update(t *testing.T) {
	base, err := base64.StdEncoding.DecodeString("gAiBAQGCA2tlaw==")
	require.NoError(t, err)

	var m piv.Metadata
	err = m.Unmarshal(base)
	require.NoError(t, err)

	m.Salt = nil
	newBytes, err := m.Marshal()
	require.NoError(t, err)

	var m1 piv.Metadata
	err = m1.Unmarshal(newBytes)
	require.NoError(t, err)

	equalMetadata(t, m, m1)
}

func equalMetadata(t *testing.T, m, m1 piv.Metadata) {
	opts := cmp.Options{cmpopts.IgnoreUnexported(piv.Metadata{})}
	require.True(t, cmp.Equal(m, m1, opts...), cmp.Diff(m, m1, opts...))
}
