package ytc

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestBuildPushByPushIDQuery(t *testing.T) {
	req := &reqs.PushByPushIDRequest{
		Push: "01f340af-2535-4b6d-88a5-26af9b4ab829",
	}

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push/2010-07]
WHERE push_id = "01f340af-2535-4b6d-88a5-26af9b4ab829"`,
		buildPushByPushIDQuery(req, "//some/dir/push/2010-07"),
	)

	subscription := "mob:e3dadcaaff0c12818ec25bff97204631"
	req.Subscription = &subscription

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push/2010-07]
WHERE push_id = "01f340af-2535-4b6d-88a5-26af9b4ab829" AND subscription_id = "mob:e3dadcaaff0c12818ec25bff97204631"`,
		buildPushByPushIDQuery(req, "//some/dir/push/2010-07"),
	)

	uid := uint64(42)
	req.UID = &uid

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push/2010-07]
WHERE push_id = "01f340af-2535-4b6d-88a5-26af9b4ab829" AND subscription_id = "mob:e3dadcaaff0c12818ec25bff97204631" AND uid = 42`,
		buildPushByPushIDQuery(req, "//some/dir/push/2010-07"),
	)

	device := "device123"
	req.Device = &device

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push/2010-07]
WHERE push_id = "01f340af-2535-4b6d-88a5-26af9b4ab829" AND subscription_id = "mob:e3dadcaaff0c12818ec25bff97204631" AND uid = 42 AND device_id = "device123"`,
		buildPushByPushIDQuery(req, "//some/dir/push/2010-07"),
	)

	app := "ru.yandex.mobile.auth.sample"
	req.App = &app

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push/2010-07]
WHERE push_id = "01f340af-2535-4b6d-88a5-26af9b4ab829" AND subscription_id = "mob:e3dadcaaff0c12818ec25bff97204631" AND uid = 42 AND device_id = "device123" AND app_id = "ru.yandex.mobile.auth.sample"`,
		buildPushByPushIDQuery(req, "//some/dir/push/2010-07"),
	)

	req.UID = nil
	req.Device = nil

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push/2010-07]
WHERE push_id = "01f340af-2535-4b6d-88a5-26af9b4ab829" AND subscription_id = "mob:e3dadcaaff0c12818ec25bff97204631" AND app_id = "ru.yandex.mobile.auth.sample"`,
		buildPushByPushIDQuery(req, "//some/dir/push/2010-07"),
	)
}

func TestBuildPushByFieldsQuery(t *testing.T) {
	uid := uint64(123)
	device := "device123"
	app := "ru.yandex.mobile.auth.sample"
	subscription := "mob:e3dadcaaff0c12818ec25bff97204631"

	req := &reqs.PushByFieldsRequest{
		UID:          &uid,
		Device:       &device,
		App:          &app,
		Subscription: &subscription,
		FromTS:       1610398800,
		ToTS:         1641810210,
	}

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push-by-app-id/2010-07]
JOIN [//some/dir/push/2010-07] USING push_id,subscription_id,uid,app_id
WHERE 9223372035212965597 < reversed_timestamp AND reversed_timestamp <= 9223372035244377007 AND uid = 123 AND device_id = "device123" AND app_id = "ru.yandex.mobile.auth.sample" AND subscription_id = "mob:e3dadcaaff0c12818ec25bff97204631"
ORDER BY uid,app_id,reversed_timestamp
LIMIT 129`,
		buildPushByFieldsQuery(req, "//some/dir", "2010-07", 129),
	)

	req.App = nil
	req.Subscription = nil

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push-by-uid/2010-07]
JOIN [//some/dir/push/2010-07] USING push_id,subscription_id,uid
WHERE 9223372035212965597 < reversed_timestamp AND reversed_timestamp <= 9223372035244377007 AND uid = 123 AND device_id = "device123"
ORDER BY uid,reversed_timestamp
LIMIT 129`,
		buildPushByFieldsQuery(req, "//some/dir", "2010-07", 129),
	)

	req.UID = nil

	require.Equal(t,
		`push_id,subscription_id,uid,device_id,app_id,unixtime,data
FROM [//some/dir/push-by-device-id/2010-07]
JOIN [//some/dir/push/2010-07] USING push_id,subscription_id,device_id
WHERE 9223372035212965597 < reversed_timestamp AND reversed_timestamp <= 9223372035244377007 AND device_id = "device123"
ORDER BY device_id,reversed_timestamp
LIMIT 129`,
		buildPushByFieldsQuery(req, "//some/dir", "2010-07", 129),
	)
}
