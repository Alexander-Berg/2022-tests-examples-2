package config

import (
	"encoding/xml"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type TestEnvConfig struct {
	Token FromEnv `xml:"token"`
	MyStr string  `xml:"my-str"`
	MyInt int     `xml:"my-int"`
}

func TestParseEnvConfig(t *testing.T) {
	testCases := []struct {
		name      string
		rawConfig []byte
		parser    func([]byte, *TestEnvConfig) error
	}{
		{
			name: "test_xml",
			rawConfig: []byte(`
<yandex>
	<my-str>asd</my-str>
	<token from-env="TOKEN" />
	<my-int>123</my-int>
</yandex>
			`),
			parser: func(rawConfig []byte, config *TestEnvConfig) error {
				return xml.Unmarshal(rawConfig, config)
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			_ = os.Setenv("TOKEN", "secret")
			var parsedConfig TestEnvConfig

			err := tc.parser(tc.rawConfig, &parsedConfig)
			require.NoError(t, err)

			assert.Equal(t, "asd", parsedConfig.MyStr)
			assert.Equal(t, 123, parsedConfig.MyInt)
			assert.Equal(t, "secret", string(parsedConfig.Token))

			_ = os.Unsetenv("TOKEN")
		})
	}
}

func TestMarshalEnvConfig(t *testing.T) {
	testCases := []struct {
		name           string
		config         *FromEnv
		marshaler      func(*TestEnvConfig) ([]byte, error)
		expectedConfig []byte
	}{
		{
			name: "marshal_xml",
			marshaler: func(c *TestEnvConfig) ([]byte, error) {
				return xml.Marshal(c)
			},
			expectedConfig: []byte(`<TestEnvConfig><token>token</token><my-str>asd</my-str><my-int>123</my-int></TestEnvConfig>`),
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			c := TestEnvConfig{
				Token: "token",
				MyStr: "asd",
				MyInt: 123,
			}

			result, err := tc.marshaler(&c)
			require.NoError(t, err)
			assert.Equal(t, tc.expectedConfig, result)
		})
	}
}
