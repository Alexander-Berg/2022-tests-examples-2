package config_test

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"

	"github.com/google/go-cmp/cmp"
	"github.com/google/go-cmp/cmp/cmpopts"
	"github.com/mitchellh/go-homedir"
	"github.com/stretchr/testify/require"
	"gopkg.in/yaml.v2"

	"a.yandex-team.ru/security/skotty/skotty/internal/config"
)

func TestMain(m *testing.M) {
	_ = os.Setenv("HOME", "/something/not/exists")
	os.Exit(m.Run())
}

func TestLoadAndBuild(t *testing.T) {
	cases, err := filepath.Glob(filepath.Join("testdata", "in", "*.yaml"))
	require.NoError(t, err)

	cmpOpts := cmp.Options{
		cmpopts.IgnoreFields(config.Startup{}, "ReplaceAuthSock"),
		cmpopts.IgnoreFields(config.KeyringYubikey{}, "PIN"),
		cmpopts.IgnoreFields(config.KeyringFiles{}, "Passphrase"),
		cmpIgnoreAnyString(),
	}

	for _, inFile := range cases {
		filename := filepath.Base(inFile)
		t.Run(filename, func(t *testing.T) {
			actualConfig, err := config.Load(inFile, true)
			require.NoError(t, err)

			expectedConfig := loadConfigFile(t, filepath.Join("testdata", "built", filename))
			if diff := cmp.Diff(expectedConfig, actualConfig, cmpOpts...); diff != "" {
				t.Fatalf("config mismatch: %s", diff)
			}
		})
	}
}

func TestLoadAndBuild_invalid(t *testing.T) {
	cases, err := filepath.Glob(filepath.Join("testdata", "invalid", "*.yaml"))
	require.NoError(t, err)

	for _, inFile := range cases {
		t.Run(filepath.Base(inFile), func(t *testing.T) {
			cfg, err := config.Load(inFile, true)
			require.Error(t, err)
			require.Nil(t, cfg)
		})
	}
}

func TestLoad(t *testing.T) {
	cases := []struct {
		filepath string
		err      bool
	}{
		{
			filepath: filepath.Join("testdata", "in", "minimal.yaml"),
			err:      false,
		},
		{
			filepath: "/lol/kek/cheburek.yaml",
			err:      true,
		},
	}
	for _, tc := range cases {
		t.Run(filepath.Base(tc.filepath), func(t *testing.T) {
			strictConfig, err := config.Load(tc.filepath, true)
			if tc.err {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.NotNil(t, strictConfig)
			}

			nonStrictConfig, err := config.Load(tc.filepath, false)
			require.NoError(t, err)
			require.NotNil(t, nonStrictConfig)

			if !tc.err {
				require.Equal(t, strictConfig, nonStrictConfig)
			}
		})
	}
}

func cmpIgnoreAnyString() cmp.Option {
	isAny := func(s string) bool {
		return s == "any"
	}

	notAny := func(s string) bool {
		return s != "any" && s != ""
	}

	return cmp.FilterValues(func(a, b string) bool {
		return isAny(a) && notAny(b) || isAny(b) && notAny(a)
	}, cmp.Ignore())
}

func loadConfigFile(t *testing.T, cfgPath string) *config.Config {
	homeDir, err := homedir.Dir()
	require.NoError(t, err)

	data, err := os.ReadFile(cfgPath)
	require.NoError(t, err)
	data = bytes.Replace(data, []byte{'~', '/'}, append([]byte(homeDir), filepath.Separator), -1)

	var out config.Config
	err = yaml.Unmarshal(data, &out)
	require.NoError(t, err)

	return &out
}
