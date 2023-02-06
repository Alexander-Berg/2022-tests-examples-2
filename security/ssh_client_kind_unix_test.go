//go:build !windows
// +build !windows

package sshclient_test

import (
	"a.yandex-team.ru/security/skotty/skotty/pkg/sshutil/sshclient"
)

var bestClient = sshclient.ClientKindOpenSSH

var socketName = "some-socket"
