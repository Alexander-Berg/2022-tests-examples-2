package serverutils

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/macrospb"
	"a.yandex-team.ru/noc/macros/pkg/macros/mcerrors"
	"a.yandex-team.ru/noc/macros/pkg/macros/server/jobsutils"
)

func TestIsSuperUser(t *testing.T) {
	helper := &Helper{
		superUsers: map[string]struct{}{
			"a": {},
			"b": {},
			"c": {},
		},
	}

	require.True(t, helper.IsSuperUser("a"))
	require.True(t, helper.IsSuperUser("b"))
	require.True(t, helper.IsSuperUser("c"))
	require.False(t, helper.IsSuperUser("anonymous"))
	require.False(t, helper.IsSuperUser("ab"))
	require.False(t, helper.IsSuperUser(""))
}

func TestGetRoles(t *testing.T) {
	helper := &Helper{}
	key := &macrospb.Key{}

	roles, err := helper.GetRoles(nil, macrospb.RoleApprover, NotExpanded)
	require.Nil(t, roles)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrKeyNotSpecified, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	roles, err = helper.GetRoles(key, macrospb.RoleApprover, NotExpanded)
	require.Nil(t, roles)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoRolesOnServer, err)

	helper.roles = map[string]jobsutils.Roles{}

	roles, err = helper.GetRoles(key, macrospb.RoleAdmin, NotExpanded)
	require.Nil(t, roles)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrMacroNotFound(macroName), err)

	helper.roles[macroName] = jobsutils.Roles{
		Approvers: map[string]struct{}{
			"approver1": {},
			"approver2": {},
		},
		Admins: map[string]struct{}{
			"admin1": {},
			"admin2": {},
		},
	}

	roles, err = helper.GetRoles(key, macrospb.RoleApprover, NotExpanded)
	require.NoError(t, err)
	require.Equal(t, map[string]struct{}{
		"approver1": {},
		"approver2": {},
	}, roles)

	roles, err = helper.GetRoles(key, macrospb.RoleAdmin, NotExpanded)
	require.NoError(t, err)
	require.Equal(t, map[string]struct{}{
		"admin1": {},
		"admin2": {},
	}, roles)

	roles, err = helper.GetRoles(key, "invalid role", NotExpanded)
	require.Nil(t, roles)
	require.Error(t, err)
	require.Contains(t, err.Error(), "invalid role type: invalid role")
}

func TestIsAdmin(t *testing.T) {
	username := "someone"
	group := "group"

	helper := &Helper{groupsToPeople: map[string]map[string]struct{}{}}
	key := &macrospb.Key{}

	isAdmin, err := helper.HasRole(nil, username, macrospb.RoleAdmin)
	require.False(t, isAdmin)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrKeyNotSpecified, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	isAdmin, err = helper.HasRole(key, username, macrospb.RoleAdmin)
	require.False(t, isAdmin)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoRolesOnServer, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{}, nil)

	isAdmin, err = helper.HasRole(key, username, macrospb.RoleAdmin)
	require.False(t, isAdmin)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrMacroNotFound(macroName), err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	isAdmin, err = helper.HasRole(key, username, macrospb.RoleAdmin)
	require.NoError(t, err)
	require.False(t, isAdmin)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
				username: {},
			},
		},
	}, nil)

	isAdmin, err = helper.HasRole(key, username, macrospb.RoleAdmin)
	require.NoError(t, err)
	require.True(t, isAdmin)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
				group:    {},
			},
		},
	}, map[string]map[string]struct{}{
		group: {
			username: {},
		},
	})

	isAdmin, err = helper.HasRole(key, username, macrospb.RoleAdmin)
	require.NoError(t, err)
	require.True(t, isAdmin)
}

func TestIsApprover(t *testing.T) {
	username := "someone"
	group := "group"

	helper := &Helper{groupsToPeople: map[string]map[string]struct{}{}}
	key := &macrospb.Key{}

	isApprover, err := helper.HasRole(nil, username, macrospb.RoleApprover)
	require.False(t, isApprover)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrKeyNotSpecified, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	isApprover, err = helper.HasRole(key, username, macrospb.RoleApprover)
	require.False(t, isApprover)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoRolesOnServer, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{}, nil)

	isApprover, err = helper.HasRole(key, username, macrospb.RoleApprover)
	require.False(t, isApprover)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrMacroNotFound(macroName), err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	isApprover, err = helper.HasRole(key, username, macrospb.RoleApprover)
	require.NoError(t, err)
	require.False(t, isApprover)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
				username:    {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	isApprover, err = helper.HasRole(key, username, macrospb.RoleApprover)
	require.NoError(t, err)
	require.True(t, isApprover)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
				group:       {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, map[string]map[string]struct{}{
		group: {
			username: {},
		},
	})

	isApprover, err = helper.HasRole(key, username, macrospb.RoleApprover)
	require.NoError(t, err)
	require.True(t, isApprover)
}

func TestCheckMacroAdminPermissions(t *testing.T) {
	username := "someone"

	helper := &Helper{groupsToPeople: map[string]map[string]struct{}{}}
	key := &macrospb.Key{}

	err := helper.CheckMacroPermissions(nil, username, macrospb.RoleAdmin)
	require.Equal(t, mcerrors.ErrKeyNotSpecified, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleAdmin)
	require.Equal(t, mcerrors.ErrNoRolesOnServer, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleAdmin)
	require.Equal(t, mcerrors.ErrMacroNotFound(macroName), err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleAdmin)
	require.Equal(t, mcerrors.ErrNotAdmin, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
				username: {},
			},
		},
	}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleAdmin)
	require.NoError(t, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleAdmin)
	require.Equal(t, mcerrors.ErrNotAdmin, err)

	helper.superUsers = map[string]struct{}{username: {}}

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleAdmin)
	require.NoError(t, err)
}

func TestCheckMacroApproverPermissions(t *testing.T) {
	username := "someone"

	helper := &Helper{
		groupsToPeople: map[string]map[string]struct{}{},
	}
	key := &macrospb.Key{}

	err := helper.CheckMacroPermissions(nil, username, macrospb.RoleApprover)
	require.Equal(t, mcerrors.ErrKeyNotSpecified, err)

	macroName := "_SOME_MACRO_"
	key.Name = macrospb.SerializeStringValue(&macroName)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleApprover)
	require.Equal(t, mcerrors.ErrNoRolesOnServer, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleApprover)
	require.Equal(t, mcerrors.ErrMacroNotFound(macroName), err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleApprover)
	require.Equal(t, mcerrors.ErrNotApprover, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
				username:    {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleApprover)
	require.NoError(t, err)

	helper.Update(nil, nil, map[string]jobsutils.Roles{
		macroName: {
			Approvers: map[string]struct{}{
				"approver1": {},
				"approver2": {},
			},
			Admins: map[string]struct{}{
				"admin1": {},
				"admin2": {},
			},
		},
	}, nil)

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleApprover)
	require.Equal(t, mcerrors.ErrNotApprover, err)

	helper.superUsers = map[string]struct{}{username: {}}

	err = helper.CheckMacroPermissions(key, username, macrospb.RoleApprover)
	require.NoError(t, err)
}
