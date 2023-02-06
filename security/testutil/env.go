package testutil

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/test/go_toolchain/gotoolchain"
	"a.yandex-team.ru/library/go/test/yatest"
)

var Logger = zap.Must(zap.ConsoleConfig(log.DebugLevel))

func SetupGoEnv() {
	if err := gotoolchain.Setup(os.Setenv); err != nil {
		panic(err)
	}
}

func GoEnv(t *testing.T, kirbyURL string) []string {
	require.NotEmpty(t, kirbyURL, "no kirby url")

	fakeHome := yatest.WorkPath(fmt.Sprintf("home-for-%s", testName(t)))
	return []string{
		"HOME=" + fakeHome,
		"GOPATH=" + filepath.Join(fakeHome, "go"),
		"GOPROXY=" + kirbyURL,
	}
}

func SetupGoMod(t *testing.T) {
	dir, err := ioutil.TempDir("", testName(t))
	require.NoError(t, err, "create tmp dir fail")

	err = os.Chdir(dir)
	require.NoError(t, err, "chdir into tmp dir fail")

	CreateFakeModule(t, dir)
}

func CreateFakeModule(t *testing.T, modDir string) {
	err := ioutil.WriteFile(filepath.Join(modDir, "go.mod"), []byte(`module fake/module`), 0644)
	require.NoError(t, err, "failed to create go.mod")
}

func testName(t *testing.T) string {
	return strings.ReplaceAll(t.Name(), string(filepath.Separator), "-")
}
