package macrosutils

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/macrospb"
	"a.yandex-team.ru/noc/macros/pkg/macros/mcerrors"
)

func TestGetDependants(t *testing.T) {
	helper := &Helper{}
	key := &macrospb.Key{}

	dependants, err := helper.GetDependants(key)
	require.Nil(t, dependants)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrEmptyKey, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	dependants, err = helper.GetDependants(key)
	require.Nil(t, dependants)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoDepsOnServer, err)

	helper.revDeps = map[string]map[string]struct{}{}

	dependants, err = helper.GetDependants(key)
	require.Nil(t, dependants)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrMacroNotFound(macroName), err)

	helper.revDeps[macroName] = map[string]struct{}{
		"_OTHER_MACRO_":  {},
		"_SECOND_MACRO_": {},
	}

	dependants, err = helper.GetDependants(key)
	require.NoError(t, err)
	require.Equal(t, map[string]struct{}{
		"_OTHER_MACRO_":  {},
		"_SECOND_MACRO_": {},
	}, dependants)
}

func TestGetExpansions(t *testing.T) {
	helper := &Helper{}
	key := &macrospb.Key{}

	expansions, err := helper.GetExpansion(nil)
	require.Nil(t, expansions)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrKeyNotSpecified, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	expansions, err = helper.GetExpansion(key)
	require.Nil(t, expansions)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoExpOnServer, err)

	helper.expansions = map[string]map[string]struct{}{}

	expansions, err = helper.GetExpansion(key)
	require.Nil(t, expansions)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrMacroNotFound(macroName), err)

	helper.expansions[macroName] = map[string]struct{}{
		"example1.com": {},
		"240.0.0.0/32": {},
	}

	expansions, err = helper.GetExpansion(key)
	require.NoError(t, err)
	require.Equal(t, map[string]struct{}{
		"example1.com": {},
		"240.0.0.0/32": {},
	}, expansions)
}
