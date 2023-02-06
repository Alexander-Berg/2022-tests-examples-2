package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestMailUserHistoryQueryTemplate(t *testing.T) {
	req := &reqs.MailUserHistoryRequest{
		UID:    100500,
		FromTS: 1604513822,
		ToTS:   1614513822,
	}

	require.Equal(t,
		`
reversed_unixtime,operation,module,data
FROM [//some/dir/users_history/2020-01-01]
WHERE uid=100500 AND 9223370422340953807 < reversed_unixtime AND reversed_unixtime <= 9223370432340953807
ORDER BY uid,reversed_unixtime
LIMIT 146`,
		buildMailUserHistoryQuery(req, "//some/dir", "2020-01-01", 146),
	)

	req.Corp = true
	req.Operation = []string{"op#1"}
	require.Equal(t,
		`
reversed_unixtime,operation,module,data
FROM [//some/dir/corp_users_history/2020-01-01]
WHERE uid=100500 AND 9223370422340953807 < reversed_unixtime AND reversed_unixtime <= 9223370432340953807 AND operation IN ("op#1")
ORDER BY uid,reversed_unixtime
LIMIT 146`,
		buildMailUserHistoryQuery(req, "//some/dir", "2020-01-01", 146),
	)

	req.Module = []string{"mod#1", `mo"%sd#2`}
	require.Equal(t,
		`
reversed_unixtime,operation,module,data
FROM [//some/dir/corp_users_history/2020-01-01]
WHERE uid=100500 AND 9223370422340953807 < reversed_unixtime AND reversed_unixtime <= 9223370432340953807 AND operation IN ("op#1") AND module IN ("mod#1","mo\"%sd#2")
ORDER BY uid,reversed_unixtime
LIMIT 146`,
		buildMailUserHistoryQuery(req, "//some/dir", "2020-01-01", 146),
	)
}
