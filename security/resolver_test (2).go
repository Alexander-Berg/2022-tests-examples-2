package agroups

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestResolveOwners(t *testing.T) {
	groupsDir := "./testdata/"

	cases := []struct {
		owners   []string
		resolved []string
	}{
		{[]string{"user2", "user1", "g:non_existing_group", "g:testgroup", "user3"}, []string{"user2", "user1", "user3", "groupuser1", "groupuser2"}},
		{[]string{"user1", "user2", "rb:emptygroup", "user3"}, []string{"user1", "user2", "user3"}},
	}

	for _, tc := range cases {
		t.Run(strings.Join(tc.owners, "__"), func(t *testing.T) {
			resolved := ResolveOwners(groupsDir, tc.owners)
			require.Equal(t, tc.resolved, resolved)
		})
	}

}
