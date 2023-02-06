package searchapp

import (
	"testing"

	"github.com/stretchr/testify/suite"

	"a.yandex-team.ru/portal/avocado/tests"
)

func TestSearchAppSuite(t *testing.T) {
	suite.Run(t, new(SearchAppSuite))
}

type SearchAppSuite struct {
	tests.CommonSuite
}
