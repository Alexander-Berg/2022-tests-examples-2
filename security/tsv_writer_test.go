package s3

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"testing"

	"github.com/golang/snappy"
	"github.com/pierrec/lz4"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/osquery/osquery-sender/batcher"
)

var (
	events = &batcher.EventBatch{
		Length:     5,
		NumColumns: 3,
		Actions: []string{
			"action1",
			"action2",
			"action3",
			"action4",
			"action5",
		},
		Hosts: []string{
			"host1",
			"host2",
			"host3",
			"host4",
			"host5",
		},
		Timestamps: []int64{
			1234,
			2345,
			3456,
			4567,
			5678,
		},
		StringValues: map[string][]string{
			"columnStr1": {
				"value1_1",
				"value1\"2",
				"value1\t3",
				"value1,4",
				"value1\n5",
			},
			"columnStr2": {
				"a",
				"b",
				"c",
				"d",
				"e",
			},
		},
		Float64Values: map[string][]float64{
			"columnFl1": {
				1,
				2,
				3,
				4,
				567890,
			},
		},
		// Unused
		SliceSize:  -1,
		StringSize: -1,
	}
	columns = []string{"columnFl1", "columnStr1", "columnStr2"}
	all     = "timestamp\taction\thost\tcolumnFl1\tcolumnStr1\tcolumnStr2\n" +
		"1234\taction1\thost1\t1\tvalue1_1\ta\n" +
		"2345\taction2\thost2\t2\t\"value1\"\"2\"\tb\n" +
		"3456\taction3\thost3\t3\t\"value1\t3\"\tc\n" +
		"4567\taction4\thost4\t4\tvalue1,4\td\n" +
		"5678\taction5\thost5\t567890\t\"value1\n5\"\te\n"
)

func TestTsvWriter(t *testing.T) {
	out := &bytes.Buffer{}
	w, err := NewTsvWriter(columns, CompressionNone, &countingWriter{writer: out})
	require.NoError(t, err)
	err = w.Write(events)
	require.NoError(t, err)
	err = w.Close()
	require.NoError(t, err)
	require.Equal(t, all, out.String())
	require.Equal(t, int64(len(all)), w.TotalBytes())
	require.Equal(t, int64(len(all)), w.CompressedBytes())
}

func TestTsvWriteCompressionLz4(t *testing.T) {
	bigEvents, bigBuf := generateEvents(50000, 0)
	bigColumns := []string{"column1", "column2"}

	out := &bytes.Buffer{}
	w, err := NewTsvWriter(bigColumns, CompressionLz4, &countingWriter{writer: out})
	require.NoError(t, err)
	err = w.Write(&batcher.EventBatch{})
	require.NoError(t, err)
	err = w.Write(bigEvents)
	require.NoError(t, err)
	err = w.Close()
	require.NoError(t, err)
	require.Equal(t, int64(out.Len()), w.CompressedBytes())

	uncompressed, err := ioutil.ReadAll(lz4.NewReader(out))
	require.NoError(t, err)
	require.Equal(t, bigBuf, string(uncompressed))
	require.Equal(t, int64(len(bigBuf)), w.TotalBytes())
}

func TestTsvWriteCompressionSnappy(t *testing.T) {
	bigEvents, bigBuf := generateEvents(50000, 0)
	bigColumns := []string{"column1", "column2"}

	out := &bytes.Buffer{}
	w, err := NewTsvWriter(bigColumns, CompressionSnappy, &countingWriter{writer: out})
	require.NoError(t, err)
	err = w.Write(bigEvents)
	require.NoError(t, err)
	err = w.Write(&batcher.EventBatch{})
	require.NoError(t, err)
	err = w.Close()
	require.NoError(t, err)
	require.Equal(t, int64(out.Len()), w.CompressedBytes())

	uncompressed, err := ioutil.ReadAll(snappy.NewReader(out))
	require.NoError(t, err)
	require.Equal(t, bigBuf, string(uncompressed))
	require.Equal(t, int64(len(bigBuf)), w.TotalBytes())
}

func generateEvents(numEvents int, baseTimestamp int64) (*batcher.EventBatch, string) {
	events := &batcher.EventBatch{
		Length:     numEvents,
		NumColumns: 2,
		Float64Values: map[string][]float64{
			"column1": nil,
		},
		StringValues: map[string][]string{
			"column2": nil,
		},
	}
	buf := &bytes.Buffer{}
	buf.WriteString("timestamp\taction\thost\tcolumn1\tcolumn2\n")
	for i := 0; i < numEvents; i++ {
		timestamp := int64(i)*123 + baseTimestamp
		action := fmt.Sprintf("action%d", i)
		host := fmt.Sprintf("host%d", i)
		column1Value := float64(i) * 3
		column2Value := fmt.Sprintf("value%d", i)
		events.Timestamps = append(events.Timestamps, timestamp)
		events.Actions = append(events.Actions, action)
		events.Hosts = append(events.Hosts, host)
		events.Float64Values["column1"] = append(events.Float64Values["column1"], column1Value)
		events.StringValues["column2"] = append(events.StringValues["column2"], column2Value)
		buf.WriteString(fmt.Sprintf("%d\t%s\t%s\t%g\t%s\n", timestamp, action, host, column1Value, column2Value))
	}
	return events, buf.String()
}
