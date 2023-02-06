package advsync

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCond(t *testing.T) {
	counter := 0
	lock := NewLock()
	cond := NewCond(lock)

	lock.Lock()
	for i := 0; i < 3; i++ {
		go func() {
			lock.Lock()
			defer lock.Unlock()
			cond.Wait()
			counter++
		}()
	}

	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		lock.Lock()
		defer lock.Unlock()
		require.Error(t, cond.WaitContext(ctx))
		counter++
	}()

	go func() {
		lock.Lock()
		defer lock.Unlock()
		require.NoError(t, cond.WaitContext(context.Background()))
		counter++
	}()

	lock.Unlock()
	advanceTime()
	require.Equal(t, 0, counter)

	cancel()
	advanceTime()
	require.Equal(t, 1, counter)

	cond.Signal()
	advanceTime()
	require.Equal(t, 2, counter)

	cond.Broadcast()
	advanceTime()
	require.Equal(t, 5, counter)
}
