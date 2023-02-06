package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

func (suite *functionalSuite) TestCreateRFC() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCAdditionalApprovers проверяет создание RFC с дополнительным списком согласующих.
func (suite *functionalSuite) TestCreateRFCAdditionalApprovers() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCRisky проверяет создание RFC с высоким риском (для разнообразия).
func (suite *functionalSuite) TestCreateRFCRisky() {
	suite.snapshot.Load(
		suite.T(),
		dbsnapshot.New(suite.tx),
		suite.startrekMockHandler,
		suite.staffMockHandler,
		suite.abcMockHandler,
	)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCParseLoginBrackets проверяет парсинг RFC с логином, содержащим ещё скобки, например, девичью
// фамилию "Кшнякина (Макарова) Елена (ya-lilo)".
func (suite *functionalSuite) TestCreateRFCParseLoginBrackets() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCValidationErrorExternalUsers проверяет ошибку при попытке добавить внешнего сотрудника как
// согласовщика (NOCDEV-6808).
func (suite *functionalSuite) TestCreateRFCValidationErrorExternalUsers() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCParseError проверяет ошибку при невалидном описании тикета.
func (suite *functionalSuite) TestCreateRFCParseError() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCTimeException проверяет ошибку, когда время начала больше времени конца.
func (suite *functionalSuite) TestCreateRFCTimeException() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCDeviceExpressionHostnames проверяет сохранение хостнеймов устройств в devices при
// явном перечислении hostnames в выражении devicesExpression.
func (suite *functionalSuite) TestCreateRFCDeviceExpressionHostnames() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCDeviceExpressionFQDNs проверяет сохранение хостнеймов устройств в devices при
// явном перечислении fqdns в выражении devicesExpression; ожидаем, что fqdn сконвертится в hostname.
func (suite *functionalSuite) TestCreateRFCDeviceExpressionFQDNs() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCDeviceExpressionRackcodes проверяет сохранение хостнеймов устройств в devices при
// указании рэккода в выражении devicesExpression; ожидаем, что рэккода отрезолвится в список
// hostname запросом в invapi.
func (suite *functionalSuite) TestCreateRFCDeviceExpressionRackcodes() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler, suite.invAPIMock)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCSetJugglerMute проверяет сохранение RFC с выставленным set juggler mute, ожидается, что в базе
// у RFC будет правильно выставлено поле juggler_mute.
func (suite *functionalSuite) TestCreateRFCSetJugglerMute() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateRFCSetJugglerMuteNoDevices проверяет ошибку при попытке запросить создание juggler mute для пустого
// набора устройств.
func (suite *functionalSuite) TestCreateRFCSetJugglerMuteNoDevices() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.staffMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}
