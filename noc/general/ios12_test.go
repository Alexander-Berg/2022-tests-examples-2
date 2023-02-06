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

type IOS12TestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	logger log.Logger
}

func (suite *IOS12TestSuite) SetupSuite() {
	suite.logger = &zap.Logger{L: zaptest.NewLogger(suite.T())}
}

func (suite *IOS12TestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
}

func makeCiscoIOSXEOutput() map[string]string {
	return map[string]string{
		"show version": showVersionXE,
	}
}

func makeCiscoIOS15Output() map[string]string {
	return map[string]string{
		"show version": showVersion15,
	}
}

func makeCiscoIOSExpOutput() map[string]string {
	return map[string]string{
		"show version": showVersionExp,
	}
}

func makeCiscoAIROutput() map[string]string {
	return map[string]string{
		"show version": showVersionAir,
	}
}

func (suite *IOS12TestSuite) TestSuccessRecognizeIOS_XE() {
	expectedSoft := IOSXEversionSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "ios12",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeCiscoIOSXEOutput()
	rec, err := recognizers.RecognizeCiscoIOS("ios12", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func (suite *IOS12TestSuite) TestSuccessRecognizeIOS_15() {
	expectedSoft := IOS15versionSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "ios12",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeCiscoIOS15Output()
	rec, err := recognizers.RecognizeCiscoIOS("ios12", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func (suite *IOS12TestSuite) TestSuccessRecognizeIOS_exp() {
	expectedSoft := IOSEXPversionSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "ios12",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeCiscoIOSExpOutput()
	rec, err := recognizers.RecognizeCiscoIOS("ios12", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func (suite *IOS12TestSuite) TestSuccessRecognizeAIR12() {
	expectedSoft := AIR12versionSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "air12",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeCiscoAIROutput()
	rec, err := recognizers.RecognizeCiscoIOS("air12", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func TestIOS12TestSuite(t *testing.T) {
	suite.Run(t, new(IOS12TestSuite))
}

var showVersionXE = `sh ver
Cisco IOS XE Software, Version 16.06.08
Cisco IOS Software [Everest], Catalyst L3 Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 16.6.8, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2020 by Cisco Systems, Inc.
Compiled Thu 23-Apr-20 17:22 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2020 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMON
BOOTLDR: CAT3K_CAA Boot Loader (CAT3K_CAA-HBOOT-M) Version 3.56, RELEASE SOFTWARE (P)

avex-101u1 uptime is 1 year, 3 weeks, 4 days, 17 hours, 51 minutes
Uptime for this control processor is 1 year, 3 weeks, 4 days, 17 hours, 55 minutes
System returned to ROM by Reload Command at 00:39:50 MSK Fri Apr 9 2021
System restarted at 00:47:03 MSK Fri Apr 9 2021
System image file is "flash:/cat3k_caa-universalk9.16.06.08.SPA.bin"
Last reload reason: Reload Command

This product contains cryptographic features and is subject to United

`

var showVersion15 = `ben-21u6#show version
Cisco IOS Software, C2960X Software (C2960X-UNIVERSALK9-M), Version 15.2(7)E4, RELEASE SOFTWARE (fc2)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2021 by Cisco Systems, Inc.
Compiled Mon 08-Mar-21 11:26 by prod_rel_team

ROM: Bootstrap program is C2960X boot loader
BOOTLDR: C2960X Boot Loader (C2960X-HBOOT-M) Version 15.2(6r)E, RELEASE SOFTWARE (fc1)

ben-21u6 uptime is 20 weeks, 4 days, 22 hours, 5 minutes
System returned to ROM by power-on
System restarted at 01:14:16 MSK Wed Dec 8 2021
System image file is "flash:/c2960x-universalk9-mz.152-7.E4/c2960x-universalk9-mz.152-7.E4.bin"
Last reload reason: Reload command
`

var showVersionExp = `#show version
Cisco IOS Software, c7600s72033_rp Software (c7600s72033_rp-ADVENTERPRISEK9_DBG-M), Experimental Version 12.2(20110630:130157) [SP_ROUTER_SRE4 197]
Copyright (c) 1986-2011 by Cisco Systems, Inc.
Compiled Thu 14-Jul-11 19:58 by rrr
ROM: System Bootstrap, Version 12.2(17r)SX7, RELEASE SOFTWARE (fc1)
a163-sr01 uptime is 1 year, 47 weeks, 13 hours, 46 minutes
Uptime for this control processor is 1 year, 47 weeks, 10 hours, 54 minutes
System returned to ROM by reload at 23:27:23 MSK Mon Jun 20 2016 (SP by reload)
System restarted at 21:50:19 MSK Tue Jun 21 2016
System image file is "disk0:c7600s72033-adventerprisek9_dbg-mz.SP_SRE4-ES.bin"
Last reload type: Normal Reload
`

var showVersionAir = `sh ver
Cisco IOS Software, C1260 Software (AP3G1-K9W7-M), Version 12.4(25d)JA2, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2012 by Cisco Systems, Inc.
Compiled Wed 12-Sep-12 01:35 by prod_rel_team

ROM: Bootstrap program is C1260 boot loader
BOOTLDR: C1260 Boot Loader (AP3G1-BOOT-M), Version 12.4 [mpleso-ap_jmr3_0328 155]

ivainfra-w1 uptime is 1 year, 35 weeks, 3 days, 20 hours, 50 minutes
System returned to ROM by power-on
System restarted at 20:09:28 MSK Fri Aug 28 2020
System image file is "flash:/ap3g1-k9w7-mx.124-25d.JA2/ap3g1-k9w7-mx.124-25d.JA2"


This product contains cryptographic features and is subject to United
`

var IOSXEversionSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Cisco_IOS-XE_16/cat3k_caa-universalk9/16.06.08.SPA.yaml",
	Type: ptr.String("ios12"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("cat3k_caa-universalk9.16.06.08.SPA.bin"),
			Type:     ptr.String("main"),
			Version:  ptr.String("16.6.8"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("cat3k_caa-universalk9.16.06.08.SPA.bin")): {},
	},
	Deprecated: false,
}

var IOS15versionSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Cisco_IOS_15.2/c2960x-universalk9/152-7.E4.yaml",
	Type: ptr.String("ios12"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("c2960x-universalk9-mz.152-7.E4.bin"),
			Type:     ptr.String("main"),
			Version:  ptr.String("15.2(7)E4"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("c2960x-universalk9-mz.152-7.E4.bin")): {},
	},
	Deprecated: false,
}

var IOSEXPversionSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Cisco_IOS_12.2/c7600s72033-adventerprisek9/12.2(20110630:130157).yaml",
	Type: ptr.String("ios12"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("c7600s72033-adventerprisek9_dbg-mz.SP_SRE4-ES.bin"),
			Type:     ptr.String("main"),
			Version:  ptr.String("12.2(20110630:130157)"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("c7600s72033-adventerprisek9_dbg-mz.SP_SRE4-ES.bin")): {},
	},
	Deprecated: false,
}

var AIR12versionSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Cisco_IOS_aironet/w7/ap3g1/124-25d.JA2.yaml",
	Type: ptr.String("ios12"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("ap3g1-k9w7-mx.124-25d.JA2"),
			Type:     ptr.String("main"),
			Version:  ptr.String("12.4(25d)JA2"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("ap3g1-k9w7-mx.124-25d.JA2")): {},
	},
	Deprecated: false,
}
