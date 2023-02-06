package advsync

import (
	"testing"

	"github.com/stretchr/testify/require"
)

type queueTester struct {
	expectTaskStart Task
	t               *testing.T
}

func (t *queueTester) StartTask(task Task) {
	require.Equal(t.t, t.expectTaskStart, task)
	t.expectTaskStart = nil
}

func (t *queueTester) TaskFinished(task Task) {}

func TestDisplacingQueue(t *testing.T) {
	queueTester := &queueTester{
		t: t,
	}
	task1 := newTask(queueTester)
	queue := NewDisplacingQueue(queueTester)

	queueTester.expectTaskStart = task1
	queue.EnqueueTask(task1)
	advanceTime()
	require.Nil(t, queueTester.expectTaskStart)

	task2 := newTask(queueTester)
	queue.EnqueueTask(task2)
	advanceTime()
	require.True(t, task1.IsCancelled())

	task3 := newTask(queueTester)
	queue.EnqueueTask(task3)
	advanceTime()
	require.True(t, task2.IsCancelled())

	task2.Finish()
	advanceTime()

	queueTester.expectTaskStart = task3
	task1.Finish()
	queue.TaskFinished(task1)
	advanceTime()
	require.Nil(t, queueTester.expectTaskStart)
}

func TestQueuedDispatcher(t *testing.T) {
	dispatcher := NewQueuedDispatcher()
	counter := 0

	processTask := func(queue TaskQueue, lockUntil Until) {
		task, ok := dispatcher.NewTask(queue)
		require.True(t, ok)
		defer task.Finish()
		defer lockUntil.Wait()
		select {
		case <-task.Started():
			counter++
		case <-task.Cancelled():
		}
	}

	queue1 := NewDisplacingQueue(dispatcher)
	queue2 := NewDisplacingQueue(dispatcher)
	until := NewUntil()

	go processTask(queue1, until)
	advanceTime()
	require.Equal(t, 1, counter)
	go processTask(queue2, until)
	advanceTime()
	require.Equal(t, 2, counter)
	go processTask(queue1, until)
	advanceTime()
	require.Equal(t, 2, counter)
	until.Fulfill()
	advanceTime()
	require.Equal(t, 3, counter)
	require.NoError(t, dispatcher.Close())
}
