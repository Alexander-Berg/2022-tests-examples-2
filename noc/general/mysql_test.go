package storage_test

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/adapters/alexandria/storage"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
)

func makeSoftSample() *entities.Soft {
	return &entities.Soft{
		Version:  generateString("version-"),
		ParentID: nil,
	}
}

func makeMatcherModelReSample(softID string) *entities.Matcher {
	return &entities.Matcher{
		Category: entities.MatcherCategoryDefault,
		ModelRe:  generateRegexp("modelRe-"),
		SoftIDs:  []string{softID},
	}
}

func makeMatcherRackCodeSample(softID string) *entities.Matcher {
	return &entities.Matcher{
		Category: entities.MatcherCategoryDefault,
		RackCode: generateStringPtr("rackCode-"),
		SoftIDs:  []string{softID},
	}
}

type baseStorageTestSuite struct {
	suite.Suite
	logger  log.Logger
	storage dependencies.Storage
}

func (suite *baseStorageTestSuite) createSoft() *entities.Soft {
	soft := makeSoftSample()
	id, err := suite.storage.PostSoft(context.Background(), soft)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	soft.ID = id

	return soft
}

func (suite *baseStorageTestSuite) SetupSuite() {
	suite.logger = makeLogger(suite.T())
	mysqlStorage, err := storage.NewMysqlStorage("mysql_user:mysql_password@tcp(localhost:3306)/racktables", suite.logger)
	suite.Require().NoError(err)
	suite.storage = mysqlStorage
}

func (suite *baseStorageTestSuite) TearDownTest() {
	suite.Require().NoError(TruncateTables())
}

type PostSoftTestSuite struct {
	baseStorageTestSuite
}

func (suite *PostSoftTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	id, err := suite.storage.PostSoft(ctx, makeSoftSample())

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostSoftTestSuite) TestSoftAlreadyExists() {
	soft := suite.createSoft()
	soft.ID = ""

	id, err := suite.storage.PostSoft(context.Background(), soft)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrSoftAlreadyExists), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostSoftTestSuite) TestSuccess() {
	parentSoft := &entities.Soft{
		Version:  "parentVersion",
		ParentID: nil,
	}
	parentID, err := suite.storage.PostSoft(context.Background(), parentSoft)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(parentID)

	soft := &entities.Soft{
		Version:  "version",
		ParentID: ptr.String(parentID),
	}
	softID, err := suite.storage.PostSoft(context.Background(), soft)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(softID)
	soft.ID = softID

	actualSoft, err := suite.storage.GetSoft(context.Background(), softID)
	suite.Require().NoError(err)
	suite.Require().Equal(soft, actualSoft)
}

func (suite *PostSoftTestSuite) TestParentIDNotFound() {
	soft := &entities.Soft{
		Version:  "version",
		ParentID: ptr.String("unexistentParentID"),
	}
	id, err := suite.storage.PostSoft(context.Background(), soft)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrParentIDNotFound))
	suite.Require().Empty(id)
}

func TestPostSoftTestSuite(t *testing.T) {
	suite.Run(t, new(PostSoftTestSuite))
}

type GetSoftTestSuite struct {
	baseStorageTestSuite
}

func (suite *GetSoftTestSuite) TestNotFound() {
	soft, err := suite.storage.GetSoft(context.Background(), "unexistentSoftID")
	suite.Require().NoError(err)
	suite.Require().Nil(soft)
}

func (suite *GetSoftTestSuite) TestSuccess() {
	expectedSoft := suite.createSoft()

	soft, err := suite.storage.GetSoft(context.Background(), expectedSoft.ID)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedSoft, soft)
}

func (suite *GetSoftTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	soft, err := suite.storage.GetSoft(ctx, "softID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Nil(soft)
}

func TestGetSoftTestSuite(t *testing.T) {
	suite.Run(t, new(GetSoftTestSuite))
}

type DeleteSoftTestSuite struct {
	baseStorageTestSuite
}

func (suite *DeleteSoftTestSuite) TestUnexistentSuccess() {
	err := suite.storage.DeleteSoft(context.Background(), "unexistentSoftID")
	suite.Require().NoError(err)
}

func (suite *DeleteSoftTestSuite) TestExistentSuccess() {
	expectedSoft := suite.createSoft()
	id := expectedSoft.ID

	soft, err := suite.storage.GetSoft(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedSoft, soft)

	err = suite.storage.DeleteSoft(context.Background(), id)
	suite.Require().NoError(err)

	soft, err = suite.storage.GetSoft(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Nil(soft)
}

func (suite *DeleteSoftTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	err := suite.storage.DeleteSoft(ctx, "softID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
}

func TestDeleteSoftTestSuite(t *testing.T) {
	suite.Run(t, new(DeleteSoftTestSuite))
}

type ListSoftTestSuite struct {
	baseStorageTestSuite
}

func (suite *ListSoftTestSuite) TestEmpty() {
	softs, err := suite.storage.ListSoft(context.Background(), nil)
	suite.Require().NoError(err)
	suite.Require().Empty(softs)
}

func (suite *ListSoftTestSuite) TestMany() {
	expectedSoft := suite.createSoft()
	expectedSofts := []*entities.Soft{expectedSoft}

	softs, err := suite.storage.ListSoft(context.Background(), nil)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedSofts, softs)
}

func (suite *ListSoftTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	softs, err := suite.storage.ListSoft(ctx, nil)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(softs)
}

func TestListSoftTestSuite(t *testing.T) {
	suite.Run(t, new(ListSoftTestSuite))
}

type baseMatcherTestSuite struct {
	baseStorageTestSuite
	soft                   *entities.Soft
	matcherSampleGenerator func(softID string) *entities.Matcher
}

func (suite *baseMatcherTestSuite) SetupTest() {
	suite.soft = suite.createSoft()
}

type PostMatcherTestSuite struct {
	baseMatcherTestSuite
}

func (suite *PostMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()

	id, err := suite.storage.PostMatcher(ctx, suite.matcherSampleGenerator("softID"))

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostMatcherTestSuite) TestSoftNotFound() {
	matcher := suite.matcherSampleGenerator("softID")
	id, err := suite.storage.PostMatcher(context.Background(), matcher)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrSoftNotFound), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostMatcherTestSuite) TestNonUniqueMatcher() {
	matcher := suite.matcherSampleGenerator(suite.soft.ID)
	id, err := suite.storage.PostMatcher(context.Background(), matcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)

	id, err = suite.storage.PostMatcher(context.Background(), matcher)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrNonUniqueMatcher), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostMatcherTestSuite) TestSuccess() {
	matcher := suite.matcherSampleGenerator(suite.soft.ID)
	id, err := suite.storage.PostMatcher(context.Background(), matcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	matcher.ID = id

	actualMatcher, err := suite.storage.GetMatcher(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Equal(matcher, actualMatcher)
}

func (suite *PostMatcherTestSuite) TestInsertAtEnd() {
	matcher1 := suite.matcherSampleGenerator(suite.soft.ID)
	id1, err := suite.storage.PostMatcher(context.Background(), matcher1)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id1)
	matcher1.ID = id1

	matcher2 := suite.matcherSampleGenerator(suite.soft.ID)
	id2, err := suite.storage.PostMatcher(context.Background(), matcher2)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id2)
	matcher2.ID = id2

	expectedMatchers := []*entities.Matcher{matcher1, matcher2}

	matchers, err := suite.storage.ListMatcher(context.Background(), nil)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatchers, matchers)
}

func (suite *PostMatcherTestSuite) TestInsertAtBegin() {
	matcher1 := suite.matcherSampleGenerator(suite.soft.ID)
	id1, err := suite.storage.PostMatcher(context.Background(), matcher1)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id1)
	matcher1.ID = id1

	matcher2 := suite.matcherSampleGenerator(suite.soft.ID)
	matcher2.NextID = ptr.String(matcher1.ID)
	id2, err := suite.storage.PostMatcher(context.Background(), matcher2)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id2)
	matcher2.ID = id2
	matcher2.NextID = nil

	expectedMatchers := []*entities.Matcher{matcher2, matcher1}

	matchers, err := suite.storage.ListMatcher(context.Background(), nil)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatchers, matchers)
}

func (suite *PostMatcherTestSuite) TestInsertAtMiddle() {
	matcher1 := suite.matcherSampleGenerator(suite.soft.ID)
	id1, err := suite.storage.PostMatcher(context.Background(), matcher1)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id1)
	matcher1.ID = id1

	matcher2 := suite.matcherSampleGenerator(suite.soft.ID)
	id2, err := suite.storage.PostMatcher(context.Background(), matcher2)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id2)
	matcher2.ID = id2

	matcher3 := suite.matcherSampleGenerator(suite.soft.ID)
	matcher3.NextID = ptr.String(matcher2.ID)
	id3, err := suite.storage.PostMatcher(context.Background(), matcher3)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id3)
	matcher3.ID = id3
	matcher3.NextID = nil

	expectedMatchers := []*entities.Matcher{matcher1, matcher3, matcher2}

	matchers, err := suite.storage.ListMatcher(context.Background(), nil)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatchers, matchers)
}

func (suite *PostMatcherTestSuite) TestCategoryNotFound() {
	matcher := suite.matcherSampleGenerator(suite.soft.ID)
	matcher.Category = "unknown category"

	id, err := suite.storage.PostMatcher(context.Background(), matcher)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrMatcherCategoryNotFound), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostMatcherTestSuite) TestMatcherCategoryLimitExceed() {
	soft := suite.createSoft()

	matcher := suite.matcherSampleGenerator(suite.soft.ID)
	// NOTE: default category has limit 1
	matcher.Category = entities.MatcherCategoryDefault
	matcher.SoftIDs = []string{suite.soft.ID, soft.ID}

	id, err := suite.storage.PostMatcher(context.Background(), matcher)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrMatcherCategoryLimitExceed), err.Error())
	suite.Require().Empty(id)
}

func (suite *PostMatcherTestSuite) TestNextMatcherNotFound() {
	matcher := suite.matcherSampleGenerator(suite.soft.ID)
	matcher.NextID = ptr.String("unexistentID")
	id, err := suite.storage.PostMatcher(context.Background(), matcher)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, dependencies.ErrNextMatcherNotFound), err.Error())
	suite.Require().Empty(id)
}

func TestPostMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &PostMatcherTestSuite{
		baseMatcherTestSuite{matcherSampleGenerator: makeMatcherRackCodeSample},
	})
}

func TestPostMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &PostMatcherTestSuite{
		baseMatcherTestSuite{matcherSampleGenerator: makeMatcherModelReSample},
	})
}

type GetMatcherTestSuite struct {
	baseMatcherTestSuite
}

func (suite *GetMatcherTestSuite) TestNotFound() {
	soft, err := suite.storage.GetMatcher(context.Background(), "unexistentMatcherID")
	suite.Require().NoError(err)
	suite.Require().Nil(soft)
}

func (suite *GetMatcherTestSuite) TestSuccess() {
	expectedMatcher := suite.matcherSampleGenerator(suite.soft.ID)
	id, err := suite.storage.PostMatcher(context.Background(), expectedMatcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	expectedMatcher.ID = id

	soft, err := suite.storage.GetMatcher(context.Background(), id)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatcher, soft)
}

func (suite *GetMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	soft, err := suite.storage.GetMatcher(ctx, "matcherID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Nil(soft)
}

func TestGetMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &GetMatcherTestSuite{
		baseMatcherTestSuite{
			matcherSampleGenerator: makeMatcherModelReSample,
		},
	})
}

func TestGetMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &GetMatcherTestSuite{
		baseMatcherTestSuite{
			matcherSampleGenerator: makeMatcherRackCodeSample,
		},
	})
}

type DeleteMatcherTestSuite struct {
	baseMatcherTestSuite
}

func (suite *DeleteMatcherTestSuite) TestUnexistentSuccess() {
	err := suite.storage.DeleteMatcher(context.Background(), "unexistentSoftID")
	suite.Require().NoError(err)
}

func (suite *DeleteMatcherTestSuite) TestExistentSuccess() {
	expectedMatcher := suite.matcherSampleGenerator(suite.soft.ID)
	id, err := suite.storage.PostMatcher(context.Background(), expectedMatcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	expectedMatcher.ID = id

	matcher, err := suite.storage.GetMatcher(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatcher, matcher)

	err = suite.storage.DeleteMatcher(context.Background(), id)
	suite.Require().NoError(err)

	matcher, err = suite.storage.GetMatcher(context.Background(), id)
	suite.Require().NoError(err)
	suite.Require().Nil(matcher)
}

func (suite *DeleteMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	err := suite.storage.DeleteMatcher(ctx, "matcherID")

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
}

func TestDeleteMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &DeleteMatcherTestSuite{
		baseMatcherTestSuite: baseMatcherTestSuite{
			matcherSampleGenerator: makeMatcherModelReSample,
		},
	})
}

func TestDeleteMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &DeleteMatcherTestSuite{
		baseMatcherTestSuite: baseMatcherTestSuite{
			matcherSampleGenerator: makeMatcherRackCodeSample,
		},
	})
}

type ListMatcherTestSuite struct {
	baseMatcherTestSuite
}

func (suite *ListMatcherTestSuite) TestEmpty() {
	softs, err := suite.storage.ListMatcher(context.Background(), nil)
	suite.Require().NoError(err)
	suite.Require().Empty(softs)
}

func (suite *ListMatcherTestSuite) TestMany() {
	expectedMatcher := suite.matcherSampleGenerator(suite.soft.ID)
	id, err := suite.storage.PostMatcher(context.Background(), expectedMatcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(id)
	expectedMatcher.ID = id
	expectedSofts := []*entities.Matcher{expectedMatcher}

	softs, err := suite.storage.ListMatcher(context.Background(), nil)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedSofts, softs)
}

func (suite *ListMatcherTestSuite) TestContextCancel() {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	softs, err := suite.storage.ListMatcher(ctx, nil)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, context.Canceled), err.Error())
	suite.Require().Empty(softs)
}

func TestListMatcherModelReTestSuite(t *testing.T) {
	suite.Run(t, &ListMatcherTestSuite{
		baseMatcherTestSuite: baseMatcherTestSuite{
			matcherSampleGenerator: makeMatcherModelReSample,
		},
	})
}

func TestListMatcherRackCodeTestSuite(t *testing.T) {
	suite.Run(t, &ListMatcherTestSuite{
		baseMatcherTestSuite: baseMatcherTestSuite{
			matcherSampleGenerator: makeMatcherRackCodeSample,
		},
	})
}

type ListMatcherFilterTestSuite struct {
	baseMatcherTestSuite
	modelReMatchers  []*entities.Matcher
	rackCodeMatchers []*entities.Matcher
}

func (suite *ListMatcherFilterTestSuite) makeMatchers(
	matcherSampleGenerator func(softID string) *entities.Matcher,
) []*entities.Matcher {
	const count = 2
	result := make([]*entities.Matcher, 0, count)
	for i := 0; i < count; i++ {
		matcher := matcherSampleGenerator(suite.soft.ID)
		id, err := suite.storage.PostMatcher(context.Background(), matcher)
		suite.Require().NoError(err)
		matcher.ID = id
		result = append(result, matcher)
	}
	return result
}

func (suite *ListMatcherFilterTestSuite) SetupTest() {
	suite.baseMatcherTestSuite.SetupTest()
	suite.modelReMatchers = suite.makeMatchers(makeMatcherModelReSample)
	suite.rackCodeMatchers = suite.makeMatchers(makeMatcherRackCodeSample)
}

func (suite *ListMatcherFilterTestSuite) TestOnlyRackCodeOnlyModelReTogether() {
	matchers, err := suite.storage.ListMatcher(
		context.Background(),
		&dependencies.ListMatcherFilter{OnlyRackCode: true, OnlyModelRe: true},
	)
	suite.Require().NoError(err)
	suite.Require().Empty(matchers)
}

func (suite *ListMatcherFilterTestSuite) TestOnlyRackCode() {
	matchers, err := suite.storage.ListMatcher(
		context.Background(),
		&dependencies.ListMatcherFilter{OnlyRackCode: true, OnlyModelRe: false},
	)
	suite.Require().NoError(err)
	suite.Require().Equal(suite.rackCodeMatchers, matchers)
}

func (suite *ListMatcherFilterTestSuite) TestOnlyModelRe() {
	matchers, err := suite.storage.ListMatcher(
		context.Background(),
		&dependencies.ListMatcherFilter{OnlyRackCode: false, OnlyModelRe: true},
	)
	suite.Require().NoError(err)
	suite.Require().Equal(suite.modelReMatchers, matchers)
}

func (suite *ListMatcherFilterTestSuite) TestDisabledFilters() {
	matchers, err := suite.storage.ListMatcher(
		context.Background(),
		&dependencies.ListMatcherFilter{OnlyRackCode: false, OnlyModelRe: false},
	)

	var expectedMatchers []*entities.Matcher
	expectedMatchers = append(expectedMatchers, suite.modelReMatchers...)
	expectedMatchers = append(expectedMatchers, suite.rackCodeMatchers...)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatchers, matchers)
}

func TestListMatcherFilterTestSuite(t *testing.T) {
	suite.Run(t, new(ListMatcherFilterTestSuite))
}
