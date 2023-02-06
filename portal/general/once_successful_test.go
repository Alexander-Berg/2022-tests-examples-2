package advsync

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestOnceSuccessful(t *testing.T) {
	counter := 0
	onceSuccessful := NewOnceSuccessful()
	lock := NewLock()

	failClosure := func() error {
		lock.Lock()
		defer lock.Unlock()
		counter++
		return fmt.Errorf("")
	}

	successClosure := func() error {
		lock.Lock()
		defer lock.Unlock()
		counter++
		return nil
	}

	wrappedClosure := func(f func() error, expectError bool) {
		err := onceSuccessful.Do(f)
		if expectError {
			require.Error(t, err)
		} else {
			require.NoError(t, err)
		}
	}

	lock.Lock()
	go wrappedClosure(failClosure, true)
	advanceTime()
	require.Equal(t, 0, counter)
	go wrappedClosure(successClosure, false)
	go wrappedClosure(successClosure, false)
	advanceTime()
	require.Equal(t, 0, counter)

	lock.Unlock()
	advanceTime()
	require.Equal(t, 2, counter)

	go wrappedClosure(successClosure, false)
	advanceTime()
	require.Equal(t, 2, counter)
}
