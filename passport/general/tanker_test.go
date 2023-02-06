package translations

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetKeyValue(t *testing.T) {
	tc, err := NewTranslationsCache()
	assert.NoError(t, err)
	assert.NotEqual(t, tc.Get("ru", "permission_request_rerun_title"), "")
	assert.Equal(t, tc.Get("ru", "non_existing_key"), "")
}
