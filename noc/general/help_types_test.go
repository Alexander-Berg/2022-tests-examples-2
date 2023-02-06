package macrosutils

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/macrospb"
	"a.yandex-team.ru/noc/macros/pkg/macros/mcerrors"
	"a.yandex-team.ru/noc/macros/pkg/macros/server/serverutils"
)

func TestTypeIsAllowed(t *testing.T) {
	inner := serverutils.NewHelper([]string{"a", "b", "c"})

	helper := &Helper{
		helper: inner,
	}

	allowed := helper.TypeIsAllowed(macrospb.NetMacro, "someone")
	require.True(t, allowed)

	allowed = helper.TypeIsAllowed(macrospb.HostMacro, "someone")
	require.True(t, allowed)

	allowed = helper.TypeIsAllowed(macrospb.AnyMacro, "someone")
	require.False(t, allowed)

	allowed = helper.TypeIsAllowed(macrospb.MixedMacro, "someone")
	require.False(t, allowed)

	allowed = helper.TypeIsAllowed(macrospb.MixedMacro, "a")
	require.True(t, allowed)
}

func TestUpdateTypesByChildMacros(t *testing.T) {
	superuser := "superuser"
	username := "someone"
	children := []string{"_OTHER_MACRO_", "_SECOND_MACRO_"}

	inner := serverutils.NewHelper([]string{superuser, "b", "c"})

	helper := &Helper{
		helper: inner,
	}

	macroType, err := helper.UpdateTypeByChildMacros(macrospb.InvalidMacro, children, username)
	require.Equal(t, macrospb.InvalidMacro, macroType)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrInvalidType, err)

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.NetMacro, children, username)
	require.Equal(t, macrospb.InvalidMacro, macroType)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoTypesOnServer, err)

	helper.types = map[string]macrospb.GoMacroType{
		"_OTHER_MACRO_": macrospb.NetMacro,
	}

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.NetMacro, children, username)
	require.Equal(t, macrospb.InvalidMacro, macroType)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrMacroNotFound("_SECOND_MACRO_"), err)

	helper.types["_SECOND_MACRO_"] = macrospb.HostMacro

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.NetMacro, children, username)
	require.Equal(t, macrospb.InvalidMacro, macroType)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrIncompatibleChildren, err)

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.NetMacro, children, superuser)
	require.Equal(t, macrospb.MixedMacro, macroType)
	require.NoError(t, err)

	helper.types["_SECOND_MACRO_"] = macrospb.NetMacro

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.HostMacro, children, username)
	require.Equal(t, macrospb.InvalidMacro, macroType)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrIncompatibleChildren, err)

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.MixedMacro, children, username)
	require.Equal(t, macrospb.InvalidMacro, macroType)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrIncompatibleChildren, err)

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.NetMacro, children, username)
	require.Equal(t, macrospb.NetMacro, macroType)
	require.NoError(t, err)

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.MixedMacro, children, superuser)
	require.Equal(t, macrospb.MixedMacro, macroType)
	require.NoError(t, err)

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.NetMacro, children, superuser)
	require.Equal(t, macrospb.NetMacro, macroType)
	require.NoError(t, err)

	macroType, err = helper.UpdateTypeByChildMacros(macrospb.HostMacro, children, superuser)
	require.Equal(t, macrospb.MixedMacro, macroType)
	require.NoError(t, err)
}
