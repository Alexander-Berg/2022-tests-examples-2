package ebn

import (
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/noc/go/xcfg"
)

func Test_LoadConfig_Ok(t *testing.T) {
	cfg, err := LoadConfig("config-local.yaml")
	require.NoError(t, err)
	require.Equal(t, cfg.HTTP.Address, ":8081")
	require.Equal(t, cfg.HTTP.UIDir, "ui")
}

func Test_LoadConfig_Error(t *testing.T) {
	_, err := LoadConfig("")
	require.Error(t, err)
	require.Equal(t, "open : no such file or directory", err.Error())
}

func Test_LoadConfig_b64_Ok(t *testing.T) {
	cfg, err := LoadConfig("config-local.yaml.b64")
	require.NoError(t, err)
	require.Equal(t, cfg.HTTP.Address, ":8081")
	require.Equal(t, cfg.HTTP.UIDir, "ui")
}

func Test_LoadConfig_b64_Error(t *testing.T) {
	var tests = []struct {
		name     string
		filename string
		expected string
	}{
		{"bad b64", "config-local.yaml.bad-b64",
			"illegal base64 data at input byte 467"},
		{"bad yaml", "config-local.bad-yaml.b64",
			"yaml: unmarshal errors:\n  line 14: field sslmode not found in type database.Config"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			_, err := LoadConfig(test.filename)
			require.Error(t, err)
			require.Equal(t, test.expected, err.Error())
		})
	}
}

func TestConfig_Validate(t *testing.T) {
	head := []byte(`
log_config:
db_config:
  hosts:
    - 127.0.0.1
  port: 5432
  dbname: test
  user: test
  password: test
`)
	var tests = []struct {
		name     string
		cfg      []byte
		expected string
	}{
		{"no http", []byte(``), "field 'HTTP' must not be empty"},
		{"empty http", []byte(`http:`), "field 'HTTP' must not be empty"},
		{"empty http address", []byte(`http:
  address: ""`), "field 'HTTP.Address' must not be empty"},
		{"empty http ui dir", []byte(`http:
  address: ":8081"`), "field 'HTTP.UI' must not be empty"}, {"empty http ui dir", []byte(`http:
  address: ":8081"
  ui: /bad/dir`), "field 'HTTP.UI' must be valid path"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			cfg := &Config{}
			err := xcfg.LoadConfigFromBytes(append(head, test.cfg...), cfg)
			require.Error(t, err)
			require.Equal(t, test.expected, err.Error())
		})
	}
}
