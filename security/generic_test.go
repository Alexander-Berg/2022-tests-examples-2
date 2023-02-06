package integration_test

import (
	"bytes"
	"context"
	"io"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/yadi/yadi/integration"
	"a.yandex-team.ru/security/yadi/yadi/pkg/analyze"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/generic"
	"a.yandex-team.ru/security/yadi/yadi/pkg/manager/gomod"
	"a.yandex-team.ru/security/yadi/yadi/pkg/outputs/genericout"
	"a.yandex-team.ru/security/yadi/yadi/pkg/outputs/writer"
)

func goModWalk(t *testing.T, ctx context.Context, target string, result io.Writer) {
	walkManager, err := gomod.NewManager(gomod.ManagerOpts{
		WithDev:    false,
		TargetPath: target,
	})
	require.NoError(t, err)

	out := bytes.NewBuffer(nil)
	consumer := genericout.NewListOutput(
		genericout.WithWriter(
			writer.NewWriter(
				writer.WithBuf(out),
			),
		),
		genericout.WithLanguage(walkManager.Language()),
		genericout.WithProjectName("test-package"),
	)

	err = consumer.Close()
	require.NoError(t, err)

	_, err = io.Copy(result, out)
	require.NoError(t, err)

	err = analyzer.Walk(ctx, analyze.WalkRequest{
		PackageManager: walkManager,
		Consumer:       consumer,
	})
	require.NoError(t, err)
}

func TestGenericGoModAnalyze(t *testing.T) {
	targetFile := testDataPath(t, "gomod/go.mod")
	resultFile := testDataPath(t, "gomod/issues.json")

	// prepare temp generic project file from go-mod manager
	projFile, err := ioutil.TempFile("", "yadi.json")
	require.NoError(t, err)
	defer func() { _ = os.Remove(projFile.Name()) }()
	goModWalk(t, context.Background(), targetFile, projFile)

	// compare native and generic analyzers
	genericManager, err := generic.NewManager(generic.ManagerOpts{
		WithDev:    false,
		TargetPath: projFile.Name(),
	})
	require.NoError(t, err)

	table := integration.AnalyzeTable{
		Manager:    genericManager,
		ResultPath: resultFile,
	}

	integration.Analyze(t, analyzer, table)
}
