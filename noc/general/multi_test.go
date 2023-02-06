package authentication

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies/mocks"
)

type MultiBackendTestSuite struct {
	suite.Suite
	backend1              *mocks.AuthenticationBackend
	backend2              *mocks.AuthenticationBackend
	authenticationBackend dependencies.AuthenticationBackend
	withLoggerCtx         context.Context
	authParams            *dependencies.AuthParams
	expectedAuthInfo      *dependencies.AuthInfo
}

func (suite *MultiBackendTestSuite) SetupSuite() {
	suite.authParams = &dependencies.AuthParams{
		OAuthToken:      ptr.String("testOAuthToken"),
		SessionIDCookie: ptr.String("testSessionID"),
		Host:            "testHost",
		UserIP:          "testUserIP",
	}
	suite.expectedAuthInfo = &dependencies.AuthInfo{
		SID:      123,
		UserName: "testUserName",
	}
}

func (suite *MultiBackendTestSuite) SetupTest() {
	suite.backend1 = &mocks.AuthenticationBackend{}
	suite.backend2 = &mocks.AuthenticationBackend{}
	suite.authenticationBackend = NewMultiBackend(suite.backend1, suite.backend2)
	suite.withLoggerCtx = makeWithLoggerCtx(suite.T())
}

func (suite *MultiBackendTestSuite) TearDownTest() {
	suite.backend1.AssertExpectations(suite.T())
	suite.backend2.AssertExpectations(suite.T())
}

func (suite *MultiBackendTestSuite) TestSuccessAuthenticated() {
	suite.backend1.On("Authenticate", mock.Anything, suite.authParams).Return(suite.expectedAuthInfo, nil).Once()

	authInfo, err := suite.authenticationBackend.Authenticate(suite.withLoggerCtx, suite.authParams)
	suite.Require().NoError(err)
	suite.Require().Equal(suite.expectedAuthInfo, authInfo)
}

func (suite *MultiBackendTestSuite) TestSuccessAnonymous() {
	suite.backend1.On("Authenticate", mock.Anything, suite.authParams).Return(nil, nil).Once()
	suite.backend2.On("Authenticate", mock.Anything, suite.authParams).Return(nil, nil).Once()

	authInfo, err := suite.authenticationBackend.Authenticate(suite.withLoggerCtx, suite.authParams)
	suite.Require().NoError(err)
	suite.Require().Nil(authInfo)
}

func (suite *MultiBackendTestSuite) TestSuccessAfterError() {
	suite.backend1.
		On("Authenticate", mock.Anything, suite.authParams).
		Return(nil, errors.New("authentication error")).
		Once()
	suite.backend2.On("Authenticate", mock.Anything, suite.authParams).Return(suite.expectedAuthInfo, nil).Once()

	authInfo, err := suite.authenticationBackend.Authenticate(suite.withLoggerCtx, suite.authParams)
	suite.Require().NoError(err)
	suite.Require().Equal(suite.expectedAuthInfo, authInfo)
}

func (suite *MultiBackendTestSuite) TestError() {
	authErr := errors.New("authentication error")
	suite.backend1.On("Authenticate", mock.Anything, suite.authParams).Return(nil, authErr).Once()
	suite.backend2.On("Authenticate", mock.Anything, suite.authParams).Return(nil, nil).Once()

	authInfo, err := suite.authenticationBackend.Authenticate(suite.withLoggerCtx, suite.authParams)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, authErr))
	suite.Require().Nil(authInfo)
}

func TestMultiBackendTestSuite(t *testing.T) {
	suite.Run(t, new(MultiBackendTestSuite))
}
