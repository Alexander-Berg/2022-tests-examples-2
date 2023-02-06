package policy_test

import (
	"bytes"
	"io/ioutil"
	"path"
	"path/filepath"
	"sort"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/test/yatest"
	"a.yandex-team.ru/security/yadi/libs/policy"
)

type (
	recordType int
	record     struct {
		recordType
		content string
	}
)

const (
	allowType recordType = iota
	denyType
	denyAll
	commentType
)

func TestPolicy(t *testing.T) {
	var cases = []struct {
		contrib string
		records []record
		out     string
	}{
		{"contrib/foo", []record{
			{allowType, "a/c"},
			{allowType, "a/b"},
			{allowType, "a/a"},
			{denyType, "x/y/z"},
			{allowType, "b/c/d"},
			{commentType, "comment 1"},
			{commentType, "comment 2"},
			{denyAll, ""},
		},
			`
# comment 1
# comment 2
ALLOW a/a -> contrib/foo
ALLOW a/b -> contrib/foo
ALLOW a/c -> contrib/foo
ALLOW b/c/d -> contrib/foo
DENY .* -> contrib/foo
`,
		},
	}

	for _, tc := range cases {
		t.Run(tc.contrib, func(t *testing.T) {
			p := policy.NewPolicy(tc.contrib)
			for _, record := range tc.records {
				switch record.recordType {
				case allowType:
					p.Allow(record.content)
				case denyType:
					p.Deny(record.content)
				case commentType:
					p.Comment(record.content)
				case denyAll:
					p.DenyAll()
				default:
					continue
				}
			}
			assert.Equal(t, p.String(), tc.out)
		})
	}
}

func TestRead(t *testing.T) {
	origPolicy, err := ioutil.ReadFile(testDataPath(t, "java.policy"))
	require.NoError(t, err)

	// skip policy header
	parts := strings.SplitN(string(origPolicy), "\n\n", 2)
	require.Equal(t, 2, len(parts))

	expectedBody := parts[1]

	policyMap, err := policy.Read(bytes.NewReader(origPolicy))
	require.NoError(t, err)

	type contribPolicy struct {
		policy  policy.Policy
		contrib string
	}

	testPolicies := make([]contribPolicy, 0, len(policyMap))
	for contrib, p := range policyMap {
		testPolicies = append(testPolicies, contribPolicy{
			policy:  *p,
			contrib: contrib,
		})
	}
	sort.Slice(testPolicies, func(i, j int) bool {
		return testPolicies[i].contrib < testPolicies[j].contrib
	})

	testPolicyData := strings.Builder{}
	for _, tp := range testPolicies {
		testPolicyData.WriteString(tp.policy.String())
	}

	require.Equal(t, expectedBody, testPolicyData.String())
}

func testDataPath(t *testing.T, requiredPath string) string {
	arcadiaPath := path.Join("security/yadi/libs/policy/testdata", requiredPath)
	targetFile, err := filepath.Abs(yatest.SourcePath(arcadiaPath))
	require.NoError(t, err)
	return targetFile
}
