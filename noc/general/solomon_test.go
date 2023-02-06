package core

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestMakeShardIDSha1Last4(t *testing.T) {
	for inValue, exp := range map[string]string{
		"host1": "shard57",
		"host2": "shard85",
		"host3": "shard81",
	} {
		res := makeShardIDSha1Last4(inValue)
		assert.Equal(t, exp, res)
	}
}
