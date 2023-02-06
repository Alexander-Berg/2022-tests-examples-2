package core

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestFixTopic(t *testing.T) {
	topic, err := fixTopic("rt3.vla--noc@nocdev--syslog")
	assert.NoError(t, err)
	assert.Equal(t, "/noc/nocdev/syslog", topic)
}
