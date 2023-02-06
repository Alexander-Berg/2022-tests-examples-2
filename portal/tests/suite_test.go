package tests

import (
	"testing"

	"github.com/stretchr/testify/suite"
)

func TestMapAddrSuite(t *testing.T) {
	suite.Run(t, new(Suite))
}

type Suite struct {
	CommonSuite
}
