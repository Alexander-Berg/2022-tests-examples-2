package metrics

import (
	"sync"
	"testing"

	"github.com/stretchr/testify/require"
)

func fillHistogram(h *RequestHistogram, maxRange int64) {
	var wg sync.WaitGroup
	wg.Add(10)
	for j := 0; j < 10; j++ {
		go func() {
			for i := int64(0); i < 100000; i++ {
				h.Add(i % maxRange)
			}
			wg.Done()
		}()
	}
	wg.Wait()
}

func testHistogram(t *testing.T, h *RequestHistogram, maxRange int64) {
	p50, p95, p99 := h.StandardQuantiles()
	require.True(t, p50 < p95)
	require.True(t, p95 <= p99)
	require.True(t, p50 > int64(float64(maxRange)*0.4))
	require.True(t, p50 > int64(float64(maxRange)*0.4))
	require.True(t, p50 < int64(float64(maxRange)*0.6))
	require.True(t, p95 > int64(float64(maxRange)*0.8))
	require.True(t, p95 < maxRange)
	require.True(t, p99 > int64(float64(maxRange)*0.9))
	require.True(t, p99 <= maxRange)
}

func TestRequestHistogram(t *testing.T) {
	h := NewRequestHistogram()
	fillHistogram(h, 100)
	testHistogram(t, h, 100)

	// Fill the histogram with values, but do not compute the quantiles, test that we "clear" the old values from the
	// previous test.
	fillHistogram(h, 1000)
	h.StandardQuantiles()
	fillHistogram(h, 1000)
	h.StandardQuantiles()

	testHistogram(t, h, 1000)
}
