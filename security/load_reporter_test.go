package metrics

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestLoadReporter(t *testing.T) {
	r := &LoadReporter{
		Period:         time.Minute,
		BucketInterval: 0,
	}
	r.ReportWork(time.Second * 15)
	r.ReportWork(time.Second * 15)
	require.Equal(t, 0.5, r.GetAverage())
}

func TestLoadReporterBatch(t *testing.T) {
	r := &LoadReporter{
		Period:         time.Minute,
		BucketInterval: time.Minute,
	}
	r.ReportWork(time.Second * 15)
	r.ReportWork(time.Second * 15)
	require.Equal(t, 0.5, r.GetAverage())
}
