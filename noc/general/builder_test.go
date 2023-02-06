package builder

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/noc/go/cvs"
	"a.yandex-team.ru/noc/tardis/pkg/graph"
	"a.yandex-team.ru/noc/tardis/pkg/storage"
)

var ts1 = time.Date(2021, 1, 1, 0, 0, 0, 0, time.UTC)
var ts2 = time.Date(2021, 1, 2, 0, 0, 0, 0, time.UTC)

type testCVS struct{}

func (testCVS) Checkout(ctx context.Context, src, dst, workdir string, ts time.Time) error {
	return nil
}

func getLogger() log.Logger {
	zapConfig := zap.TSKVConfig(log.DebugLevel)
	zapConfig.OutputPaths = []string{"stdout"}
	logger, _ := zap.New(zapConfig)
	return logger
}

var logger = getLogger()

func _Test1(t *testing.T) {
	g := graph.NewGraph(nil, logger)

	checkoutDir := yatest.OutputPath("checkout")
	err := os.MkdirAll(checkoutDir, 0755)
	require.NoError(t, err)

	storeDir := yatest.OutputPath("store")
	err = os.MkdirAll(storeDir, 0755)
	require.NoError(t, err)

	cfg := Config{
		CheckoutDir: checkoutDir,
		Step:        24 * time.Hour,
		BatchSize:   1,
		Start:       ts1,
	}

	storeCfg := storage.FolderStorageConfig{
		Folder:          storeDir,
		RetentionPolicy: nil,
	}

	store, err := storage.NewFolderStorage(&storeCfg, ts1, nil, logger)
	require.NoError(t, err)

	//vcs := testCVS{}
	vcs := CVSWrapper{VCS: cvs.NewCVS("tree.yandex.ru:/opt/CVSROOT", cvs.WithLog(logger))}

	builder := NewBuilder(&cfg, g, vcs, []storage.Storage{store}, nil, logger)
	err = builder.Run(context.Background())
	assert.NoError(t, err)
}
