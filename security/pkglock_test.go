package integration_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/pkglock"
)

func TestPkgLockAnalyze(t *testing.T) {
	targetFile := testDataPath(t, "pkglock/package-lock.json")
	resultFile := testDataPath(t, "pkglock/issues.json")

	pkglockManager, err := pkglock.NewManager(pkglock.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	table := integration.AnalyzeTable{
		Manager:    pkglockManager,
		ResultPath: resultFile,
	}

	integration.Analyze(t, analyzer, table)
}

func TestPkgLockAnalyzePkg(t *testing.T) {
	targetFile := testDataPath(t, "pkglock/package-lock.json")

	// not implemented
	defer func() {
		if r := recover(); r == nil {
			t.Errorf("should panic")
		}
	}()

	pkglockManager, err := pkglock.NewManager(pkglock.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	_, _ = analyzer.AnalyzePkg(context.Background(), analyze.PkgRequest{
		PackageManager: pkglockManager,
		PackageName:    "fresh",
		PackageVersion: "0.5.0",
	})
}

func TestPkgLockWalk(t *testing.T) {
	targetFile := testDataPath(t, "pkglock/package-lock.json")
	resultFile := testDataPath(t, "pkglock/walk_result.json")

	pkglockManager, err := pkglock.NewManager(pkglock.ManagerOpts{
		WithDev:    false,
		TargetPath: targetFile,
	})
	require.NoError(t, err)

	table := integration.WalkTable{
		Manager:    pkglockManager,
		ResultPath: resultFile,
	}

	integration.Walk(t, analyzer, table)
}
