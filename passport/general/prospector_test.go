package ammo

import (
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestProspector(t *testing.T) {
	tmpDir := "./tmpdir"
	require.NoError(t, os.Mkdir(tmpDir, os.ModePerm))
	defer func() { _ = os.RemoveAll(tmpDir) }()

	cfg := Config{
		Dir: tmpDir,
	}
	state, err := NewAmmo(cfg)
	require.NoError(t, err)
	defer state.Stop()

	res, err := state.GetTask("host1")
	require.NoError(t, err)
	require.Equal(t, "", res.ID)
	require.Equal(t, uint32(0), res.Duration)

	res, err = state.GetTask("host2")
	require.NoError(t, err)
	require.Equal(t, "", res.ID)
	require.Equal(t, uint32(0), res.Duration)

	state.task = &createTask{
		id: "kek",
		hosts: []string{
			"host1",
		},
		duration: 42,
	}

	res, err = state.GetTask("host1")
	require.NoError(t, err)
	require.Equal(t, "kek", res.ID)
	require.Equal(t, uint32(42), res.Duration)

	res, err = state.GetTask("host2")
	require.NoError(t, err)
	require.Equal(t, "", res.ID)
	require.Equal(t, uint32(0), res.Duration)
}
