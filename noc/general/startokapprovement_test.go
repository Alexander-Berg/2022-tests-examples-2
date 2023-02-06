package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestStartOKApprovementMulti проверяет запуск согласования через OK с несколькими ответсвенными, в том числе
// получаемыми из когфига.
func (suite *functionalSuite) TestStartOKApprovementMulti() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestStartOKApprovementSingle проверяет запуск согласования через OK с одним ответсвенным.
func (suite *functionalSuite) TestStartOKApprovementSingle() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.approversLoader)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}
