package deploy_test

import (
	"io/ioutil"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
	"gopkg.in/yaml.v2"

	grpcconfig "a.yandex-team.ru/security/xray/internal/servers/grpc/config"
	humanizerconfig "a.yandex-team.ru/security/xray/internal/servers/humanizer/config"
	watcherconfig "a.yandex-team.ru/security/xray/internal/servers/watcher/config"
	workerconfig "a.yandex-team.ru/security/xray/internal/servers/worker/config"
)

func TestConfigs(t *testing.T) {
	cases := []struct {
		name   string
		target interface{}
	}{
		{
			name:   "grpc_api.yaml",
			target: new(grpcconfig.Config),
		},
		{
			name:   "humanizer.yaml",
			target: new(humanizerconfig.Config),
		},
		{
			name:   "stage_watcher.yaml",
			target: new(watcherconfig.Config),
		},
		{
			name:   "worker.yaml",
			target: new(workerconfig.Config),
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			yamlCFG, err := ioutil.ReadFile(filepath.Join("configs", tc.name))
			require.NoError(t, err)

			require.NoError(t, yaml.UnmarshalStrict(yamlCFG, tc.target))
		})
	}
}
