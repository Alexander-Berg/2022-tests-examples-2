package storage_test

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
)

func makeModelInfoSample(softID string) *entities.ModelInfo {
	return &entities.ModelInfo{
		SoftID:       softID,
		Description:  generateStringPtr("description-"),
		SoftArchive:  generateStringPtr("soft-archive-"),
		PatchArchive: generateStringPtr("patch-archive-"),
		License:      generateStringPtr("license-"),
		CheckSum:     generateStringPtr("check-sum-"),
		ImageURL:     generateStringPtr("image-url-"),
	}
}

func makeModelInfoMatcherRackCodeSample(modelInfoID string, softID string) *entities.ModelInfoMatcher {
	return &entities.ModelInfoMatcher{
		SoftID:      softID,
		RackCode:    generateStringPtr("rackCode-"),
		ModelInfoID: modelInfoID,
	}
}

func makeModelInfoMatcherModelReSample(modelInfoID string, softID string) *entities.ModelInfoMatcher {
	return &entities.ModelInfoMatcher{
		SoftID:      softID,
		ModelRe:     generateRegexp("modelRe-"),
		ModelInfoID: modelInfoID,
	}
}

type baseModelInfoTestSuite struct {
	baseStorageTestSuite
	soft *entities.Soft
}

func (suite *baseModelInfoTestSuite) createModelInfo() *entities.ModelInfo {
	expectedModelInfo := makeModelInfoSample(suite.soft.ID)
	id, err := suite.storage.PostModelInfo(context.Background(), expectedModelInfo)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	expectedModelInfo.ID = id
	return expectedModelInfo
}

func (suite *baseModelInfoTestSuite) SetupTest() {
	suite.soft = suite.createSoft()
}

type PostModelInfoTestSuite struct {
	baseModelInfoTestSuite
}

func (suite *PostModelInfoTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	id, err := suite.storage.PostModelInfo(ctx, makeModelInfoSample(suite.soft.ID))

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostModelInfoTestSuite) TestSuccess() {
	modelInfo := suite.createModelInfo()

	actualModelInfo, err := suite.storage.GetModelInfo(context.Background(), modelInfo.ID)
	suite.Require().NoError(err)
	suite.Require().Equal(modelInfo, actualModelInfo)
}

func (suite *PostModelInfoTestSuite) TestSoftNotFound() {
	modelInfo := makeModelInfoSample("unexistentSoftID")
	id, err := suite.storage.PostModelInfo(context.Background(), modelInfo)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrSoftNotFound))
	suite.Require().Empty(id)
}

func TestPostModelInfoTestSuite(t *testing.T) {
	suite.Run(t, new(PostModelInfoTestSuite))
}

type GetModelInfoTestSuite struct {
	baseModelInfoTestSuite
}

func (suite *GetModelInfoTestSuite) TestNotFound() {
	modelInfo, err := suite.storage.GetModelInfo(context.Background(), "unexistentModelInfoID")
	suite.Require().NoError(err)
	suite.Require().Nil(modelInfo)
}

func (suite *GetModelInfoTestSuite) TestSuccess() {
	expectedModelInfo := suite.createModelInfo()

	modelInfo, err := suite.storage.GetModelInfo(context.Background(), expectedModelInfo.ID)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfo, modelInfo)
}

func (suite *GetModelInfoTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	modelInfo, err := suite.storage.GetModelInfo(ctx, "modelInfoID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Nil(modelInfo)
}

func TestGetModelInfoTestSuite(t *testing.T) {
	suite.Run(t, new(GetModelInfoTestSuite))
}

type DeleteModelInfoTestSuite struct {
	baseModelInfoTestSuite
}

func (suite *DeleteModelInfoTestSuite) TestUnexistentSuccess() {
	err := suite.storage.DeleteModelInfo(context.Background(), "unexistentModelInfoID")
	suite.Require().NoError(err)
}

func (suite *DeleteModelInfoTestSuite) TestExistentSuccess() {
	expectedModelInfo := suite.createModelInfo()
	id := expectedModelInfo.ID

	modelInfo, err := suite.storage.GetModelInfo(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfo, modelInfo)

	err = suite.storage.DeleteModelInfo(context.Background(), id)
	suite.Require().NoError(err)

	modelInfo, err = suite.storage.GetModelInfo(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Nil(modelInfo)
}

func (suite *DeleteModelInfoTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	err := suite.storage.DeleteModelInfo(ctx, "modelInfoID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
}

func TestDeleteModelInfoTestSuite(t *testing.T) {
	suite.Run(t, new(DeleteModelInfoTestSuite))
}

type ListModelInfoTestSuite struct {
	baseModelInfoTestSuite
}

func (suite *ListModelInfoTestSuite) TestEmpty() {
	modelInfos, err := suite.storage.ListModelInfo(context.Background(), nil)
	suite.Require().NoError(err)
	suite.Require().Empty(modelInfos)
}

func (suite *ListModelInfoTestSuite) TestMany() {
	expectedModelInfo := suite.createModelInfo()

	expectedModelInfos := []*entities.ModelInfo{expectedModelInfo}

	modelInfos, err := suite.storage.ListModelInfo(context.Background(), nil)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfos, modelInfos)
}

func (suite *ListModelInfoTestSuite) TestIDsFilter() {
	suite.createModelInfo()
	expectedModelInfo2 := suite.createModelInfo()
	expectedModelInfos := []*entities.ModelInfo{expectedModelInfo2}

	modelInfos, err := suite.storage.ListModelInfo(
		context.Background(),
		&dependencies.ListModelInfoFilter{IDs: []string{expectedModelInfo2.ID}},
	)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfos, modelInfos)
}

func (suite *ListModelInfoTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	modelInfos, err := suite.storage.ListModelInfo(ctx, nil)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(modelInfos)
}

func TestListModelInfoTestSuite(t *testing.T) {
	suite.Run(t, new(ListModelInfoTestSuite))
}

type baseModelInfoMatcherTestSuite struct {
	baseModelInfoTestSuite
	modelInfo                       *entities.ModelInfo
	modelInfoMatcherSampleGenerator func(modelInfoID string, softID string) *entities.ModelInfoMatcher
}

func (suite *baseModelInfoMatcherTestSuite) SetupTest() {
	suite.baseModelInfoTestSuite.SetupTest()
	suite.modelInfo = suite.createModelInfo()
}

type PostModelInfoMatcherTestSuite struct {
	baseModelInfoMatcherTestSuite
}

func (suite *PostModelInfoMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	id, err := suite.storage.PostModelInfoMatcher(
		ctx,
		suite.modelInfoMatcherSampleGenerator("modelInfoID", suite.soft.ID),
	)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostModelInfoMatcherTestSuite) TestModelInfoNotFound() {
	modelInfoMatcher := suite.modelInfoMatcherSampleGenerator("modelInfoID", "softID")
	id, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrModelInfoNotFound), err.Error())
	suite.Require().Empty(id)
}

// TODO: TestNonUniqueModelInfoMatcher?

func (suite *PostModelInfoMatcherTestSuite) TestSuccess() {
	modelInfoMatcher := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	modelInfoMatcher.ID = id

	actualModelInfoMatcher, err := suite.storage.GetModelInfoMatcher(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Equal(modelInfoMatcher, actualModelInfoMatcher)
}

func (suite *PostModelInfoMatcherTestSuite) TestInsertAtEnd() {
	modelInfoMatcher1 := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id1, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher1)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id1)
	modelInfoMatcher1.ID = id1

	modelInfoMatcher2 := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id2, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher2)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id2)
	modelInfoMatcher2.ID = id2

	expectedModelInfoMatchers := []*entities.ModelInfoMatcher{modelInfoMatcher1, modelInfoMatcher2}

	ModelInfoMatchers, err := suite.storage.ListModelInfoMatcher(context.Background(), &dependencies.ListModelInfoMatcherFilter{})
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatchers, ModelInfoMatchers)
}

func (suite *PostModelInfoMatcherTestSuite) TestInsertAtBegin() {
	modelInfoMatcher1 := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id1, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher1)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id1)
	modelInfoMatcher1.ID = id1

	modelInfoMatcher2 := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	modelInfoMatcher2.NextID = ptr.String(modelInfoMatcher1.ID)
	id2, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher2)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id2)
	modelInfoMatcher2.ID = id2
	modelInfoMatcher2.NextID = nil

	expectedModelInfoMatchers := []*entities.ModelInfoMatcher{modelInfoMatcher2, modelInfoMatcher1}

	ModelInfoMatchers, err := suite.storage.ListModelInfoMatcher(context.Background(), &dependencies.ListModelInfoMatcherFilter{})
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatchers, ModelInfoMatchers)
}

func (suite *PostModelInfoMatcherTestSuite) TestInsertAtMiddle() {
	modelInfoMatcher1 := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id1, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher1)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id1)
	modelInfoMatcher1.ID = id1

	modelInfoMatcher2 := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id2, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher2)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id2)
	modelInfoMatcher2.ID = id2

	modelInfoMatcher3 := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	modelInfoMatcher3.NextID = ptr.String(modelInfoMatcher2.ID)
	id3, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher3)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id3)
	modelInfoMatcher3.ID = id3
	modelInfoMatcher3.NextID = nil

	expectedModelInfoMatchers := []*entities.ModelInfoMatcher{modelInfoMatcher1, modelInfoMatcher3, modelInfoMatcher2}

	ModelInfoMatchers, err := suite.storage.ListModelInfoMatcher(context.Background(), nil)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatchers, ModelInfoMatchers)
}

func (suite *PostModelInfoMatcherTestSuite) TestNextModelInfoMatcherNotFound() {
	modelInfoMatcher := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	modelInfoMatcher.NextID = ptr.String("unexistentID")
	id, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrNextModelInfoMatcherNotFound), err.Error())
	suite.Require().Empty(id)
}

func TestPostModelInfoMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &PostModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite{modelInfoMatcherSampleGenerator: makeModelInfoMatcherRackCodeSample},
	})
}

func TestPostModelInfoMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &PostModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite{modelInfoMatcherSampleGenerator: makeModelInfoMatcherModelReSample},
	})
}

type GetModelInfoMatcherTestSuite struct {
	baseModelInfoMatcherTestSuite
}

func (suite *GetModelInfoMatcherTestSuite) TestNotFound() {
	modelInfo, err := suite.storage.GetModelInfoMatcher(context.Background(), "unexistentModelInfoMatcherID")
	suite.Require().NoError(err)
	suite.Require().Nil(modelInfo)
}

func (suite *GetModelInfoMatcherTestSuite) TestSuccess() {
	expectedModelInfoMatcher := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id, err := suite.storage.PostModelInfoMatcher(context.Background(), expectedModelInfoMatcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	expectedModelInfoMatcher.ID = id

	modelInfo, err := suite.storage.GetModelInfoMatcher(context.Background(), id)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatcher, modelInfo)
}

func (suite *GetModelInfoMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	modelInfo, err := suite.storage.GetModelInfoMatcher(ctx, "ModelInfoMatcherID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Nil(modelInfo)
}

func TestGetModelInfoMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &GetModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite{
			modelInfoMatcherSampleGenerator: makeModelInfoMatcherModelReSample,
		},
	})
}

func TestGetModelInfoMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &GetModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite{
			modelInfoMatcherSampleGenerator: makeModelInfoMatcherRackCodeSample,
		},
	})
}

type DeleteModelInfoMatcherTestSuite struct {
	baseModelInfoMatcherTestSuite
}

func (suite *DeleteModelInfoMatcherTestSuite) TestUnexistentSuccess() {
	err := suite.storage.DeleteModelInfoMatcher(context.Background(), "unexistentModelInfoID")
	suite.Require().NoError(err)
}

func (suite *DeleteModelInfoMatcherTestSuite) TestExistentSuccess() {
	expectedModelInfoMatcher := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id, err := suite.storage.PostModelInfoMatcher(context.Background(), expectedModelInfoMatcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	expectedModelInfoMatcher.ID = id

	modelInfoMatcher, err := suite.storage.GetModelInfoMatcher(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatcher, modelInfoMatcher)

	err = suite.storage.DeleteModelInfoMatcher(context.Background(), id)
	suite.Require().NoError(err)

	modelInfoMatcher, err = suite.storage.GetModelInfoMatcher(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Nil(modelInfoMatcher)
}

func (suite *DeleteModelInfoMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	err := suite.storage.DeleteModelInfoMatcher(ctx, "ModelInfoMatcherID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
}

func TestDeleteModelInfoMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &DeleteModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite: baseModelInfoMatcherTestSuite{
			modelInfoMatcherSampleGenerator: makeModelInfoMatcherModelReSample,
		},
	})
}

func TestDeleteModelInfoMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &DeleteModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite: baseModelInfoMatcherTestSuite{
			modelInfoMatcherSampleGenerator: makeModelInfoMatcherRackCodeSample,
		},
	})
}

type ListModelInfoMatcherTestSuite struct {
	baseModelInfoMatcherTestSuite
}

func (suite *ListModelInfoMatcherTestSuite) TestEmpty() {
	modelInfos, err := suite.storage.ListModelInfoMatcher(context.Background(), &dependencies.ListModelInfoMatcherFilter{})
	suite.Require().NoError(err)
	suite.Require().Empty(modelInfos)
}

func (suite *ListModelInfoMatcherTestSuite) TestMany() {
	expectedModelInfoMatcher := suite.modelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
	id, err := suite.storage.PostModelInfoMatcher(context.Background(), expectedModelInfoMatcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	expectedModelInfoMatcher.ID = id
	expectedModelInfos := []*entities.ModelInfoMatcher{expectedModelInfoMatcher}

	modelInfos, err := suite.storage.ListModelInfoMatcher(context.Background(), &dependencies.ListModelInfoMatcherFilter{})

	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfos, modelInfos)
}

func (suite *ListModelInfoMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	modelInfos, err := suite.storage.ListModelInfoMatcher(ctx, &dependencies.ListModelInfoMatcherFilter{})

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(modelInfos)
}

func TestListModelInfoMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &ListModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite: baseModelInfoMatcherTestSuite{
			modelInfoMatcherSampleGenerator: makeModelInfoMatcherModelReSample,
		},
	})
}

func TestListModelInfoMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &ListModelInfoMatcherTestSuite{
		baseModelInfoMatcherTestSuite: baseModelInfoMatcherTestSuite{
			modelInfoMatcherSampleGenerator: makeModelInfoMatcherRackCodeSample,
		},
	})
}

type ListModelInfoMatcherFilterTestSuite struct {
	baseModelInfoMatcherTestSuite
	modelReModelInfoMatchers  []*entities.ModelInfoMatcher
	rackCodeModelInfoMatchers []*entities.ModelInfoMatcher
}

func (suite *ListModelInfoMatcherFilterTestSuite) makeModelInfoMatchers(
	ModelInfoMatcherSampleGenerator func(modelInfoID string, softID string) *entities.ModelInfoMatcher,
) []*entities.ModelInfoMatcher {
	const count = 2
	result := make([]*entities.ModelInfoMatcher, 0, count)
	for i := 0; i < count; i++ {
		modelInfoMatcher := ModelInfoMatcherSampleGenerator(suite.modelInfo.ID, suite.soft.ID)
		id, err := suite.storage.PostModelInfoMatcher(context.Background(), modelInfoMatcher)
		suite.Require().NoError(err)
		modelInfoMatcher.ID = id
		result = append(result, modelInfoMatcher)
	}
	return result
}

func (suite *ListModelInfoMatcherFilterTestSuite) SetupTest() {
	suite.baseModelInfoMatcherTestSuite.SetupTest()
	suite.modelReModelInfoMatchers = suite.makeModelInfoMatchers(makeModelInfoMatcherModelReSample)
	suite.rackCodeModelInfoMatchers = suite.makeModelInfoMatchers(makeModelInfoMatcherRackCodeSample)
}

func (suite *ListModelInfoMatcherFilterTestSuite) TestOnlyRackCodeOnlyModelReTogether() {
	ModelInfoMatchers, err := suite.storage.ListModelInfoMatcher(
		context.Background(),
		&dependencies.ListModelInfoMatcherFilter{OnlyRackCode: true, OnlyModelRe: true},
	)
	suite.Require().NoError(err)
	suite.Require().Empty(ModelInfoMatchers)
}

func (suite *ListModelInfoMatcherFilterTestSuite) TestOnlyRackCode() {
	ModelInfoMatchers, err := suite.storage.ListModelInfoMatcher(
		context.Background(),
		&dependencies.ListModelInfoMatcherFilter{OnlyRackCode: true, OnlyModelRe: false},
	)
	suite.Require().NoError(err)
	suite.Require().Equal(suite.rackCodeModelInfoMatchers, ModelInfoMatchers)
}

func (suite *ListModelInfoMatcherFilterTestSuite) TestOnlyModelRe() {
	ModelInfoMatchers, err := suite.storage.ListModelInfoMatcher(
		context.Background(),
		&dependencies.ListModelInfoMatcherFilter{OnlyRackCode: false, OnlyModelRe: true},
	)
	suite.Require().NoError(err)
	suite.Require().Equal(suite.modelReModelInfoMatchers, ModelInfoMatchers)
}

func (suite *ListModelInfoMatcherFilterTestSuite) TestDisabledFilters() {
	ModelInfoMatchers, err := suite.storage.ListModelInfoMatcher(
		context.Background(),
		&dependencies.ListModelInfoMatcherFilter{OnlyRackCode: false, OnlyModelRe: false},
	)

	var expectedModelInfoMatchers []*entities.ModelInfoMatcher
	expectedModelInfoMatchers = append(expectedModelInfoMatchers, suite.modelReModelInfoMatchers...)
	expectedModelInfoMatchers = append(expectedModelInfoMatchers, suite.rackCodeModelInfoMatchers...)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedModelInfoMatchers, ModelInfoMatchers)
}

func TestListModelInfoMatcherFilterTestSuite(t *testing.T) {
	suite.Run(t, new(ListModelInfoMatcherFilterTestSuite))
}
