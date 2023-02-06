package server_test

import (
	"context"
	"encoding/json"
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/feed"
	"a.yandex-team.ru/security/yadi/yaudit/internal/npmaudit"
)

func TestSimple(t *testing.T) {
	feedPath, err := filepath.Abs(filepath.Join("testdata", "nodejs-fixed-feed.json.gz"))
	require.NoError(t, err)

	dirPath, err := filepath.Abs("testdata")
	require.NoError(t, err)

	pkgPath, err := filepath.Abs(filepath.Join("testdata", "npm", "package.json"))
	require.NoError(t, err)

	lockPath, err := filepath.Abs(filepath.Join("testdata", "npm", "package-lock.json"))
	require.NoError(t, err)

	for _, file := range []string{feedPath, dirPath, pkgPath, lockPath} {
		_, err := os.Stat(file)
		require.NoError(t, err)
	}
	analyzer, err := npmaudit.NewAnalyzer(
		analyze.WithFeedOptions(feed.Options{
			MinimumSeverity: 0,
			FeedURI:         feedPath,
		}),
		analyze.WithSuggest(false),
		analyze.WithStatsTracking(true),
	)
	require.NoError(t, err)

	analyzeOpts := npmaudit.AnalyzerOpts{
		Ctx: context.Background(),
	}

	pkgData, err := ioutil.ReadFile(pkgPath)
	require.NoError(t, err)

	err = json.Unmarshal(pkgData, &analyzeOpts.PkgJSON)
	require.NoError(t, err)

	pkgLockData, err := ioutil.ReadFile(lockPath)
	require.NoError(t, err)

	err = json.Unmarshal(pkgLockData, &analyzeOpts.PkgLock)
	require.NoError(t, err)

	yadiResults, err := analyzer.AnalyzePkgLock(analyzeOpts)
	require.NoError(t, err)

	report := npmaudit.NewReport()
	err = report.Generate(yadiResults, false, true)
	require.NoError(t, err)

	assert.Equal(t, "express>qs", report.Advisories["YADI-NODEJS-QS-10019"].Findings[0].Paths[0])
	assert.NotZero(t, report.Meta.TotalDeps)
}
