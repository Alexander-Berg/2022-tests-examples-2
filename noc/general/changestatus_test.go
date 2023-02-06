package rfcapi

import (
	"bytes"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestChangeRFCStatusAgreementCancel проверяет успешную отмену RFC, находящегося в статусе agreementNeeded.
func (suite *functionalSuite) TestChangeRFCStatusAgreementCancel() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler)
	body := bytes.NewBufferString(`{"action":"cancel"}`)
	resp := suite.doSelfRequest("POST", "/NOCRFCS-1/changeStatus", body)
	defer resp.Body.Close()
	suite.snapshot.Snapshot(suite.T(), suite.selfHTTPServer, suite.mockHTTPServer)
}

// TestChangeRFCStatusBeginExecution проверяет успешное начало работы RFC.
func (suite *functionalSuite) TestChangeRFCStatusBeginExecution() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler)
	body := bytes.NewBufferString(`{"action":"beginExecution"}`)
	resp := suite.doSelfRequest("POST", "/NOCRFCS-1/changeStatus", body)
	defer resp.Body.Close()
	suite.snapshot.Snapshot(suite.T(), suite.selfHTTPServer, suite.mockHTTPServer)
}

// TestChangeRFCStatusPendingExecution проверяет успешную отмену RFC, находящегося в статусе pending.
func (suite *functionalSuite) TestChangeRFCStatusPendingExecution() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler)
	body := bytes.NewBufferString(`{"action":"cancel"}`)
	resp := suite.doSelfRequest("POST", "/NOCRFCS-1/changeStatus", body)
	defer resp.Body.Close()
	suite.snapshot.Snapshot(suite.T(), suite.selfHTTPServer, suite.mockHTTPServer)
}

// TestChangeRFCStatusInProgressClose проверяет успешное завершение RFC, находящегося в статусе inProgress.
func (suite *functionalSuite) TestChangeRFCStatusInProgressClose() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler)
	body := bytes.NewBufferString(`{"action":"done"}`)
	resp := suite.doSelfRequest("POST", "/NOCRFCS-1/changeStatus", body)
	defer resp.Body.Close()
	suite.snapshot.Snapshot(suite.T(), suite.selfHTTPServer, suite.mockHTTPServer)
}

// TestChangeRFCConflictTransition проверяет ошибку 409 Conflict при невозможном переходе.
func (suite *functionalSuite) TestChangeRFCConflictTransition() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler)
	body := bytes.NewBufferString(`{"action":"done"}`)
	resp := suite.doSelfRequest("POST", "/NOCRFCS-1/changeStatus", body)
	defer resp.Body.Close()
	suite.snapshot.Snapshot(suite.T(), suite.selfHTTPServer, suite.mockHTTPServer)
}

// TestChangeRFCStatusNotFound проверяет ошибку при попытке изменить статус у несуществующего RFC.
func (suite *functionalSuite) TestChangeRFCStatusNotFound() {
	body := bytes.NewBufferString(`{"action":"done"}`)
	resp := suite.doSelfRequest("POST", "/NOCRFCS-1/changeStatus", body)
	defer resp.Body.Close()
	suite.snapshot.Snapshot(suite.T(), suite.selfHTTPServer)
}
