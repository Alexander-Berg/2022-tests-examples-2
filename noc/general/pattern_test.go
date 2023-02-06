package pattern

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPattern(t *testing.T) {
	as := assert.New(t)
	pattern, err := NewPattern("/+/")
	as.Error(err)
	as.Nil(pattern)
	pattern, err = NewPattern("/^olo$/")
	as.NoError(err)
	as.True(pattern.Match("olo"))
	as.False(pattern.Match("-olo"))
	as.False(pattern.Match("olo-"))

	pattern, err = NewPattern("olo")
	as.NoError(err)
	as.True(pattern.Match("olo"))
	as.True(pattern.Match("-olo"))
	as.True(pattern.Match("olo-"))
}
