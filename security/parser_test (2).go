package gitconfig_test

import (
	"fmt"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/security/libs/go/gitconfig"
)

func TestSimple(t *testing.T) {
	config := `
; This is a comment !\"\#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcd"
# This is another comment !\"\#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcd"
[user]
	name = Andrew Krasichkov
	email = buglloc@yandex.ru
[push]
	default = simple
`
	cfg := strings.NewReader(config)
	parsed, err := gitconfig.Parse(cfg)
	if !assert.NoError(t, err, "oops, parsed fail: %s", err) {
		return
	}
	fmt.Println(parsed)
	assert.Equal(t, "Andrew Krasichkov", parsed["user.name"])
	assert.Equal(t, "buglloc@yandex.ru", parsed["user.email"])
	assert.Equal(t, "simple", parsed["push.default"])
}

func TestHuge(t *testing.T) {
	config := `
# https://gist.github.com/pksunkara/988716
[diff]
[sequence]
	editor = interactive-rebase-tool
[alias]
	ams = am --skip
	#############
	b = branch
	ba = branch -a
	ours = "!f() { git checkout --ours \n $@ && git add $@; }; f"
	subrepo = !sh -c 'git filter-branch --prune-empty --subdirectory-filter $1 master' \
--name-only --refs=refs/heads/*
`
	cfg := strings.NewReader(config)
	parsed, err := gitconfig.Parse(cfg)
	if !assert.NoError(t, err, "oops, parsed fail: %s", err) {
		return
	}

	assert.Equal(t, "interactive-rebase-tool", parsed["sequence.editor"])
	assert.Equal(t, "am --skip", parsed["alias.ams"])
	assert.Equal(t, "branch -a", parsed["alias.ba"])
	assert.Equal(t, "!f() { git checkout --ours \n $@ && git add $@; }; f", parsed["alias.ours"])
	assert.Equal(t,
		"!sh -c 'git filter-branch --prune-empty --subdirectory-filter $1 master' --name-only --refs=refs/heads/*",
		parsed["alias.subrepo"],
	)
}

func TestRepo(t *testing.T) {
	config := `
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[remote "origin"]
	url = ssh://git@bb.yandex-team.ru/cloud/ydb-go.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
	remote = origin
	merge = refs/heads/master
`
	cfg := strings.NewReader(config)
	parsed, err := gitconfig.Parse(cfg)
	if !assert.NoError(t, err, "oops, parsed fail: %s", err) {
		return
	}

	assert.Equal(t, "ssh://git@bb.yandex-team.ru/cloud/ydb-go.git", parsed["remote.origin.url"])
	assert.Equal(t, "origin", parsed["branch.master.remote"])
}
