package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestYasmsSmsHistoryChooseFields(t *testing.T) {
	require.Equal(t, "global_sms_id,action,unixtime", chooseYasmsSmsHistoryFields(YasmsSmsHistoryBase))
	require.Equal(t, "global_sms_id,action,unixtime,uid,phone", chooseYasmsSmsHistoryFields(YasmsSmsHistoryCommon))
	require.Equal(t, "global_sms_id,action,unixtime,uid,phone,data", chooseYasmsSmsHistoryFields(YasmsSmsHistoryFull))
}

func TestYasmsSmsHistoryBuildQuery(t *testing.T) {
	require.Equal(
		t,
		`
global_sms_id,action,unixtime
FROM [//home/yasms/sms_history/sms_history]
WHERE global_sms_id = "some_id"
ORDER BY unixtime DESC
LIMIT 999
`,
		buildYasmsSmsHistoryQuery(&reqs.SmsByGlobalIDRequest{
			GlobalSmsID: "some_id",
			Limit:       999,
		}, YasmsSmsHistoryBase, "//home"),
	)

	require.Equal(
		t,
		`
global_sms_id,action,unixtime,uid,phone,data
FROM [//home/yasms/sms_history/sms_history]
WHERE global_sms_id = "some_other_id"
ORDER BY unixtime DESC
LIMIT 1
`,
		buildYasmsSmsHistoryQuery(&reqs.SmsByGlobalIDRequest{
			GlobalSmsID: "some_other_id",
			Limit:       1,
		}, YasmsSmsHistoryFull, "//home"),
	)
}

func TestYasmsSmsHistoryBuildQueryByFields(t *testing.T) {
	phone := "foo"
	fromTS := uint64(1600000000)
	toTS := uint64(1660000000)
	uid := uint64(12345)

	require.Equal(t, "", buildYasmsSmsHistoryByFieldsQuery(&reqs.SmsByFieldsRequest{}, YasmsSmsHistoryBase, "//home"))
	require.Equal(t, "", buildYasmsSmsHistoryByFieldsQuery(&reqs.SmsByFieldsRequest{Phone: &phone}, YasmsSmsHistoryBase, "//home"))

	phone = "+88005553535"
	query := buildYasmsSmsHistoryByFieldsQuery(&reqs.SmsByFieldsRequest{
		Phone: &phone,
		Limit: 129,
	}, YasmsSmsHistoryBase, "//home")
	require.Equal(t,
		`
global_sms_id,action,unixtime
FROM [//home/yasms/sms_history_by_phone/sms_history_by_phone]
JOIN [//home/yasms/sms_history/sms_history] USING global_sms_id,action,phone
WHERE phone = 88005553535
ORDER BY phone,reversed_timestamp
LIMIT 129
`,
		query,
	)

	query = buildYasmsSmsHistoryByFieldsQuery(&reqs.SmsByFieldsRequest{
		UID:   &uid,
		ToTS:  &toTS,
		Limit: 17,
	}, YasmsSmsHistoryFull, "//home")
	require.Equal(
		t,
		`
global_sms_id,action,unixtime,uid,phone,data
FROM [//home/yasms/sms_history_by_uid/sms_history_by_uid]
JOIN [//home/yasms/sms_history/sms_history] USING global_sms_id,action,uid
WHERE uid = 12345 AND 9221712036854775807 < reversed_timestamp
ORDER BY uid,reversed_timestamp
LIMIT 17
`,
		query,
	)

	query = buildYasmsSmsHistoryByFieldsQuery(&reqs.SmsByFieldsRequest{
		Phone:  &phone,
		FromTS: &fromTS,
		Limit:  17,
	}, YasmsSmsHistoryBase, "//home")
	require.Equal(
		t,
		`
global_sms_id,action,unixtime
FROM [//home/yasms/sms_history_by_phone/sms_history_by_phone]
JOIN [//home/yasms/sms_history/sms_history] USING global_sms_id,action,phone
WHERE phone = 88005553535 AND reversed_timestamp <= 9221772036854775807
ORDER BY phone,reversed_timestamp
LIMIT 17
`,
		query,
	)

	query = buildYasmsSmsHistoryByFieldsQuery(&reqs.SmsByFieldsRequest{
		Phone:  &phone,
		UID:    &uid,
		FromTS: &fromTS,
		ToTS:   &toTS,
		Limit:  129,
	}, YasmsSmsHistoryFull, "//home")
	require.Equal(
		t,
		`
global_sms_id,action,unixtime,uid,phone,data
FROM [//home/yasms/sms_history_by_phone/sms_history_by_phone]
JOIN [//home/yasms/sms_history/sms_history] USING global_sms_id,action,phone
WHERE phone = 88005553535 AND uid = 12345 AND 9221712036854775807 < reversed_timestamp AND reversed_timestamp <= 9221772036854775807
ORDER BY phone,reversed_timestamp
LIMIT 129
`,
		query,
	)
}
