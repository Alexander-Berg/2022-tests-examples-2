package decryptor

import (
	"encoding/hex"
	"io/ioutil"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/yasmsd/internal/logs"
	"a.yandex-team.ru/passport/shared/golibs/utils"
)

func TestLooksLikeEncrypted(t *testing.T) {
	badCases := []string{
		"",
		"1:1",
		"1:1:35e9ca653c69104c300726c2:7abcef:56a70bac2ea734d1ea29d016fda",
		"2:5:8e65c6e09ad911bd5badf900:7a:bb8407dfef741c0c8f0a2490e43646f2",
		"1:5.8e65c6e09ad911bd5badf900:7a:bb8407dfef741c0c8f0a2490e43646f2",
		"1:5:8e65c6e09ad911bd5badf900:7aыbb8407dfef741c0c8f0a2490e43646f2",
		"1:5:8e65c6e09_d911bd5badf900:7a:bb8407dfef741c0c8f0a2490e43646f2",
	}

	goodCases := []string{
		"1:5:8e65c6e09ad911bd5badf900:7a:bb8407dfef741c0c8f0a2490e43646f2",
		"1:100500:8e65c6e09ad911bd5badf900:2d6bd78921a44c1a3275a974232123f74ddb9abd56ee160e6d307cfbfd80a7b8:bb8407dfef741c0c8f0a2490e43646f2",
	}

	for _, c := range badCases {
		require.False(t, looksLikeEncrypted([]byte(c)))
	}

	for _, c := range goodCases {
		require.True(t, looksLikeEncrypted([]byte(c)))
	}
}

func TestDecodeHexField(t *testing.T) {
	b, err := decodeHexField([]byte(""), "field")
	require.Error(t, err)
	require.Contains(t, err.Error(), "bad field format: ")
	require.Nil(t, b)

	b, err = decodeHexField([]byte("no"), "field")
	require.Error(t, err)
	require.Contains(t, err.Error(), "bad field format: no")
	require.Nil(t, b)

	b, err = decodeHexField([]byte("abcde"), "field")
	require.Error(t, err)
	require.Contains(t, err.Error(), "bad field format: abcde")
	require.Nil(t, b)

	b, err = decodeHexField([]byte("0abcde"), "field")
	require.NoError(t, err)
	require.Equal(t, []byte{0xa, 0xbc, 0xde}, b)
}

func TestParseEncrypted(t *testing.T) {
	badCases := []struct {
		str string
		err string
	}{
		{
			str: "",
			err: "bad field count",
		},
		{
			str: "unencrypted sms text message",
			err: "bad field count",
		},
		{
			str: "1:2:3:4:5:6:7",
			err: "bad field count",
		},
		{
			str: "8:8:8:8:8",
			err: "bad version: 8",
		},
		{
			str: "1::a:b:c",
			err: "bad key id: ",
		},
		{
			str: "1:a:b:c:d",
			err: "bad key id: a",
		},
		{
			str: "1:1::b:c",
			err: "bad iv format: ",
		},
		{
			str: "1:2:3:b:c",
			err: "bad iv format: 3",
		},
		{
			str: "1:2:abcd::c",
			err: "bad body format: ",
		},
		{
			str: "1:2:abcd:body:c",
			err: "bad body format: body",
		},
		{
			str: "1:2:abcd:12345678abcd:",
			err: "bad tag format: ",
		},
		{
			str: "1:2:abcd:12345678abcd:tag",
			err: "bad tag format: tag",
		},
		{
			str: "1:2:abcd:12345678abcd:123",
			err: "bad tag format: 123",
		},
	}

	for _, c := range badCases {
		d, err := parseEncrypted([]byte(c.str))
		require.Nil(t, d)
		require.Error(t, err)
		require.Contains(t, err.Error(), c.err)
	}

	d, err := parseEncrypted([]byte("1:100500:8e65c6e09ad911bd5badf900:2d6bd78921a44c1a3275a974232123f74ddb9abd56ee160e6d307cfbfd80a7b8:bb8407dfef741c0c8f0a2490e43646f2"))
	require.NoError(t, err)
	require.Equal(t, 100500, d.keyID)
	require.Equal(t, "8e65c6e09ad911bd5badf900", hex.EncodeToString(d.iv))
	require.Equal(t, "2d6bd78921a44c1a3275a974232123f74ddb9abd56ee160e6d307cfbfd80a7b8", hex.EncodeToString(d.body))
	require.Equal(t, "bb8407dfef741c0c8f0a2490e43646f2", hex.EncodeToString(d.tag))
}

func TestDecryptor(t *testing.T) {
	loggers := logs.NewNullLogs()

	configDir := "./tmp"
	configFileName := configDir + "/config.json"

	require.NoError(t, os.Mkdir(configDir, os.ModePerm))
	defer os.RemoveAll(configDir)

	cfg := KeyringConfig{
		KeysFile:         configFileName,
		KeysReloadPeriod: utils.Duration{Duration: 1 * time.Second},
	}

	configData := `[ {"id": 10, "body": "8a91d7c21672cb6fedc7561794086d1dd09b531b23be21420d5cb2ff4644410a","create_ts":12345}, {"id":9,"body":"DEADBEEF","create_ts":1111111111}, {"id":100500, "body": "6810f87d177ae701e44b78d726eb59df9c7b8733875d5bbdfdb54cdaf42ed617"}, {"id": 2, "body": "0032f5654b65d7f1a9a53b5df888d29f63fde51d87ab71f6eac25fdfa4648379"}]`

	require.NoError(t, ioutil.WriteFile(configFileName, []byte(configData), os.ModePerm))

	keyring, err := NewKeyring(&cfg, loggers)
	require.NoError(t, err)

	decryptor := NewDecryptor(keyring, loggers)

	text, err := decryptor.DecryptText([]byte("незашифрованное SMS старого формата"), "", 0)
	require.NoError(t, err)
	require.Equal(t, "незашифрованное SMS старого формата", string(text))

	text, err = decryptor.DecryptText([]byte("незашифрованное SMS старого формата"), "phone number which is unused", 0)
	require.NoError(t, err)
	require.Equal(t, "незашифрованное SMS старого формата", string(text))

	text, err = decryptor.DecryptText([]byte(""), "", 0)
	require.NoError(t, err)
	require.Equal(t, "", string(text))

	text, err = decryptor.DecryptText([]byte("1:2:3:4:5:6:7"), "123", 0)
	require.NoError(t, err)
	require.Equal(t, "1:2:3:4:5:6:7", string(text))

	text, err = decryptor.DecryptText([]byte("1:10:ec75cbb9eb187492592818d5:a367d39740bb6611b565e19a24fc3c8a73875e5f5e71609cee9ddaee:ea5e8e888401336afc6e08b6d2323a8f"), "", 0)
	require.NoError(t, err)
	require.Equal(t, "test зашЫфровано!", string(text))

	text, err = decryptor.DecryptText([]byte("1:2:3f056011f0f47433f3165e9c:df68f0756b39b6ecde2c14e15a4c7da37091b742ae6098df1d55ad90:939953e014f2e0eeaa4f0b1d7c2c715e"), "+70001112233", 0)
	require.NoError(t, err)
	require.Equal(t, "test зашЫфровано!", string(text))

	text, err = decryptor.DecryptText([]byte("1:10:ec75cbb9eb187492592818d5:a367d39740bb6611b565e19a24fc3c8a73875e5f5e71609cee9ddaee:ea5e8e888401336afc6e08b6d2323a8f"), "+70001112233", 0)
	require.Error(t, err)
	require.Contains(t, err.Error(), "cipher: message authentication failed")
	require.Nil(t, text)

	text, err = decryptor.DecryptText([]byte("1:2:3f056011f0f47433f3165e9c:df68f0756b39b6ecde2c14e15a4c7da37091b742ae6098df1d55ad90:939953e014f2e0eeaa4f0b1d7c2c715e"), "", 0)
	require.Error(t, err)
	require.Contains(t, err.Error(), "cipher: message authentication failed")
	require.Nil(t, text)

	text, err = decryptor.DecryptText([]byte("1:2:3f056011f0f47433f3165e9c:df68f0756b39b6ecde2c14e15a4c7da37091b742ae6098df1d55ad90:939953e014f2e0eeaa4f0b1d7c2c715e"), "+79161111111", 0)
	require.Error(t, err)
	require.Contains(t, err.Error(), "cipher: message authentication failed")
	require.Nil(t, text)

	text, err = decryptor.DecryptText([]byte("1:100500:6e6690af8bc43bd05f293b8f:09706c2fda5163e9bd0c3751dd:045f647689f3d2f5b81e343493e5b2d1"), "", 0)
	require.NoError(t, err)
	require.Equal(t, "[]{}+\"'*#$@<>", string(text))

	text, err = decryptor.DecryptText([]byte("1:100500:7e0dfe7d5e1fcd4e4df4b63f:79cdb0e7:41e2aedb955b16e74ba5ae71e05cfe13"), "", 0)
	require.NoError(t, err)
	require.Equal(t, "\xf0\x9f\xa4\xa6", string(text))
}
