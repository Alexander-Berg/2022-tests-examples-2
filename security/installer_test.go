package installer_test

import (
	"crypto/sha256"
	"fmt"
	"io"
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

func requireSameFile(t *testing.T, expected, actual string) {
	hashFile := func(p string) (string, error) {
		f, err := os.Open(p)
		if err != nil {
			return "", err
		}

		defer func() { _ = f.Close() }()

		h := sha256.New()
		if _, err := io.Copy(h, f); err != nil {
			return "", err
		}

		return fmt.Sprintf("%x", h.Sum(nil)), nil
	}

	statE, err := os.Stat(expected)
	require.NoError(t, err)

	statA, err := os.Stat(actual)
	require.NoError(t, err)

	require.Equal(t, statE.Size(), statA.Size())
	require.Equal(t, statE.Mode(), statA.Mode())

	hashE, err := hashFile(expected)
	require.NoError(t, err)

	hashA, err := hashFile(actual)
	require.NoError(t, err)

	require.Equalf(t, hashE, hashA, "hash mismatch")
}
