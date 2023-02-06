package aggregator

import (
	"net/netip"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestExtractIPv4FromIPv6(t *testing.T) {
	as := assert.New(t)
	res, ok := ExtractIPv4FromIPv6(netip.MustParseAddr("64:ff9b::ac18:ce42"))
	as.True(ok)
	as.Equal("172.24.206.66", res.String())
}
