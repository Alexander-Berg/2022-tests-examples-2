package caesar

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
)

type baseSoftTestSuite struct {
	baseStorageTestSuite
	soft *entities.Soft
}

func (suite *baseSoftTestSuite) SetupTest() {
	suite.baseStorageTestSuite.SetupTest()
	suite.soft = makeSoft()
}

type baseAuthorizationSoftTestSuite struct {
	baseAuthorizationTestSuite
	soft *entities.Soft
}

func (suite *baseAuthorizationSoftTestSuite) SetupTest() {
	suite.baseAuthorizationTestSuite.SetupTest()
	suite.soft = makeSoft()
}

type PostSoftTestSuite struct {
	baseAuthorizationSoftTestSuite
}

func (suite *PostSoftTestSuite) TestPermissionDenied() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, nil).Once()
	soft, err := PostSoft(suite.ctx, suite.authorizationBackend, suite.storage, suite.soft, suite.logger)
	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, ErrPermissionDenied), err.Error())
	suite.Require().Nil(soft)
}

func (suite *PostSoftTestSuite) TestAuthorizationBackendError() {
	authorizationBackendErr := errors.New("authorization backend error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, authorizationBackendErr).Once()
	soft, err := PostSoft(suite.ctx, suite.authorizationBackend, suite.storage, suite.soft, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, authorizationBackendErr), err.Error())
	suite.Require().Nil(soft)
}

func (suite *PostSoftTestSuite) TestSuccess() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	expectedSoft := *suite.soft
	expectedSoft.ID = testSoftID

	suite.storage.On("PostSoft", mock.Anything, suite.soft).Return(testSoftID, nil).Once()

	soft, err := PostSoft(suite.ctx, suite.authorizationBackend, suite.storage, suite.soft, suite.logger)
	suite.Require().NoError(err)
	suite.Require().Equal(&expectedSoft, soft)
}

func (suite *PostSoftTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	suite.storage.On("PostSoft", mock.Anything, suite.soft).Return("", storageErr).Once()

	soft, err := PostSoft(suite.ctx, suite.authorizationBackend, suite.storage, suite.soft, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(soft)
}

func TestPostSoftTestSuite(t *testing.T) {
	suite.Run(t, new(PostSoftTestSuite))
}

type GetSoftTestSuite struct {
	baseSoftTestSuite
}

func (suite *GetSoftTestSuite) TestSuccess() {
	expectedSoft := *suite.soft

	suite.storage.On("GetSoft", mock.Anything, suite.soft.ID).Return(suite.soft, nil).Once()

	soft, err := GetSoft(suite.ctx, suite.storage, suite.soft.ID)
	suite.Require().NoError(err)
	suite.Require().Equal(&expectedSoft, soft)
}

func (suite *GetSoftTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")

	suite.storage.On("GetSoft", mock.Anything, testSoftID).Return(nil, storageErr).Once()

	soft, err := GetSoft(suite.ctx, suite.storage, testSoftID)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(soft)
}

func TestGetSoftTestSuite(t *testing.T) {
	suite.Run(t, new(GetSoftTestSuite))
}

type DeleteSoftTestSuite struct {
	baseAuthorizationSoftTestSuite
}

func (suite *DeleteSoftTestSuite) TestPermissionDenied() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, nil).Once()
	err := DeleteSoft(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, ErrPermissionDenied), err.Error())
}

func (suite *DeleteSoftTestSuite) TestAuthorizationBackendError() {
	authorizationBackendErr := errors.New("authorization backend error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(false, authorizationBackendErr).Once()
	err := DeleteSoft(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, authorizationBackendErr), err.Error())
}

func (suite *DeleteSoftTestSuite) TestSuccess() {
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	suite.storage.On("DeleteSoft", mock.Anything, testSoftID).Return(nil).Once()

	err := DeleteSoft(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)
	suite.Require().NoError(err)
}

func (suite *DeleteSoftTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")
	suite.authorizationBackend.On("Authorize", mock.Anything, suite.authInfo).Return(true, nil).Once()

	suite.storage.On("DeleteSoft", mock.Anything, testSoftID).Return(storageErr).Once()

	err := DeleteSoft(suite.ctx, suite.authorizationBackend, suite.storage, testSoftID, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
}

func TestDeleteSoftTestSuite(t *testing.T) {
	suite.Run(t, new(DeleteSoftTestSuite))
}

type ListSoftTestSuite struct {
	baseSoftTestSuite
}

func (suite *ListSoftTestSuite) TestSuccessEmpty() {
	var filter *dependencies.ListSoftFilter
	suite.storage.On("ListSoft", mock.Anything, filter).Return([]*entities.Soft{}, nil).Once()

	softs, err := ListSoft(suite.ctx, suite.storage, filter)
	suite.Require().NoError(err)
	suite.Require().Empty(softs)
}

func (suite *ListSoftTestSuite) TestSuccessMany() {
	expectedSofts := []*entities.Soft{suite.soft}
	var filter *dependencies.ListSoftFilter
	suite.storage.On("ListSoft", mock.Anything, filter).Return(expectedSofts, nil).Once()

	softs, err := ListSoft(suite.ctx, suite.storage, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedSofts, softs)
}

func (suite *ListSoftTestSuite) TestStorageError() {
	storageErr := errors.New("storage error")

	var filter *dependencies.ListSoftFilter
	suite.storage.On("ListSoft", mock.Anything, filter).Return(nil, storageErr).Once()

	softs, err := ListSoft(suite.ctx, suite.storage, filter)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(softs)
}

func TestListSoftTestSuite(t *testing.T) {
	suite.Run(t, new(ListSoftTestSuite))
}
