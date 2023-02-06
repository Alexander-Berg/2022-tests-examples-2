package xcfg

import (
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

type testConfig struct {
	F1    string `yaml:"f1"`
	Outer struct {
		Inner struct {
			Deep struct {
				Rabbit *RabbitConfig
			}
		}
	}
}

func (m *testConfig) Validate() error {
	if len(m.F1) == 0 {
		return fmt.Errorf("field 'f1' must not be empty")
	}

	return nil
}

type RabbitConfig struct {
	Hole string `yaml:"hole"`
}

func (m *RabbitConfig) Validate() error {
	if m == nil {
		return fmt.Errorf("must not be empty")
	}
	if len(m.Hole) == 0 {
		return fmt.Errorf("field 'hole' must not be empty")
	}

	return nil
}

func Test_LoadConfigWithRequiredField(t *testing.T) {
	cfg := &testConfig{}
	err := LoadConfigFromBytes([]byte(""), cfg)

	require.Error(t, err)
	require.Equal(t, "field 'f1' must not be empty", err.Error())
}

func Test_LoadConfigWithRequiredNestedField(t *testing.T) {
	cfg := &testConfig{}
	err := LoadConfigFromBytes([]byte("f1: power"), cfg)

	require.Error(t, err)
	require.Equal(t, "outer.inner.deep.rabbit: must not be empty", err.Error())
}

func Test_LoadConfigWithRequiredNestedField2(t *testing.T) {
	cfg := &testConfig{}
	err := LoadConfigFromBytes([]byte(`
f1: some
outer:
  inner:
    deep:
      rabbit: {}
`), cfg)

	require.Error(t, err)
	require.Equal(t, "outer.inner.deep.rabbit: field 'hole' must not be empty", err.Error())
}

type testIntConfig struct {
	F1 int `yaml:"f1" xcfg:"required"`
}

func Test_LoadConfigFromBytes(t *testing.T) {
	cfg := &testIntConfig{}
	err := LoadConfigFromBytes([]byte("f1: 1"), cfg)
	require.NoError(t, err)
}

func Test_LoadConfigFromFile(t *testing.T) {
	var tests = []struct {
		name     string
		file     string
		expected string
	}{
		{"no file", "", "open : no such file or directory"},
		{"unmarshal error", "cfg_bad_1.yaml", "yaml: unmarshal errors:\n  line 1: cannot unmarshal !!str `bad` into int"},
		{"required error", "cfg_bad_2.yaml", "f1: must be provided"},
		{"ok", "cfg_ok.yaml", ""},
	}
	cwd, _ := os.Getwd()
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			cfg := &testIntConfig{}
			file := filepath.Join(cwd, test.file)
			if test.file == "" {
				file = ""
			}
			err := LoadConfig(file, cfg)
			if test.expected == "" {
				require.NoError(t, err)
				return
			}
			require.Error(t, err)
			require.Equal(t, test.expected, err.Error())
		})
	}
}

func Test_LoadConfigWithBadIntValue(t *testing.T) {
	cfg := &testIntConfig{}
	err := LoadConfigFromBytes([]byte("f1: power"), cfg)
	require.Error(t, err)
	require.Equal(t, "yaml: unmarshal errors:\n  line 1: cannot unmarshal !!str `power` into int", err.Error())
}

type testFloat32Config struct {
	F1 float32 `yaml:"f1" xcfg:"required"`
}

func Test_LoadConfigWithUnknownKind(t *testing.T) {
	cfg := &testFloat32Config{}
	err := LoadConfigFromBytes([]byte("f1:"), cfg)
	require.Error(t, err)
	require.Equal(t, "unknown float32 kind for required [].f1", err.Error())
}

type testRequiredConfig struct {
	AS1 []string `yaml:"as1" xcfg:"required"`
	S1  string   `yaml:"s1" xcfg:"required"`
	I1  int      `yaml:"i1" xcfg:"required"`
}

func Test_LoadConfigWithRequiredTag(t *testing.T) {
	var tests = []struct {
		name     string
		cfg      []byte
		expected string
	}{
		{"empty array", []byte(`
as1:
s1: some
i1: 1
`), "as1: must be provided"},
		{"empty string", []byte(`
as1: []
s1:
i1: 1
`), "s1: must be provided"},
		{"empty integer", []byte(`
as1:
  - test1
s1: some
i1:
`), "i1: must be provided"},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			cfg := &testRequiredConfig{}
			err := LoadConfigFromBytes(test.cfg, cfg)
			require.Error(t, err)
			require.Equal(t, test.expected, err.Error())
		})
	}
}
