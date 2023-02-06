package yputil_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/xray/internal/yputil"
)

func TestAccountToABC(t *testing.T) {
	cases := []struct {
		AccountID string
		ABCID     int
	}{
		{
			AccountID: "abc:lol:909",
			ABCID:     0,
		},
		{
			AccountID: "kek:service:909",
			ABCID:     0,
		},
		{
			AccountID: "service:909",
			ABCID:     0,
		},
		{
			AccountID: "909",
			ABCID:     0,
		},
		{
			AccountID: "tmp",
			ABCID:     0,
		},
		{
			AccountID: "abc:service:909",
			ABCID:     909,
		},
		{
			AccountID: "abc:service:470",
			ABCID:     470,
		},
	}

	for _, tc := range cases {
		t.Run(tc.AccountID, func(t *testing.T) {
			actualABCID := yputil.AccountToABC(tc.AccountID)
			require.Equal(t, tc.ABCID, actualABCID)
		})
	}
}
