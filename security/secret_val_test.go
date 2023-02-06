package passutil_test

import (
	"reflect"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/skotty/skotty/internal/passutil"
)

func TestEncryptDecrypt(t *testing.T) {
	enc, err := passutil.Encrypt([]byte("tst"), []byte("key"))
	require.NoError(t, err)

	out, err := passutil.Decrypt(enc, []byte("lol"))
	require.Error(t, err)
	require.Empty(t, out)

	out, err = passutil.Decrypt(enc, []byte("key"))
	require.NoError(t, err)
	require.Equal(t, []byte("tst"), out)
}

func TestSecretVal(t *testing.T) {
	enc, err := passutil.SecretVal("").ToEncrypted()
	require.NoError(t, err)
	require.Empty(t, enc)

	val := passutil.SecretVal("tst")
	require.Equal(t, "tst", string(val))
	enc, err = val.ToEncrypted()
	require.NoError(t, err)
	require.Regexp(t, `^secret:[0-9a-f]+:[0-9a-f]+$`, enc)
	yamlEnc, err := val.MarshalYAML()
	require.NoError(t, err)
	enc, ok := yamlEnc.(string)
	require.True(t, ok)

	require.NoError(t, val.FromAny("tst1"))
	require.Equal(t, "tst1", val.String())

	require.NoError(t, val.UnmarshalYAML(func(v interface{}) error {
		reflect.ValueOf(v).Elem().SetString("tst1")
		return nil
	}))
	require.Equal(t, "tst1", val.String())

	require.NoError(t, val.FromAny(enc))
	require.Equal(t, "tst", val.String())

	require.NoError(t, val.UnmarshalYAML(func(v interface{}) error {
		reflect.ValueOf(v).Elem().SetString(enc)
		return nil
	}))
	require.Equal(t, "tst", val.String())
}
