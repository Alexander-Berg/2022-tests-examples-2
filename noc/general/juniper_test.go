package recognizers_test

import (
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

type JUNOSTestSuite struct {
	suite.Suite
	stash  *mocks.Stash
	logger log.Logger
}

func (suite *JUNOSTestSuite) SetupSuite() {
	suite.logger = &zap.Logger{L: zaptest.NewLogger(suite.T())}
}

func (suite *JUNOSTestSuite) SetupTest() {
	suite.stash = &mocks.Stash{}
}

func makeJunosQFXOutput() map[string]string {
	return map[string]string{
		"show version": showVersionQFX,
	}
}

func (suite *JUNOSTestSuite) TestSuccessRecognizeJunosQFX() {
	expectedSoft := JunosQFXversionSoft
	stashedSofts := []*entities.SoftArcadia{
		expectedSoft,
	}

	filter := dependencies.ListSoftMarcusFilter{
		Type: "jun10",
	}
	suite.stash.On("ListSofts", &filter).Return(stashedSofts, nil).Once()
	cmds := makeJunosQFXOutput()
	rec, err := recognizers.RecognizeJunos("jun10", cmds, "1234", suite.stash, suite.logger)

	suite.Require().NoError(err)
	suite.Require().NotEmpty(rec.ObjectID)
	suite.Require().Equal(expectedSoft.ID, rec.RecognizedSoft.ID)
	suite.Require().Equal(len(expectedSoft.Files), len(rec.RecognizedSoft.Files))
	suite.Require().NotNil(rec.ParsedSoft)
}

func TestJUNOSTestSuite(t *testing.T) {
	suite.Run(t, new(JUNOSTestSuite))
}

var showVersionQFX = `show version 
Hostname: sas-61d1
Model: qfx10016
Junos: 20.4R3.8 flex
JUNOS OS Kernel 64-bit FLEX [20210618.f43645e_builder_stable_11-204ab]
JUNOS OS libs [20210618.f43645e_builder_stable_11-204ab]
JUNOS OS runtime [20210618.f43645e_builder_stable_11-204ab]
JUNOS OS time zone information [20210618.f43645e_builder_stable_11-204ab]
JUNOS OS libs compat32 [20210618.f43645e_builder_stable_11-204ab]
JUNOS OS 32-bit compatibility [20210618.f43645e_builder_stable_11-204ab]
JUNOS py extensions2 [20210907.154329_builder_junos_204_r3]
JUNOS py extensions [20210907.154329_builder_junos_204_r3]
JUNOS py base2 [20210907.154329_builder_junos_204_r3]
JUNOS py base [20210907.154329_builder_junos_204_r3]
JUNOS OS vmguest [20210618.f43645e_builder_stable_11-204ab]
JUNOS OS crypto [20210618.f43645e_builder_stable_11-204ab]
JUNOS OS boot-ve files [20210618.f43645e_builder_stable_11-204ab]
JUNOS network stack and utilities [20210907.154329_builder_junos_204_r3]
JUNOS libs [20210907.154329_builder_junos_204_r3]
JUNOS libs compat32 [20210907.154329_builder_junos_204_r3]
JUNOS runtime [20210907.154329_builder_junos_204_r3]
JUNOS na telemetry [20.4R3.8]
JUNOS Web Management Platform Package [20210907.154329_builder_junos_204_r3]
JUNOS qfx modules [20210907.154329_builder_junos_204_r3]
JUNOS qfx runtime [20210907.154329_builder_junos_204_r3]
JUNOS Routing Protocol Services Daemons [20.4R3.8]
JUNOS probe utility [20210907.154329_builder_junos_204_r3]
JUNOS common platform support [20210907.154329_builder_junos_204_r3]
JUNOS qfx platform support [20210907.154329_builder_junos_204_r3]
JUNOS Openconfig [20.4R3.8]
JUNOS dcp network modules [20210907.154329_builder_junos_204_r3]
JUNOS modules [20210907.154329_builder_junos_204_r3]
JUNOS qfx Data Plane Crypto Support [20210907.154329_builder_junos_204_r3]
JUNOS daemons [20210907.154329_builder_junos_204_r3]
JUNOS qfx daemons [20210907.154329_builder_junos_204_r3]
JUNOS SDN Software Suite [20210907.154329_builder_junos_204_r3]
JUNOS Extension Toolkit [20210907.154329_builder_junos_204_r3]
JET app jpuppet [3.6.1_4.0]
JUNOS Phone-home [20210907.154329_builder_junos_204_r3]
JUNOS Packet Forwarding Engine Support (DC-PFE) [20210907.154329_builder_junos_204_r3]
JUNOS Packet Forwarding Engine Support (M/T Common) [20210907.154329_builder_junos_204_r3]
JUNOS Juniper Malware Removal Tool (JMRT) [1.0.0+20210907.154329_builder_junos_204_r3]
JUNOS J-Insight [20210907.154329_builder_junos_204_r3]
JUNOS jfirmware [20210907.154329_builder_junos_204_r3]
JUNOS Online Documentation [20210907.154329_builder_junos_204_r3]
JUNOS jail runtime [20210618.f43645e_builder_stable_11-204ab]
JET app chef [11.10.4_3.0]
JUNOS Host Software [3.14.64-rt67-WR7.0.0.26_ovp:3.1.0]
JUNOS Host qfx-10-m platform package [20.4R3.8]
JUNOS Host qfx-10-m data-plane package [20.4R3.8]
JUNOS Host qfx-10-m control-plane flex package [20.4R3.8]
JUNOS Host qfx-10-m fabric package [20.4R3.8]
JUNOS Host qfx-10-m base package [20.4R3.8]
Junos for Automation Enhancement

{master}

`

var JunosQFXversionSoft *entities.SoftArcadia = &entities.SoftArcadia{
	ID:     "JunOS_20/QFX/20.4R3.8.yaml",
	Type:   ptr.String(`jun10`),
	SWType: ptr.String(`JunOS 20`),
	Files: []entities.SoftFile{
		{
			Type:     ptr.String(`main`),
			FileName: ptr.String(`JUNOS 20.4R3.8`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS Kernel 64-bit FLEX [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS libs [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS runtime [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS time zone information [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS libs compat32 [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS 32-bit compatibility [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS py extensions2 [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS py extensions [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS py base2 [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS py base [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS vmguest [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS crypto [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS OS boot-ve files [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS network stack and utilities [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS libs [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS libs compat32 [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS runtime [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS na telemetry [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Web Management Platform Package [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS qfx modules [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS qfx runtime [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Routing Protocol Services Daemons [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS probe utility [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS common platform support [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS qfx platform support [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Openconfig [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS dcp network modules [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS modules [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS qfx Data Plane Crypto Support [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS daemons [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS qfx daemons [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS SDN Software Suite [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Extension Toolkit [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JET app jpuppet [3.6.1_4.0]`),
			Version:  ptr.String(`3.6.1_4.0`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Phone-home [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Packet Forwarding Engine Support (DC-PFE) [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Packet Forwarding Engine Support (M/T Common) [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Juniper Malware Removal Tool (JMRT) [1.0.0+20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`1.0.0+20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS J-Insight [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS jfirmware [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Online Documentation [20210907.154329_builder_junos_204_r3]`),
			Version:  ptr.String(`20210907.154329_builder_junos_204_r3`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS jail runtime [20210618.f43645e_builder_stable_11-204ab]`),
			Version:  ptr.String(`20210618.f43645e_builder_stable_11-204ab`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JET app chef [11.10.4_3.0]`),
			Version:  ptr.String(`11.10.4_3.0`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Host Software [3.14.64-rt67-WR7.0.0.26_ovp:3.1.0]`),
			Version:  ptr.String(`3.14.64-rt67-WR7.0.0.26_ovp:3.1.0`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Host qfx-10-m platform package [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Host qfx-10-m data-plane package [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Host qfx-10-m control-plane flex package [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Host qfx-10-m fabric package [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
		{
			Type:     ptr.String(`package`),
			FileName: ptr.String(`JUNOS Host qfx-10-m base package [20.4R3.8]`),
			Version:  ptr.String(`20.4R3.8`),
		},
	},
	FilesMap: map[entities.SoftFileKey]struct{}{
		{
			Type:     "main",
			FileName: "junos 20.4r3.8",
		}: {},
		{
			Type:     "package",
			FileName: "junos os kernel 64-bit flex [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os libs [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os runtime [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os time zone information [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os libs compat32 [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os 32-bit compatibility [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos py extensions2 [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos py extensions [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos py base2 [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos py base [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os vmguest [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os crypto [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos os boot-ve files [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "junos network stack and utilities [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos libs [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos libs compat32 [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos runtime [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos na telemetry [20.4r3.8]",
		}: {},
		{
			Type:     "package",
			FileName: "junos web management platform package [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos qfx modules [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos qfx runtime [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos routing protocol services daemons [20.4r3.8]",
		}: {},
		{
			Type:     "package",
			FileName: "junos probe utility [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos common platform support [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos qfx platform support [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos openconfig [20.4r3.8]",
		}: {},
		{
			Type:     "package",
			FileName: "junos dcp network modules [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos modules [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos qfx data plane crypto support [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos daemons [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos qfx daemons [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos sdn software suite [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos extension toolkit [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "jet app jpuppet [3.6.1_4.0]",
		}: {},
		{
			Type:     "package",
			FileName: "junos phone-home [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos packet forwarding engine support (dc-pfe) [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos packet forwarding engine support (m/t common) [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos juniper malware removal tool (jmrt) [1.0.0+20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos j-insight [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos jfirmware [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos online documentation [20210907.154329_builder_junos_204_r3]",
		}: {},
		{
			Type:     "package",
			FileName: "junos jail runtime [20210618.f43645e_builder_stable_11-204ab]",
		}: {},
		{
			Type:     "package",
			FileName: "jet app chef [11.10.4_3.0]",
		}: {},
		{
			Type:     "package",
			FileName: "junos host software [3.14.64-rt67-wr7.0.0.26_ovp:3.1.0]",
		}: {},
		{
			Type:     "package",
			FileName: "junos host qfx-10-m platform package [20.4r3.8]",
		}: {},
		{
			Type:     "package",
			FileName: "junos host qfx-10-m data-plane package [20.4r3.8]",
		}: {},
		{
			Type:     "package",
			FileName: "junos host qfx-10-m control-plane flex package [20.4r3.8]",
		}: {},
		{
			Type:     "package",
			FileName: "junos host qfx-10-m fabric package [20.4r3.8]",
		}: {},
		{
			Type:     "package",
			FileName: "junos host qfx-10-m base package [20.4r3.8]",
		}: {},
	},
	Deprecated: false,
}
