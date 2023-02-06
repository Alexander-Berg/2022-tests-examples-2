package app

import (
	"bufio"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/puncher/client/cauth"
	"a.yandex-team.ru/noc/puncher/client/macrosd"
	"a.yandex-team.ru/noc/puncher/client/racktables"
	"a.yandex-team.ru/noc/puncher/client/rulesd"
	"a.yandex-team.ru/noc/puncher/client/securityfw"
	"a.yandex-team.ru/noc/puncher/client/usersd"
	"a.yandex-team.ru/noc/puncher/config"
	"a.yandex-team.ru/noc/puncher/lib/logging"
	"a.yandex-team.ru/noc/puncher/lib/proc"
	"a.yandex-team.ru/noc/puncher/mock/macrosdmock"
	"a.yandex-team.ru/noc/puncher/mock/rulesdmock"
	"a.yandex-team.ru/noc/puncher/mock/usersdmock"
	"a.yandex-team.ru/noc/puncher/models"
)

func targetsFromStrings(targets []string) []models.RuleTarget {
	ret := make([]models.RuleTarget, len(targets))
	for i, t := range targets {
		ret[i] = models.RuleTarget{
			Target: models.Target{
				MachineName: t,
				Sections:    []string{"VS"},
			},
		}
	}
	return ret
}

func portsFromStrings(ports []string) []models.Port {
	ret := make([]models.Port, len(ports))
	for i, p := range ports {
		port, _ := models.NewPort(p) // assume that all ports are valid
		ret[i] = port
	}
	return ret
}

var cauthRules = []models.Rule{{
	Protocol: "udp",
	Sources: []models.RuleTarget{
		{
			Target: models.Target{
				MachineName: "%user1%",
				Sections:    []string{"VS"},
				Type:        models.TargetTypeUser,
			},
		},
	},
	Destinations: targetsFromStrings([]string{"ns64-cache.yandex.net"}),
	Ports:        portsFromStrings([]string{"53"}),
	System:       "cauth",
	Status:       "active",
}, {
	Protocol: "udp",
	Sources: []models.RuleTarget{
		{
			Target: models.Target{
				MachineName: "%user2%",
				Sections:    []string{"VS"},
				Type:        models.TargetTypeUser,
			},
		},
	},
	Destinations: targetsFromStrings([]string{"ns64-cache.yandex.net"}),
	Ports:        portsFromStrings([]string{"53"}),
	System:       "cauth",
	Status:       "active",
}, {
	Protocol: "udp",
	Sources: []models.RuleTarget{
		{
			Target: models.Target{
				MachineName: "@srv_svc_plan@",
				Type:        models.TargetTypeStaffGroup,
			},
		},
	},
	Destinations: targetsFromStrings([]string{"ns64-cache.yandex.net"}),
	Ports:        portsFromStrings([]string{"53"}),
	System:       "cauth",
	Status:       "active",
}}
var cauthRulesExp = []string{
	"add allow udp from { %user1% } to { ns64-cache.yandex.net } 53",
	"add allow udp from { %user2% } to { ns64-cache.yandex.net } 53",
}

var puncherRules = []models.Rule{{
	Protocol: "udp",
	Sources: []models.RuleTarget{
		{
			Target: models.Target{
				MachineName: "%puncher%",
				Sections:    []string{"VS"},
				Type:        models.TargetTypeUser,
			},
		},
	},
	Destinations: targetsFromStrings([]string{"ns64-cache.yandex.net"}),
	Ports:        portsFromStrings([]string{"53"}),
	System:       "puncher",
	Status:       "active",
}}
var puncherRulesExp = []string{
	"add allow udp from { %puncher% } to { ns64-cache.yandex.net } 53",
}

var staticRules = []models.Rule{{
	Protocol:     "udp",
	Sources:      targetsFromStrings([]string{"_YANDEXNETS_", "_YANDEXALIENSUPERNETS_"}),
	Destinations: targetsFromStrings([]string{"ns64-cache.yandex.net"}),
	Ports:        portsFromStrings([]string{"53"}),
	System:       "static",
	Status:       "active",
}, {
	Protocol: "udp",
	Sources:  targetsFromStrings([]string{"_M2_"}),
	Destinations: []models.RuleTarget{
		{
			Target: models.Target{
				MachineName: "m2.yandex.net",
				Sections:    []string{"VS.p"},
				Type:        models.TargetTypeHost,
			},
		},
	},
	Ports: portsFromStrings([]string{
		"53",
		"1001",
		"1002",
		"1003",
		"1004",
		"1005",
		"1006",
		"1007",
		"1008",
		"1009",
		"1010",
		"1011",
		"1012",
		"1013",
		"1014",
		"1015",
		"1016",
		"1018",
		"1019",
	}),
	System: "static",
	Status: "active",
}, {
	Protocol: "udp",
	Sources:  targetsFromStrings([]string{"_M2_", "_YANDEXNETS_"}),
	Destinations: []models.RuleTarget{
		{
			Target: models.Target{
				MachineName: "m2.yandex.net",
				Sections:    []string{"VS.y"},
				Type:        models.TargetTypeHost,
			},
		},
	},
	Ports: portsFromStrings([]string{
		"53",
		"1001",
		"1002",
		"1003",
		"1004",
		"1005",
		"1006",
		"1007",
		"1008",
		"1009",
		"1010",
		"1011",
		"2012",
		"1013",
		"1014",
		"1015",
		"1016",
		"1018",
		"1019",
		"2020",
	}),
	System: "static",
	Status: "active",
}}
var staticRulesExp map[string][]string

var rules []models.Rule

var app *App
var rulesdClient rulesd.Client
var exportdir string

func touchFile(path string) error {
	file, err := os.OpenFile(path, os.O_RDONLY|os.O_CREATE, 0644)
	if err != nil {
		return err
	}
	return file.Close()
}

func runCvs(args ...string) error {
	p := proc.New("cvs", args...)
	p.Env = map[string]string{
		"CVSROOT": app.configService.CVS.CVSRoot,
	}
	p.StderrHandler = proc.LogAsWarningHandler
	return p.Run(app.logger)
}

func initModule(base, path string, files []string) (err error) {
	mpath := filepath.Join(base, path)
	cwdir, err := os.Getwd()
	if err != nil {
		return err
	}
	err = os.MkdirAll(mpath, 0755)
	if os.IsExist(err) {
		return nil
	}
	if err != nil {
		return err
	}
	defer func() {
		err = os.Chdir(cwdir)
	}()
	err = os.Chdir(mpath)
	if err != nil {
		return err
	}
	for _, f := range files {
		err = touchFile(filepath.Join(mpath, f))
		if err != nil {
			return err
		}
	}
	err = runCvs("import", "-m \"Initial import\"", path, "i", "start")
	if err != nil {
		return err
	}
	return nil
}

func prepareCVS() (err error) {
	cvsdir, err := ioutil.TempDir("", "puncher-cvs-")
	if err != nil {
		return err
	}
	defer func() {
		err = os.RemoveAll(cvsdir)
	}()
	cvsrootdir := strings.TrimPrefix(app.configService.CVS.CVSRoot, ":local:")
	err = os.MkdirAll(cvsrootdir, 0755)
	if os.IsExist(err) {
		return nil
	}
	if err != nil {
		return err
	}
	_, err = exec.LookPath("cvs")
	if err != nil {
		return err
	}
	err = runCvs("init")
	if err != nil {
		return err
	}

	modules := map[string][]string{
		"noc/routers/fw":      {},
		"noc/routers/fw-test": {},
		"noc/routers/fw-test/ipfw": {
			"DEFAULT_SECTION",
		},
		"noc/routers/fw-test/iptables": {},
		"noc/routers": {
			"global-routers-inc.m4",
		},
		"security/certs": {
			"certs.json",
		},
		"noc/balancers/iptables": {},
		"securityfw": {
			"cauth_rules.m4",
		},
	}
	for mod, files := range modules {
		err = initModule(cvsdir, mod, files)
		if err != nil {
			return err
		}
	}
	staticRulesExp = make(map[string][]string)
	staticRulesExp["cvs-write/noc/routers/fw-test/ipfw/VS"] = []string{
		"ALLOW_FROM_YANDEXNETS(udp, { ns64-cache.yandex.net }, 53)",
		"add allow udp from { _YANDEXALIENSUPERNETS_ } to { ns64-cache.yandex.net } 53",
	}
	staticRulesExp["cvs-write/noc/routers/fw-test/iptables/VS/VS.p"] = []string{
		"-A _CURRENTTABLE_ -m multiport -p udp --source { _M2_ } --dports 53,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,1012,1013,1014 -j ACCEPT",
		"-A _CURRENTTABLE_ -m multiport -p udp --source { _M2_ } --dports 1015,1016,1018,1019 -j ACCEPT",
	}
	staticRulesExp["cvs-write/noc/routers/fw-test/iptables/VS/VS.y"] = []string{
		"ALLOW_FROM_YANDEXNETS(udp, _CURRENTIPLIST_, 53,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,2012,1013,1014)",
		"ALLOW_FROM_YANDEXNETS(udp, _CURRENTIPLIST_, 1015,1016,1018,1019,2020)",
		"-A _CURRENTTABLE_ -m multiport -p udp --source { _M2_ } --dports 53,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1011,2012,1013,1014 -j ACCEPT",
		"-A _CURRENTTABLE_ -m multiport -p udp --source { _M2_ } --dports 1015,1016,1018,1019,2020 -j ACCEPT",
	}
	return nil
}

func TestMain(m *testing.M) {
	logger := logging.Must(log.DebugLevel)

	usersdServer := usersdmock.NewServer()
	defer usersdServer.Close()

	rulesdServer := rulesdmock.NewServer()
	defer rulesdServer.Close()

	rules = append(rules, staticRules...)
	rules = append(rules, puncherRules...)
	rules = append(rules, cauthRules...)

	for _, r := range rules {
		rulesdServer.CreateRule(r)
	}

	macrosdServer := macrosdmock.NewServer()
	defer macrosdServer.Close()

	var err error
	exportdir, err = ioutil.TempDir("", "puncher-export-cvs-")
	if err != nil {
		return
	}
	defer func() {
		if err := os.RemoveAll(exportdir); err != nil {
			app.logger.Error("Error while remove exportdir", log.Error(err))
		}
	}()
	configService := &config.Service{
		ExportDaemon: config.ExportDaemonConfig{
			TimeZone:     "Europe/Moscow",
			CVSCommitDir: filepath.Join(exportdir, "cvs-write"),
		},
		SecurityFW: securityfw.Config{
			DataDir: filepath.Join(exportdir, "securityfw"),
		},
		RulesTarget: struct {
			Path string
		}{
			Path: "rulestarget",
		},
		CAuth: cauth.Config{
			RulesPath: "cauth_rules.m4",
		},
		CVS: racktables.CVSConfig{
			CVSRoot:          ":local:/tmp/cvs-local-root",
			SectionsDir:      "/noc/routers/fw-test/ipfw",
			BalancersDir:     "/noc/routers/fw-test/iptables",
			RouterFWDir:      "/noc/routers/fw-test",
			BalancersIpfwDir: "/noc/routers/fw-test/balancer_ipfw",
			IdentityFile:     "/etc/hosts", // FIXME: Нужен существующий файл, но он не используется
		},
	}

	usersdClient := usersd.NewClient(usersdServer.URL)
	rulesdClient = rulesd.NewClient(rulesdServer.URL)
	macrosdClient := macrosd.NewClient(macrosdServer.URL)

	app = &App{}
	app.configService = configService
	app.groupsEmpty = make(map[string]bool)
	app.groupsEmpty["@srv_svc_plan@"] = false // for ease of testing PUNCHER-881
	app.logger = logger

	app.usersdClient = usersdClient
	app.rulesdClient = rulesdClient
	app.macrosdClient = macrosdClient
	gopath := os.Getenv("GOPATH")
	if len(gopath) == 0 {
		app.logger.Error("Look GOPATH failed")
	}
	if err := os.Setenv("PATH", os.Getenv("PATH")+":"+gopath+"/src/a.yandex-team.ru/noc/puncher/scripts"); err != nil {
		app.logger.Error("Error while set PATH", log.Error(err))
	}
	// app.Master = election.New(session, "exportd", launchid.Get(), false, app.logger)
	defer func() {
		if err := os.RemoveAll(strings.TrimPrefix(app.configService.CVS.CVSRoot, ":local:")); err != nil {
			app.logger.Error("Error while remove cvsroot", log.Error(err))
		}
	}()
	os.Exit(m.Run())
}

func sliceDiff(expected, actual []string) ([]string, []string) {
	m := make(map[string]int)
	for _, v := range expected {
		val := 1
		if ev, ok := m[v]; ok {
			val += ev
		}
		m[v] = val
	}
	for _, v := range actual {
		val := -1
		if ev, ok := m[v]; ok {
			val += ev
		}
		m[v] = val
	}
	var exp, act []string
	for k, v := range m {
		if v > 0 {
			exp = append(exp, k)
		}
		if v < 0 {
			act = append(act, k)
		}
	}
	return exp, act
}

func checkRule(t *testing.T, path string, rules []string) {
	f, err := os.Open(path)
	assert.NoError(t, err)
	scanner := bufio.NewScanner(f)
	var prules []string
	for scanner.Scan() {
		l := scanner.Text()
		if strings.HasPrefix(l, "#") || len(l) == 0 {
			continue
		}
		prules = append(prules, l)
	}
	expDiff, actDiff := sliceDiff(rules, prules)
	if len(expDiff) > 0 {
		t.Errorf("Not found %d rules. %v", len(expDiff), strings.Join(expDiff, ", "))
	}
	if len(actDiff) > 0 {
		t.Errorf("Found additional %d rules. %v", len(actDiff), strings.Join(actDiff, ", "))
	}
	assert.Equal(t, expDiff, actDiff)
}

func TestExportRules(t *testing.T) {
	// location, err := time.LoadLocation(app.configService.ExportDaemon.TimeZone)
	// assert.NoError(t, err)
	err := prepareCVS()
	assert.NoError(t, err)
	err = app.ExportRules()
	assert.NoError(t, err)
	// Check cauth
	checkRule(t, filepath.Join(exportdir, "securityfw/cauth_rules.m4"), cauthRulesExp)

	// Static
	for f, rules := range staticRulesExp {
		checkRule(t, filepath.Join(exportdir, f), rules)
	}

	// puncher
	checkRule(t, filepath.Join(exportdir, "securityfw/rulestarget"), puncherRulesExp)
}
