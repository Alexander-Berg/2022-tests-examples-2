package xiva

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/push_subscription/internal/model"
)

func TestCreateUnsubscribeQueryParams(t *testing.T) {
	require.EqualValues(t,
		map[string]string{
			"service": "some_service",
			"user":    "",
			"uuid":    "",
		},
		createUnsubscribeQueryParams(
			&model.UnsubscribeRequest{},
			"some_service",
		),
	)

	require.EqualValues(t,
		map[string]string{
			"service": "some_service",
			"user":    "someuser",
			"uuid":    "someuuid",
		},
		createUnsubscribeQueryParams(
			&model.UnsubscribeRequest{
				User: "someuser",
				UUID: "someuuid",
			},
			"some_service",
		),
	)
}
