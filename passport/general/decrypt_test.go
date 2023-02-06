package ytc

import (
	"encoding/base64"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/libs/go/keys"
)

func TestDecryptFailed(t *testing.T) {
	key, err := base64.StdEncoding.DecodeString("d3afIKJ+MB2ZnAMxwsNQN729osL9meb33YP/5wilfCU=")
	require.NoError(t, err)

	keyMap := keys.CreateKeyMap()
	keyMap.AddKey("1", key)
	require.NoError(t, keyMap.SetDefaultKeyID("1"))

	iv, err := base64.StdEncoding.DecodeString("iH+Z2iiFuBs4KaeK")
	require.NoError(t, err)
	text, err := base64.StdEncoding.DecodeString("89D9FuKIwuM/lLxCS9lwD/a7ZozU78Qt4VSQTCgJpMcxb+FzgIhUasdeAe4PiJCDSCuWNXVMjfXuZve4Ng==")
	require.NoError(t, err)
	tag, err := base64.StdEncoding.DecodeString("m4WK79aFsWMEF1E7")
	require.NoError(t, err)

	codec := "gzip"
	invalidCodec := "invalid"
	size := uint64(46)

	encrypted := EncryptedData{
		Version: 2,
		KeyID:   12,
		Iv:      iv,
		Text:    text,
		Tag:     tag,
		Codec:   &codec,
	}

	_, err = encrypted.Decrypt(keyMap)
	require.Error(t, err)
	require.Contains(t, err.Error(), "unsupported version: 2")

	encrypted.Version = 1
	_, err = encrypted.Decrypt(keyMap)
	require.Error(t, err)
	require.Contains(t, err.Error(), "failed to create cipher block")

	encrypted.KeyID = 1
	_, err = encrypted.Decrypt(keyMap)
	require.Error(t, err)
	require.Contains(t, err.Error(), "missing 'size' for compressed data")

	encrypted.Size = &size
	encrypted.Codec = &invalidCodec
	_, err = encrypted.Decrypt(keyMap)
	require.Error(t, err)
	require.Contains(t, err.Error(), "unsupported compression codec: invalid")
}

func TestDecrypt(t *testing.T) {
	key, err := base64.StdEncoding.DecodeString("d3afIKJ+MB2ZnAMxwsNQN729osL9meb33YP/5wilfCU=")
	require.NoError(t, err)

	keyMap := keys.CreateKeyMap()
	keyMap.AddKey("1", key)
	require.NoError(t, keyMap.SetDefaultKeyID("1"))

	iv, err := base64.StdEncoding.DecodeString("XicaYk6VkP+oAfMo")
	require.NoError(t, err)
	text, err := base64.StdEncoding.DecodeString("iXAL8FWDYmyhc4CLAyv6uEEFhdRnFPWJs5fOs7IoQwqVXaNp9O3/QS8RrLJSXno3qDs=")
	require.NoError(t, err)
	tag, err := base64.StdEncoding.DecodeString("6FFMmpv9BWb6XMJg")
	require.NoError(t, err)

	decrypted, err := decrypt(keyMap.GetKey("1"), iv, text, tag)
	require.NoError(t, err)
	require.Equal(t, `{"key":"value","other":{"key":"other value"}}"`, string(decrypted))

	encrypted := EncryptedData{
		Version: 1,
		KeyID:   1,
		Iv:      iv,
		Text:    text,
		Tag:     tag,
	}
	decrypted, err = encrypted.Decrypt(keyMap)
	require.NoError(t, err)
	require.Equal(t, `{"key":"value","other":{"key":"other value"}}"`, string(decrypted))
}

func TestDecryptCompressed(t *testing.T) {
	key, err := base64.StdEncoding.DecodeString("d3afIKJ+MB2ZnAMxwsNQN729osL9meb33YP/5wilfCU=")
	require.NoError(t, err)

	keyMap := keys.CreateKeyMap()
	keyMap.AddKey("1", key)
	require.NoError(t, keyMap.SetDefaultKeyID("1"))

	iv, err := base64.StdEncoding.DecodeString("iH+Z2iiFuBs4KaeK")
	require.NoError(t, err)
	text, err := base64.StdEncoding.DecodeString("89D9FuKIwuM/lLxCS9lwD/a7ZozU78Qt4VSQTCgJpMcxb+FzgIhUasdeAe4PiJCDSCuWNXVMjfXuZve4Ng==")
	require.NoError(t, err)
	tag, err := base64.StdEncoding.DecodeString("m4WK79aFsWMEF1E7")
	require.NoError(t, err)

	codec := "gzip"
	size := uint64(46)

	encrypted := EncryptedData{
		Version: 1,
		KeyID:   1,
		Iv:      iv,
		Text:    text,
		Tag:     tag,
		Codec:   &codec,
		Size:    &size,
	}
	decrypted, err := encrypted.Decrypt(keyMap)
	require.NoError(t, err)
	require.Equal(t, `{"key":"value","other":{"key":"other value"}}"`, string(decrypted))
}
