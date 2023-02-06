package app

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestClientCompatNotice(t *testing.T) {
	cases := []struct {
		banner string
		notice string
	}{
		{
			banner: "OpenSSH_7.2",
			notice: noticeTooOldOpenSSH,
		},
		{
			banner: "OpenSSH_7.2p1 Ubuntu-4ubuntu0.4",
			notice: noticeTooOldOpenSSH,
		},
		{
			banner: "OpenSSH_for_Windows_8.1",
			notice: noticeTooOldOpenSSH,
		},
		{
			banner: "OpenSSH_8.6",
			notice: noticeNoRSAOpenSSH,
		},
		{
			banner: "OpenSSH_9.0",
			notice: noticeNoRSAOpenSSH,
		},
		{
			banner: "OpenSSH_for_Windows_8.6p1",
			notice: noticeNoRSAOpenSSH,
		},
		{
			banner: "OpenSSH_for_Windows_8.9",
			notice: noticeNoRSAOpenSSH,
		},
		{
			banner: "PuTTY-Release-0.57",
			notice: noticeTooOldPutty,
		},
		{
			banner: "PuTTY_Release_0.57",
			notice: noticeTooOldPutty,
		},
		{
			banner: "PuTTY_Release_0.75",
			notice: noticeTooOldPutty,
		},

		{
			banner: "OpenSSH_8.2",
		},
		{
			banner: "OpenSSH_8.4",
		},
		{
			banner: "OpenSSH_8.2p1 Ubuntu-4ubuntu0.4",
		},
		{
			banner: "OpenSSH_for_Windows_8.2",
		},
		{
			banner: "PuTTY_Release_0.76",
		},
	}

	for _, tc := range cases {
		t.Run(tc.banner, func(t *testing.T) {
			actual := clientCompatNotice(tc.banner)
			require.Equal(t, tc.notice, actual)
		})
	}
}
