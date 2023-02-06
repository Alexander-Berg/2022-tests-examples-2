package recognizers_test

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/suite"
	"go.uber.org/zap/zaptest"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/alexandria/internal/entities"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/dependencies/mocks"
	"a.yandex-team.ru/noc/alexandria/internal/usecases/recognizers"
)

type EOSTestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	logger log.Logger
}

func (suite *EOSTestSuite) SetupSuite() {
	suite.logger = &zap.Logger{L: zaptest.NewLogger(suite.T())}
}

func (suite *EOSTestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
}

func makeAristaEos4Output() map[string]string {
	return map[string]string{
		"show version": showVersionEos4,
		"dir":          dirEos4,
	}
}

func (suite *EOSTestSuite) TestSuccessRecognizeEOS4() {
	expectedSoft := eos4VersionAndMagic
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "eos4",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeAristaEos4Output()
	rec, err := recognizers.RecognizeEOS("eos4", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func TestEOSTestSuite(t *testing.T) {
	suite.Run(t, new(EOSTestSuite))
}

// "show version"
var showVersionEos4 string = `
#sh ver
Arista DCS-7260CX3-64-F
Hardware version: 11.04
Serial number: SSJ18363557
Hardware MAC address: 985d.8218.3e29
System MAC address: 985d.8218.3e29

Software image version: 4.25.2F
Architecture: i686
Internal build version: 4.25.2F-20711308.4252F
Internal build ID: d314b2cb-9b28-4b3b-a39c-7d8238d8602d
`

// "dir"
var dirEos4 string = `
Directory of flash:/
       -rw-   852774748           Apr 14  2020  EOS-4.22.4M.swi
       -rw-   949208936            Nov 2  2020  EOS-4.24.3M.swi
       -rw-   976897137           Mar 22  2021  EOS-4.25.2F.swi
       -rw-   976791715           Mar 23  2021  EOS64-4.25.2F.swi
       -rw-          27           Aug 26  2019  enable3px.key

29343125504 bytes total (23544217600 bytes free)
`

var eos4VersionAndMagic *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Arista_EOS_4/4.25.2F.yaml",
	Type: ptr.String("eos4"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("EOS-4.25.2F.swi"),
			Type:     ptr.String("main"),
			Version:  ptr.String("4.25.2F"),
		},
		{
			FileName: ptr.String("enable3px.key"),
			Type:     ptr.String("magic_file"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("EOS-4.25.2F.swi")):     {},
		recognizers.MakeMapKey("magic_file", strings.ToLower("enable3px.key")): {},
	},
	Deprecated: false,
}
