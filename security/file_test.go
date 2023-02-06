package file_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/internal/secrets"
	"a.yandex-team.ru/security/gideon/gideon/internal/secrets/file"
)

func TestProvider(t *testing.T) {
	cases := []struct {
		Name  string
		Path  string
		Value string
	}{
		{
			Name:  "simple",
			Path:  "LB_TOKEN",
			Value: "lol",
		},
		{
			Name:  "dotted",
			Path:  ".LB_TOKEN",
			Value: "lol",
		},
		{
			Name:  "SECTION",
			Path:  "kek.LB_TOKEN",
			Value: "cheburek",
		},
	}

	cfg := secrets.Config{
		Kind:     secrets.ProviderKindFile,
		FilePath: "./testdata/secrets",
		Secrets:  make(map[string]string),
	}
	for _, tc := range cases {
		cfg.Secrets[tc.Name] = tc.Path
	}

	p, err := file.NewProvider(cfg)
	require.NoError(t, err)

	for _, tc := range cases {
		t.Run(tc.Name, func(t *testing.T) {
			actual, err := p.GetSecret(context.Background(), tc.Name)
			require.NoError(t, err)
			require.Equal(t, tc.Value, actual)
		})
	}
}
