package netmap

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParse(t *testing.T) {
	c, err := NewNetmapClient()
	if err != nil {
		t.Errorf("error on NewNetmapClient: %v", err)
	}
	input := "2a02:6b8:a::a\tXXXX\n2a02:6b8::242\tYYY\n"
	targets := c.parseNetmap(input)

	require.Equal(t, 2, len(targets))
	require.Equal(t, "2a02:6b8:a::a", targets[0].IP.String())
	require.Equal(t, "2a02:6b8::242", targets[1].IP.String())
}
