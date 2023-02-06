package batcher

import (
	"errors"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"go.uber.org/atomic"

	"a.yandex-team.ru/security/osquery/osquery-sender/parser"
)

type testSubmitter struct {
	t *testing.T

	mu     sync.Mutex
	events map[string]*EventBatch
}

func (s *testSubmitter) SubmitEvents(name string, events *EventBatch) error {
	time.Sleep(time.Millisecond)
	s.mu.Lock()
	defer s.mu.Unlock()

	s.events[name] = AppendBatch(s.events[name], events)
	return nil
}

func (s *testSubmitter) OnDropDueToFullMemory() {
	s.t.Fatal("got OnDropDueToFullMemory")
}

func (s *testSubmitter) OnDropDueToFullQueue() {
	s.t.Fatal("got OnDropDueToFullQueue")
}

func (s *testSubmitter) OnFlushDueToMemoryPressure() {
	s.t.Fatal("got OnFlushDueToMemoryPressure")
}

func (s *testSubmitter) OnDropAfterRetries() {
	s.t.Fatal("got OnDropAfterRetries")
}

func TestWorkers(t *testing.T) {
	s := &testSubmitter{
		t:      t,
		events: map[string]*EventBatch{},
	}
	config := WorkersConfig{
		MaxMemory:  1024 * 1024,
		MaxDelay:   time.Hour * 24,
		MaxWorkers: 4,
	}
	w := NewWorkers(New(nil, nil, true, nil), config, s, "")
	w.Start()

	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		for i := 0; i < 10; i++ {
			w.Enqueue(prepareEventBatch("name1", i, 100))
		}
		wg.Done()
	}()

	go func() {
		for i := 0; i < 10; i++ {
			w.Enqueue(prepareEventBatch("name2", i, 100))
		}
		wg.Done()
	}()
	wg.Wait()

	w.Stop()

	require.Equal(t, 2, len(s.events))
	require.Equal(t, 1000, s.events["name1"].Length)
	require.Equal(t, 1000, s.events["name2"].Length)

	require.Equal(t, 1000, len(s.events["name1"].Actions))
	require.Equal(t, 1000, len(s.events["name2"].Actions))
	require.Equal(t, 1000, len(s.events["name1"].StringValues["column"]))
	require.Equal(t, 1000, len(s.events["name2"].StringValues["column"]))
	for i := 0; i < 1000; i++ {
		require.Equal(t, "added", s.events["name1"].Actions[i])
		require.Equal(t, "added", s.events["name2"].Actions[i])
		value := fmt.Sprintf("%d-%d", i/100, i%100)
		require.Equal(t, value, s.events["name1"].StringValues["column"][i])
		require.Equal(t, value, s.events["name2"].StringValues["column"][i])
	}
}

func prepareEventBatch(name string, idx int, num int) []*parser.ParsedEvent {
	var ret []*parser.ParsedEvent
	for i := 0; i < num; i++ {
		columns := map[string]interface{}{
			"column": fmt.Sprintf("%d-%d", idx, i),
		}
		ret = append(ret, &parser.ParsedEvent{
			Name: name,
			Data: map[string]interface{}{
				"action":  "added",
				"columns": columns,
			},
		})
	}
	return ret
}

type testSubmitterOverflow struct {
	t *testing.T

	fullMemory     bool
	memoryPressure bool

	sleepUntil sync.WaitGroup
}

func (s *testSubmitterOverflow) SubmitEvents(name string, events *EventBatch) error {
	s.sleepUntil.Wait()
	return nil
}

func (s *testSubmitterOverflow) OnDropDueToFullMemory() {
	s.fullMemory = true
}

func (s *testSubmitterOverflow) OnDropDueToFullQueue() {
	s.t.Fatal("got OnDropDueToFullQueue")
}

func (s *testSubmitterOverflow) OnFlushDueToMemoryPressure() {
	s.memoryPressure = true
}

func (s *testSubmitterOverflow) OnDropAfterRetries() {
	s.t.Fatal("got OnDropAfterRetries")
}

func TestWorkersOverflow(t *testing.T) {
	s := &testSubmitterOverflow{
		t: t,
	}
	s.sleepUntil.Add(1)

	config := WorkersConfig{
		MaxMemory:  1024,
		MaxDelay:   time.Hour * 24,
		MaxWorkers: 4,
	}
	w := NewWorkers(New(nil, nil, true, nil), config, s, "")
	w.Start()
	defer w.Stop()

	// The first batch overflows the memory, gets flushed, but not processed due to worker sleeping on
	// sleepUntil.
	w.Enqueue(prepareEventBatch("name", 0, 1000000))
	// The second gets dropped.
	w.Enqueue(prepareEventBatch("another", 1, 1))

	s.sleepUntil.Done()
	require.True(t, s.fullMemory)
	require.True(t, s.memoryPressure)
}

type testSubmitterRetry struct {
	t *testing.T

	finished chan struct{}

	numRetry  atomic.Int32
	completed bool
}

func (s *testSubmitterRetry) SubmitEvents(name string, events *EventBatch) error {
	defer func() {
		s.numRetry.Inc()
	}()

	if s.numRetry.Load() > 0 {
		s.completed = true
		close(s.finished)
		return nil
	} else {
		return errors.New("retriable error")
	}
}

func (s *testSubmitterRetry) OnDropDueToFullMemory() {
	s.t.Fatal("got OnDropDueToFullMemory")
}

func (s *testSubmitterRetry) OnDropDueToFullQueue() {
	s.t.Fatal("got OnDropDueToFullQueue")
}

func (s *testSubmitterRetry) OnFlushDueToMemoryPressure() {
	s.t.Fatal("got OnFlushDueToMemoryPressure")
}

func (s *testSubmitterRetry) OnDropAfterRetries() {
	s.t.Fatal("got OnDropAfterRetries")
}

func TestWorkersRetry(t *testing.T) {
	s := &testSubmitterRetry{
		t:        t,
		finished: make(chan struct{}),
	}

	config := WorkersConfig{
		MaxMemory:  1024 * 1024,
		MaxDelay:   time.Hour * 24,
		MaxWorkers: 4,
	}
	w := NewWorkers(New(nil, nil, true, nil), config, s, "")
	w.Start()
	defer w.Stop()

	w.Enqueue(prepareEventBatch("name", 0, 1000))
	w.ForceFlush()
	// Hacky way to WaitUntilTimeout().
	select {
	case <-s.finished:
	case <-time.After(time.Second * 10):
		t.Fatal("did not finish after 10sec")
	}

	require.True(t, s.completed)
	require.Equal(t, 2, int(s.numRetry.Load()))
}

type testSubmitterSplit struct {
	t *testing.T

	mu     sync.Mutex
	events map[string][]*EventBatch
}

func (s *testSubmitterSplit) SubmitEvents(name string, events *EventBatch) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	s.events[name] = append(s.events[name], events)
	return nil
}

func (s *testSubmitterSplit) OnDropDueToFullMemory() {
	s.t.Fatal("got OnDropDueToFullMemory")
}

func (s *testSubmitterSplit) OnDropDueToFullQueue() {
	s.t.Fatal("got OnDropDueToFullQueue")
}

func (s *testSubmitterSplit) OnFlushDueToMemoryPressure() {
	s.t.Fatal("got OnFlushDueToMemoryPressure")
}

func (s *testSubmitterSplit) OnDropAfterRetries() {
	s.t.Fatal("got OnDropAfterRetries")
}

func TestWorkersSplitDay(t *testing.T) {
	s := &testSubmitterSplit{
		t:      t,
		events: map[string][]*EventBatch{},
	}
	config := WorkersConfig{
		MaxMemory:  1024 * 1024,
		MaxDelay:   time.Hour * 24,
		MaxWorkers: 1,
		SplitDays:  true,
		SplitLoc:   time.UTC,
	}
	b := New(nil, nil, true, nil)
	w := NewWorkers(b, config, s, "")
	w.Start()

	event1 := &parser.ParsedEvent{
		Host: "host1",
		Name: "name",
		Data: map[string]interface{}{
			"action": "added",
			"columns": map[string]interface{}{
				"column1": "hello1",
				"column2": 1.0,
				"column3": "goodbye1",
				"column4": 1000.0,
			},
		},
	}
	time1 := time.Date(2000, 11, 3, 12, 34, 56, 0, time.UTC)
	b.AppendWithTimestamp([]*parser.ParsedEvent{event1}, time1)
	event2 := &parser.ParsedEvent{
		Host: "host2",
		Name: "name",
		Data: map[string]interface{}{
			"action": "removed",
			"columns": map[string]interface{}{
				"column1": "hello2",
				"column2": 2.0,
				"column3": "goodbye2",
				"column4": 2000.0,
			},
		},
	}
	time2 := time.Date(2000, 11, 3, 23, 59, 59, 0, time.UTC)
	b.AppendWithTimestamp([]*parser.ParsedEvent{event2}, time2)
	event3 := &parser.ParsedEvent{
		Host: "host3",
		Name: "name",
		Data: map[string]interface{}{
			"action": "removed",
			"columns": map[string]interface{}{
				"column1": "hello3",
				"column2": 3.0,
				"column3": "goodbye3",
				"column4": 3000.0,
			},
		},
	}
	time3 := time.Date(2000, 11, 4, 0, 0, 0, 0, time.UTC)
	b.AppendWithTimestamp([]*parser.ParsedEvent{event3}, time3)
	event4 := &parser.ParsedEvent{
		Host: "host4",
		Name: "name",
		Data: map[string]interface{}{
			"action": "added",
			"columns": map[string]interface{}{
				"column1": "hello4",
				"column2": 4.0,
				"column3": "goodbye4",
				"column4": 4000.0,
			},
		},
	}
	time4 := time.Date(2000, 11, 4, 0, 0, 1, 0, time.UTC)
	b.AppendWithTimestamp([]*parser.ParsedEvent{event4}, time4)

	w.Stop()

	require.Equal(t, 2, len(s.events["name"]))
	gotBatch1 := s.events["name"][0]
	gotBatch2 := s.events["name"][1]
	if gotBatch1.Timestamps[0] > gotBatch2.Timestamps[0] {
		gotBatch2, gotBatch1 = gotBatch1, gotBatch2
	}

	require.Equal(t, 2, gotBatch1.Length)
	require.Equal(t, []int64{time1.Unix(), time2.Unix()}, gotBatch1.Timestamps)
	require.Equal(t, []string{"host1", "host2"}, gotBatch1.Hosts)
	require.Equal(t, []string{"added", "removed"}, gotBatch1.Actions)
	require.Equal(t, map[string][]string{
		"column1": {"hello1", "hello2"},
		"column3": {"goodbye1", "goodbye2"},
	}, gotBatch1.StringValues)
	require.Equal(t, map[string][]float64{
		"column2": {1, 2},
		"column4": {1000, 2000},
	}, gotBatch1.Float64Values)

	require.Equal(t, 2, gotBatch2.Length)
	require.Equal(t, []int64{time3.Unix(), time4.Unix()}, gotBatch2.Timestamps)
	require.Equal(t, []string{"host3", "host4"}, gotBatch2.Hosts)
	require.Equal(t, []string{"removed", "added"}, gotBatch2.Actions)
	require.Equal(t, map[string][]string{
		"column1": {"hello3", "hello4"},
		"column3": {"goodbye3", "goodbye4"},
	}, gotBatch2.StringValues)
	require.Equal(t, map[string][]float64{
		"column2": {3, 4},
		"column4": {3000, 4000},
	}, gotBatch2.Float64Values)
}

func TestWorkersSplitDaySingle(t *testing.T) {
	s := &testSubmitterSplit{
		t:      t,
		events: map[string][]*EventBatch{},
	}
	config := WorkersConfig{
		MaxMemory:  1024 * 1024,
		MaxDelay:   time.Hour * 24,
		MaxWorkers: 1,
		SplitDays:  true,
		SplitLoc:   time.UTC,
	}
	b := New(nil, nil, true, nil)
	w := NewWorkers(b, config, s, "")
	w.Start()

	events := prepareEventBatch("name", 10, 100)
	w.Enqueue(events)
	w.Stop()

	require.Equal(t, 1, len(s.events["name"]))
	require.Equal(t, 100, s.events["name"][0].Length)

	require.Equal(t, 100, len(s.events["name"][0].Actions))
	require.Equal(t, 100, len(s.events["name"][0].StringValues["column"]))
	for i := 0; i < 100; i++ {
		require.Equal(t, "added", s.events["name"][0].Actions[i])
		value := fmt.Sprintf("10-%d", i)
		require.Equal(t, value, s.events["name"][0].StringValues["column"][i])
	}
}
