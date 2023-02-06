package httpdtvm

import (
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/yandex/tvm"
)

func TestReadSettingsEmpty(t *testing.T) {
	_, err := readSettings(TvmConfig{})
	require.EqualError(t, err, "tvm cache dir is not configured")

	settings, err := readSettings(TvmConfig{
		CacheDir: "some_dir",
	})
	require.NoError(t, err)
	assert.Nil(t, settings.BlackboxEnv)
	assert.Nil(t, settings.ServiceTicketOptions)
}

func TestReadSettingsWithEnv(t *testing.T) {
	_, err := readSettings(TvmConfig{
		CacheDir:    "some_dir",
		BlackboxEnv: "kek",
	})
	require.EqualError(t, err, "blackbox env is unknown: 'kek'")

	settings, err := readSettings(TvmConfig{
		CacheDir:    "some_dir",
		BlackboxEnv: "test",
	})
	require.NoError(t, err)
	assert.NotNil(t, settings.BlackboxEnv)
	assert.Equal(t, tvm.BlackboxTest, *settings.BlackboxEnv)
	assert.Nil(t, settings.ServiceTicketOptions)
}

func TestReadSettingsWithServiceTicketOptions(t *testing.T) {
	settings, err := readSettings(TvmConfig{
		CacheDir:     "some_dir",
		Destinations: map[string]tvm.ClientID{"somealias": 42},
	})
	require.NoError(t, err)
	assert.Nil(t, settings.BlackboxEnv)
	assert.NotNil(t, settings.ServiceTicketOptions)

	require.NoError(t, os.Setenv("FOO", ""))
	_, err = readSettings(TvmConfig{
		CacheDir:     "some_dir",
		SecretEnvVar: "FOO",
	})
	require.EqualError(t, err, "Failed to get TVM client secret from env var 'FOO'")

	require.NoError(t, os.Setenv("FOO", "kek"))
	defer func() { _ = os.Setenv("FOO", "") }()

	settings, err = readSettings(TvmConfig{
		CacheDir:     "some_dir",
		SecretEnvVar: "FOO",
	})
	require.NoError(t, err)
	assert.Nil(t, settings.BlackboxEnv)
	assert.NotNil(t, settings.ServiceTicketOptions)
}

func TestConvertBbEnv(t *testing.T) {
	type Case struct {
		in       string
		notFound bool
		env      tvm.BlackboxEnv
		err      string
	}
	cases := []Case{
		{in: "", notFound: true},
		{in: "prod", env: tvm.BlackboxProd},
		{in: "kek", err: "blackbox env is unknown: 'kek'"},
	}

	for idx, c := range cases {
		res, err := convertBbEnv(c.in)

		if c.err == "" {
			assert.NoError(t, err, idx)

			if c.notFound {
				assert.Nil(t, res, idx)
			} else {
				assert.NotNil(t, res, idx)
				assert.Equal(t, c.env, *res, idx)
			}
		} else {
			assert.EqualError(t, err, c.err, idx)
		}
	}
}

func TestReadSecret(t *testing.T) {
	secret, err := readSecret("", "")
	require.NoError(t, err)
	require.Equal(t, "", secret)

	_, err = readSecret("foo", "bar")
	require.EqualError(t, err, "options 'secret_env_var' and 'secret_filepath' conflict with each other: you should provide only one option")
}

func TestReadSecretFromEnv(t *testing.T) {
	require.NoError(t, os.Setenv("FOO", ""))
	_, err := readSecret("FOO", "")
	require.EqualError(t, err, "Failed to get TVM client secret from env var 'FOO'")

	require.NoError(t, os.Setenv("FOO", "kek"))
	defer func() { _ = os.Setenv("FOO", "") }()

	secret, err := readSecret("FOO", "")
	require.NoError(t, err)
	require.Equal(t, "kek", secret)
}

func TestReadSecretFromFile(t *testing.T) {
	_ = os.Remove("bar")

	_, err := readSecret("", "bar")
	require.Error(t, err)
	require.Contains(t, err.Error(), "Failed to read TVM secret")

	require.NoError(t, ioutil.WriteFile("bar", []byte("lol"), os.FileMode(0666)))
	defer func() { _ = os.Remove("bar") }()

	secret, err := readSecret("", "bar")
	require.NoError(t, err)
	require.Equal(t, "lol", secret)
}
