package resps

import (
	"encoding/base64"
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/yt/go/yson"
)

const (
	jsonItem1 = `{
	"affected": "1",
	"date": 1613671356224,
	"ip": "2a02:6b8:c08:671e:0:1406:6218:0",
	"module": "mailbox_oper",
	"operation": "delete",
	"state": "175077435514571963",
	"target": "message",
	"unixtime": "1613671356"
}`
	jsonItem2 = `{
	"affected": "1",
	"browser": {
		"name": "Unknown",
		"version": "Some"
	},
	"date": 1613671354354,
	"internetProvider": "AS13238",
	"ip": "2a02:6b8:c08:671e:0:1406:6218:0",
	"module": "sendbernar",
	"operation": "send",
	"regionId": "213",
	"state": "message-id=<312521613671354@sas1-955161ff6430",
	"target": "mailbox",
	"unixtime": "1613671354"
}`
)

func TestMailUserHistoryJSON(t *testing.T) {
	cases := []struct {
		data      string
		date      uint64
		operation string
		module    string
	}{
		{
			data:      jsonItem1,
			date:      1613671356224,
			module:    "mailbox_oper",
			operation: "delete",
		},
		{
			data:      jsonItem2,
			date:      1613671354354,
			module:    "sendbernar",
			operation: "send",
		},
	}

	for idx, c := range cases {
		item := MailUserHistoryItem{}
		require.NoError(t, json.Unmarshal([]byte(c.data), &item), idx)

		out, err := json.Marshal(&item)
		require.NoError(t, err, idx)
		require.JSONEq(t, c.data, string(out), idx)

		require.Equal(t, c.date, item.Common.Date, idx)
		require.Equal(t, c.operation, item.Common.Operation, idx)
		require.Equal(t, c.module, item.Common.Module, idx)
	}
}

func TestMailUserHistoryYSON(t *testing.T) {
	cases := []struct {
		data      string
		date      uint64
		operation string
		module    string
		json      string
	}{
		{
			data: `{
	"affected" = "1";
	"ip" = "2a02:6b8:c08:671e:0:1406:6218:0";
	"state" = "175077435514571963";
	"target" = "message"
}`,
			date:      1613671356224,
			module:    "mailbox_oper",
			operation: "delete",
			json:      jsonItem1,
		},
		{
			data: `{
	"affected" = "1";
	"browser.name" = "Unknown";
	"browser.version" = "Some";
	"internetProvider" = "AS13238";
	"ip" = "2a02:6b8:c08:671e:0:1406:6218:0";
	"regionId" = "213";
	"state" = "message-id=<312521613671354@sas1-955161ff6430";
	"target" = "mailbox"
}`,
			date:      1613671354354,
			module:    "sendbernar",
			operation: "send",
			json:      jsonItem2,
		},
	}

	for idx, c := range cases {
		item := MailUserHistoryItem{}
		require.NoError(t, yson.Unmarshal([]byte(c.data), &item), idx)

		item.SetDate(c.date)
		item.SetOperation(c.operation)
		item.SetModule(c.module)

		out, err := json.Marshal(&item)
		require.NoError(t, err, idx)
		require.JSONEq(t, c.json, string(out), idx)
	}
}

func TestMailUserHistoryCompare(t *testing.T) {
	item1 := MailUserHistoryItem{}
	item1.SetDate(100500)
	item1.SetOperation("op1")
	item1.SetOperation("m1")

	item2 := MailUserHistoryItem{}
	item2.SetDate(100500)
	item2.SetOperation("op1")
	item2.SetOperation("m1")

	require.True(t, item1.Equals(&item2))

	item2.SetDate(100501)
	require.False(t, item1.Equals(&item2))

	require.False(t, item1.After(&item2))
	require.True(t, item2.After(&item1))

	item2.SetDate(100500)
	require.True(t, item1.Equals(&item2))

	item2.SetOperation("op2")
	require.False(t, item1.Equals(&item2))
	require.False(t, item1.After(&item2))
	require.False(t, item2.After(&item1))
}

func base64ToBin(s string) string {
	res, err := base64.StdEncoding.DecodeString(s)
	if err != nil {
		panic(err)
	}
	return string(res)
}

func TestDecompressBrotli(t *testing.T) {

	cases := []struct {
		encoded string
		decoded string
	}{
		{
			encoded: base64ToBin("awAD"),
			decoded: "",
		},
		{
			encoded: base64ToBin("CwOAcXdleXRydQM="),
			decoded: "qweytru",
		},
		{
			encoded: base64ToBin("iyUAACTCArFAigED"),
			decoded: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		},
	}

	for idx, c := range cases {
		res, err := decompressBrotli(uint64(len(c.decoded)), c.encoded)
		require.NoError(t, err, idx)
		require.Equal(t, c.decoded, res, idx)
	}

	casesErrs := []struct {
		encoded string
		len     uint64
		err     string
	}{
		{
			encoded: "aaaaaaaaaaaaaaaaaaaaaa",
			len:     100500,
			err:     "failed to decompress blob:",
		},
		{
			encoded: base64ToBin("CwOAcXdleXRydQM="),
			len:     100500,
			err:     "failed to decompress blob:",
		},
		{
			encoded: base64ToBin("0wOAcXdleXRydQM="),
			len:     7,
			err:     "failed to decompress blob:",
		},
	}

	for idx, c := range casesErrs {
		_, err := decompressBrotli(c.len, c.encoded)
		require.Error(t, err)
		require.Contains(t, err.Error(), c.err, idx)
	}
}

func TestDecompressMailUserHistoryItemField(t *testing.T) {
	cases := []struct {
		field interface{}
		res   string
		err   string
	}{
		{
			field: 100500,
			err:   "'kek' in '_compressed' is not map[string]interface{}",
		},
		{
			field: map[string]interface{}{},
			err:   "missing 'size'",
		},
		{
			field: map[string]interface{}{
				"size": "lol",
			},
			err: "'size' is not uint64 but string",
		},
		{
			field: map[string]interface{}{
				"size": uint64(42),
			},
			err: "missing 'value'",
		},
		{
			field: map[string]interface{}{
				"size":  uint64(42),
				"value": 100500,
			},
			err: "'value' is not string but int",
		},
		{
			field: map[string]interface{}{
				"size":  uint64(76),
				"value": base64ToBin("iyUAACTCArFAigED"),
			},
			res: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		},
	}

	for idx, c := range cases {
		res, err := decompressMailUserHistoryItemField("kek", c.field)
		if c.err == "" {
			require.NoError(t, err, idx)
			require.Equal(t, c.res, res)
		} else {
			require.Error(t, err, idx)
			require.Contains(t, err.Error(), c.err, idx)
		}
	}
}

func TestDecompress(t *testing.T) {
	cases := []struct {
		item MailUserHistoryItem
		err  []string
	}{
		{},
		{
			item: MailUserHistoryItem{all: map[string]interface{}{
				compressedKey: 100500,
			}},
			err: []string{"'_compressed' is not map[string]interface{}"},
		},
		{
			item: MailUserHistoryItem{all: map[string]interface{}{
				compressedKey: map[string]interface{}{},
			}},
		},
		{
			item: MailUserHistoryItem{all: map[string]interface{}{
				compressedKey: map[string]interface{}{
					"foo": 100500,
					"bar": 100500,
				},
			}},
			err: []string{
				"failed to decompress 'bar': 'bar' in '_compressed' is not map[string]interface{}:",
				"failed to decompress 'foo': 'foo' in '_compressed' is not map[string]interface{}:",
			},
		},
	}

	for idx, c := range cases {
		err := c.item.Decompress()
		if len(c.err) == 0 {
			require.NoError(t, err, idx)
		} else {
			require.Error(t, err, idx)
			for _, e := range c.err {
				require.Contains(t, err.Error(), e, idx)
			}
		}

		_, ok := c.item.all[compressedKey]
		require.False(t, ok, idx)
	}
}
