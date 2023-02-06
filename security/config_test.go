package config

import (
	"io/ioutil"
	"net"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
	"gopkg.in/yaml.v2"
)

func TestConfigCreateParse(t *testing.T) {
	const testFilename = "config.yaml"

	tempDir, err := ioutil.TempDir("", "tmp_osquery_")
	if err != nil {
		t.Fatal(err.Error())
	}

	tempFile := filepath.Join(tempDir, testFilename)
	config := createConfigAndSave(t, tempFile)
	newConfig := loadConfigFromFile(t, tempFile)

	require.Equal(t, config, newConfig)

	defer func() { _ = os.RemoveAll(tempDir) }()
}

func createConfigAndSave(t *testing.T, filename string) *SenderConfig {
	testConfig := &SenderConfig{
		false,
		0,
		0,
		0,
		"test_key_file",
		"test_cert_file",
		[]string{"other_test_key_file", "another_test_key_file"},
		[]string{"other_test_cert_file", "another_test_cert_file"},
		0,
		0,
		false,
		map[string]*HostConfig{
			"localhost:8008": {
				"test_spllunk_enroll",
				true,
				"http://test-splunk-url:9090/test",
				"test_splunk_token",
				"",
			},
			"evil.com": {
				"test_evil_enroll_secret",
				false,
				"https://evil.com/",
				"test_evil_com_token",
				"",
			},
		},
		"test_test_test",
		&SplunkConfig{
			QueueLength: 12,
			Workers:     34,
		},
		true,
		[]string{"hostname_key"},
		[]string{"cloud_id"},
		[]AddForPeersConfig{
			{
				Subnets: []Subnet{
					{mustParseCidr(t, "::/0")},
					{mustParseCidr(t, "0.0.0.0/0")},
				},
				Values: map[string]string{
					"field1": "value1",
					"field2": "value2",
				},
			},
		},
		nil,
		nil,
		nil,
		nil,
	}

	data, err := yaml.Marshal(testConfig)
	require.NoError(t, err)

	err = ioutil.WriteFile(filename, data, os.ModePerm)
	require.NoError(t, err, "failed to save config")

	return testConfig
}

func mustParseCidr(t *testing.T, s string) *net.IPNet {
	_, subnet, err := net.ParseCIDR(s)
	require.NoError(t, err)
	return subnet
}

func loadConfigFromFile(t *testing.T, filename string) *SenderConfig {
	conf, err := FromFile(filename)
	require.NoError(t, err)

	require.Equal(t, false, conf.EnableTLS, "tls must not be enabled by default")
	require.NotEmpty(t, conf.HostsConfig)

	return conf
}
