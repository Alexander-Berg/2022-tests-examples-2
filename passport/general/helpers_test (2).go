package mysql

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/filter"
	"a.yandex-team.ru/passport/infra/daemons/yasms_internal/internal/model"
)

func TestPrepareSelectCountQuery(t *testing.T) {
	query, args, err := prepareSelectCountQuery("smsrt AS routes", nil, nil)
	require.NoError(t, err)
	require.Equal(t, `
SELECT COUNT(*) as count
FROM smsrt AS routes
`, query)
	require.Nil(t, args)

	query, args, err = prepareSelectCountQuery("smsrt AS routes", &filter.FieldFilter{
		Field:     model.GateIDFieldAlias,
		CompareOp: filter.Equal,
		Values:    []string{"113", "114"},
	}, routesFilterFields)
	require.NoError(t, err)
	require.Equal(t, `
SELECT COUNT(*) as count
FROM smsrt AS routes
WHERE routes.gateid IN (?, ?)
`, query)
	require.EqualValues(t, []interface{}{"113", "114"}, args)
}
