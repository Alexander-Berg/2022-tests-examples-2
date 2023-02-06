package module_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/kirby/internal/module"
)

func TestParseModule(t *testing.T) {
	cases := []struct {
		req string
		mod module.Module
		err bool
	}{
		{
			req: "gopkg.in/v3/@v/list",
			err: true,
		},
		{
			req: "gopkg.in/kek.v1/@v/list",
			mod: module.Module{
				Path:        "gopkg.in/kek.v1",
				EscapedPath: "gopkg.in/kek.v1",
				What:        module.WhatList,
			},
		},
		{
			req: "go.etcd.io/etcd/v3/@v/list",
			mod: module.Module{
				Path:        "go.etcd.io/etcd/v3",
				EscapedPath: "go.etcd.io/etcd/v3",
				What:        module.WhatList,
			},
		},
		{
			req: "github.com/lol/kek/v1@latest",
			err: true,
		},
		{
			req: "github.com/lol/kek/@latest",
			mod: module.Module{
				Path:        "github.com/lol/kek",
				EscapedPath: "github.com/lol/kek",
				What:        module.WhatLatest,
			},
		},
		{
			req: "github.com/lol/kek/v2/@latest",
			mod: module.Module{
				Path:        "github.com/lol/kek/v2",
				EscapedPath: "github.com/lol/kek/v2",
				What:        module.WhatLatest,
			},
		},
		{
			req: "gopkg.in/!acconut/lockfile.v1/@v/v1.1.0.info",
			mod: module.Module{
				Path:           "gopkg.in/Acconut/lockfile.v1",
				EscapedPath:    "gopkg.in/!acconut/lockfile.v1",
				What:           module.WhatInfo,
				Version:        "v1.1.0",
				EscapedVersion: "v1.1.0",
			},
		},
		{
			req: "github.com/lol/kek/v2/@v/v2.0.0.info",
			mod: module.Module{
				Path:           "github.com/lol/kek/v2",
				EscapedPath:    "github.com/lol/kek/v2",
				What:           module.WhatInfo,
				Version:        "v2.0.0",
				EscapedVersion: "v2.0.0",
			},
		},
		{
			req: "github.com/lol/kek/v2/@v/785f5dacf0770b91a4ae2882bfe1202ae5e33b46.info",
			mod: module.Module{
				Path:           "github.com/lol/kek/v2",
				EscapedPath:    "github.com/lol/kek/v2",
				What:           module.WhatInfo,
				Version:        "785f5dacf0770b91a4ae2882bfe1202ae5e33b46",
				EscapedVersion: "785f5dacf0770b91a4ae2882bfe1202ae5e33b46",
			},
		},
		{
			req: "github.com/lol/kek/v2/@v/v2.1.0.mod",
			mod: module.Module{
				Path:           "github.com/lol/kek/v2",
				EscapedPath:    "github.com/lol/kek/v2",
				What:           module.WhatMod,
				Version:        "v2.1.0",
				EscapedVersion: "v2.1.0",
			},
		},
		{
			req: "github.com/lol/kek/v2/@v/v2.0.1.zip",
			mod: module.Module{
				Path:           "github.com/lol/kek/v2",
				EscapedPath:    "github.com/lol/kek/v2",
				What:           module.WhatZip,
				Version:        "v2.0.1",
				EscapedVersion: "v2.0.1",
			},
		},
		{
			req: "lol/kek",
			err: true,
		},
		{
			req: "lol/kek@latest",
			err: true,
		},
		{
			req: "lol/kek/@latest",
			err: true,
		},
		{
			req: "lol/kek/v2/@latest",
			err: true,
		},
		{
			req: "lol/kek@v/list",
			err: true,
		},
		{
			req: "lol/kek@v/v1.0.0.info",
			err: true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.req, func(t *testing.T) {
			m, err := module.ParseModule(tc.req)
			if tc.err {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.NotNil(t, m)
			require.Equal(t, tc.mod, *m)
		})
	}
}
