package caesar

import (
	"errors"
	"regexp"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
)

func makeMatcher() *entities.Matcher {
	return &entities.Matcher{
		ID:       "testMatcherID",
		ModelRe:  regexp.MustCompile("modelRe"),
		RackCode: nil,
		SoftIDs:  []string{testSoftID},
	}
}

type baseMatcherTestSuite struct {
	baseStorageTestSuite
	matcher *entities.Matcher
}

func (suite *baseMatcherTestSuite) SetupTest() {
	suite.baseStorageTestSuite.SetupTest()
	suite.matcher = makeMatcher()
}

type baseAuthorizationMatcherTestSuite struct {
	baseAuthorizationTestSuite
	matcher *entities.Matcher
}

func (suite *baseAuthorizationMatcherTestSuite) SetupTest() {
	suite.baseAuthorizationTestSuite.SetupTest()
	suite.matcher = makeMatcher()
}

type PostMatcherTestSuite struct {
	baseAuthorizationMatcherTestSuite
}

func (suite *PostMatcherTestSuite) TestPermissionDenied() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, nil).Once()
	soft, err := PostMatcher(suite.ctx, suite.authorizationBackend, suite.storage, suite.matcher,
		suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, ErrPermissionDenied), err.Error())
	suite.Require().Nil(soft)
}

func (suite *PostMatcherTestSuite) TestAuthorizationBackendError() {
	authorizationBackendErr := errors.New("authorization backend error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, authorizationBackendErr).Once()
	soft, err := PostMatcher(suite.ctx, suite.authorizationBackend, suite.storage, suite.matcher, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, authorizationBackendErr), err.Error())
	suite.Require().Nil(soft)
}

func (suite *PostMatcherTestSuite) TestSuccess() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	expectedMatcher := *suite.matcher
	expectedMatcher.ID = testSoftID

	suite.storage.On("PostMatcher", mock.Anything, suite.matcher).Return(testSoftID, nil).Once()

	soft, err := PostMatcher(suite.ctx, suite.authorizationBackend, suite.storage, suite.matcher, suite.logger)
	suite.Require().NoError(err)
	suite.Require().Equal(&expectedMatcher, soft)
}

func (suite *PostMatcherTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	suite.storage.On("PostMatcher", mock.Anything, suite.matcher).Return("", storageErr).Once()

	soft, err := PostMatcher(suite.ctx, suite.authorizationBackend, suite.storage, suite.matcher, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(soft)
}

func TestPostMatcherTestSuite(t *testing.T) {
	suite.Run(t, new(PostMatcherTestSuite))
}

type GetMatcherTestSuite struct {
	baseMatcherTestSuite
}

func (suite *GetMatcherTestSuite) TestSuccess() {
	expectedMatcher := *suite.matcher

	suite.storage.On("GetMatcher", mock.Anything, suite.matcher.ID).Return(suite.matcher, nil).Once()

	soft, err := GetMatcher(suite.ctx, suite.storage, suite.matcher.ID)
	suite.Require().NoError(err)
	suite.Require().Equal(&expectedMatcher, soft)
}

func (suite *GetMatcherTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")

	suite.storage.On("GetMatcher", mock.Anything, testSoftID).Return(nil, storageErr).Once()

	soft, err := GetMatcher(suite.ctx, suite.storage, testSoftID)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(soft)
}

func TestGetMatcherTestSuite(t *testing.T) {
	suite.Run(t, new(GetMatcherTestSuite))
}

type DeleteMatcherTestSuite struct {
	baseAuthorizationMatcherTestSuite
}

func (suite *DeleteMatcherTestSuite) TestPermissionDenied() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, nil).Once()
	err := DeleteMatcher(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, ErrPermissionDenied), err.Error())
}

func (suite *DeleteMatcherTestSuite) TestAuthorizationBackendError() {
	authorizationBackendErr := errors.New("authorization backend error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, authorizationBackendErr).Once()
	err := DeleteMatcher(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, authorizationBackendErr), err.Error())
}

func (suite *DeleteMatcherTestSuite) TestSuccess() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	suite.storage.On("DeleteMatcher", mock.Anything, testSoftID).Return(nil).Once()

	err := DeleteMatcher(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)
	suite.Require().NoError(err)
}

func (suite *DeleteMatcherTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	suite.storage.On("DeleteMatcher", mock.Anything, testSoftID).Return(storageErr).Once()

	err := DeleteMatcher(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
}

func TestDeleteMatcherTestSuite(t *testing.T) {
	suite.Run(t, new(DeleteMatcherTestSuite))
}

type ListMatcherTestSuite struct {
	baseMatcherTestSuite
}

func (suite *ListMatcherTestSuite) TestSuccessEmpty() {
	filter := &dependencies.ListMatcherFilter{}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return([]*entities.Matcher{}, nil).Once()

	softs, err := ListMatcher(suite.ctx, suite.storage, filter)
	suite.Require().NoError(err)
	suite.Require().Empty(softs)
}

func (suite *ListMatcherTestSuite) TestSuccessMany() {
	expectedMatchers := []*entities.Matcher{suite.matcher}
	filter := &dependencies.ListMatcherFilter{}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(expectedMatchers, nil).Once()

	softs, err := ListMatcher(suite.ctx, suite.storage, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatchers, softs)
}

func (suite *ListMatcherTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")

	filter := &dependencies.ListMatcherFilter{}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(nil, storageErr).Once()

	softs, err := ListMatcher(suite.ctx, suite.storage, filter)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(softs)
}

func TestListMatcherTestSuite(t *testing.T) {
	suite.Run(t, new(ListMatcherTestSuite))
}
