package integration_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/pip"
)

func NoTestPipAnalyze(t *testing.T) {
	targetFile := testDataPath(t, "pip/requirements.txt")
	resultFile := testDataPath(t, "pip/issues.json")

	pipManager, err := pip.NewManager(pip.ManagerOpts{
		WithDev:     false,
		TargetPath:  targetFile,
		ResolveMode: manager.ResolveLocal,
	})
	require.NoError(t, err)

	table := integration.AnalyzeTable{
		Manager:    pipManager,
		ResultPath: resultFile,
	}

	integration.Analyze(t, analyzer, table)
}

func NoTestPipAnalyzePkg(t *testing.T) {
	targetFile := testDataPath(t, "pip/requirements.txt")
	resultFile := testDataPath(t, "pip/analyze_requests.2.1.0.json")

	pipManager, err := pip.NewManager(pip.ManagerOpts{
		WithDev:     false,
		TargetPath:  targetFile,
		ResolveMode: manager.ResolveLocal,
	})
	require.NoError(t, err)
	integration.AnalyzePkg(t, analyzer, integration.AnalyzePkgTable{
		Manager:    pipManager,
		Package:    struct{ Name, Version string }{Name: "requests", Version: "2.1.0"},
		ResultPath: resultFile,
	})
}

func NoTestPipWalk(t *testing.T) {
	targetFile := testDataPath(t, "pip/requirements.txt")
	resultFile := testDataPath(t, "pip/walk_result.json")

	pipManager, err := pip.NewManager(pip.ManagerOpts{
		WithDev:     false,
		TargetPath:  targetFile,
		ResolveMode: manager.ResolveLocal,
	})
	require.NoError(t, err)

	table := integration.WalkTable{
		Manager:    pipManager,
		ResultPath: resultFile,
	}

	integration.Walk(t, analyzer, table)
}
