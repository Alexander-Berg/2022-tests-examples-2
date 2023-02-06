package integration_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/gomod"
)

func TestGomodAnalyze(t *testing.T) {
	targetFile := testDataPath(t, "gomod/go.mod")
	resultFile := testDataPath(t, "gomod/issues.json")

	gomodManager, err := gomod.NewManager(gomod.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	table := integration.AnalyzeTable{
		Manager:    gomodManager,
		ResultPath: resultFile,
	}

	integration.Analyze(t, analyzer, table)
}

func TestGomodAnalyzePkg(t *testing.T) {
	// not implemented
	defer func() {
		if r := recover(); r == nil {
			t.Errorf("should panic")
		}
	}()

	targetFile := testDataPath(t, "gomod/go.mod")
	gomodManager, err := gomod.NewManager(gomod.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	_, _ = analyzer.AnalyzePkg(context.Background(), analyze.PkgRequest{
		PackageManager: gomodManager,
		PackageName:    "github.com/labstack/echo/v4",
		PackageVersion: "0",
	})
}

func TestGomodWalk(t *testing.T) {
	targetFile := testDataPath(t, "gomod/go.mod")
	resultFile := testDataPath(t, "gomod/walk_result.json")

	gomodManager, err := gomod.NewManager(gomod.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	table := integration.WalkTable{
		Manager:    gomodManager,
		ResultPath: resultFile,
	}

	integration.Walk(t, analyzer, table)
}
