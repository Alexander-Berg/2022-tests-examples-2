package configuration

import (
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"gopkg.in/yaml.v2"
)

// The test pins the rendered default config so that it is easy to copy the structure.
// Each time you modify the test think if you need to modify your production config too.
func TestNewDefaultConfig(t *testing.T) {
	cfg := NewDefaultConfig()
	bytes, err := yaml.Marshal(cfg)
	if !assert.NoError(t, err) {
		return
	}
	curdir, err := os.Getwd()
	if !assert.NoError(t, err) {
		return
	}
	expected, err := ioutil.ReadFile("default.yaml")
	if !assert.NoError(t, err, "curdir: %s", curdir) {
		return
	}
	assert.Equal(t, string(expected), string(bytes))
}
