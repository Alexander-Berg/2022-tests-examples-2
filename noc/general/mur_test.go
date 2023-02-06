package murchi

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCleanupPath(t *testing.T) {
	assert.Equal(t, "/",
		CleanupPath("/"))
	assert.Equal(t, "/documents",
		CleanupPath("/documents"))
	assert.Equal(t, "/documents/{document_id}",
		CleanupPath("/documents/{document_id:[0-9]+}"))
	assert.Equal(t, "/a/{a_id}/b/{b_id}",
		CleanupPath("/a/{a_id:[0-9]+}/b/{b_id:[0-9]+}"))
}
