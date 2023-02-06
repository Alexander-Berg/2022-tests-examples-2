package porto_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/porto"
)

var (
	testStates = map[string]porto.State{
		"stopped":    porto.StateStopped,
		"starting":   porto.StateStarting,
		"running":    porto.StateRunning,
		"stopping":   porto.StateStopping,
		"paused":     porto.StatePaused,
		"dead":       porto.StateDead,
		"meta":       porto.StateMeta,
		"respawning": porto.StateRespawning,
	}
)

func TestStateParse(t *testing.T) {
	for name, mode := range testStates {
		result, err := porto.StateParse(name)
		assert.NoError(t, err)
		assert.Equal(t, mode, result)
	}
}

func TestStateString(t *testing.T) {
	for name, mode := range testStates {
		assert.Equal(t, name, mode.String())
	}
}
