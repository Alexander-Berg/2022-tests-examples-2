package caesar

import (
	"context"
	"errors"
	"regexp"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies/mocks"
)

const (
	testModel = "testModel"
)

var (
	testModelRe  = regexp.MustCompile("^" + testModel + ".*$")
	testRackCode = "{testTag}"
)

type GetMatchByModelTestSuite struct {
	suite.Suite
	storage *mocks.Storage
	logger  log.Logger
}

type BulkMatchTestSuite struct {
	suite.Suite
	storage          *mocks.Storage
	racktablesClient *mocks.RacktablesClient
	logger           log.Logger
}

func (suite *GetMatchByModelTestSuite) SetupSuite() {
	suite.logger = makeLogger(suite.T())
}

func (suite *GetMatchByModelTestSuite) SetupTest() {
	suite.storage = &mocks.Storage{}
}

func (suite *GetMatchByModelTestSuite) TearDownTest() {
	suite.storage.AssertExpectations(suite.T())
}

func (suite *GetMatchByModelTestSuite) TestSuccessSingleMatch() {
	matchers := []*entities.Matcher{
		{
			ID:      "testMatcherID1",
			ModelRe: regexp.MustCompile("^" + testModel + ".*$"),
			SoftIDs: []string{testSoftID},
		},
		{
			ID:      "testMatcherID2",
			ModelRe: regexp.MustCompile("^$"),
			SoftIDs: []string{"testSoftID2"},
		},
	}

	expectedSofts := []*entities.Soft{makeSoft()}
	category := entities.MatcherCategoryDefault
	filter := &dependencies.ListMatcherFilter{OnlyModelRe: true, Category: category}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(matchers, nil).Once()
	suite.storage.
		On("ListSoft", mock.Anything, &dependencies.ListSoftFilter{IDs: []string{testSoftID}}).
		Return(expectedSofts, nil).
		Once()
	suite.storage.
		On("ListModelInfoMatcher", mock.Anything, &dependencies.ListModelInfoMatcherFilter{OnlyModelRe: true, SoftIDs: []string{testSoftID}}).
		Return([]*entities.ModelInfoMatcher{}, nil).
		Once()

	expectedMatch := &entities.Match{
		Matcher: matchers[0],
		Softs:   expectedSofts,
	}

	match, err := GetMatchByModel(context.Background(), suite.storage, testModel, category, suite.logger)
	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatch, match)
}

func (suite *GetMatchByModelTestSuite) TestSuccessFirstMatch() {
	matcher := &entities.Matcher{
		ID:      "testMatcherID2",
		ModelRe: regexp.MustCompile("^"),
		SoftIDs: []string{testSoftID},
	}
	matchers := []*entities.Matcher{
		{
			ID:      "testMatcherID1",
			ModelRe: regexp.MustCompile("^unmatched regexp$"),
			SoftIDs: []string{"testSoftID1"},
		},
		matcher,
		{
			ID:      "testMatcherID3",
			ModelRe: testModelRe,
			SoftIDs: []string{"testSoftID3"},
		},
	}

	expectedSofts := []*entities.Soft{makeSoft()}
	category := entities.MatcherCategoryDefault
	filter := &dependencies.ListMatcherFilter{OnlyModelRe: true, Category: category}
	expectedMatch := &entities.Match{
		Matcher: matcher,
		Softs:   expectedSofts,
	}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(matchers, nil).Once()
	suite.storage.
		On("ListSoft", mock.Anything, &dependencies.ListSoftFilter{IDs: []string{testSoftID}}).
		Return(expectedSofts, nil).
		Once()
	suite.storage.
		On("ListModelInfoMatcher", mock.Anything, &dependencies.ListModelInfoMatcherFilter{OnlyModelRe: true, SoftIDs: []string{testSoftID}}).
		Return([]*entities.ModelInfoMatcher{}, nil).
		Once()

	match, err := GetMatchByModel(context.Background(), suite.storage, testModel, category, suite.logger)

	suite.Require().NoError(err)
	suite.Require().Equal(expectedMatch, match)
}

func (suite *GetMatchByModelTestSuite) TestNotMatch() {
	matchers := []*entities.Matcher{
		{
			ID:      "testMatcherID",
			ModelRe: regexp.MustCompile("^unmatched regexp$"),
			SoftIDs: []string{testSoftID},
		},
	}

	category := entities.MatcherCategoryDefault
	filter := &dependencies.ListMatcherFilter{OnlyModelRe: true, Category: category}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(matchers, nil).Once()

	softs, err := GetMatchByModel(context.Background(), suite.storage, testModel, category, suite.logger)
	suite.Require().NoError(err)
	suite.Require().Nil(softs)
}

func (suite *GetMatchByModelTestSuite) TestSoftDeletedAfterFoundMatch() {
	matchers := []*entities.Matcher{
		{
			ID:      "testMatcherID",
			ModelRe: testModelRe,
			SoftIDs: []string{testSoftID},
		},
	}

	category := entities.MatcherCategoryDefault
	filter := &dependencies.ListMatcherFilter{OnlyModelRe: true, Category: category}

	suite.storage.On("ListMatcher", mock.Anything, filter).Return(matchers, nil).Once()
	suite.storage.
		On("ListSoft", mock.Anything, &dependencies.ListSoftFilter{IDs: []string{testSoftID}}).
		Return(nil, nil).
		Once()

	match, err := GetMatchByModel(context.Background(), suite.storage, testModel, category, suite.logger)
	suite.Require().NoError(err)
	suite.Require().Nil(match)
}

func (suite *GetMatchByModelTestSuite) TestStorageListMatcherError() {
	storageErr := errors.New("storage ListMatcher error")
	category := entities.MatcherCategoryDefault
	filter := &dependencies.ListMatcherFilter{OnlyModelRe: true, Category: category}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(nil, storageErr).Once()

	softs, err := GetMatchByModel(context.Background(), suite.storage, testModel, category, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(softs)
}

func (suite *GetMatchByModelTestSuite) TestStorageListSoftError() {
	storageErr := errors.New("storage ListSoft error")
	matchers := []*entities.Matcher{
		{
			ID:      "testMatcherID",
			ModelRe: testModelRe,
			SoftIDs: []string{testSoftID},
		},
	}

	category := entities.MatcherCategoryDefault
	filter := &dependencies.ListMatcherFilter{OnlyModelRe: true, Category: category}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(matchers, nil).Once()
	suite.storage.
		On("ListSoft", mock.Anything, &dependencies.ListSoftFilter{IDs: []string{testSoftID}}).
		Return(nil, storageErr).
		Once()

	softs, err := GetMatchByModel(context.Background(), suite.storage, testModel, category, suite.logger)

	suite.Require().Error(err)
	suite.Require().True(errors.Is(err, storageErr), err.Error())
	suite.Require().Nil(softs)
}

func TestGetMatchByModelTestSuite(t *testing.T) {
	suite.Run(t, new(GetMatchByModelTestSuite))
}

func (suite *BulkMatchTestSuite) SetupSuite() {
	suite.logger = makeLogger(suite.T())
}

func (suite *BulkMatchTestSuite) SetupTest() {
	suite.storage = &mocks.Storage{}
	suite.racktablesClient = &mocks.RacktablesClient{}
}

func (suite *BulkMatchTestSuite) TearDownTest() {
	suite.storage.AssertExpectations(suite.T())
	suite.racktablesClient.AssertExpectations(suite.T())
}

func (suite *BulkMatchTestSuite) TestMatchByRackCodeNotNilMatcher() {
	fqdns := make([]string, 0)
	objectIDs := []entities.RacktablesObjectID{188888, 288888}
	category := entities.MatcherCategoryDefault
	matchers := []*entities.Matcher{
		{
			ID:       "testMatcherID1",
			RackCode: &testRackCode,
			SoftIDs:  []string{"testSoftID"},
		},
	}

	filter := &dependencies.ListMatcherFilter{OnlyRackCode: true, Category: category}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(matchers, nil).Once()
	suite.racktablesClient.On("GetFQDNToObjectID", mock.Anything, fqdns).Return(map[string]entities.RacktablesObjectID{}, nil).Once()

	rackCodes := []string{testRackCode}
	suite.racktablesClient.On("FirstMatchIndex", mock.Anything, 188888, rackCodes).Return(0, nil).Once()
	suite.racktablesClient.On("FirstMatchIndex", mock.Anything, 288888, rackCodes).Return(-1, nil).Once()

	expectedMatcher := matchers[0]

	fqdnToMatcher, objectIDToMatcher, _ := bulkMatchByRackCode(
		context.Background(),
		suite.storage,
		suite.racktablesClient,
		fqdns,
		objectIDs,
		category,
		suite.logger,
	)

	suite.Assert().Equal(expectedMatcher, objectIDToMatcher[188888])
	suite.Assert().NotContains(objectIDToMatcher, 288888)
	suite.Assert().Empty(fqdnToMatcher)
}

func (suite *BulkMatchTestSuite) TestMatchByModelReNotNilMatcher() {
	matchers := []*entities.Matcher{
		{
			ID:      "testMatcherID1",
			ModelRe: regexp.MustCompile("^" + testModel + ".*$"),
		},
	}
	category := entities.MatcherCategoryDefault
	models := []string{"testModel", "neverMatchModel"}

	filter := &dependencies.ListMatcherFilter{OnlyModelRe: true, Category: category}
	suite.storage.On("ListMatcher", mock.Anything, filter).Return(matchers, nil).Once()

	expectedMatcher := matchers[0]

	modelToMatcher, _ := bulkMatchByModelRe(
		context.Background(),
		suite.storage,
		models,
		category,
		suite.logger,
	)
	suite.Assert().Equal(expectedMatcher, modelToMatcher[models[0]])
	suite.Assert().NotContains(modelToMatcher, models[1])
}

func TestBulkMatchTestSuite(t *testing.T) {
	suite.Run(t, new(BulkMatchTestSuite))
}
