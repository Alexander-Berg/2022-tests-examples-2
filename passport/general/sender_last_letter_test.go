package ytc

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/historydb_api2/internal/reqs"
)

func TestBuildSenderLastLetterQuery(t *testing.T) {
	req := &reqs.SenderLastLetterRequest{
		UID:    100500,
		MaxAge: 300,
	}

	require.Equal(t,
		`
unsibscribe_list,timestamp
FROM [//some/dir/sendr/last_letter]
WHERE uid = 100500 AND timestamp > 1234567590`,
		buildSenderLastLetterQuery(req, "//some/dir", time.Unix(1234567890, 0)),
	)
}
