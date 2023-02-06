package ytc

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestBuildPushSubscriptionQuery(t *testing.T) {
	req := &reqs.PushSubscriptionRequest{
		UID:    145,
		MaxAge: 1000,
	}

	require.Equal(t,
		`
app_id,device_id,timestamp,count
FROM [//some/dir/push_subscription/push_subscription]
WHERE uid = 145 AND timestamp > 1234566890`,
		buildPushSubscriptionQuery(req, "//some/dir", time.Unix(1234567890, 0)),
	)
}
