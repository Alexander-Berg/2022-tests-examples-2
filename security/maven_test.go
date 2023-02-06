package integration_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/maven"
)

func TestMavenAnalyze(t *testing.T) {
	targetFile := testDataPath(t, "maven/deps.dot")
	resultFile := testDataPath(t, "maven/issues.json")

	mvnManager, err := maven.NewManagerFromDotFile(maven.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	table := integration.AnalyzeTable{
		Manager:    mvnManager,
		ResultPath: resultFile,
	}

	integration.Analyze(t, analyzer, table)
}

func TestMavenAnalyzePkg(t *testing.T) {
	// not implemented
	defer func() {
		if r := recover(); r == nil {
			t.Errorf("should panic")
		}
	}()

	targetFile := testDataPath(t, "maven/deps.dot")

	mvnManager, err := maven.NewManagerFromDotFile(maven.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	_, _ = analyzer.AnalyzePkg(context.Background(), analyze.PkgRequest{
		PackageManager: mvnManager,
		PackageName:    "log4j:log4j",
		PackageVersion: "0",
	})
}

func TestMavenWalk(t *testing.T) {
	targetFile := testDataPath(t, "maven/deps.dot")
	resultFile := testDataPath(t, "maven/walk_result.json")

	mvnManager, err := maven.NewManagerFromDotFile(maven.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	table := integration.WalkTable{
		Manager:    mvnManager,
		ResultPath: resultFile,
	}

	integration.Walk(t, analyzer, table)
}
