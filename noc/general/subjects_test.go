package objects

import (
	"fmt"
	"os"
	"testing"

	"github.com/sirupsen/logrus"

	"a.yandex-team.ru/noc/traffic/dns/junk/cc-core/cmd/config"
)

// FetchGroups implements fetchin abc group
// as http call to abc api, also we need
// configuration load here at least for abc
// endpoints and tokens

const (
	FETCHGROUPS_RESULT_OK     = 1
	FETCHGROUPS_RESULT_FAILED = 0

	TEST_CONFIG_FILE = "/home/slayer/dns2-api/dns2-api-cc-core.yaml"
)

func TestFetchGroups(t *testing.T) {

	type TTestsFetchGroups struct {
		group  string
		result int
	}

	var TestsFetchGroups = []TTestsFetchGroups{
		{"ycnetinfra_administration", FETCHGROUPS_RESULT_OK},
		{"svc_ycnetinfra_administration", FETCHGROUPS_RESULT_OK},
		{"maildelivery_administration", FETCHGROUPS_RESULT_OK},
		{"sre_vteam_development", FETCHGROUPS_RESULT_OK},
		{"dpt_yandex_infra_tech_servop", FETCHGROUPS_RESULT_FAILED},
	}

	var Subjects *Subjects
	var err error

	// Init configuration and logging
	var g config.CmdGlobal
	g = config.CmdGlobal{Opts: &config.ConfYaml{}}
	*g.Opts, err = config.LoadConf(TEST_CONFIG_FILE)

	g.Log = logrus.New()
	g.Log.Formatter = &logrus.TextFormatter{
		TimestampFormat: "2006/01/02 - 15:04:05.000",
		FullTimestamp:   true,
	}
	level, _ := logrus.ParseLevel("debug")
	g.Log.Level = level
	g.Log.Out = os.Stdout

	if Subjects, err = CreateSubjects(&g); err != nil {
		t.Error("subjects create failed", fmt.Sprintf(", err:'%s'", err))
	}

	for _, pair := range TestsFetchGroups {
		var members []string
		if members, err = Subjects.FetchGroup(pair.group); err != nil {
			if pair.result == FETCHGROUPS_RESULT_OK {
				t.Error("expected group", pair.group, "to be resolved")
			}
		}

		if len(members) == 0 {
			if pair.result == FETCHGROUPS_RESULT_OK {
				t.Error("expected group", pair.group, "to have some members")
			}
		}
	}
}
