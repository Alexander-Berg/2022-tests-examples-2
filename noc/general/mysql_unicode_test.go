package storage_test

import (
	"context"
	"regexp"
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
)

type UnicodeTestSuite struct {
	baseStorageTestSuite
}

func (suite *UnicodeTestSuite) makeUnicodeSoftSample() *entities.Soft {
	return &entities.Soft{
		Version:  "Версия",
		ParentID: nil,
	}
}

func (suite *UnicodeTestSuite) TestSoft() {
	soft := suite.makeUnicodeSoftSample()
	softID, err := suite.storage.PostSoft(context.Background(), soft)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(softID)
	soft.ID = softID

	actualSoft, err := suite.storage.GetSoft(context.Background(), softID)
	suite.Require().NoError(err)
	suite.Require().Equal(soft, actualSoft)
}

type testMatcherParams struct {
	RackCode *string
	ModelRe  *regexp.Regexp
}

func (suite *UnicodeTestSuite) testMatcher(params *testMatcherParams) {
	soft := suite.makeUnicodeSoftSample()
	softID, err := suite.storage.PostSoft(context.Background(), soft)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(softID)
	soft.ID = softID

	matcher := &entities.Matcher{
		Category: entities.MatcherCategoryDangerous,
		RackCode: params.RackCode,
		ModelRe:  params.ModelRe,
		SoftIDs:  []string{softID},
	}

	matcherID, err := suite.storage.PostMatcher(context.Background(), matcher)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(matcherID)
	matcher.ID = matcherID

	actualMatcher, err := suite.storage.GetMatcher(context.Background(), matcherID)
	suite.Require().NoError(err)
	suite.Require().Equal(matcher, actualMatcher)
}

func (suite *UnicodeTestSuite) TestRackCodeMatcher() {
	suite.testMatcher(&testMatcherParams{
		RackCode: ptr.String("Рэк-код"),
	})
}

func (suite *UnicodeTestSuite) TestModelReMatcher() {
	suite.testMatcher(&testMatcherParams{
		ModelRe: regexp.MustCompile("Регулярное выражение"),
	})
}

func TestUnicodeTestSuite(t *testing.T) {
	suite.Run(t, new(UnicodeTestSuite))
}
