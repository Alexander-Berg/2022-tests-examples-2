package bench_test

import (
	"context"
	"errors"
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"

	"github.com/gofrs/uuid"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/libs/go/simplelog"
	"a.yandex-team.ru/security/yadi/yadi/internal/config"
	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/feed"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/pkglock"
)

var (
	targetFolder string
	analyzer     analyze.Analyzer
)

func init() {
	// TODO(buglloc): Move this!
	config.CheckDevDependencies = true

	simplelog.SetLevel(simplelog.ErrorLevel)
	if folder, err := prepareData(); err != nil {
		panic(err)
	} else {
		targetFolder = folder
	}

	feedPath, err := filepath.Abs(filepath.Join("feed", "yadi", "nodejs.json"))
	if err != nil {
		panic(err)
	}

	analyzer = analyze.NewAnalyzer(
		analyze.WithFeedOptions(feed.Options{
			FeedURI: feedPath,
		}),
		analyze.WithStatsTracking(true),
		analyze.WithSuggest(false),
	)
}

func copyFile(src, dst string) error {
	input, err := ioutil.ReadFile(src)
	if err != nil {
		return err
	}

	err = ioutil.WriteFile(dst, input, 0644)
	if err != nil {
		return err
	}
	return nil
}

func prepareData() (targetFolder string, resultErr error) {
	uuid4, err := uuid.DefaultGenerator.NewV4()
	if err != nil {
		resultErr = errors.New("failed to generate UUID4")
		return
	}
	simplelog.Debug("uuid was generated", "uuid", uuid4)

	targetFolder, err = ioutil.TempDir("", "yaudit-bench-")
	if err != nil {
		resultErr = err
		return
	}

	if err := os.MkdirAll(targetFolder, 0755); err != nil {
		resultErr = err
		return
	}

	if err := copyFile(yatest.SourcePath("security/yadi/yadi/bench/testdata/package.json"), filepath.Join(targetFolder, "package.json")); err != nil {
		resultErr = err
		return
	}

	if err := copyFile(yatest.SourcePath("security/yadi/yadi/bench/testdata/package-lock.json"), filepath.Join(targetFolder, "package-lock.json")); err != nil {
		resultErr = err
		return
	}
	return
}

func audit(analyzer analyze.Analyzer) {
	pm, err := pkglock.NewManager(pkglock.ManagerOpts{
		TargetPath: filepath.Join(targetFolder, "package-lock.json"),
	})
	if err != nil {
		simplelog.Error("failed to create new package manager", "err", err.Error())
		return
	}

	_, err = analyzer.Analyze(context.Background(), analyze.Request{
		PackageManager: pm,
	})
	if err != nil {
		simplelog.Error("failed to analyze", "err", err.Error())
	}
}

func BenchmarkYaudit(b *testing.B) {
	for i := 0; i < b.N; i++ {
		audit(analyzer)
	}
}
