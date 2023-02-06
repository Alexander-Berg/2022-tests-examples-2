package integration_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/npm"
)

func TestNPMAnalyze(t *testing.T) {
	targetFile := testDataPath(t, "npm/package.json")
	resultFile := testDataPath(t, "npm/issues.json")

	npmManager, err := npm.NewManager(npm.ManagerOpts{
		WithDev:     false,
		TargetPath:  targetFile,
		ResolveMode: manager.ResolveLocal,
	})
	require.NoError(t, err)

	table := integration.AnalyzeTable{
		Manager:    npmManager,
		ResultPath: resultFile,
	}

	integration.Analyze(t, analyzer, table)
}

func TestNPMAnalyzePkg(t *testing.T) {
	targetFile := testDataPath(t, "npm/package.json")
	resultFile := testDataPath(t, "npm/analyze_minimatch.2.0.10.json")

	npmManager, err := npm.NewManager(npm.ManagerOpts{
		WithDev:     false,
		TargetPath:  targetFile,
		ResolveMode: manager.ResolveLocal,
	})
	require.NoError(t, err)
	integration.AnalyzePkg(t, analyzer, integration.AnalyzePkgTable{
		Manager:    npmManager,
		Package:    struct{ Name, Version string }{Name: "minimatch", Version: "2.0.10"},
		ResultPath: resultFile,
	})
}

func TestNPMWalk(t *testing.T) {
	targetFile := testDataPath(t, "npm/package.json")
	resultFile := testDataPath(t, "npm/walk_result.json")

	npmManager, err := npm.NewManager(npm.ManagerOpts{
		WithDev:     false,
		TargetPath:  targetFile,
		ResolveMode: manager.ResolveLocal,
	})
	require.NoError(t, err)

	table := integration.WalkTable{
		Manager:    npmManager,
		ResultPath: resultFile,
	}

	integration.Walk(t, analyzer, table)
}
