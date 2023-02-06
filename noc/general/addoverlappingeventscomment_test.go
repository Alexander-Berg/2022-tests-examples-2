package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

// TestAddOverlappingEventsComment is a common test for receiving infra events, filtering them and adding
// overlapping comment, NOCDEV-6768 and NOCRFCS-11151 are the test data reference.
func (suite *functionalSuite) TestAddOverlappingEventsComment() {
	suite.snapshot.Load(suite.T(), dbsnapshot.New(suite.tx), suite.startrekMockHandler, suite.infraMockHandler)
	suite.Nil(suite.bg.SelectAndRun(context.Background()))
	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx), suite.mockHTTPServer)
}
