package keys

import (
	"encoding/hex"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCreateKeyMap(t *testing.T) {
	require := require.New(t)

	badCases := []struct {
		ID  string
		Key string
		Err string
	}{
		{
			ID:  "",
			Key: "",
			Err: "Empty default key id or body: '':''",
		},
		{
			ID:  "test",
			Key: "",
			Err: "Empty default key id or body: 'test':''",
		},
		{
			ID:  "",
			Key: "key",
			Err: "Empty default key id or body: '':'key'",
		},
		{
			ID:  "test",
			Key: "    ",
			Err: "Bad hex key '    '",
		},
		{
			ID:  "test",
			Key: "test",
			Err: "Bad hex key 'test'",
		},
	}

	for _, c := range badCases {
		keyMap, err := CreateKeyMap(c.ID, c.Key)
		require.Nil(keyMap)
		require.Error(err)
		require.Contains(err.Error(), c.Err)
	}

	key1, _ := hex.DecodeString("abcdef")
	key2, _ := hex.DecodeString("aabbccdd")
	key3, _ := hex.DecodeString("deadbeefc0ffee")

	keyMap, err := CreateKeyMap("id", "abcdef")
	require.NoError(err)
	require.Equal("id", keyMap.DefaultKeyID)
	require.Equal(map[string][]byte{"id": key1}, keyMap.keys)

	require.NoError(keyMap.AddHexKey("id", "aabbccdd"))
	require.NoError(keyMap.AddHexKey("3", "deadbeefc0ffee"))
	require.Equal("id", keyMap.DefaultKeyID)
	require.Equal(map[string][]byte{"id": key2, "3": key3}, keyMap.keys)

	require.Equal(key2, keyMap.GetDefaultKey())
	require.Equal(key2, keyMap.GetKey("id"))
	require.Equal(key3, keyMap.GetKey("3"))
	require.Nil(keyMap.GetKey(""))
	require.Nil(keyMap.GetKey(" 3 "))
	require.Nil(keyMap.GetKey("2"))
}

func TestInitKeyMap(t *testing.T) {
	require := require.New(t)

	tmpdir := "./tmp"
	configFileName := tmpdir + "/config.json"

	require.NoError(os.Mkdir(tmpdir, os.ModePerm))
	defer os.RemoveAll(tmpdir)

	badCases := []struct {
		Cfg         Config
		FileContent string
		Err         string
	}{
		{
			Cfg: Config{
				Filename:   "",
				DefaultKey: "",
			},
			FileContent: "",
			Err:         "Keys file or default key not configured",
		},
		{
			Cfg: Config{
				Filename:   "missing",
				DefaultKey: "",
			},
			FileContent: "",
			Err:         "Keys file or default key not configured",
		},
		{
			Cfg: Config{
				Filename:   "missing_file",
				DefaultKey: "1",
			},
			FileContent: "",
			Err:         "Failed to read keys file 'missing_file': open missing_file: no such file or directory",
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "",
			Err:         "Failed to parse keys file " + configFileName,
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "Hello",
			Err:         "Failed to parse keys file " + configFileName,
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "{}",
			Err:         "Default key '1' not in keys file " + configFileName,
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "{\"key\":\"value\"}",
			Err:         "Default key '1' not in keys file " + configFileName,
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "{\"1\":\"\"}",
			Err:         "Empty key id or body: '1':''",
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "{\"1\":\"qwerty\"}",
			Err:         "Bad hex key 'qwerty'",
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "{\"1\":\"cafebabe\",\"2\":\"bad\"}",
			Err:         "Bad hex key 'bad'",
		},
		{
			Cfg: Config{
				Filename:   configFileName,
				DefaultKey: "1",
			},
			FileContent: "{\"1\":\"cafebabe\",\"\":\"0\"}",
			Err:         "Empty key id or body: '':'0'",
		},
	}

	for _, c := range badCases {
		require.NoError(ioutil.WriteFile(configFileName, []byte(c.FileContent), os.ModePerm))
		keyMap, err := InitKeyMap(c.Cfg)
		require.Nil(keyMap)
		require.Error(err)
		require.Contains(err.Error(), c.Err)
	}

	FileContent := "{\"1\":\"0000000000\", \"id\": \"abcdef\"}"
	require.NoError(ioutil.WriteFile(configFileName, []byte(FileContent), os.ModePerm))

	key1, _ := hex.DecodeString("abcdef")
	key2, _ := hex.DecodeString("0000000000")
	key3, _ := hex.DecodeString("aabbccdd")
	key4, _ := hex.DecodeString("deadbeefc0ffee")

	keyMap, err := InitKeyMap(Config{Filename: configFileName, DefaultKey: "id"})
	require.NoError(err)
	require.Equal("id", keyMap.DefaultKeyID)

	require.Equal(map[string][]byte{"id": key1, "1": key2}, keyMap.keys)

	require.NoError(keyMap.AddHexKey("id", "aabbccdd"))
	require.NoError(keyMap.AddHexKey("3", "deadbeefc0ffee"))
	require.Equal("id", keyMap.DefaultKeyID)
	require.Equal(map[string][]byte{"id": key3, "1": key2, "3": key4}, keyMap.keys)

	require.Equal(key3, keyMap.GetDefaultKey())
	require.Equal(key3, keyMap.GetKey("id"))
	require.Equal(key2, keyMap.GetKey("1"))
	require.Equal(key4, keyMap.GetKey("3"))
	require.Nil(keyMap.GetKey(""))
	require.Nil(keyMap.GetKey(" 3 "))
	require.Nil(keyMap.GetKey("2"))
}
