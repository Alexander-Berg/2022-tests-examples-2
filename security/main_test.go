package integration

import (
	"context"
	"flag"
	"fmt"
	"os"
	"testing"

	"a.yandex-team.ru/security/kirby/integration/testutil"
)

var (
	kirbyURL string
)

func TestMain(m *testing.M) {
	var boomboxTapePath string
	flag.StringVar(&boomboxTapePath, "save-boombox", "", "generate&save boombox")
	flag.Parse()

	if !isFlagPassed("test.list") {
		proxy := boomboxTapePath != ""
		if proxy {
			// gen new boombox
			_ = os.Remove(boomboxTapePath)
			testutil.KirbyTapePath = boomboxTapePath
			testutil.KirbyTapeRo = false
		}

		goProxySrv, err := testutil.StartGoProxy(proxy)
		if err != nil {
			panic(fmt.Sprintf("can't start goproxy boombox: %v", err))
		}
		defer func() {
			_ = goProxySrv.Shutdown(context.Background())
		}()

		testutil.SetupGoEnv()

		url, closer, err := testutil.StartKirby(goProxySrv.TestURL())
		if err != nil {
			panic(err)
		}

		kirbyURL = url
		defer closer()
	}

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
