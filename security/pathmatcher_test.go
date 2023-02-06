package fim

import (
	"runtime"
	"sort"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestPathMatcher_pathMatches(t *testing.T) {
	_, err := newPathMatcher("category", []string{testPath("**")}, nil)
	require.Error(t, err)

	_, err = newPathMatcher("category", []string{testPath("/**")}, []string{"abc"})
	require.Error(t, err)

	matcher, err := newPathMatcher("category", []string{testPath("/usr/**"), testPath("/etc/*")},
		[]string{testPath("/**.log"), testPath("/usr/bin/*.sh")})
	require.NoError(t, err)
	require.True(t, matcher.pathMatches(testPath("/usr/bin")))
	require.True(t, matcher.pathMatches(testPath("/usr/bin/sh")))
	require.True(t, matcher.pathMatches(testPath("/usr/bin/local/a.sh")))
	require.False(t, matcher.pathMatches(testPath("/usr/bin/a.sh")))
	require.False(t, matcher.pathMatches(testPath("/etc")))
	require.True(t, matcher.pathMatches(testPath("/etc/a")))
	require.False(t, matcher.pathMatches(testPath("/etc/usr/bin")))
	require.False(t, matcher.pathMatches(testPath("/usr/.log")))
	require.False(t, matcher.pathMatches(testPath("/usr/var/log/this.log")))

	matcher, err = newPathMatcher("category", []string{testPath("/**")}, []string{testPath("/var/?/*.log")})
	require.NoError(t, err)
	require.True(t, matcher.pathMatches(testPath("/usr/bin")))
	require.True(t, matcher.pathMatches(testPath("/var/ab/1.log")))
	require.False(t, matcher.pathMatches(testPath("/var/a/1.log")))
	require.False(t, matcher.pathMatches(testPath("/var/a/.log")))
}

func TestPathMatcher_roots(t *testing.T) {
	matcher, err := newPathMatcher("category", []string{
		testPath("/usr/**"),
		testPath("/usr/bin/*"),
		testPath("/usr/share/*.t?t"),
		testPath("/etc/*"),
		testPath("/etc/%"),
		testPath("/etc/service/*"),
		testPath("/etc/service/specific.conf")},
		nil)
	require.NoError(t, err)
	require.Equal(t, []pathRoot{
		{
			isFile:    false,
			path:      testPath("/usr"),
			recursive: true,
		},
		{
			isFile:    false,
			path:      testPath("/usr/bin"),
			recursive: false,
		},
		{
			isFile:    false,
			path:      testPath("/usr/share"),
			recursive: false,
		},
		{
			isFile:    false,
			path:      testPath("/etc"),
			recursive: false,
		},
		{
			isFile:    false,
			path:      testPath("/etc"),
			recursive: false,
		},
		{
			isFile:    false,
			path:      testPath("/etc/service"),
			recursive: false,
		},
		{
			isFile:    true,
			path:      testPath("/etc/service/specific.conf"),
			recursive: false,
		},
	}, matcher.roots)
}

func TestPrepareRoots(t *testing.T) {
	matcher1, err := newPathMatcher("category1", []string{
		testPath("/usr/**"),
		testPath("/usr/bin/*"),
		testPath("/usr/share/*.t?t"),
		testPath("/etc/%"),
		testPath("/etc/service/*"),
		testPath("/etc/service/specific.conf"),
		testPath("/var/log/specific.log")},
		nil)
	require.NoError(t, err)
	matcher2, err := newPathMatcher("category2", []string{
		testPath("/usr/sbin/**"),
		testPath("/etc/*"),
		testPath("/var/log/specific.log")},
		nil)
	require.NoError(t, err)
	roots := prepareRoots([]*pathMatcher{matcher1, matcher2})
	sort.Slice(roots, func(i, j int) bool {
		return roots[i].root.path < roots[j].root.path
	})
	require.Equal(t, []pathRootWithMatchers{
		{
			root:     pathRoot{isFile: false, path: "/etc", recursive: false},
			matchers: []*pathMatcher{matcher1, matcher2},
		},
		{
			root:     pathRoot{isFile: false, path: "/etc/service", recursive: false},
			matchers: []*pathMatcher{matcher1},
		},
		{
			root:     pathRoot{isFile: false, path: "/usr", recursive: true},
			matchers: []*pathMatcher{matcher1, matcher2},
		},
		{
			root:     pathRoot{isFile: true, path: "/var/log/specific.log", recursive: false},
			matchers: []*pathMatcher{matcher1, matcher2},
		},
	}, roots)
}

func testPath(path string) string {
	if runtime.GOOS == "windows" {
		p := strings.ReplaceAll(path, "/", "\\")
		if len(path) > 0 && path[0] == '/' {
			return "C:" + p
		}
		return p
	} else {
		return path
	}
}
