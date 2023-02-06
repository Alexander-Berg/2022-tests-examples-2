package porto_test

import (
	"os"
	"testing"
)

func isPortoAllowed(t *testing.T) bool {
	if os.Getenv("TEST_LOCAL_PORTO") == "yes" {
		return true
	}

	t.Skip("skipping test; porto using not allowed (env[TEST_LOCAL_PORTO] != yes)")
	return false
}
