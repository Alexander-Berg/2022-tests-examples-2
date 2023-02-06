package interfaces

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/go/abc"
)

func TestABC(t *testing.T) {
	require.Implements(t, (*ABCClient)(nil), (*abc.Client)(nil))
}
