package e2e

import (
	"testing"

	"a.yandex-team.ru/security/gideon/gideon/e2e/e2e"
)

func TestKernelVersion(t *testing.T) {
	e2e.TestKernelVersion(t, "4.19.143")
}

func TestGideon(t *testing.T) {
	e2e.RunAll(t)
}
