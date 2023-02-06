package serverutils

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/macros/pkg/macros/mcerrors"
)

func TestExpandGroups(t *testing.T) {
	server := &Helper{}

	people, err := server.ExpandGroups(nil)
	require.Nil(t, people)
	require.Error(t, err)
	require.Equal(t, mcerrors.ErrNoGroupsToPeople, err)

	server.groupsToPeople = map[string]map[string]struct{}{
		"group1": {
			"person1": {},
			"person2": {},
		},
		"group2": {
			"person3": {},
			"person1": {},
		},
		"group3": {
			"person1": {},
			"person2": {},
			"person3": {},
		},
		"group4": {
			"person1": {},
			"person4": {},
		},
	}

	people, err = server.ExpandGroups(nil)
	require.NoError(t, err)
	require.Equal(t, map[string]struct{}{}, people)

	groups := map[string]struct{}{
		"group1":  {},
		"group2":  {},
		"group3":  {},
		"person5": {},
	}
	people, err = server.ExpandGroups(groups)
	require.NoError(t, err)
	require.Equal(t, map[string]struct{}{
		"person1": {},
		"person2": {},
		"person3": {},
		"person5": {},
	}, people)
}
