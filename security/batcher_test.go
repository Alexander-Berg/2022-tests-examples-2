package batcher

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/osquery/osquery-sender/parser"
)

func makeEvent(name string, action string, host string, columns map[string]interface{}) *parser.ParsedEvent {
	return &parser.ParsedEvent{
		Name: name,
		Host: host,
		Data: map[string]interface{}{
			"action":  action,
			"columns": columns,
		},
	}
}

func makeEventWithDecorators(name string, action string, host string, columns map[string]interface{}, key string, value interface{}) *parser.ParsedEvent {
	return &parser.ParsedEvent{
		Name: name,
		Host: host,
		Data: map[string]interface{}{
			"action":  action,
			"columns": columns,
			key:       value,
		},
	}
}

func TestEventBatcherAppend(t *testing.T) {
	b := New(nil, nil, true, nil)

	b.Append(nil)
	batch1 := []*parser.ParsedEvent{
		makeEvent("name1", "added", "host1", map[string]interface{}{"column1": 123.0, "column2": "hello"}),
		makeEvent("name1", "removed", "host2", map[string]interface{}{"column2": "goodbye"}),
		makeEvent("name2", "snapshot", "host3", map[string]interface{}{"column4": "new one"}),
	}
	b.Append(batch1)
	batch2 := []*parser.ParsedEvent{
		makeEvent("name1", "snapshot", "host4", map[string]interface{}{"column2": "yes", "column3": 345.0}),
		makeEvent("name2", "added", "host5", map[string]interface{}{"column3": "goodbye"}),
		{
			Name: "name2",
			Host: "host6",
			Data: map[string]interface{}{
				"action": "snapshot",
				"snapshot": []map[string]interface{}{
					{"column5": "another one"},
					{"column4": "back again", "column5": "very new"},
				},
			},
		},
	}
	b.Append(batch2)

	result := b.FlushAll()
	resultBatch1 := result["name1"]
	require.NotNil(t, resultBatch1)
	resultBatch2 := result["name2"]
	require.NotNil(t, resultBatch2)
	require.Equal(t, int64(0), b.MemorySize())

	require.Equal(t, 3, resultBatch1.Length)
	require.Equal(t, 2, len(resultBatch1.Float64Values))
	require.Equal(t, 1, len(resultBatch1.StringValues))
	require.Equal(t, []float64{123.0, 0.0, 0.0}, resultBatch1.Float64Values["column1"])
	require.Equal(t, []float64{0.0, 0.0, 345.0}, resultBatch1.Float64Values["column3"])
	require.Equal(t, []string{"hello", "goodbye", "yes"}, resultBatch1.StringValues["column2"])
	require.Equal(t, []string{"added", "removed", "snapshot"}, resultBatch1.Actions)
	require.Equal(t, []string{"host1", "host2", "host4"}, resultBatch1.Hosts)

	require.Equal(t, 4, resultBatch2.Length)
	require.Equal(t, 0, len(resultBatch2.Float64Values))
	require.Equal(t, 3, len(resultBatch2.StringValues))
	require.Equal(t, []string{"", "goodbye", "", ""}, resultBatch2.StringValues["column3"])
	require.Equal(t, []string{"new one", "", "", "back again"}, resultBatch2.StringValues["column4"])
	require.Equal(t, []string{"", "", "another one", "very new"}, resultBatch2.StringValues["column5"])
	require.Equal(t, []string{"snapshot", "added", "snapshot", "snapshot"}, resultBatch2.Actions)
	require.Equal(t, []string{"host3", "host5", "host6", "host6"}, resultBatch2.Hosts)
}

func TestEventBatcherFlushTop1(t *testing.T) {
	b := New(nil, nil, true, nil)

	tinyBatchNum := 2
	tinyString := "tiny value"
	var tinyBatch []*parser.ParsedEvent
	for i := 0; i < tinyBatchNum; i++ {
		tinyBatch = append(tinyBatch, makeEvent("tiny", "added", "host", map[string]interface{}{"column": tinyString}))
	}
	b.Append(tinyBatch)

	smallBatchNum := 20
	smallString := "small value"
	var smallBatch []*parser.ParsedEvent
	for i := 0; i < smallBatchNum; i++ {
		smallBatch = append(smallBatch, makeEvent("small1", "added", "host", map[string]interface{}{"column": smallString}))
	}
	for i := 0; i < smallBatchNum; i++ {
		smallBatch = append(smallBatch, makeEvent("small2", "added", "host", map[string]interface{}{"column": smallString}))
	}
	b.Append(smallBatch)

	// The same as smallBatchNum.
	bigBatchNum := 20
	bigString := "much bigger value"
	for i := 0; i < 100; i++ {
		bigString = bigString + " and bigger, and bigger"
	}
	var bigBatch []*parser.ParsedEvent
	for i := 0; i < bigBatchNum; i++ {
		bigBatch = append(bigBatch, makeEvent("big", "added", "host", map[string]interface{}{"column": bigString}))
	}
	b.Append(bigBatch)

	// Should only flush bigBatch.
	bigResult := b.FlushTop(b.MemorySize() / 2)
	require.Equal(t, 1, len(bigResult))
	bigResultBatch := bigResult["big"]
	require.NotNil(t, bigResultBatch)
	require.NotNil(t, bigResultBatch.StringValues["column"])
	require.Equal(t, bigBatchNum, len(bigResultBatch.StringValues["column"]))
	require.Equal(t, bigString, bigResultBatch.StringValues["column"][0])

	// Should flush both smallBatch1 and smallBatch2.
	smallResult := b.FlushTop(b.MemorySize() / 4)
	require.Equal(t, 2, len(smallResult))
	smallResultBatch1 := smallResult["small1"]
	require.NotNil(t, smallResultBatch1)
	require.NotNil(t, smallResultBatch1.StringValues["column"])
	require.Equal(t, smallBatchNum, len(smallResultBatch1.StringValues["column"]))
	require.Equal(t, smallString, smallResultBatch1.StringValues["column"][0])
	smallResultBatch2 := smallResult["small2"]
	require.NotNil(t, smallResultBatch2)
	require.NotNil(t, smallResultBatch2.StringValues["column"])
	require.Equal(t, smallBatchNum, len(smallResultBatch2.StringValues["column"]))
	require.Equal(t, smallString, smallResultBatch2.StringValues["column"][0])

	// Should flush the tiny batch.
	tinyResult := b.FlushTop(b.MemorySize() / 2)
	require.Equal(t, 1, len(tinyResult))
	tinyResultBatch := tinyResult["tiny"]
	require.NotNil(t, tinyResultBatch)
	require.NotNil(t, tinyResultBatch.StringValues["column"])
	require.Equal(t, tinyBatchNum, len(tinyResultBatch.StringValues["column"]))
	require.Equal(t, tinyString, tinyResultBatch.StringValues["column"][0])

	emptyResult := b.FlushTop(b.MemorySize())
	require.Empty(t, emptyResult)
	require.Equal(t, int64(0), b.MemorySize())
}

func TestEventBatcherFlushTop2(t *testing.T) {
	b := New(nil, nil, true, nil)

	tinyBatchNum := 100
	tinyString := "tiny value"
	var tinyBatch []*parser.ParsedEvent
	for i := 0; i < tinyBatchNum; i++ {
		tinyBatch = append(tinyBatch, makeEvent(fmt.Sprintf("tiny%d", i), "removed", "hostname", map[string]interface{}{"column": tinyString}))
	}
	b.Append(tinyBatch)

	topMemorySize := b.MemorySize()
	result := b.FlushTop(topMemorySize / 5)
	require.Equal(t, tinyBatchNum*4/5, len(result))
	require.Equal(t, topMemorySize/5, b.MemorySize())

	result = b.FlushAll()
	require.Equal(t, tinyBatchNum/5, len(result))
	require.Equal(t, int64(0), b.MemorySize())
}

func TestCleanNames(t *testing.T) {
	b := New(nil, nil, true, nil)
	batch := []*parser.ParsedEvent{
		makeEvent("event.name@with/имя", "added", "hostname", map[string]interface{}{"имя_column": "значение/"}),
	}
	b.Append(batch)
	result := b.FlushAll()
	event := result["event.name_with____"]
	require.NotNil(t, event)
	column := event.StringValues["____column"]
	require.NotNil(t, column)
	require.Equal(t, column[0], "значение/")
}

func TestAddDecorators(t *testing.T) {
	b := New(nil, nil, true, []string{"cloud_id", "folder_id"})
	batch := []*parser.ParsedEvent{
		makeEvent("event_name", "added", "hostname", map[string]interface{}{"column": "value0"}),
		makeEventWithDecorators("event_name", "added", "hostname", map[string]interface{}{"column": "value1"}, "cloud_id", "12345"),
		makeEventWithDecorators("event_name", "added", "hostname", map[string]interface{}{"column": "value2"}, "folder_id", "67890"),
	}
	b.Append(batch)
	result := b.FlushAll()
	event := result["event_name"]
	require.NotNil(t, event)
	require.Equal(t, event.StringValues["column"], []string{"value0", "value1", "value2"})
	require.Equal(t, event.StringValues["cloud_id"], []string{"", "12345", ""})
	require.Equal(t, event.StringValues["folder_id"], []string{"", "", "67890"})
}
