package s3

import (
	"bytes"
	"io/ioutil"
	"strings"
	"testing"

	"github.com/pierrec/lz4"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/osquery/osquery-sender/batcher"
)

func TestMerge(t *testing.T) {
	columns := []string{"column2", "column1", "column3"}

	out := &bytes.Buffer{}
	m, err := NewTsvMerger(columns, CompressionNone, &countingWriter{writer: out})
	require.NoError(t, err)

	src1 := "column1\nabc\ndef"
	src2 := "column2\tcolumn3\n1\t2\n3\t4\n"
	src3 := "column2\tcolumn1\tcolumn3\nx\ty\tz\nq\tw\te\n"

	err = m.Append([]string{"column1"}, CompressionNone, bytes.NewReader([]byte(src1)))
	require.NoError(t, err)
	err = m.Append([]string{"column2", "column3"}, CompressionNone, bytes.NewReader([]byte(src2)))
	require.NoError(t, err)
	err = m.Append([]string{"column2", "column1", "column3"}, CompressionNone, bytes.NewReader([]byte(src3)))
	require.NoError(t, err)

	err = m.Close()
	require.NoError(t, err)

	expectedBuf := "column2\tcolumn1\tcolumn3\n" +
		"\tabc\t\n" +
		"\tdef\t\n" +
		"1\t\t2\n" +
		"3\t\t4\n" +
		"x\ty\tz\n" +
		"q\tw\te\n"
	require.Equal(t, expectedBuf, out.String())
}

func TestMergeCompressed(t *testing.T) {
	bigColumns := []string{"column1", "column2"}

	bigEvents1, bigBuf1 := generateEvents(25000, 0)
	data1 := writeEvents(t, bigColumns, CompressionSnappy, bigEvents1)

	bigEvents2, bigBuf2 := generateEvents(25000, 0)
	data2 := writeEvents(t, bigColumns, CompressionLz4, bigEvents2)

	bigBuf := bigBuf1
	// Skip the header
	idx := strings.IndexByte(bigBuf2, '\n')
	bigBuf += bigBuf2[idx+1:]

	out := &bytes.Buffer{}
	fullColumns := []string{"timestamp", "action", "host"}
	fullColumns = append(fullColumns, bigColumns...)
	m, err := NewTsvMerger(fullColumns, CompressionLz4, &countingWriter{writer: out})
	require.NoError(t, err)

	err = m.Append(fullColumns, CompressionSnappy, bytes.NewReader(data1))
	require.NoError(t, err)
	err = m.Append(fullColumns, CompressionLz4, bytes.NewReader(data2))
	require.NoError(t, err)
	err = m.Close()
	require.NoError(t, err)

	uncompressed, err := ioutil.ReadAll(lz4.NewReader(out))
	require.NoError(t, err)
	require.Equal(t, bigBuf, string(uncompressed))
	require.Equal(t, int64(len(bigBuf)), m.TotalBytes())
}

func writeEvents(t *testing.T, columns []string, alg CompressionAlg, events *batcher.EventBatch) []byte {
	out := &bytes.Buffer{}
	w, err := NewTsvWriter(columns, alg, &countingWriter{writer: out})
	require.NoError(t, err)
	err = w.Write(&batcher.EventBatch{})
	require.NoError(t, err)
	err = w.Write(events)
	require.NoError(t, err)
	err = w.Close()
	require.NoError(t, err)
	require.Equal(t, int64(out.Len()), w.CompressedBytes())
	return out.Bytes()
}
