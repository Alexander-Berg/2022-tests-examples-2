package integration_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/bazelmaven"
)

func TestBazelMavenAnalyze(t *testing.T) {
	targetFile := testDataPath(t, "bazelmaven/maven_install.json")
	resultFile := testDataPath(t, "bazelmaven/issues.json")

	mvnManager, err := maven.NewManager(maven.ManagerOpts{
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

func TestBazelMavenWalk(t *testing.T) {
	targetFile := testDataPath(t, "bazelmaven/maven_install.json")
	resultFile := testDataPath(t, "bazelmaven/walk_result.json")

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
