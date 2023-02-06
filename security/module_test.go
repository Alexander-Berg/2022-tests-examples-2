package bpf

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/internal/kernel"
)

func TestChooseResourceKey(t *testing.T) {
	cases := []struct {
		kernVer kernel.Version
		resKey  string
		err     bool
	}{
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 91,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_4.19.91.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 95,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_4.19.91.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 100,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_4.19.100.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 119,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_4.19.119.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 131,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_4.19.131.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 143,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_4.19.143.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 144,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_4.19.143.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 5,
				Minor: 4,
				Patch: 144,
			},
			resKey: "security/gideon/gideon/bpf/gideon_bpf_btf.elf",
		},
		{
			kernVer: kernel.Version{
				Major: 4,
				Minor: 19,
				Patch: 1,
			},
			err: true,
		},
		{
			kernVer: kernel.Version{
				Major: 3,
				Minor: 6,
				Patch: 1,
			},
			err: true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.kernVer.String(), func(t *testing.T) {
			resKey, err := chooseResourceKey(&tc.kernVer)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.resKey, resKey)
		})
	}
}
