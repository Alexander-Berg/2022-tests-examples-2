package task

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func getWithTimeout(c <-chan int, timeout time.Duration) (int, error) {
	select {
	case val := <-c:
		return val, nil
	case <-time.NewTimer(timeout).C:
		return 0, fmt.Errorf("timeout reached")
	}
}

func setWithTimeout(c chan<- int, val int, timeout time.Duration) error {
	select {
	case c <- val:
		return nil
	case <-time.NewTimer(timeout).C:
		return fmt.Errorf("timeout reached")
	}
}

func waitWithTimeout(c <-chan bool, timeout time.Duration) (bool, error) {
	select {
	case failed := <-c:
		return failed, nil
	case <-time.NewTimer(timeout).C:
		return false, fmt.Errorf("timeout reached")
	}
}

func TestRegularTask_SuccessfulRun(t *testing.T) {
	counter := 0
	in := make(chan int)
	out := make(chan int)

	task := NewRegularTask(
		func() (Status, error) {
			val := <-in
			counter += val
			out <- counter

			return StatusSuccess, nil
		}, RegularTaskSettings{
			Period: time.Millisecond,
		})

	runOnce := func(val int, timeout time.Duration) error {
		err := setWithTimeout(in, val, timeout)
		if err != nil {
			return err
		}

		res, err := getWithTimeout(out, timeout)
		if err != nil {
			return err
		}

		require.Equal(t, counter, res)

		return nil
	}

	require.Equal(t, 0, counter)
	require.NoError(t, runOnce(10, time.Second))
	require.Equal(t, 10, counter)
	require.NoError(t, runOnce(15, time.Second))
	require.Equal(t, 25, counter)

	task.Stop()
	_ = runOnce(0, 100*time.Millisecond)

	failed, err := waitWithTimeout(task.StopHook(), time.Second)
	require.NoError(t, err)
	require.Equal(t, false, failed)

	require.Error(t, runOnce(10, 100*time.Millisecond))
	require.Equal(t, 25, counter)
}

func TestRegularTask_RunNow(t *testing.T) {
	counter := 0
	out := make(chan int)

	task := NewRegularTask(
		func() (Status, error) {
			counter++
			out <- counter

			return StatusSuccess, nil
		}, RegularTaskSettings{
			Period: 24 * time.Hour,
		})

	_, err := getWithTimeout(out, 100*time.Millisecond)
	require.Error(t, err)

	task.RunNow()
	res, err := getWithTimeout(out, time.Second)
	require.NoError(t, err)
	require.Equal(t, 1, res)

	_, err = getWithTimeout(out, 100*time.Millisecond)
	require.Error(t, err)

	task.Stop()

	failed, err := waitWithTimeout(task.StopHook(), time.Second)
	require.NoError(t, err)
	require.Equal(t, false, failed)

	task.RunNow()
	_, err = getWithTimeout(out, 100*time.Millisecond)
	require.Error(t, err)

	require.Equal(t, 1, counter)
}

func TestRegularTask_FailedRun(t *testing.T) {
	task := NewRegularTask(
		func() (Status, error) {
			return -1, fmt.Errorf("something bad happend")
		}, RegularTaskSettings{
			Period: 24 * time.Hour,
		}).RunNow()

	failed, err := waitWithTimeout(task.StopHook(), time.Second)
	require.NoError(t, err)
	require.Equal(t, true, failed)
}

func TestRegularTask_ContextCancel(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())

	task := NewRegularTask(
		func() (Status, error) {
			return StatusSuccess, nil
		}, RegularTaskSettings{
			Period: 24 * time.Hour,
			Ctx:    ctx,
		})

	cancel()

	failed, err := waitWithTimeout(task.StopHook(), time.Second)
	require.NoError(t, err)
	require.Equal(t, false, failed)
}
