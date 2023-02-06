package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestBuildRestoreQuery(t *testing.T) {
	req := &reqs.EventsRestoreRequest{
		UID:     123,
		FromTS:  1651135864,
		ToTS:    1651235864,
		OrderBy: reqs.OrderByDesc,
		Limit:   1000,
	}
	require.Equal(t,
		`
reversed_timestamp, data
FROM [//some/dir/restore/restore]
WHERE uid = 123 AND 9221720800990775807 < reversed_timestamp AND reversed_timestamp <= 9221720900990775807
ORDER BY uid, reversed_timestamp
LIMIT 1000
`,
		buildRestoreQuery(req, "//some/dir"),
	)

	req = &reqs.EventsRestoreRequest{
		UID:     100500,
		FromTS:  1617236028,
		ToTS:    1651236028,
		OrderBy: reqs.OrderByAsc,
		Limit:   312,
	}
	require.Equal(t,
		`
reversed_timestamp, data
FROM [//some/dir/restore/restore]
WHERE uid = 100500 AND 9221720800826775807 < reversed_timestamp AND reversed_timestamp <= 9221754800826775807
ORDER BY uid, reversed_timestamp
LIMIT 312
`,
		buildRestoreQuery(req, "//some/dir"),
	)
}
