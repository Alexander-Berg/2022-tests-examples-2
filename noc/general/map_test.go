package stashmap_test

import (
	"regexp"
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/adapters/alexandria/stashmap"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
)

const (
	softid   = "Cisco_IOS_12.2/2960_lanbase/122-55.SE12.yaml"
	swtype   = "ios"
	swdepric = false
	modelre  = "C.*"
	rackcode = "{Cisco}"
)

type stashTestSuite struct {
	suite.Suite
	teststash dependencies.Stash
}

type stashInput struct {
	softID       string
	swType       string
	swDeprecated bool
	modelRE      string
	rackCode     string
}

func (suite *stashTestSuite) SetupSuite() {
	input := stashInput{softid, swtype, swdepric, modelre, rackcode}
	suite.teststash = makeTestStash(input)
}

func makeTestStash(input stashInput) dependencies.Stash {
	matcher := makeTestMatcher(input.modelRE, input.rackCode, input.softID)
	matchers := makeTestMatchers(matcher)

	softarc := makeTestSoft(input.softID, input.swType, input.swDeprecated)
	softmap := makeTestSoftMap(softarc, input.softID)
	return &stashmap.Stash{
		Matchers: matchers,
		Softs:    softmap,
	}
}

func makeTestStashStruct(input stashInput) stashmap.Stash {
	matcher := makeTestMatcher(input.modelRE, input.rackCode, input.softID)
	matchers := makeTestMatchers(matcher)

	softarc := makeTestSoft(input.softID, input.swType, input.swDeprecated)
	softmap := makeTestSoftMap(softarc, input.softID)
	return stashmap.Stash{
		Matchers: matchers,
		Softs:    softmap,
	}
}

func makeTestMatcher(modelRE string, rackCode string, softID string) *entities.MatcherArcadia {
	return &entities.MatcherArcadia{
		Index:    0,
		ModelRe:  regexp.MustCompile(modelRE),
		RackCode: ptr.String(rackCode),
		SoftID:   ptr.String(softID),
	}
}

func makeTestMatchers(matcher *entities.MatcherArcadia) []*entities.MatcherArcadia {
	return []*entities.MatcherArcadia{matcher}
}

func makeTestSoft(id string, swType string, swDeprecated bool) *entities.SoftArcadia {
	return &entities.SoftArcadia{
		ID:         id,
		Type:       ptr.String(swType),
		Deprecated: swDeprecated,
	}
}

func makeTestSoftMap(softArcadia *entities.SoftArcadia, softID string) entities.SoftArcadiaMap {
	return entities.SoftArcadiaMap{softID: softArcadia}
}

type GetSoftTestSuite struct {
	stashTestSuite
}

func (suite *GetSoftTestSuite) TestNotFound() {
	soft, err := suite.teststash.GetSoft("unrealSoftID")
	suite.Require().Error(err)
	suite.Require().Nil(soft)
}

func (suite *GetSoftTestSuite) TestSuccess() {
	soft, err := suite.teststash.GetSoft(softid)

	suite.Require().NoError(err)
	suite.Require().Equal(swtype, *soft.Type)
}

func TestGetSoftTestSuite(t *testing.T) {
	suite.Run(t, new(GetSoftTestSuite))
}

type ListSoftsTestSuite struct {
	stashTestSuite
}

func (suite *ListSoftsTestSuite) TestEmptyByFilter() {
	badfilter := &dependencies.ListSoftMarcusFilter{
		Type: "bad_sw_type",
	}
	softs, err := suite.teststash.ListSofts(badfilter)
	suite.Require().NoError(err)
	suite.Require().Empty(softs)
}

func (suite *ListSoftsTestSuite) TestNotEmptyByFilter() {
	filter := &dependencies.ListSoftMarcusFilter{
		Type: swtype,
	}
	softs, err := suite.teststash.ListSofts(filter)
	suite.Require().Len(softs, 1)
	suite.Require().NoError(err)
	suite.Require().NotEmpty(softs)
}

func (suite *ListSoftsTestSuite) TestSuccess() {
	softArcadia := makeTestSoft(softid, swtype, swdepric)
	softs, _ := suite.teststash.ListSofts(nil)

	suite.Require().Len(softs, 1)
	suite.Require().Equal(*softs[0], *softArcadia)
}

func TestListSoftTestSuite(t *testing.T) {
	suite.Run(t, new(ListSoftsTestSuite))
}

type GetMatcherTestSuite struct {
	stashTestSuite
}

func (suite *GetMatcherTestSuite) TestNotFound() {
	matcher, err := suite.teststash.GetMatcher(100000)
	suite.Require().Error(err)
	suite.Require().Nil(matcher)
}

func (suite *GetMatcherTestSuite) TestSuccess() {
	matcher, err := suite.teststash.GetMatcher(0)
	suite.Require().NoError(err)
	suite.Require().Equal(*matcher.SoftID, softid)
}

func TestGetMatcherTestSuite(t *testing.T) {
	suite.Run(t, new(GetMatcherTestSuite))
}

type ListMatchersTestSuite struct {
	stashTestSuite
}

func (suite *ListMatchersTestSuite) TestNotEmpty() {
	matchers, err := suite.teststash.ListMatchers()
	suite.Require().NoError(err)
	suite.Require().NotEmpty(matchers)
	suite.Require().Len(matchers, 1)
}

func TestListMatchersTestSuite(t *testing.T) {
	suite.Run(t, new(ListMatchersTestSuite))
}

/*
type MatchersSoftsConsistencyTestSuite struct {
	stashTestSuite
}

func (suite *MatchersSoftsConsistencyTestSuite) TestSuccess() {
	stash := makeTestStashStruct(stashInput{softid, swtype, swdepric, modelre, rackcode})
	err := stashmap.MatchersSoftsConsistency(stash)
	suite.Require().NoError(err)
}

func (suite *MatchersSoftsConsistencyTestSuite) TestFailed() {
	stash := makeTestStashStruct(stashInput{softid, swtype, swdepric, modelre, rackcode})
	unrealsoft := "unreal_soft"
	stash.Matchers[0].SoftID = &unrealsoft
	err := stashmap.MatchersSoftsConsistency(stash)
	suite.Require().Error(err)
}

func TestMatchersSoftsConsistencyTestSuite(t *testing.T) {
	suite.Run(t, new(MatchersSoftsConsistencyTestSuite))
}
*/
