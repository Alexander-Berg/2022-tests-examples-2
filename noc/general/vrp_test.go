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

type VRPTestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	logger log.Logger
}

func (suite *VRPTestSuite) SetupSuite() {
	suite.logger = &zap.Logger{L: zaptest.NewLogger(suite.T())}
}

func (suite *VRPTestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
}

func makeHuweiVRP85Output() map[string]string {
	return map[string]string{
		"display version":    displayVer85,
		"display patch-info": displayPatchInfo85,
		"dir":                dirVerVRP85,
	}
}

func makeHuweiVRP55Output() map[string]string {
	return map[string]string{
		"display version":    displayVer55,
		"display patch-info": displayPatchInfo55,
		"dir":                dirVer55,
	}
}

func (suite *VRPTestSuite) TestSuccessRecognizeVRP85() {
	expectedSoft := vrp85versionAndPatch
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "vrp85",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeHuweiVRP85Output()
	rec, err := recognizers.RecognizeVRP("vrp85", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func (suite *VRPTestSuite) TestSuccessRecognizeVRP55() {
	expectedSoft := vrp55versionAndPatch
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "vrp55",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeHuweiVRP55Output()
	rec, err := recognizers.RecognizeVRP("vrp55", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().NotNil(rec.ParsedSoft)
}

func TestVRPTestSuite(t *testing.T) {
	suite.Run(t, new(VRPTestSuite))
}

// "display version"
var displayVer85 string = `
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.191 (CE6865EI V200R019C10SPC800)
Copyright (C) 2012-2020 Huawei Technologies Co., Ltd.
HUAWEI CE6865-48S8CQ-EI uptime is 607 days, 19 hours, 10 minutes 
Patch Version: V200R019SPH012

CE6865-48S8CQ-EI(Master) 1 : uptime is  607 days, 19 hours, 9 minutes
        StartupTime 2020/06/30   16:51:26+03:00
Memory    Size    : 4096 M bytes
Flash     Size    : 2048 M bytes
CE6865-48S8CQ-EI version information                               
1. PCB    Version : CEM48S8CQP04 VER A
2. MAB    Version : 1
3. Board  Type    : CE6865-48S8CQ-EI
4. CPLD1  Version : 102
5. CPLD2  Version : 102
6. BIOS   Version : 205
`

// "display patch-info"
var displayPatchInfo85 string = `
Patch Package Name    :flash:/CE6865EI-V200R019SPH012.PAT
Patch Package Version :V200R019SPH012
Patch Package State   :Running   
Patch Package Run Time:2021-09-28 10:48:20+03:00
`

// "dir"
var dirVerVRP85 string = `
Directory of flash:/

  Idx  Attr     Size(Byte)  Date        Time       FileName                     
    0  dr-x              -  Feb 09 2022 11:33:31   $_checkpoint                                   
    6  -rw-    208,761,524  Jun 26 2020 15:35:49   CE6865EI-V200R019C10SPC800.cc
    7  -rw-      6,811,857  Sep 28 2021 10:47:57   CE6865EI-V200R019SPH012.PAT  
    8  drwx              -  Feb 28 2022 06:24:58   KPISTAT                      
    9  drwx              -  Nov 14 2019 12:49:50   POST                              
   16  -rw-          7,862  Apr 29 2020 04:32:39   ztp_20200429013218.log.1     

1,002,816 KB total (698,972 KB free)
`

// bad "dir" 85
var huDirWrong string = `
Directory of flash:/

  Idx  Attr     Size(Byte)  Date        Time       FileName                                    
    5  dr-x              -  Jun 30 2020 16:52:39   $_system                     
    6  -rw-    208,761,524  Jun 26 2020 15:35:49   CE6865EI-V200R019C10SPC801.cc
    7  -rw-      6,811,857  Sep 28 2021 10:47:57   CE6865EI-V200R019SPH012.PAT  
    8  drwx              -  Feb 28 2022 06:24:58   KPISTAT                      


1,002,816 KB total (698,972 KB free)
`

// bad vesion85
var displayVerWrong string = `
Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.191 (CE6865EI V200R019C10SPC801)
Copyright (C) 2012-2020 Huawei Technologies Co., Ltd.
`

var dirVer55 string = `
Directory of flash:/

  Idx  Attr     Size(Byte)  Date        Time       FileName 
    0  -rw-          1,737  Oct 01 2008 00:01:46   private-data.txt
    1  -rw-            836  Oct 01 2008 00:02:26   rr.dat
    2  -rw-            836  Oct 01 2008 00:02:26   rr.bak
    3  -rw-             36  Oct 04 2008 08:21:00   $_patchstate_reboot
    4  -rw-          6,610  Mar 28 2022 14:59:10   vrpcfg.zip
    5  -rw-          3,684  Oct 04 2008 08:21:54   $_patch_history
    6  -rw-     15,843,596  Oct 01 2008 00:34:54   s5300si-v200r005c00spc500.cc
    7  -rw-        837,945  Oct 04 2008 08:20:56   s5300si-v200r005sph021.pat`

var displayVer55 = `
Huawei Versatile Routing Platform Software
VRP (R) software, Version 5.150 (S5300 V200R005C00SPC500)
Copyright (C) 2000-2015 HUAWEI TECH CO., LTD
Quidway S5352C-SI Routing Switch uptime is 66 weeks, 0 day, 4 hours, 29 minutes

CX22EMGEC 0(Master) : uptime is 66 weeks, 0 day, 4 hours, 27 minutes
256M bytes DDR Memory
32M bytes FLASH
`

var displayPatchInfo55 = `
Patch Package Name   :flash:/s5300si-v200r005sph021.pat 
Patch Package Version:V200R005SPH021
The state of the patch state file is: Running
The current state is: Running

`

var vrp85versionAndPatch *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Huawei_VRP_8.5/CE6865EI/V200R019C10SPC800_V200R019SPH012.yaml",
	Type: ptr.String("vrp85"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("CE6865EI-V200R019C10SPC800.cc"),
			Type:     ptr.String("main"),
		},
		{
			FileName: ptr.String("CE6865EI-V200R019SPH012.PAT"),
			Type:     ptr.String("patch"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("CE6865EI-V200R019C10SPC800.cc")): {},
		recognizers.MakeMapKey("patch", strings.ToLower("CE6865EI-V200R019SPH012.PAT")):  {},
	},
	Deprecated: false,
}

var vrp55versionAndPatch *entities.SoftArcadia = &entities.SoftArcadia{
	ID:   "Huawei_VRP_5.11/S5300SI/V200R005C00SPC500_V200R005SPH021.yaml",
	Type: ptr.String("vrp55"),
	Files: []entities.SoftFile{
		{
			FileName: ptr.String("S5300SI-V200R005C00SPC500.cc"),
			Type:     ptr.String("main"),
		},
		{
			FileName: ptr.String("S5300SI-V200R005SPH021.pat"),
			Type:     ptr.String("patch"),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		recognizers.MakeMapKey("main", strings.ToLower("S5300SI-V200R005C00SPC500.cc")): {},
		recognizers.MakeMapKey("patch", strings.ToLower("S5300SI-V200R005SPH021.pat")):  {},
	},
	Deprecated: false,
}
