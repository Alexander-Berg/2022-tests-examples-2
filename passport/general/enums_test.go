package mysql

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

func TestMySQLProvider_GetRouteEnums(t *testing.T) {
	provider, _ := initProvider()
	require.NoError(t, provider.SetGates(context.Background(), nil, []*model.Gate{
		{Alias: "infobipvrt", AlphaName: "Yandex"},
	}, nil, nil))
	enums, err := provider.GetRouteEnums(context.Background())
	require.NoError(t, err)
	require.Equal(t, map[string][]string{
		"infobipvrt": {"o.yandex.ru", "Yandex"},
		"m1":         {"Yandex"},
		"mitto":      {"Yandex"},
	}, enums.Aliases)
	require.Equal(t, map[string][]string{
		"o.yandex.ru": {"infobipvrt"},
		"Yandex":      {"infobipvrt", "m1", "mitto"},
	}, enums.AlphaNames)
}
