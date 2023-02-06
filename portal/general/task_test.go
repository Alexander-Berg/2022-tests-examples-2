package advsync

import (
	"testing"

	"github.com/stretchr/testify/require"
)

type taskTracker struct {
	finished bool
}

func (t *taskTracker) TaskFinished(_ Task) {
	t.finished = true
}

func TestTask(t *testing.T) {
	tracker := &taskTracker{}
	task := newTask(tracker)

	started := false
	cancelled := false

	processTask := func(task Task) {
		started = false
		cancelled = false
		defer task.Finish()
		select {
		case <-task.Started():
			started = true
		case <-task.Cancelled():
			cancelled = true
		}
	}

	go processTask(task)
	advanceTime()
	require.False(t, started)
	require.False(t, cancelled)
	require.False(t, tracker.finished)

	task.Start()

	advanceTime()
	require.True(t, started)
	require.False(t, cancelled)
	require.True(t, tracker.finished)

	tracker.finished = false
	task = newTask(tracker)

	go processTask(task)
	advanceTime()
	require.False(t, started)
	require.False(t, cancelled)
	require.False(t, tracker.finished)

	task.Cancel()

	advanceTime()
	require.False(t, started)
	require.True(t, cancelled)
	require.True(t, tracker.finished)

}
