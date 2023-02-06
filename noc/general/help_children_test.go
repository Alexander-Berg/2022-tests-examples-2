package macrosutils

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/macrospb"
	"a.yandex-team.ru/noc/macros/pkg/macros/mcerrors"
	"a.yandex-team.ru/noc/macros/pkg/macros/server/jobsutils"
	"a.yandex-team.ru/noc/macros/pkg/macros/server/serverutils"
)

func TestCheckNoSelfDependant(t *testing.T) {
	helper := &Helper{}

	err := helper.CheckNoSelfDependant("_MACRO_", []string{"example.com", "240.0.0.0/1"})
	require.NoError(t, err)

	err = helper.CheckNoSelfDependant("_MACRO_", []string{"example.com", "_MACRO_", "240.0.0.0/1"})
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrSelfDependant, err)
}

func TestCheckNoCycles(t *testing.T) {
	helper := &Helper{}
	key := &macrospb.Key{}

	err := helper.CheckNoCycles(key, []string{"example.com"})
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrEmptyKey, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	helper.revDeps = map[string]map[string]struct{}{}
	helper.revDeps[macroName] = map[string]struct{}{
		"_OTHER_MACRO_":  {},
		"_SECOND_MACRO_": {},
	}

	err = helper.CheckNoCycles(key, []string{"example.com", "_OTHER_MACRO_", "240.0.0.0/1"})
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrCycleOccurs, err)

	err = helper.CheckNoCycles(key, []string{"example.com", "240.0.0.0/1"})
	require.NoError(t, err)
}

func TestGetNeededChildrenGrants(t *testing.T) {
	username := "someone"
	children := []string{"example.com", "_OTHER_MACRO_", "240.0.0.0/32", "_SECOND_MACRO_"}

	innerHelper := &serverutils.Helper{}
	innerHelper.Update(nil, nil, nil, map[string]map[string]struct{}{})

	helper := &Helper{
		helper: innerHelper,
	}

	neededGrants, err := helper.GetNeededChildrenGrants(children, username)
	require.Nil(t, neededGrants)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoSpecMacrosOnServer, err)

	helper.mostSpecific = map[string]string{}

	neededGrants, err = helper.GetNeededChildrenGrants(children, username)
	require.Nil(t, neededGrants)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoRolesOnServer, err)

	helper.helper.Update(nil, nil, map[string]jobsutils.Roles{}, nil)

	neededGrants, err = helper.GetNeededChildrenGrants(children, username)
	require.Nil(t, neededGrants)
	require.EqualError(t, err, mcerrors.ErrMacroNotFound("_OTHER_MACRO_").Error())

	helper.helper.Update(nil, nil, map[string]jobsutils.Roles{
		"_OTHER_MACRO_": {
			Approvers: map[string]struct{}{
				"a": {},
			},
			Admins: map[string]struct{}{},
		},
		"_SECOND_MACRO_": {
			Approvers: map[string]struct{}{
				username: {},
			},
			Admins: map[string]struct{}{},
		},
	}, nil)
	helper.mostSpecific["240.0.0.0/32"] = "_OTHER_MACRO_"

	neededGrants, err = helper.GetNeededChildrenGrants(children, username)
	require.NoError(t, err)
	require.Equal(t, map[string]string{
		"example.com":   "",
		"_OTHER_MACRO_": "_OTHER_MACRO_",
		"240.0.0.0/32":  "_OTHER_MACRO_",
	}, neededGrants)

	helper.helper.Update(nil, nil, map[string]jobsutils.Roles{
		"_OTHER_MACRO_": {
			Approvers: map[string]struct{}{
				"a": {},
			},
			Admins: map[string]struct{}{},
		},
		"_SECOND_MACRO_": {
			Approvers: map[string]struct{}{
				username: {},
			},
			Admins: map[string]struct{}{},
		},
		"_THIRD_MACRO_": {
			Approvers: map[string]struct{}{
				username: {},
			},
		},
	}, nil)
	helper.mostSpecific["example.com"] = "_THIRD_MACRO_"

	neededGrants, err = helper.GetNeededChildrenGrants(children, username)
	require.NoError(t, err)
	require.Equal(t, map[string]string{
		"_OTHER_MACRO_": "_OTHER_MACRO_",
		"240.0.0.0/32":  "_OTHER_MACRO_",
	}, neededGrants)
}

func TestCheckChildrenGrants(t *testing.T) {
	username := "someone"
	children := []string{"example.com", "_OTHER_MACRO_", "240.0.0.0/32", "_SECOND_MACRO_", "example2.com"}

	innerHelper := &serverutils.Helper{}
	innerHelper.Update(nil, nil, nil, map[string]map[string]struct{}{})

	helper := &Helper{
		helper: innerHelper,
	}

	err := helper.CheckChildrenGrants(children, username)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoSpecMacrosOnServer, err)

	helper.mostSpecific = map[string]string{
		"example.com":  "_THIRD_MACRO_",
		"240.0.0.0/32": "_OTHER_MACRO_",
	}
	helper.helper.Update(nil, nil, map[string]jobsutils.Roles{
		"_OTHER_MACRO_": {
			Approvers: map[string]struct{}{
				"a": {},
			},
			Admins: map[string]struct{}{},
		},
		"_SECOND_MACRO_": {
			Approvers: map[string]struct{}{
				username: {},
			},
			Admins: map[string]struct{}{},
		},
		"_THIRD_MACRO_": {
			Approvers: map[string]struct{}{
				username: {},
			},
		},
	}, nil)

	err = helper.CheckChildrenGrants(children, username)
	require.Error(t, err)
	require.Contains(t, err.Error(), "\"240.0.0.0/32\":\"the most specific macro is _OTHER_MACRO_, you need to be its or its parent's approver\"")
	require.Contains(t, err.Error(), "\"_OTHER_MACRO_\":\"you need to be an approver of this macro\"")
	require.Contains(t, err.Error(), "\"example2.com\":\"no such child in already existing macros, you need permission from NOC\"")
	require.NotContains(t, err.Error(), "_SECOND_MACRO_")
	require.NotContains(t, err.Error(), "example.com")

	helper.helper.Update(nil, nil, map[string]jobsutils.Roles{
		"_OTHER_MACRO_": {
			Approvers: map[string]struct{}{
				"a":      {},
				username: {},
			},
			Admins: map[string]struct{}{},
		},
		"_SECOND_MACRO_": {
			Approvers: map[string]struct{}{
				username: {},
			},
			Admins: map[string]struct{}{},
		},
		"_THIRD_MACRO_": {
			Approvers: map[string]struct{}{
				username: {},
			},
		},
	}, nil)
	helper.mostSpecific["example2.com"] = "_OTHER_MACRO_"

	err = helper.CheckChildrenGrants(children, username)
	require.NoError(t, err)
}
