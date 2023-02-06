package keys

import (
	"encoding/base64"
	"encoding/hex"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestKeyMap(t *testing.T) {
	require := require.New(t)

	key1, _ := hex.DecodeString("abcdef")
	key2, _ := hex.DecodeString("aabbccdd")
	key3, _ := hex.DecodeString("deadbeefc0ffee")
	key4, _ := base64.StdEncoding.DecodeString("d3afIKJ+MB2ZnAMxwsNQN729osL9meb33YP/5wilfCU=")
	key5, _ := base64.StdEncoding.DecodeString("eik8oMR/sfgUE0O4NEaY/yGgtkfbN3sBCRiyqS0ZDV0=")

	keyMap := CreateKeyMap()

	require.Equal("", keyMap.GetDefaultKeyID())
	require.Nil(keyMap.GetDefaultKey())
	require.Nil(keyMap.GetKey("id"))

	err := keyMap.SetDefaultKeyID("id")
	require.Error(err)
	require.Contains(err.Error(), "No key for default id 'id'")
	require.Equal("", keyMap.GetDefaultKeyID())
	require.Nil(keyMap.GetDefaultKey())
	require.Nil(keyMap.GetKey("id"))

	require.NoError(keyMap.AddHexKey("id", "abcdef"))
	require.Equal(map[string][]byte{"id": key1}, keyMap.keys)
	require.Equal(key1, keyMap.GetKey("id"))

	require.NoError(keyMap.SetDefaultKeyID("id"))
	require.Equal("id", keyMap.GetDefaultKeyID())
	require.Equal(key1, keyMap.GetDefaultKey())

	require.NoError(keyMap.AddHexKey("id", "aabbccdd"))
	require.NoError(keyMap.AddHexKey("3", "deadbeefc0ffee"))
	require.Equal(map[string][]byte{"id": key2, "3": key3}, keyMap.keys)

	require.Equal("id", keyMap.GetDefaultKeyID())
	require.Equal(key2, keyMap.GetDefaultKey())

	require.Equal(key2, keyMap.GetKey("id"))
	require.Equal(key3, keyMap.GetKey("3"))
	require.Nil(keyMap.GetKey(""))
	require.Nil(keyMap.GetKey(" 3 "))
	require.Nil(keyMap.GetKey("2"))

	require.NoError(keyMap.AddBase64Key("id", "d3afIKJ+MB2ZnAMxwsNQN729osL9meb33YP/5wilfCU="))
	require.NoError(keyMap.AddBase64Key("64", "eik8oMR/sfgUE0O4NEaY/yGgtkfbN3sBCRiyqS0ZDV0="))
	require.Equal(map[string][]byte{"id": key4, "3": key3, "64": key5}, keyMap.keys)

	require.Equal(key3, keyMap.GetKeyNum(3))
	require.Equal(key5, keyMap.GetKeyNum(64))
	require.Nil(keyMap.GetKeyNum(100500))
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
				Filename:     configFileName,
				DefaultKey:   "",
				KeysEncoding: "hex",
			},
			FileContent: "",
			Err:         "Default key is not configured",
		},
		{
			Cfg: Config{
				Filename:     "",
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "",
			Err:         "Keys file is not configured",
		},
		{
			Cfg: Config{
				Filename:     "missing_file",
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "",
			Err:         "Failed to read keys file 'missing_file': open missing_file: no such file or directory",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "",
			Err:         "Failed to parse keys file",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "Hello",
			Err:         "Failed to parse keys file",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "{}",
			Err:         "No key for default id '1'",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "{\"key\":\"cafebabe\"}",
			Err:         "No key for default id '1'",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "{\"1\":\"\"}",
			Err:         "Empty key id or body: '1':''",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "{\"1\":\"qwerty\"}",
			Err:         "Bad hex key 'qwerty'",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "{\"1\":\"cafebabe\",\"2\":\"bad\"}",
			Err:         "Bad hex key 'bad'",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "base64",
			},
			FileContent: "{\"1\":\"qwerty\"}",
			Err:         "Bad base64 key 'qwerty'",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "base64",
			},
			FileContent: "{\"1\":\"d3afIKJ+MB2ZnAMxwsNQN729osL9meb33YP/5wilfCU=\",\"2\":\"bad\"}",
			Err:         "Bad base64 key 'bad'",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "hex",
			},
			FileContent: "{\"1\":\"cafebabe\",\"\":\"0\"}",
			Err:         "Empty key id or body: '':'0'",
		},
		{
			Cfg: Config{
				Filename:     configFileName,
				DefaultKey:   "1",
				KeysEncoding: "invalid",
			},
			FileContent: "{\"1\":\"cafebabe\"}",
			Err:         "Unsupported keys encoding type: invalid",
		},
	}

	for _, c := range badCases {
		require.NoError(ioutil.WriteFile(configFileName, []byte(c.FileContent), os.ModePerm))
		keyMap, err := InitKeyMapWithDefaultKey(c.Cfg)
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

	keyMap, err := InitKeyMap(Config{Filename: configFileName, DefaultKey: "id", KeysEncoding: "hex"})
	require.NoError(err)
	require.Equal("id", keyMap.GetDefaultKeyID())

	require.Equal(map[string][]byte{"id": key1, "1": key2}, keyMap.keys)

	require.NoError(keyMap.AddHexKey("id", "aabbccdd"))
	require.NoError(keyMap.AddHexKey("3", "deadbeefc0ffee"))
	require.Equal("id", keyMap.GetDefaultKeyID())
	require.Equal(map[string][]byte{"id": key3, "1": key2, "3": key4}, keyMap.keys)

	require.Equal(key3, keyMap.GetDefaultKey())
	require.Equal(key3, keyMap.GetKey("id"))
	require.Equal(key2, keyMap.GetKey("1"))
	require.Equal(key4, keyMap.GetKey("3"))
	require.Nil(keyMap.GetKey(""))
	require.Nil(keyMap.GetKey(" 3 "))
	require.Nil(keyMap.GetKey("2"))
}
