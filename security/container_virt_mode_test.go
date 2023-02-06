package porto_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/porto"
)

var (
	testVirtModes = map[string]porto.VirtMode{
		"app":  porto.VirtModeApp,
		"os":   porto.VirtModeOs,
		"host": porto.VirtModeHost,
		"job":  porto.VirtModeJob,
	}
)

func TestVirtModeParse(t *testing.T) {
	for name, mode := range testVirtModes {
		result, err := porto.VirtModeParse(name)
		assert.NoError(t, err)
		assert.Equal(t, mode, result)
	}
}

func TestVirtModeString(t *testing.T) {
	for name, mode := range testVirtModes {
		assert.Equal(t, name, mode.String())
	}
}
