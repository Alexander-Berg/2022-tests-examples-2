//go:build windows
// +build windows

package sshclient_test

import "a.yandex-team.ru/security/skotty/skotty/pkg/sshutil/sshclient"

var bestClient = sshclient.ClientKindWin32OpenSSH

var socketName = "some-socket-Win32-OpenSSH"
