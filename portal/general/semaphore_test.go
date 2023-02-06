package advsync

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestSemaphore(t *testing.T) {
	semaphore := NewSemaphore(2)
	counter := 0
	lock := NewLock()
	starter := make(chan struct{})

	for i := 0; i < 3; i++ {
		go func() {
			<-starter
			semaphore.Up()
			lock.Lock()
			defer lock.Unlock()
			counter++
		}()
	}

	close(starter)
	advanceTime()
	require.Equal(t, 2, counter)

	semaphore.Down()
	advanceTime()
	require.Equal(t, 3, counter)
	semaphore.Down()
	semaphore.Down()
	defer func() {
		recovered := recover()
		require.NotNil(t, recovered)
		require.Equal(t, semaphoreDownBottomError{}, recovered)
	}()
	semaphore.Down()
}
