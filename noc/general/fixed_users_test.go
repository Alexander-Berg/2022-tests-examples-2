package authorization

import (
	"context"
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
)

type FixedUsersTestSuite struct {
	suite.Suite
	backend       dependencies.AuthorizationBackend
	login         string
	withLoggerCtx context.Context
}

func (suite *FixedUsersTestSuite) SetupSuite() {
	suite.login = "testLogin"
	suite.backend = NewFixedUsersBackend([]string{suite.login})
	suite.withLoggerCtx = makeWithLoggerCtx(suite.T())
}

func (suite *FixedUsersTestSuite) TestFailAuthenticatedUser() {
	isAuthorized, err := suite.backend.Authorize(suite.withLoggerCtx, &dependencies.AuthInfo{
		SID:      0,
		UserName: "unexistentUserName",
	})
	suite.Require().NoError(err)
	suite.Require().False(isAuthorized)
}

func (suite *FixedUsersTestSuite) TestFailAnonymous() {
	isAuthorized, err := suite.backend.Authorize(suite.withLoggerCtx, nil)
	suite.Require().NoError(err)
	suite.Require().False(isAuthorized)
}

func (suite *FixedUsersTestSuite) TestSuccess() {
	isAuthorized, err := suite.backend.Authorize(suite.withLoggerCtx, &dependencies.AuthInfo{
		SID:      0,
		UserName: suite.login,
	})

	suite.Require().NoError(err)
	suite.Require().True(isAuthorized)
}

func TestFixedUsersTestSuite(t *testing.T) {
	suite.Run(t, new(FixedUsersTestSuite))
}
