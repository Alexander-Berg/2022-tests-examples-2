package nuvault

import (
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestNewTLSConfig_woCert(t *testing.T) {
	cfg, err := newTLSConfig("")
	require.NoError(t, err)
	require.NotNil(t, cfg)
	require.NotNil(t, cfg.RootCAs)
}

func TestNewTLSConfig_fails(t *testing.T) {
	clientCerts, err := filepath.Glob(filepath.Join("testdata", "certs", "*.pem"))
	require.NoError(t, err)

	for _, certPath := range clientCerts {
		t.Run(filepath.Base(certPath), func(t *testing.T) {
			cfg, err := newTLSConfig(certPath)
			require.Error(t, err)
			require.Nil(t, cfg)
		})
	}
}
