package advsync

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestDispatcher(t *testing.T) {
	dispatcher := NewDispatcher()

	dispatcher.Lock()

	taskTaken := false
	taskStarted := false
	taskCancelled := false

	go func() {
		taskTaken = false
		taskStarted = false
		taskCancelled = false
		task, ok := dispatcher.NewTask()
		taskTaken = ok
		if !ok {
			return
		}
		defer task.Finish()
		select {
		case <-task.Started():
			taskStarted = true
		case <-task.Cancelled():
			taskCancelled = true
		}
	}()

	advanceTime()
	require.False(t, taskTaken)
	require.False(t, taskStarted)
	require.False(t, taskCancelled)

	dispatcher.Unlock()
	advanceTime()
	require.True(t, taskTaken)
	require.True(t, taskStarted)
	require.False(t, taskCancelled)

	go func() {
		taskTaken = false
		taskCancelled = false
		task, ok := dispatcher.NewTask()
		taskTaken = ok
		advanceTime()
		advanceTime()
		if !ok {
			return
		}
		defer task.Finish()
		select {
		case <-task.Cancelled():
			taskCancelled = true
		default:
		}
	}()
	advanceTime()
	require.True(t, taskTaken)
	require.False(t, taskCancelled)

	require.NoError(t, dispatcher.Close())
	advanceTime()
	require.True(t, taskTaken)
	require.True(t, taskCancelled)
}
