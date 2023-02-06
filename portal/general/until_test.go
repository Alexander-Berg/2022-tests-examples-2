package advsync

import (
	"context"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestUntil(t *testing.T) {
	until := NewUntil()
	doneViaWait := false
	lock := NewLock()

	go func() {
		lock.Lock()
		until.Wait()
		defer lock.Unlock()
		doneViaWait = true
	}()

	advanceTime()
	require.Equal(t, false, doneViaWait)
	select {
	case <-until.Done():
		t.Error("done before expected")
	default:
	}

	until.Fulfill()

	select {
	case <-until.Done():
	default:
		t.Error("not done after expected")
	}

	lock.Lock()
	require.Equal(t, true, doneViaWait)
	lock.Unlock()

	oldDone := until.Done()
	until.Prolong()

	select {
	case <-oldDone:
	default:
		t.Error("old done not done after fulfilling and prolonging")
	}

	select {
	case <-until.Done():
		t.Error("done after being prolonged but not yet fulfilled")
	default:
	}

	ctx, cancelCtx := context.WithTimeout(context.Background(), -time.Second)
	err := until.WaitContext(ctx)
	cancelCtx()
	require.Error(t, err)

	until.Fulfill()

	err = until.WaitContext(context.Background())
	require.NoError(t, err)

	select {
	case <-oldDone:
	default:
		t.Error("old not done after fulfilling")
	}

	select {
	case <-until.Done():
	default:
		t.Error("not done after fulfilling")
	}
}
