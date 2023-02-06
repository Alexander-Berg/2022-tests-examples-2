package fim

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestBandwidthLimiter(t *testing.T) {
	var now time.Time
	limiter := newBandWidthLimiterWithNow(1000, func() time.Time {
		return now
	})

	require.Equal(t, time.Duration(0), limiter.computeSleepFor(1))
	require.Equal(t, 1*time.Millisecond, limiter.computeSleepFor(1))
	require.Equal(t, 2*time.Millisecond, limiter.computeSleepFor(998))
	require.Equal(t, time.Second, limiter.computeSleepFor(1000))

	// Wait enough time after the previous requests.
	now = now.Add(2 * time.Second)
	require.Equal(t, time.Duration(0), limiter.computeSleepFor(10))
	require.Equal(t, 10*time.Millisecond, limiter.computeSleepFor(1))
}
