package interfaces

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/go/startrek"
)

func TestStartrek(t *testing.T) {
	require.Implements(t, (*StartrekClient)(nil), (*startrek.Client)(nil))
}
