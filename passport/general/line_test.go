package tskv

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestQuote(t *testing.T) {
	require.Equal(t, "some string", Escape("some string"))
	require.Equal(t, `some\nstring`, Escape("some\nstring"))
	require.Equal(t, `-aa7\=bff\td4\\42\=\n\'\'\"`, Escape("-aa7=bff\td4\\42=\n''\""))
}

func TestLine(t *testing.T) {
	line := NewTskvLine("some_format").
		AddValue("key", "value", true).
		AddValue("empty_key", "", true).
		String()
	require.Equal(t, "tskv\ttskv_format=some_format\tkey=value", line)

	line = NewTskvLine("").
		AddValue("key1", "hello world", true).
		AddValue("key2", "{a=b\nc='d'}", true).
		String()
	require.Equal(t, "tskv\tkey1=hello world\tkey2={a\\=b\\nc\\=\\'d\\'}", line)

	line = NewTskvLine("").
		AddValues(nil, true).
		AddValues(
			map[string]string{
				"key1": "hello world",
				"key2": "{a=b\nc='d'}",
			},
			true,
		).
		String()
	require.Equal(t, "tskv\t", line[:5])
	require.Contains(t, line, "\tkey1=hello world")
	require.Contains(t, line, "\tkey2={a\\=b\\nc\\=\\'d\\'}")
}
