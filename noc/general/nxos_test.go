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

type NXOSTestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	logger log.Logger
}

func (suite *NXOSTestSuite) SetupSuite() {
	suite.logger = &zap.Logger{L: zaptest.NewLogger(suite.T())}
}

func (suite *NXOSTestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
}

func makeCiscoNXOS6Output() map[string]string {
	return map[string]string{
		"show version": showVersionNX6,
	}
}

func makeCiscoNXOS7Output() map[string]string {
	return map[string]string{
		"show version": showVersionNX7,
	}
}

func (suite *NXOSTestSuite) TestSuccessRecognizeNXOS6() {
	expectedSoft := NXOS6versionSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "nxos4",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeCiscoNXOS6Output()
	rec, err := recognizers.RecognizeCiscoNXOS("nxos4", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func (suite *NXOSTestSuite) TestSuccessRecognizeNXOS7() {
	expectedSoft := NXOS7versionSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "nxos4",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeCiscoNXOS7Output()
	rec, err := recognizers.RecognizeCiscoNXOS("nxos4", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func TestNXOSTestSuite(t *testing.T) {
	suite.Run(t, new(NXOSTestSuite))
}

var showVersionNX6 = `# sh ver
Cisco Nexus Operating System (NX-OS) Software
TAC support: http://www.cisco.com/tac
Documents: http://www.cisco.com/en/US/products/ps9372/tsd_products_support_series_home.html
Copyright (c) 2002-2016, Cisco Systems, Inc. All rights reserved.
The copyrights to certain works contained herein are owned by
other third parties and are used and distributed under license.
Some parts of this software are covered under the GNU Public
License. A copy of the license is available at
http://www.gnu.org/licenses/gpl.html.

Software
  BIOS:      version 1.7.0
  loader:    version N/A
  kickstart: version 6.0(2)U6(7)
  system:    version 6.0(2)U6(7)
  Power Sequencer Firmware: 
             Module 1: version v1.1
  BIOS compile time:       06/23/2014
  kickstart image file is: bootflash:///n3000-uk9-kickstart.6.0.2.U6.7.bin
  kickstart compile time:  7/28/2016 9:00:00 [07/28/2016 19:40:23]
  system image file is:    bootflash:///n3000-uk9.6.0.2.U6.7.bin
  system compile time:     7/28/2016 9:00:00 [07/28/2016 20:12:38]
`

var showVersionNX7 = `# sh ver
Cisco Nexus Operating System (NX-OS) Software
TAC support: http://www.cisco.com/tac
Copyright (C) 2002-2020, Cisco and/or its affiliates.
All rights reserved.
The copyrights to certain works contained in this software are
owned by other third parties and used and distributed under their own
licenses, such as open source.  This software is provided "as is," and unless
otherwise stated, there is no warranty, express or implied, including but not
limited to warranties of merchantability and fitness for a particular purpose.
Certain components of this software are licensed under
the GNU General Public License (GPL) version 2.0 or 
GNU General Public License (GPL) version 3.0  or the GNU
Lesser General Public License (LGPL) Version 2.1 or 
Lesser General Public License (LGPL) Version 2.0. 
A copy of each such license is available at
http://www.opensource.org/licenses/gpl-2.0.php and
http://opensource.org/licenses/gpl-3.0.html and
http://www.opensource.org/licenses/lgpl-2.1.php and
http://www.gnu.org/licenses/old-licenses/library.txt.

Software
  BIOS: version 5.3.1
  NXOS: version 7.0(3)I7(8)
  BIOS compile time:  05/17/2019
  NXOS image file is: bootflash:///nxos.7.0.3.I7.8.bin
  NXOS compile time:  3/3/2020 20:00:00 [03/04/2020 06:49:49]
`

var NXOS6versionSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Cisco_NX-OS_6.0/6.0.2.U6.7.yaml",
	Type: ptr.String("nxos4"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("n3000-uk9.6.0.2.U6.7.bin"),
			Type:     ptr.String("main"),
			Version:  ptr.String("6.0(2)U6(7)"),
		},
		{
			FileName: ptr.String("n3000-uk9-kickstart.6.0.2.U6.7.bin"),
			Type:     ptr.String("kickstart"),
			Version:  ptr.String("6.0(2)U6(7)"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("n3000-uk9.6.0.2.U6.7.bin")):                {},
		recognizers.MakeMapKey("kickstart", strings.ToLower("n3000-uk9-kickstart.6.0.2.U6.7.bin")): {},
	},
	Deprecated: false,
}

var NXOS7versionSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Cisco_NX-OS_7.0/7.0.3.I7.8.yaml",
	Type: ptr.String("ios12"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("nxos.7.0.3.I7.8.bin"),
			Type:     ptr.String("main"),
			Version:  ptr.String("7.0(3)I7(8)"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("nxos.7.0.3.I7.8.bin")): {},
	},
	Deprecated: false,
}
