package resps

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
)

func testAuthsAggregatedEntryKey(entry AuthsAggregatedEntry) string {
	return fmt.Sprintf("%d_%s_%s", entry.Count, entry.Auth.AuthType, entry.Auth.Status)
}

func slicesUnorderedEqual[Entry any](t *testing.T, expected, actual []Entry, key func(Entry) string, msgAndArgs ...interface{}) {
	convertToComparable := func(entries []Entry) map[string]Entry {
		res := make(map[string]Entry)
		for _, entry := range entries {
			res[key(entry)] = entry
		}
		return res
	}

	require.Equal(t, convertToComparable(expected), convertToComparable(actual), msgAndArgs...)
}

func TestAuthsAggregatedToList(t *testing.T) {
	cases := []struct {
		input  AuthsAggregated
		output []AuthsAggregatedEntry
	}{
		{
			input: AuthsAggregated{
				AuthItem{
					AuthType: "foo",
					Status:   "kek",
				}: 1,
				AuthItem{
					AuthType: "bar",
					Status:   "kek",
				}: 2,
				AuthItem{
					AuthType: "bar",
					Status:   "lol",
				}: 3,
			},
			output: []AuthsAggregatedEntry{
				{
					Count: 1,
					Auth: &AuthItem{
						AuthType: "foo",
						Status:   "kek",
					},
				},
				{
					Count: 2,
					Auth: &AuthItem{
						AuthType: "bar",
						Status:   "kek",
					},
				},
				{
					Count: 3,
					Auth: &AuthItem{
						AuthType: "bar",
						Status:   "lol",
					},
				},
			},
		},
	}

	for idx, c := range cases {
		slicesUnorderedEqual(t, c.output, c.input.ToList(), testAuthsAggregatedEntryKey, idx)
	}
}

func TestAuthsRuntimeAggregatedBuilder(t *testing.T) {
	type builderEntry struct {
		timestamp uint64
		item      *AuthItem
	}

	cases := []struct {
		width    uint64
		entries  []builderEntry
		expected []AuthsRuntimeAggregatedEntry
	}{
		{
			width: 100,
			entries: []builderEntry{
				{
					timestamp: 100500,
					item: &AuthItem{
						AuthType: "foo",
						Status:   "kek",
					},
				},
				{
					timestamp: 100499,
					item: &AuthItem{
						AuthType: "foo",
						Status:   "kek",
					},
				},
				{
					timestamp: 100489,
					item: &AuthItem{
						AuthType: "bar",
						Status:   "lol",
					},
				},
				{
					timestamp: 100479,
					item: &AuthItem{
						AuthType: "foo",
						Status:   "kek",
					},
				},
				{
					timestamp: 100000,
					item: &AuthItem{
						AuthType: "bar",
						Status:   "lol",
					},
				},
			},
			expected: []AuthsRuntimeAggregatedEntry{
				{
					Timestamp: 100500,
					Auths: []AuthsAggregatedEntry{
						{
							Count: 1,
							Auth: &AuthItem{
								AuthType: "foo",
								Status:   "kek",
							},
						},
					},
				},
				{
					Timestamp: 100400,
					Auths: []AuthsAggregatedEntry{
						{
							Count: 1,
							Auth: &AuthItem{
								AuthType: "bar",
								Status:   "lol",
							},
						},
						{
							Count: 2,
							Auth: &AuthItem{
								AuthType: "foo",
								Status:   "kek",
							},
						},
					},
				},
				{
					Timestamp: 100000,
					Auths: []AuthsAggregatedEntry{
						{
							Count: 1,
							Auth: &AuthItem{
								AuthType: "bar",
								Status:   "lol",
							},
						},
					},
				},
			},
		},
	}

	for idx, c := range cases {
		builder := NewAuthsRuntimeAggregatedBuilder(c.width)
		for _, entry := range c.entries {
			builder.Collect(entry.timestamp, entry.item)
		}
		res := builder.Finish()

		require.Equal(t, len(c.expected), len(res), idx)
		for eidx := range res {
			require.Equal(t, c.expected[eidx].Timestamp, res[eidx].Timestamp, idx, eidx)
			slicesUnorderedEqual(t, c.expected[eidx].Auths, res[eidx].Auths, testAuthsAggregatedEntryKey, idx, eidx)
		}
	}
}
