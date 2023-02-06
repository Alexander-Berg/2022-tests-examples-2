package integration_test

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/go_toolchain/gotoolchain"
	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/libs/go/boombox/httpreplay"
	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/internal/config"
	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/feed"
)

var (
	analyzer analyze.Analyzer
	homePath string
)

func TestMain(m *testing.M) {
	var boomboxTapePath string
	flag.StringVar(&boomboxTapePath, "save-boombox", "", "generate&save boombox")
	flag.Parse()

	if isFlagPassed("test.list") {
		os.Exit(m.Run())
		return
	}

	proxy := boomboxTapePath != ""
	if proxy {
		// gen new boombox
		_ = os.Remove(boomboxTapePath)
		integration.YadiTapePath = boomboxTapePath
		integration.YadiTapeRo = false
	}

	closeRecorder := func(r *httpreplay.Replay) {
		_ = r.Shutdown(context.Background())
	}

	goProxy, err := integration.NewGoProxy(proxy)
	if err != nil {
		panic(err)
	}
	defer closeRecorder(goProxy)

	npmAPI, err := integration.NewNpmAPI(proxy)
	if err != nil {
		panic(err)
	}
	defer closeRecorder(npmAPI)

	yadiAPI, err := integration.NewYadiAPI(proxy)
	if err != nil {
		panic(err)
	}
	defer closeRecorder(yadiAPI)

	setupGoEnv(goProxy.TestURL())

	config.YadiHost = yadiAPI.TestURL()
	config.NpmRepositoryURI = npmAPI.TestURL()
	config.FeedURI = fmt.Sprintf("%s/db/{lang}.json.gz", yadiAPI.TestURL())

	analyzer = analyze.NewAnalyzer(
		analyze.WithFeedOptions(feed.Options{
			MinimumSeverity: 0,
			FeedURI:         config.FeedURI,
		}),
		analyze.WithStatsTracking(false),
		analyze.WithSuggest(false),
	)

	os.Exit(m.Run())
}

func isFlagPassed(name string) bool {
	found := false
	flag.Visit(func(f *flag.Flag) {
		if f.Name == name {
			found = true
		}
	})
	return found
}

func setupGoEnv(goProxyURL string) {
	if err := gotoolchain.Setup(os.Setenv); err != nil {
		panic(err)
	}

	_ = os.Setenv("GOPROXY", goProxyURL)
	_ = os.Setenv("GOSUMDB", "off")

	homePath = yatest.WorkPath("fakehome")
	_ = os.Setenv("HOME", homePath)
	_ = os.Setenv("GOPATH", filepath.Join(homePath, "go"))
}

func testDataPath(t *testing.T, requiredPath string) string {
	arcadiaPath := path.Join("security/yadi/yadi/integration/testdata", requiredPath)
	targetFile, err := filepath.Abs(yatest.SourcePath(arcadiaPath))
	require.NoError(t, err)
	return targetFile
}
