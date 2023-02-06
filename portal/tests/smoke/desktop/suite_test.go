package desktop

import (
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/portal/avocado/tests"
)

type DesktopSuite struct {
	tests.CommonSuite
}

func TestSearchAppSuite(t *testing.T) {
	suite.Run(t, new(DesktopSuite))
}
