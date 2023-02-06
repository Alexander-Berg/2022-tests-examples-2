package workflow

import (
	"context"

	"a.yandex-team.ru/noc/nocrfcsd/internal/snapshot/dbsnapshot"
)

func (suite *functionalSuite) TestCreateNewRFCTask() {
	_, err := suite.wf.CreateNewRFCTask(context.Background(), "NOCRFCS-7696")
	suite.Nil(err)

	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}

func (suite *functionalSuite) TestCreatePostEventTask() {
	_, err := suite.wf.CreatePostEventTask(context.Background(), "NOCRFCS-7696")
	suite.Nil(err)

	suite.snapshot.Snapshot(suite.T(), dbsnapshot.New(suite.tx))
}
