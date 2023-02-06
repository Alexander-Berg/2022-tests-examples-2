package module_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/kirby/internal/module"
)

func TestValidateModule(t *testing.T) {
	cases := []struct {
		Req string
		Ok  bool
	}{
		{
			Req: "go.etcd.io/etcd/v3/@v/list",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/@v/list",
			Ok:  true,
		},
		{
			Req: "go.opencensus.io/@v/list",
			Ok:  true,
		},
		{
			Req: "go.opencensus.io/@latest",
			Ok:  true,
		},
		{
			Req: "go.opencensus.io/@v/v0.22.2.info",
			Ok:  true,
		},
		{
			Req: "go.opencensus.io/@v/v0.22.2.mod",
			Ok:  true,
		},
		{
			Req: "go.opencensus.io/@v/v0.22.2.zip",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/@latest",
			Ok:  true,
		},
		{
			Req: "github.com/google/tink/go/@latest",
			Ok:  true,
		},
		{
			Req: "github.com/google/tink/go/@v/list",
			Ok:  true,
		},
		{
			Req: "github.com/google/tink/go/@v/v1.4.0-rc2.info",
			Ok:  true,
		},
		{
			Req: "github.com/google/tink/go/@v/v1.4.0-rc2.mod",
			Ok:  true,
		},
		{
			Req: "github.com/google/tink/go/@v/v1.4.0-rc2.zip",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/@v/v1.0.0.info",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/@v/785f5dacf0770b91a4ae2882bfe1202ae5e33b46.info",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/@v/v1.0.1.mod",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/@v/v1.1.0.zip",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/v2/@v/list",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/v2/@latest",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/v2/@v/v2.0.0.info",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/v2/@v/785f5dacf0770b91a4ae2882bfe1202ae5e33b46.info",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/v2/@v/v2.0.0.mod",
			Ok:  true,
		},
		{
			Req: "github.com/foo/bar/v2/@v/v2.0.0.zip",
			Ok:  true,
		},
		{
			Req: "golang.org/x/arch/@v/list",
			Ok:  true,
		},
		{
			Req: "gopkg.in/yaml.v2/@v/list",
			Ok:  true,
		},
		{
			Req: "gopkg.in/square/go-jose.v2/@v/list",
			Ok:  true,
		},
		{
			Req: "github.com/@v/list",
			Ok:  false,
		},
		{
			Req: "github.com/v2/@v/list",
			Ok:  false,
		},
		{
			Req: "github.com/foo/@v/list",
			Ok:  false,
		},
		{
			Req: "github.com/foo/bar/v2/@v/v3.0.0.info",
			Ok:  false,
		},
		{
			Req: "github.com/foo/bar/v2/@v/v3.0.1.mod",
			Ok:  false,
		},
		{
			Req: "github.com/foo/bar/v2/@v/v3.1.0.zip",
			Ok:  false,
		},
		{
			Req: "github.com/foo/bar/@v/latest.info",
			Ok:  false,
		},
		{
			Req: "github.com/foo/bar/@v/latest.mod",
			Ok:  false,
		},
		{
			Req: "github.com/foo/bar/@v/latest.zip",
			Ok:  false,
		},
		{
			Req: "golang.org/x/@v/list",
			Ok:  false,
		},
		{
			Req: "golang.org/@v/list",
			Ok:  false,
		},
		{
			Req: "golang.org/v2/@v/list",
			Ok:  false,
		},
		{
			Req: "gopkg.in/@v/list",
			Ok:  false,
		},
	}

	for _, tc := range cases {
		t.Run(tc.Req, func(t *testing.T) {
			m, err := module.ParseModule(tc.Req)
			require.NoError(t, err)

			err = module.ValidateModule(m)
			if tc.Ok {
				require.NoError(t, err)
			} else {
				require.Error(t, err)
			}
		})
	}
}
