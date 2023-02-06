package main

import (
	"embed"
	"io/fs"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/stretchr/testify/suite"
)

const (
	softid   = "Cisco_IOS_12.2/2960_lanbase/122-55.SE12.yaml"
	swtype   = "flat"
	modelre  = "C.*"
	rackcode = "{Cisco}"
)

type stashTestSuite struct {
	suite.Suite
}

type NewStashTestSuite struct {
	stashTestSuite
	softid   string
	swtype   string
	modelre  string
	rackcode string
	empty    string
	any      string
}

func (suite *NewStashTestSuite) SetupSuite() {
	suite.softid = "Cisco_IOS_12.2/2960_lanbase/122-55.SE12.yaml"
	suite.swtype = "flat"
	suite.modelre = "C.*"
	suite.rackcode = "{Cisco}"
	suite.empty = ""
	suite.any = ".*"
}

func makeMatchersRawTest(modelRE *string, rackCode *string, softID *string) MatchersRaw {
	return MatchersRaw{
		{
			Index:    0,
			ModelRe:  modelRE,
			RackCode: rackCode,
			SoftID:   softID,
		},
	}
}

func makeSoftsRawTest(softID string, swType *string) SoftRaw {
	return SoftRaw{
		ID:   softID,
		Type: swType,
	}
}

func (suite *NewStashTestSuite) TestlistMatchersFailedLen() {
	matchers := make(MatchersRaw, 0, 1)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawSuccess() {
	matchers := makeMatchersRawTest(&suite.modelre, &suite.rackcode, &suite.softid)
	err := checkMatchersRaw(matchers)

	suite.Require().NoError(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawFailedEmtyModelRe() {
	matchers := makeMatchersRawTest(&suite.empty, &suite.rackcode, &suite.softid)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawFailedNilModelRe() {
	matchers := makeMatchersRawTest(nil, &suite.rackcode, &suite.softid)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawFailedBadModelRe() {
	bad := "+++"
	matchers := makeMatchersRawTest(&bad, &suite.rackcode, &suite.softid)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawFailedContentFst() {
	matchers := makeMatchersRawTest(&suite.any, nil, &suite.softid)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawFailedContentSnd() {
	matchers := makeMatchersRawTest(&suite.any, &suite.empty, &suite.softid)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawFailedEmptySoft() {
	matchers := makeMatchersRawTest(&suite.modelre, &suite.rackcode, &suite.empty)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckMatchersRawFailedNilSoft() {
	matchers := makeMatchersRawTest(&suite.modelre, &suite.rackcode, nil)
	err := checkMatchersRaw(matchers)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckSoftRawFailedLen() {
	softs := SoftRaw{}
	err := checkSoftRaw(softs)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckSoftRawFailedID() {
	softs := makeSoftsRawTest("", &suite.swtype)
	err := checkSoftRaw(softs)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckSoftRawFailedTypeValue() {
	softs := makeSoftsRawTest(suite.softid, &suite.empty)
	err := checkSoftRaw(softs)

	suite.Require().Error(err)
}

func (suite *NewStashTestSuite) TestcheckSoftRawFailedTypeNil() {
	softs := makeSoftsRawTest(suite.softid, nil)
	err := checkSoftRaw(softs)

	suite.Require().Error(err)
}

func TestNewStashTestSuite(t *testing.T) {
	suite.Run(t, new(NewStashTestSuite))
}

//go:embed gotest/source_test
var embedfstest embed.FS

func TestEmbedFSWalk(t *testing.T) {

	contentDir := "gotest/source_test"
	pathes := SoftDirs{}
	targetFS, err := fs.Sub(embedfstest, contentDir)

	require.NoError(t, err)
	errWalk := fs.WalkDir(targetFS, ".", pathes.FindSofts)
	require.NoError(t, errWalk)
	require.Equal(t, "Cisco_IOS_12.2/2960_lanlitek/150-2.SE11.yaml", pathes[0])
	require.Equal(t, 1, len(pathes))
}
