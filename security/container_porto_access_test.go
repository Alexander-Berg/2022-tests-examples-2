package porto_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/porto"
)

var (
	testPortoAccesses = map[string]porto.PortoAccess{
		"none":         porto.PortoAccessNone,
		"read-isolate": porto.PortoAccessReadIsolate,
		"read-only":    porto.PortoAccessReadOnly,
		"isolate":      porto.PortoAccessIsolate,
		"child-only":   porto.PortoAccessChildOnly,
		"full":         porto.PortoAccessFull,
	}
)

func TestPortoAccessParse(t *testing.T) {
	for name, mode := range testPortoAccesses {
		result, err := porto.PortoAccessParse(name)
		assert.NoError(t, err)
		assert.Equal(t, mode, result)
	}
}

func TestPortoAccessString(t *testing.T) {
	for name, mode := range testPortoAccesses {
		assert.Equal(t, name, mode.String())
	}
}
