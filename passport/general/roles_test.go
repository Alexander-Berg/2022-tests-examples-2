package knifeunittest

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
)

func TestReadRolesFromDir(t *testing.T) {
	dir := yatest.SourcePath("passport/infra/daemons/tvmtool/internal/knifeunittest/gotest")

	_, err := readRolesFromDir(dir, []string{"some_slug", "broken"})
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to parse roles")

	roles, err := readRolesFromDir(dir, []string{"some_slug"})
	require.NoError(t, err)
	require.Contains(t, roles, "some_slug")
	require.EqualValues(t, "foobar", roles["some_slug"].GetMeta().Revision)
}
