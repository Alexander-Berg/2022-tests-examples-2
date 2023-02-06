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

type ArubaInstantTestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	logger log.Logger
}

func (suite *ArubaInstantTestSuite) SetupSuite() {
	suite.logger = &zap.Logger{L: zaptest.NewLogger(suite.T())}
}

func (suite *ArubaInstantTestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
}

func makeAristaAurbaInstantHerculesOutput() map[string]string {
	return map[string]string{
		"show version":       showVersionHercules,
		"show image version": showImageHercules,
	}
}

func (suite *ArubaInstantTestSuite) TestSuccessRecognizeArubaInstantHercules() {
	expectedSoft := HerculesVersion
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "aruins",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeAristaAurbaInstantHerculesOutput()
	rec, err := recognizers.RecognizeAurbaInstantCMD("aruins", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func TestArubaTestSuite(t *testing.T) {
	suite.Run(t, new(ArubaInstantTestSuite))
}

// "show version"
var showVersionHercules string = `
# show version 
Aruba Operating System Software.
ArubaOS (MODEL: 324), Version 8.9.0.1
Website: http://www.arubanetworks.com
(c) Copyright 2021 Hewlett Packard Enterprise Development LP.
Compiled on 2021-11-08 at 18:18:44 PST (build 82154) by jenkins
FIPS Mode :disabled

AP uptime is 14 weeks 5 days 11 hours 51 minutes 2 seconds
Reboot Time and Cause: AP rebooted Thu Jan 27 09:14:01 UTC 2022; CLI cmd at uptime 0D 0H 12M 41S: reload
`

// "dir"
var showImageHercules string = `
# show image version 

Primary Partition                 :1
Primary Partition Build Time      :2021-11-8 18:18:44 PST
Primary Partition Build Version   :8.9.0.1_82154 (Digitally Signed - Production Build)
Backup Partition                  :0
Backup Partition Build Time       :2021-04-7 06:31:44 UTC
Backup Partition Build Version    :8.6.0.9_79813 (Digitally Signed - Production Build)
AP Images Classes
-----------------
Class
-----
Hercules
`

var HerculesVersion *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Aruba_ArubaInstant/Hercules/8.9.0.1_82154.yaml",
	Type: ptr.String("aruins"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("ArubaInstant_Hercules_8.9.0.1_82154"),
			Type:     ptr.String("main"),
			Version:  ptr.String("8.9.0.1_82154"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("ArubaInstant_Hercules_8.9.0.1_82154")): {},
	},
	Deprecated: false,
}
