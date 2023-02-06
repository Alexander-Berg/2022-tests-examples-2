package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestCreateInfraEventSkipMissingDC проверяет исключение из создаваемого события датацентров, которых нет у infra
// environment; см. NOCDEV-6540.
func (suite *functionalSuite) TestCreateInfraEventSkipMissingDC() {
	// Загружаем в базу парсинг тикета NOCRFCS-10665
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	// Убеждаемся, что в запросе на создание infra-event стоит "vla: false", не смотря на то, что в тикете
	// NOCRFCS-10665 указан ДЦ VLA
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateInfraEventVLX проверяет создание infra-события в новом датацентре VLX; см. NOCDEV-7325.
func (suite *functionalSuite) TestCreateInfraEventVLX() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	// Убеждаемся, что в запросе на создание infra-event стоит "vlx: true"
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateInfraEventDevices проверяет указание устройств в infra-событии; см. NOCDEV-4507.
func (suite *functionalSuite) TestCreateInfraEventDevices() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateInfraEventImpactedServices проверяет указание затронутых ABC-сервисов в infra-событии.
func (suite *functionalSuite) TestCreateInfraEventImpactedServices() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}
