package yasmsd

import (
	"database/sql"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/fraud"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/logs"
	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/storage"
)

type FakeFraudChecker struct{}

func (checker FakeFraudChecker) CheckFraudStatus(fraud.Metadata) (*fraud.AntiFraudResponse, *fraud.AntiFraudRetry, error) {
	return &fraud.AntiFraudResponse{Action: fraud.AntiFraudActionAllow}, nil, nil
}

func (checker FakeFraudChecker) Host() string {
	return "localhost"
}

func TestCheckFraud(t *testing.T) {
	loggers := &logs.Logs{
		General: logs.NewGeneralLog("general.log"),
		Private: logs.NewPrivateStatboxLog("statbox.private.log"),
		Public:  logs.NewPublicStatboxLog("statbox.log"),
	}
	ff := &FakeFraudChecker{}

	result, _ := checkSmsFraud(ff, &storage.SmsRow{
		Metadata: sql.NullString{
			Valid:  true,
			String: `{"service":"asdf1"}`,
		},
		CreateTime: "2022-01-12 12:32:34",
	}, nil, loggers)
	require.True(t, result)

	result, _ = checkSmsFraud(ff, &storage.SmsRow{
		Metadata: sql.NullString{
			Valid:  true,
			String: `{"service:"asdf1"}`,
		},
		CreateTime: "2022-01-12 12:32:34",
	}, nil, loggers)
	require.False(t, result)

	result, _ = checkSmsFraud(ff, &storage.SmsRow{
		Metadata: sql.NullString{
			Valid:  true,
			String: `{"service":"asdf1"}`,
		},
		CreateTime: "asdf",
	}, nil, loggers)
	require.False(t, result)
}
