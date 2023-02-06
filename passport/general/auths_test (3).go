package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestAuthsBuildQuery(t *testing.T) {
	req := &reqs.AuthsRequest{
		UID:    100500,
		FromTS: 1604513822,
		ToTS:   1614513822,
	}

	require.Equal(
		t,
		`uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221762523032775807`,
		buildAuthsCondition(req, 1609513822),
	)

	req.Status = []string{"successful"}
	require.Equal(
		t,
		`uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221765523032775807 AND status IN ("successful")`,
		buildAuthsCondition(req, 1606513822),
	)

	req.Type = []string{"web", "oauthcheck"}
	req.ClientName = []string{"bb", "passport"}
	require.Equal(
		t,
		`uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221768523032775807 AND type IN ("web","oauthcheck") AND status IN ("successful") AND client_name IN ("bb","passport")`,
		buildAuthsCondition(req, 1603513822),
	)

	require.Equal(t,
		`
reversed_timestamp,type,status,client_name,data
FROM [//some/table]
WHERE uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221762523032775807
ORDER BY uid,reversed_timestamp
LIMIT 129`,
		buildAuthsQuery("//some/table", `uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221762523032775807`, 129),
	)
}

func TestAuthsRuntimeAggregatedBuildQuery(t *testing.T) {
	req := &reqs.AuthsRuntimeAggregatedRequest{
		UID:    100500,
		FromTS: 1604513822,
		ToTS:   1614513822,
	}

	require.Equal(
		t,
		`uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221762523032775807 AND (status IN ("ses_create","ses_update") OR (status = "successful" AND not type = "web"))`,
		buildAuthsRuntimeAggregatedCondition(req, 1609513822),
	)

	require.Equal(
		t,
		`uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221765523032775807 AND (status IN ("ses_create","ses_update") OR (status = "successful" AND not type = "web"))`,
		buildAuthsRuntimeAggregatedCondition(req, 1606513822),
	)

	require.Equal(t,
		`
reversed_timestamp,type,status,client_name,data
FROM [//some/table]
WHERE uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221765523032775807 AND (status IN ("ses_create","ses_update") OR (status = "successful" AND not type = "web"))
ORDER BY uid,reversed_timestamp
LIMIT 129`,
		buildAuthsQuery("//some/table", `uid = 100500 AND 9221757523032775807 < reversed_timestamp AND reversed_timestamp <= 9221765523032775807 AND (status IN ("ses_create","ses_update") OR (status = "successful" AND not type = "web"))`, 129),
	)
}
