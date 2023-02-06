package advsync

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestWaitgroup(t *testing.T) {
	counter := 0
	until1 := NewUntil()
	until2 := NewUntil()
	lock := NewLock()

	waitGroup := NewWaitGroup()
	secondaryWaitGroup1 := NewWaitGroup()
	secondaryWaitGroup2 := NewWaitGroup()

	for i := 0; i < 3; i++ {
		go func() {
			waitGroup.Add(1)
			defer waitGroup.Done()
			secondaryWaitGroup1.Add(1)
			defer secondaryWaitGroup1.Done()
			until1.Wait()
			lock.Lock()
			defer lock.Unlock()
			counter++
		}()
	}
	for i := 0; i < 2; i++ {
		go func() {
			waitGroup.Add(1)
			defer waitGroup.Done()
			secondaryWaitGroup2.Add(1)
			defer secondaryWaitGroup2.Done()
			until2.Wait()
			lock.Lock()
			defer lock.Unlock()
			counter++
		}()
	}

	advanceTime()
	require.Equal(t, 0, counter)
	require.Equal(t, 5, waitGroup.Count())

	until1.Fulfill()
	secondaryWaitGroup1.Wait()
	require.Equal(t, 3, counter)
	require.Equal(t, 2, waitGroup.Count())

	until2.Fulfill()
	secondaryWaitGroup2.Wait()
	require.Equal(t, 5, counter)
	require.Equal(t, 0, waitGroup.Count())
	secondaryWaitGroup1.Wait()
	secondaryWaitGroup2.Wait()
	waitGroup.Wait()
}
