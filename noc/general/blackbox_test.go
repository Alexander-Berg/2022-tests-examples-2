package authentication

import (
	"context"
	"errors"
	"fmt"
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/library/go/yandex/blackbox"
	"a.yandex-team.ru/library/go/yandex/blackbox/mocks"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
)

const (
	oAuthToken = "testOAuthToken"
	sessionID  = "testSessionID"
	host       = "testHost"
	userIP     = "192.168.10.40"

	login = "testLogin"
	uid   = 123
)

func makeUser(uid uint64, login string) blackbox.User {
	return blackbox.User{
		UID: blackbox.UID{
			ID: uid,
		},
		Login: login,
	}
}

func makeBlackboxStatusError() *blackbox.StatusError {
	return &blackbox.StatusError{
		Status:  blackbox.StatusExpired,
		Message: "expired token",
	}
}

func makeBlackboxUnauthorizedError() *blackbox.UnauthorizedError {
	return &blackbox.UnauthorizedError{
		StatusError: *makeBlackboxStatusError(),
	}
}

type baseBlackboxTestSuite struct {
	suite.Suite
	mockCtrl      *gomock.Controller
	mockClient    *mocks.MockClient
	withLoggerCtx context.Context
}

func (suite *baseBlackboxTestSuite) SetupTest() {
	suite.mockCtrl = gomock.NewController(suite.T())
	suite.mockClient = mocks.NewMockClient(suite.mockCtrl)

	suite.withLoggerCtx = makeWithLoggerCtx(suite.T())
}

func (suite *baseBlackboxTestSuite) TearDownTest() {
	suite.mockCtrl.Finish()
}

type BlackboxSessionIDBackendTestSuite struct {
	baseBlackboxTestSuite
	authenticationBackend dependencies.AuthenticationBackend
}

func (suite *BlackboxSessionIDBackendTestSuite) SetupTest() {
	suite.baseBlackboxTestSuite.SetupTest()
	authenticationBackend, err := NewBlackboxSessionIDBackend(suite.mockClient)
	suite.Require().NoError(err)
	suite.authenticationBackend = authenticationBackend
}

func (suite *BlackboxSessionIDBackendTestSuite) TestSuccess() {
	suite.mockClient.EXPECT().SessionID(gomock.Any(), blackbox.SessionIDRequest{
		SessionID: sessionID,
		UserIP:    userIP,
		Host:      host,
	}).Return(&blackbox.SessionIDResponse{
		User: makeUser(uid, login),
	}, nil)

	expectedAuthInfo := &dependencies.AuthInfo{
		SID:      uid,
		UserName: login,
	}

	authInfo, err := suite.authenticationBackend.Authenticate(
		suite.withLoggerCtx,
		&dependencies.AuthParams{
			OAuthToken:      nil,
			SessionIDCookie: ptr.String(sessionID),
			Host:            host,
			UserIP:          userIP,
		},
	)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedAuthInfo, authInfo)
}

func (suite *BlackboxSessionIDBackendTestSuite) TestEmptySessionID() {
	authInfo, err := suite.authenticationBackend.Authenticate(
		context.Background(),
		&dependencies.AuthParams{
			OAuthToken:      ptr.String(oAuthToken),
			SessionIDCookie: nil,
			Host:            host,
			UserIP:          userIP,
		},
	)
	suite.Require().NoError(err)
	suite.Require().Nil(authInfo)
}

func (suite *BlackboxSessionIDBackendTestSuite) testBlackboxErrorToUnauthorizedError(err error) {
	suite.mockClient.EXPECT().SessionID(gomock.Any(), blackbox.SessionIDRequest{
		SessionID: sessionID,
		UserIP:    userIP,
		Host:      host,
	}).Return(nil, err)

	authInfo, err := suite.authenticationBackend.Authenticate(
		suite.withLoggerCtx,
		&dependencies.AuthParams{
			OAuthToken:      nil,
			SessionIDCookie: ptr.String(sessionID),
			Host:            host,
			UserIP:          userIP,
		},
	)

	suite.Require().Error(err)
	var targetErr *dependencies.UnauthorizedError
	suite.Require().True(errors.As(err, &targetErr), fmt.Sprintf("%#v", err))
	suite.Require().Nil(authInfo)
}

func (suite *BlackboxSessionIDBackendTestSuite) TestStatusErrorToUnauthorizedError() {
	suite.testBlackboxErrorToUnauthorizedError(makeBlackboxStatusError())
}

func (suite *BlackboxSessionIDBackendTestSuite) TestUnauthorizedErrorToUnauthorizedError() {
	suite.testBlackboxErrorToUnauthorizedError(makeBlackboxUnauthorizedError())
}

func (suite *BlackboxSessionIDBackendTestSuite) TestOtherError() {
	otherErr := errors.New("other error type")

	suite.mockClient.EXPECT().SessionID(gomock.Any(), blackbox.SessionIDRequest{
		SessionID: sessionID,
		UserIP:    userIP,
		Host:      host,
	}).Return(nil, otherErr)

	authInfo, err := suite.authenticationBackend.Authenticate(
		suite.withLoggerCtx,
		&dependencies.AuthParams{
			OAuthToken:      nil,
			SessionIDCookie: ptr.String(sessionID),
			Host:            host,
			UserIP:          userIP,
		},
	)

	suite.Require().Error(err)
	suite.Require().Nil(authInfo)
}

func TestBlackboxSessionIDBackend(t *testing.T) {
	suite.Run(t, new(BlackboxSessionIDBackendTestSuite))
}

type BlackboxOAuthBackendTestSuite struct {
	baseBlackboxTestSuite
	authenticationBackend dependencies.AuthenticationBackend
}

func (suite *BlackboxOAuthBackendTestSuite) SetupTest() {
	suite.baseBlackboxTestSuite.SetupTest()
	authenticationBackend, err := NewBlackboxOAuthBackend(suite.mockClient)
	suite.Require().NoError(err)
	suite.authenticationBackend = authenticationBackend
}

func (suite *BlackboxOAuthBackendTestSuite) TestSuccess() {
	suite.mockClient.EXPECT().OAuth(gomock.Any(), blackbox.OAuthRequest{
		OAuthToken: oAuthToken,
		UserIP:     userIP,
	}).Return(&blackbox.OAuthResponse{
		User: makeUser(uid, login),
	}, nil)

	expectedAuthInfo := &dependencies.AuthInfo{
		SID:      uid,
		UserName: login,
	}

	authInfo, err := suite.authenticationBackend.Authenticate(
		suite.withLoggerCtx,
		&dependencies.AuthParams{
			OAuthToken:      ptr.String(oAuthToken),
			SessionIDCookie: nil,
			Host:            host,
			UserIP:          userIP,
		},
	)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedAuthInfo, authInfo)
}

func (suite *BlackboxOAuthBackendTestSuite) TestEmptyOAuth() {
	authInfo, err := suite.authenticationBackend.Authenticate(
		context.Background(),
		&dependencies.AuthParams{
			OAuthToken:      nil,
			SessionIDCookie: ptr.String(sessionID),
			Host:            host,
			UserIP:          userIP,
		},
	)
	suite.Require().NoError(err)
	suite.Require().Nil(authInfo)
}

func (suite *BlackboxOAuthBackendTestSuite) testBlackboxErrorToUnauthorizedError(err error) {
	suite.mockClient.EXPECT().OAuth(gomock.Any(), blackbox.OAuthRequest{
		OAuthToken: oAuthToken,
		UserIP:     userIP,
	}).Return(nil, err)

	authInfo, err := suite.authenticationBackend.Authenticate(
		suite.withLoggerCtx,
		&dependencies.AuthParams{
			OAuthToken:      ptr.String(oAuthToken),
			SessionIDCookie: nil,
			Host:            "host",
			UserIP:          userIP,
		},
	)

	suite.Require().Error(err)
	var targetErr *dependencies.UnauthorizedError
	suite.Require().True(errors.As(err, &targetErr), fmt.Sprintf("%#v", err))
	suite.Require().Nil(authInfo)
}

func (suite *BlackboxOAuthBackendTestSuite) TestStatusErrorToUnauthorizedError() {
	suite.testBlackboxErrorToUnauthorizedError(makeBlackboxStatusError())
}

func (suite *BlackboxOAuthBackendTestSuite) TestUnauthorizedErrorToUnauthorizedError() {
	suite.testBlackboxErrorToUnauthorizedError(makeBlackboxUnauthorizedError())
}

func (suite *BlackboxOAuthBackendTestSuite) TestOtherError() {
	otherErr := errors.New("other error type")

	suite.mockClient.EXPECT().OAuth(gomock.Any(), blackbox.OAuthRequest{
		OAuthToken: oAuthToken,
		UserIP:     userIP,
	}).Return(nil, otherErr)

	authInfo, err := suite.authenticationBackend.Authenticate(
		suite.withLoggerCtx,
		&dependencies.AuthParams{
			OAuthToken:      ptr.String(oAuthToken),
			SessionIDCookie: nil,
			Host:            host,
			UserIP:          userIP,
		},
	)

	suite.Require().Error(err)
	suite.Require().Nil(authInfo)
}

func TestBlackboxOAuthBackendTestSuite(t *testing.T) {
	suite.Run(t, new(BlackboxOAuthBackendTestSuite))
}
