package daemon_test

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/libs/go/daemon"
)

func TestPassInfo(t *testing.T) {
	type Data struct {
		Foo string
		Bar int
	}

	expectedData := Data{Foo: "foo", Bar: 31337}
	d := daemon.NewDaemon("passdata")
	if d.IsParent() {
		child, err := d.StartChild(context.Background())
		require.NoError(t, err)

		t.Logf("child started with PID: %d\n", child.PID())
		assert.Greater(t, child.PID(), 0)

		var actualData Data
		err = child.Unmarshal(&actualData)
		require.NoError(t, err)

		require.EqualValues(t, expectedData, actualData)
		return
	}

	err := d.NotifyStarted(expectedData)
	require.NoError(t, err)
}

func TestPassError(t *testing.T) {
	d := daemon.NewDaemon("passerr")
	if d.IsParent() {
		child, err := d.StartChild(context.Background())
		require.Error(t, err)
		require.Nil(t, child)
		require.Contains(t, err.Error(), "ooops")
		return
	}

	err := d.NotifyError(errors.New("ooops"))
	require.Error(t, err)
}
