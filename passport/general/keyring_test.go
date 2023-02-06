package decryptor

import (
	"context"
	"encoding/hex"
	"io/ioutil"
	"os"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/logs"
	"a.yandex-team.ru/passport/shared/golibs/utils"
)

func TestCreateKeyringBadParams(t *testing.T) {
	require := require.New(t)

	logs := logs.NewNullLogs()

	cases := []struct {
		config KeyringConfig
		err    string
	}{
		{
			err: "empty keys file path",
		},
		{
			config: KeyringConfig{
				KeysFile:         "",
				KeysReloadPeriod: utils.Duration{Duration: 0},
			},
			err: "empty keys file path",
		},
		{
			config: KeyringConfig{
				KeysFile:         "missing file",
				KeysReloadPeriod: utils.Duration{Duration: 0},
			},
			err: "invalid keys reload period",
		},
		{
			config: KeyringConfig{
				KeysFile:         "missing file",
				KeysReloadPeriod: utils.Duration{Duration: -1 * time.Second},
			},
			err: "invalid keys reload period",
		},
		{
			config: KeyringConfig{
				KeysFile:         "missing file",
				KeysReloadPeriod: utils.Duration{Duration: 1 * time.Second},
			},
			err: "failed to stat keys file missing file",
		},
	}

	for _, c := range cases {
		keyring, err := NewKeyring(&c.config, logs)
		require.Nil(keyring)
		require.Error(err)
		require.Contains(err.Error(), c.err)
	}
}

func TestCreateKeyringBadConfig(t *testing.T) {
	require := require.New(t)

	logs := logs.NewNullLogs()

	configDir := "./tmp"
	configFileName := configDir + "/config.json"

	require.NoError(os.Mkdir(configDir, os.ModePerm))
	defer os.RemoveAll(configDir)

	config := KeyringConfig{
		KeysFile:         configFileName,
		KeysReloadPeriod: utils.Duration{Duration: 1 * time.Second},
	}

	cases := []struct {
		config string
		err    string
	}{
		{
			config: "",
			err:    "Failed to parse keys file ./tmp/config.json",
		},
		{
			config: "key=value",
			err:    "Failed to parse keys file ./tmp/config.json",
		},
		{
			config: "{ key }",
			err:    "Failed to parse keys file ./tmp/config.json",
		},
		{
			config: "{ \"key\": \"body\" }",
			err:    "Failed to parse keys file ./tmp/config.json",
		},
		{
			config: "[ 1, 2, 3]",
			err:    "Failed to parse keys file ./tmp/config.json",
		},
		{
			config: "[ {} ]",
			err:    "Bad hex key: ",
		},
		{
			config: `[ {"id": 1, "body": "qwerty"} ]`,
			err:    "Bad hex key: qwerty",
		},
	}

	for _, c := range cases {
		require.NoError(ioutil.WriteFile(configFileName, []byte(c.config), os.ModePerm))

		keyring, err := NewKeyring(&config, logs)
		require.Nil(keyring)
		require.Error(err)
		require.Contains(err.Error(), c.err)
	}
}

func TestCreateUpdateKeyring(t *testing.T) {
	require := require.New(t)

	logs := logs.NewNullLogs()

	configDir := "./tmp"
	configFileName := configDir + "/config.json"

	require.NoError(os.Mkdir(configDir, os.ModePerm))
	defer os.RemoveAll(configDir)

	config := KeyringConfig{
		KeysFile:         configFileName,
		KeysReloadPeriod: utils.Duration{Duration: 1 * time.Second},
	}

	configData := `[ {"id": 1, "body": "0123456789abcdef","create_ts":12345}, {"id":2, "body": "123456"}, {"id":2, "body":"abcdef"}, {"id":9,"body":"DEADBEEF","create_ts":1111111111} ]`

	require.NoError(ioutil.WriteFile(configFileName, []byte(configData), os.ModePerm))

	keyring, err := NewKeyring(&config, logs)
	require.NoError(err)

	require.Nil(keyring.getKey(0))
	require.Equal("0123456789abcdef", hex.EncodeToString(keyring.getKey(1)))
	require.Equal("abcdef", hex.EncodeToString(keyring.getKey(2)))
	require.Nil(keyring.getKey(3))
	require.Equal("deadbeef", hex.EncodeToString(keyring.getKey(9)))
	require.Nil(keyring.getKey(10))

	time.Sleep(1 * time.Second)

	stat, err := os.Stat(configFileName)
	require.NoError(err)

	configData = `[ {"id": 7, "body": "83c0783e6eddd38bb43ff04466d720981781229e8b596d2cc70db7b0fb453fbb","create_ts":12345}, {"id":9,"body":"f011fe8926e0fcfff727b6dd0cc483a2d7daaa006af9fb1796173294bfc87578","create_ts":1111111111} ]`

	require.NoError(ioutil.WriteFile(configFileName, []byte(configData), os.ModePerm))
	require.NoError(os.Chtimes(configFileName, stat.ModTime(), stat.ModTime()))

	require.NoError(keyring.update())

	// not updated because file mod time not changed
	require.Nil(keyring.getKey(0))
	require.Equal("0123456789abcdef", hex.EncodeToString(keyring.getKey(1)))
	require.Equal("abcdef", hex.EncodeToString(keyring.getKey(2)))
	require.Nil(keyring.getKey(3))
	require.Equal("deadbeef", hex.EncodeToString(keyring.getKey(9)))
	require.Nil(keyring.getKey(10))

	require.NoError(os.Chtimes(configFileName, time.Now(), time.Now()))

	require.NoError(keyring.update())

	require.Nil(keyring.getKey(0))
	require.Nil(keyring.getKey(1))
	require.Nil(keyring.getKey(2))
	require.Nil(keyring.getKey(3))
	require.Equal("83c0783e6eddd38bb43ff04466d720981781229e8b596d2cc70db7b0fb453fbb", hex.EncodeToString(keyring.getKey(7)))
	require.Equal("f011fe8926e0fcfff727b6dd0cc483a2d7daaa006af9fb1796173294bfc87578", hex.EncodeToString(keyring.getKey(9)))
	require.Nil(keyring.getKey(10))
}

func TestKeyringMonitor(t *testing.T) {
	require := require.New(t)

	loggers := logs.NewNullLogs()

	configDir := "./tmp"
	configFileName := configDir + "/config.json"

	require.NoError(os.Mkdir(configDir, os.ModePerm))
	defer os.RemoveAll(configDir)

	config := KeyringConfig{
		KeysFile:         configFileName,
		KeysReloadPeriod: utils.Duration{Duration: 3 * time.Second},
	}

	configData := `[ {"id": 1, "body": "0123456789abcdef","create_ts":12345} ]`

	require.NoError(ioutil.WriteFile(configFileName, []byte(configData), os.ModePerm))

	// first loaded config
	keyring, err := NewKeyring(&config, loggers)
	require.NoError(err)

	require.Nil(keyring.getKey(0))
	require.Equal("0123456789abcdef", hex.EncodeToString(keyring.getKey(1)))
	require.Nil(keyring.getKey(2))
	require.Nil(keyring.getKey(3))
	require.Nil(keyring.getKey(111))

	var wg sync.WaitGroup
	ctx, cancel := context.WithCancel(context.Background())

	wg.Add(1)
	go keyring.Monitor(ctx, &wg)

	time.Sleep(time.Second)

	require.Nil(keyring.getKey(0))
	require.Equal("0123456789abcdef", hex.EncodeToString(keyring.getKey(1)))
	require.Nil(keyring.getKey(2))
	require.Nil(keyring.getKey(3))
	require.Nil(keyring.getKey(111))

	time.Sleep(3 * time.Second)

	// after reload time config is the same
	require.Nil(keyring.getKey(0))
	require.Equal("0123456789abcdef", hex.EncodeToString(keyring.getKey(1)))
	require.Nil(keyring.getKey(2))
	require.Nil(keyring.getKey(3))
	require.Nil(keyring.getKey(111))

	configData = `[ {"id": 111, "body": "1111222233334444","create_ts":12345} ]`

	require.NoError(ioutil.WriteFile(configFileName, []byte(configData), os.ModePerm))

	time.Sleep(time.Second)

	// short after modification config is still the same
	require.Nil(keyring.getKey(0))
	require.Equal("0123456789abcdef", hex.EncodeToString(keyring.getKey(1)))
	require.Nil(keyring.getKey(2))
	require.Nil(keyring.getKey(3))
	require.Nil(keyring.getKey(111))

	time.Sleep(3 * time.Second)

	// config reloaded by monitoring thread
	require.Nil(keyring.getKey(0))
	require.Nil(keyring.getKey(1))
	require.Nil(keyring.getKey(2))
	require.Nil(keyring.getKey(3))
	require.Equal("1111222233334444", hex.EncodeToString(keyring.getKey(111)))

	cancel()
	wg.Wait()
}
