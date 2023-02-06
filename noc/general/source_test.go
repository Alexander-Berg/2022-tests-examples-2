package distributor

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/susanin/internal/zk"
)

func TestImplementations(t *testing.T) {
	require.Implements(t, (*SnapshotSource)(nil), (*zk.Client)(nil))
	require.Implements(t, (*SnapshotSource)(nil), (*fileSource)(nil))
}
