package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestCreateJugglerMute проверяет создание juggler-mute джобы в ЦК.
func (suite *functionalSuite) TestCreateJugglerMute() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}

// TestCreateJugglerMuteNoJugglerMute проверяет, что juggler-mute джоба в ЦК не создаётся (и вообще
// шаг завершается), если rfc.JugglerMute равен nil.
func (suite *functionalSuite) TestCreateJugglerMuteNoJugglerMute() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx))
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}
