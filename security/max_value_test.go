package metrics

import (
	"sync"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestMaxValueGauge(t *testing.T) {
	var g MaxValue
	c := make(chan struct{}, 1000000)
	const numGoroutines = 10
	const numPush = 10000
	var wg sync.WaitGroup
	wg.Add(numGoroutines)
	// This code models our usage of MaxValue.
	for i := 0; i < numGoroutines; i++ {
		go func() {
			for j := 0; j < numPush; j++ {
				c <- struct{}{}
				g.Report(uint64(len(c)))
			}
			wg.Done()
		}()
	}
	wg.Wait()
	require.Equal(t, uint64(numGoroutines*numPush), g.Get())
}
