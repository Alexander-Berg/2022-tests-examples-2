package sshclient_test

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/pkg/sshutil/sshclient"
)

func TestBestClient(t *testing.T) {
	require.Equal(t, bestClient, sshclient.BestClient())
}

func TestBestClient_sockName(t *testing.T) {
	require.Equal(t, socketName, sshclient.BestClient().SocketName("some-socket"))
}
