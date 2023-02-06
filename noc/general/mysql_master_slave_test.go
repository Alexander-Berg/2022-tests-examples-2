package storage_test

import (
	"context"
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/noc/alexandria/internal/adapters/alexandria/storage"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies/mocks"
)

type baseMysqlMasterSlaveStorageTestSuite struct {
	suite.Suite
	tempDir    string
	masterFile string

	rwStorage          *mocks.Storage
	roStorage          *mocks.Storage
	mysqlMasterStorage dependencies.Storage
}

func (suite *baseMysqlMasterSlaveStorageTestSuite) SetupSuite() {
	tempDir, err := ioutil.TempDir("", "alexandria")
	suite.Require().NoError(err)
	suite.tempDir = tempDir
}

func (suite *baseMysqlMasterSlaveStorageTestSuite) TearDownSuite() {
	suite.Require().NoError(os.RemoveAll(suite.tempDir))
}

func (suite *baseMysqlMasterSlaveStorageTestSuite) SetupTest() {
	suite.rwStorage = &mocks.Storage{}
	suite.roStorage = &mocks.Storage{}
	mysqlMasterStorage, err := storage.NewMysqlMasterSlaveStorage(
		suite.rwStorage,
		suite.roStorage,
		suite.masterFile,
		makeLogger(suite.T()),
	)
	suite.Require().NoError(err)
	suite.mysqlMasterStorage = mysqlMasterStorage
}

func (suite *baseMysqlMasterSlaveStorageTestSuite) TearDownTest() {
	suite.rwStorage.AssertExpectations(suite.T())
	suite.roStorage.AssertExpectations(suite.T())
}

type MysqlMasterStorageTestSuite struct {
	baseMysqlMasterSlaveStorageTestSuite
}

func (suite *MysqlMasterStorageTestSuite) SetupSuite() {
	suite.baseMysqlMasterSlaveStorageTestSuite.SetupSuite()
	suite.masterFile = filepath.Join(suite.tempDir, "master")
	_, err := os.Create(suite.masterFile)
	suite.Require().NoError(err)
}

func (suite *MysqlMasterStorageTestSuite) TestPostSoft() {
	soft := makeSoftSample()
	ctx := context.Background()
	expectedID := "id"

	suite.rwStorage.On("PostSoft", ctx, soft).Return(expectedID, nil).Once()
	id, err := suite.mysqlMasterStorage.PostSoft(ctx, soft)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedID, id)
}

func (suite *MysqlMasterStorageTestSuite) TestGetSoft() {
	ctx := context.Background()
	id := "id"
	expectedSoft := makeSoftSample()
	expectedSoft.ID = id

	suite.roStorage.On("GetSoft", ctx, id).Return(expectedSoft, nil).Once()
	soft, err := suite.mysqlMasterStorage.GetSoft(ctx, id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedSoft, soft)
}

func (suite *MysqlMasterStorageTestSuite) TestDeleteSoft() {
	ctx := context.Background()
	id := "id"

	suite.rwStorage.On("DeleteSoft", ctx, id).Return(nil).Once()
	err := suite.mysqlMasterStorage.DeleteSoft(ctx, id)
	suite.Require().NoError(err)
}

func (suite *MysqlMasterStorageTestSuite) TestListSoft() {
	ctx := context.Background()
	expectedSofts := []*entities.Soft{
		makeSoftSample(),
	}
	filter := &dependencies.ListSoftFilter{}
	suite.roStorage.On("ListSoft", ctx, filter).Return(expectedSofts, nil).Once()
	softs, err := suite.mysqlMasterStorage.ListSoft(ctx, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedSofts, softs)
}

func (suite *MysqlMasterStorageTestSuite) TestPostMatcher() {
	matcher := makeMatcherModelReSample("softID")
	ctx := context.Background()
	expectedID := "id"

	suite.rwStorage.On("PostMatcher", ctx, matcher).Return(expectedID, nil).Once()
	id, err := suite.mysqlMasterStorage.PostMatcher(ctx, matcher)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedID, id)
}

func (suite *MysqlMasterStorageTestSuite) TestGetMatcher() {
	ctx := context.Background()
	id := "id"
	expectedMatcher := makeMatcherModelReSample("softID")
	expectedMatcher.ID = id

	suite.roStorage.On("GetMatcher", ctx, id).Return(expectedMatcher, nil).Once()
	matcher, err := suite.mysqlMasterStorage.GetMatcher(ctx, id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatcher, matcher)
}

func (suite *MysqlMasterStorageTestSuite) TestDeleteMatcher() {
	ctx := context.Background()
	id := "id"

	suite.rwStorage.On("DeleteMatcher", ctx, id).Return(nil).Once()
	err := suite.mysqlMasterStorage.DeleteMatcher(ctx, id)
	suite.Require().NoError(err)
}

func (suite *MysqlMasterStorageTestSuite) TestListMatcher() {
	ctx := context.Background()
	expectedMatchers := []*entities.Matcher{
		makeMatcherModelReSample("softID"),
	}

	filter := &dependencies.ListMatcherFilter{}

	suite.roStorage.On("ListMatcher", ctx, filter).Return(expectedMatchers, nil).Once()
	matchers, err := suite.mysqlMasterStorage.ListMatcher(ctx, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatchers, matchers)
}

func TestMysqlMasterStorageTestSuite(t *testing.T) {
	suite.Run(t, new(MysqlMasterStorageTestSuite))
}

type MysqlSlaveStorageTestSuite struct {
	baseMysqlMasterSlaveStorageTestSuite
}

func (suite *MysqlSlaveStorageTestSuite) SetupSuite() {
	suite.baseMysqlMasterSlaveStorageTestSuite.SetupSuite()
	suite.masterFile = filepath.Join(suite.tempDir, "unexistentiFile")
}

func (suite *MysqlSlaveStorageTestSuite) TestPostSoft() {
	soft := makeSoftSample()
	ctx := context.Background()
	expectedID := "id"

	suite.roStorage.On("PostSoft", ctx, soft).Return(expectedID, nil).Once()
	id, err := suite.mysqlMasterStorage.PostSoft(ctx, soft)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedID, id)
}

func (suite *MysqlSlaveStorageTestSuite) TestGetSoft() {
	ctx := context.Background()
	id := "id"
	expectedSoft := makeSoftSample()
	expectedSoft.ID = id

	suite.roStorage.On("GetSoft", ctx, id).Return(expectedSoft, nil).Once()
	soft, err := suite.mysqlMasterStorage.GetSoft(ctx, id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedSoft, soft)
}

func (suite *MysqlSlaveStorageTestSuite) TestDeleteSoft() {
	ctx := context.Background()
	id := "id"

	suite.roStorage.On("DeleteSoft", ctx, id).Return(nil).Once()
	err := suite.mysqlMasterStorage.DeleteSoft(ctx, id)
	suite.Require().NoError(err)
}

func (suite *MysqlSlaveStorageTestSuite) TestListSoft() {
	ctx := context.Background()
	expectedSofts := []*entities.Soft{
		makeSoftSample(),
	}

	filter := &dependencies.ListSoftFilter{}
	suite.roStorage.On("ListSoft", ctx, filter).Return(expectedSofts, nil).Once()
	softs, err := suite.mysqlMasterStorage.ListSoft(ctx, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedSofts, softs)
}

func (suite *MysqlSlaveStorageTestSuite) TestPostMatcher() {
	matcher := makeMatcherModelReSample("softID")
	ctx := context.Background()
	expectedID := "id"

	suite.roStorage.On("PostMatcher", ctx, matcher).Return(expectedID, nil).Once()
	id, err := suite.mysqlMasterStorage.PostMatcher(ctx, matcher)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedID, id)
}

func (suite *MysqlSlaveStorageTestSuite) TestGetMatcher() {
	ctx := context.Background()
	id := "id"
	expectedMatcher := makeMatcherModelReSample("softID")
	expectedMatcher.ID = id

	suite.roStorage.On("GetMatcher", ctx, id).Return(expectedMatcher, nil).Once()
	matcher, err := suite.mysqlMasterStorage.GetMatcher(ctx, id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatcher, matcher)
}

func (suite *MysqlSlaveStorageTestSuite) TestDeleteMatcher() {
	ctx := context.Background()
	id := "id"

	suite.roStorage.On("DeleteMatcher", ctx, id).Return(nil).Once()
	err := suite.mysqlMasterStorage.DeleteMatcher(ctx, id)
	suite.Require().NoError(err)
}

func (suite *MysqlSlaveStorageTestSuite) TestListMatcher() {
	ctx := context.Background()
	expectedMatchers := []*entities.Matcher{
		makeMatcherModelReSample("softID"),
	}

	filter := &dependencies.ListMatcherFilter{}
	suite.roStorage.On("ListMatcher", ctx, filter).Return(expectedMatchers, nil).Once()
	matchers, err := suite.mysqlMasterStorage.ListMatcher(ctx, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatchers, matchers)
}

func (suite *MysqlSlaveStorageTestSuite) TestPostModelInfo() {
	matcher := makeModelInfoSample("softID")
	ctx := context.Background()
	expectedID := "id"

	suite.roStorage.On("PostModelInfo", ctx, matcher).Return(expectedID, nil).Once()
	id, err := suite.mysqlMasterStorage.PostModelInfo(ctx, matcher)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedID, id)
}

func (suite *MysqlSlaveStorageTestSuite) TestGetModelInfo() {
	ctx := context.Background()
	id := "id"
	expectedModelInfo := makeModelInfoSample("softID")
	expectedModelInfo.ID = id

	suite.roStorage.On("GetModelInfo", ctx, id).Return(expectedModelInfo, nil).Once()
	matcher, err := suite.mysqlMasterStorage.GetModelInfo(ctx, id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfo, matcher)
}

func (suite *MysqlSlaveStorageTestSuite) TestDeleteModelInfo() {
	ctx := context.Background()
	id := "id"

	suite.roStorage.On("DeleteModelInfo", ctx, id).Return(nil).Once()
	err := suite.mysqlMasterStorage.DeleteModelInfo(ctx, id)
	suite.Require().NoError(err)
}

func (suite *MysqlSlaveStorageTestSuite) TestListModelInfo() {
	ctx := context.Background()
	expectedModelInfos := []*entities.ModelInfo{
		makeModelInfoSample("softID"),
	}

	filter := &dependencies.ListModelInfoFilter{}
	suite.roStorage.On("ListModelInfo", ctx, filter).Return(expectedModelInfos, nil).Once()
	matchers, err := suite.mysqlMasterStorage.ListModelInfo(ctx, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfos, matchers)
}

func (suite *MysqlSlaveStorageTestSuite) TestPostModelInfoMatcher() {
	matcher := makeModelInfoMatcherModelReSample("modelInfoID", "softID")
	ctx := context.Background()
	expectedID := "id"

	suite.roStorage.On("PostModelInfoMatcher", ctx, matcher).Return(expectedID, nil).Once()
	id, err := suite.mysqlMasterStorage.PostModelInfoMatcher(ctx, matcher)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedID, id)
}

func (suite *MysqlSlaveStorageTestSuite) TestGetModelInfoMatcher() {
	ctx := context.Background()
	id := "id"
	expectedModelInfoMatcher := makeModelInfoMatcherModelReSample("modelInfoID", "softID")
	expectedModelInfoMatcher.ID = id

	suite.roStorage.On("GetModelInfoMatcher", ctx, id).Return(expectedModelInfoMatcher, nil).Once()
	matcher, err := suite.mysqlMasterStorage.GetModelInfoMatcher(ctx, id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatcher, matcher)
}

func (suite *MysqlSlaveStorageTestSuite) TestDeleteModelInfoMatcher() {
	ctx := context.Background()
	id := "id"

	suite.roStorage.On("DeleteModelInfoMatcher", ctx, id).Return(nil).Once()
	err := suite.mysqlMasterStorage.DeleteModelInfoMatcher(ctx, id)
	suite.Require().NoError(err)
}

func (suite *MysqlSlaveStorageTestSuite) TestListModelInfoMatcher() {
	ctx := context.Background()
	expectedModelInfoMatchers := []*entities.ModelInfoMatcher{
		makeModelInfoMatcherModelReSample("modelInfoID", "softID"),
	}

	filter := &dependencies.ListModelInfoMatcherFilter{}
	suite.roStorage.On("ListModelInfoMatcher", ctx, filter).Return(expectedModelInfoMatchers, nil).Once()
	matchers, err := suite.mysqlMasterStorage.ListModelInfoMatcher(ctx, filter)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatchers, matchers)
}

func TestMysqlSlaveStorageTestSuite(t *testing.T) {
	suite.Run(t, new(MysqlSlaveStorageTestSuite))
}
