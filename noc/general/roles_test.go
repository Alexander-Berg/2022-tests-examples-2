package jobsutils

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCheckAllAdminsAreApprovers(t *testing.T) {
	roles := map[string]Roles{}
	err := CheckAllAdminsAreApprovers(roles)
	require.NoError(t, err)

	roles = nil
	err = CheckAllAdminsAreApprovers(roles)
	require.NoError(t, err)

	roles = map[string]Roles{
		macroOne: {
			Approvers: map[string]struct{}{
				personOne: {},
			},
			Admins: map[string]struct{}{},
		},
	}
	err = CheckAllAdminsAreApprovers(roles)
	require.NoError(t, err)

	roles = map[string]Roles{
		macroOne: {
			Approvers: map[string]struct{}{
				personOne: {},
			},
			Admins: map[string]struct{}{
				personOne: {},
				personTwo: {},
			},
		},
	}
	err = CheckAllAdminsAreApprovers(roles)
	require.Error(t, err)
	require.Equal(t, "some admins of macro "+macroOne+" are not approvers", err.Error())
}

func TestEnsureAllMacrosHaveRoles(t *testing.T) {
	expansions := map[string]map[string]struct{}{
		macroOne: {
			sampleHostOne: {},
		},
		macroTwo: {},
		macroThree: {
			sampleNetOneIP: {},
		},
	}
	roles := map[string]Roles{
		macroOne: {
			Approvers: map[string]struct{}{
				personOne: {},
			},
			Admins: map[string]struct{}{},
		},
	}
	EnsureAllMacrosHaveRoles(roles, expansions)
	for macro := range expansions {
		_, ok := roles[macro]
		require.True(t, ok)
	}
}

func TestApplyParentsGrantsToChildren(t *testing.T) {
	rolesSpec := map[string]Roles{
		macroOne: {
			Approvers: map[string]struct{}{
				personOne: {},
				personTwo: {},
			},
			Admins: map[string]struct{}{},
		},
		macroTwo: {
			Approvers: map[string]struct{}{
				personTwo:   {},
				personThree: {},
			},
			Admins: map[string]struct{}{
				personTwo: {},
			},
		},
		macroThree: {
			Approvers: map[string]struct{}{},
			Admins: map[string]struct{}{
				personFour: {},
			},
		},
	}

	revDeps := map[string]map[string]struct{}{
		macroOne: {},
		macroTwo: {},
		macroThree: {
			macroFour: {},
		},
	}
	allRoles, err := ApplyParentsGrantsToChildren(rolesSpec, revDeps)
	require.Nil(t, allRoles)
	require.Error(t, err)
	require.Equal(t, "macro "+macroFour+" is a key in revDeps but not in roles", err.Error())

	revDeps = map[string]map[string]struct{}{
		macroOne: {
			macroTwo: {},
		},
		macroTwo: {},
		macroThree: {
			macroOne: {},
			macroTwo: {},
		},
	}
	allRoles, err = ApplyParentsGrantsToChildren(rolesSpec, revDeps)
	require.NoError(t, err)
	require.Equal(t, map[string]Roles{
		macroOne: {
			Approvers: map[string]struct{}{
				personOne:   {},
				personTwo:   {},
				personThree: {},
			},
			Admins: map[string]struct{}{
				personTwo: {},
			},
		},
		macroTwo: {
			Approvers: map[string]struct{}{
				personTwo:   {},
				personThree: {},
			},
			Admins: map[string]struct{}{
				personTwo: {},
			},
		},
		macroThree: {
			Approvers: map[string]struct{}{
				personOne:   {},
				personTwo:   {},
				personThree: {},
			},
			Admins: map[string]struct{}{
				personTwo:  {},
				personFour: {},
			},
		},
	}, allRoles)
}
