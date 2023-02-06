package advsync

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestLock(t *testing.T) {
	lock := NewLock()
	flag := false

	lock.Lock()

	go func() {
		lock.Lock()
		defer lock.Unlock()
		flag = true
	}()
	advanceTime()
	require.False(t, flag)

	lock.Unlock()
	advanceTime()
	require.True(t, flag)
}
