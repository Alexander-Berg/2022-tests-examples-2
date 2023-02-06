package tools

import (
	"testing"
)

// DomainNameReverse implements a conversion from
// zone notation to a CIDR in ip4 and ip6, for ip4
// partial variants all should be implemented
func TestExtractAddressFromReverse(t *testing.T) {

	type TTestsReverse struct {
		arpa string
		cidr string
	}

	var TestsReverse = []TTestsReverse{
		{"7.1.5.c.8.c.e.5.d.7.c.4.0.0.0.0.1.a.1.4.0.0.c.0.8.b.6.0.2.0.a.2.ip6.arpa", "2a02:6b8:c00:41a1:0:4c7d:5ec8:c517"},
		{"7.1.5.c.8.c.e.5.d.7.c.4.0.0.0.0.1.a.1.4.0.0.c.0.8.b.6.0.2.0.a.2.ip6.arpa.", "2a02:6b8:c00:41a1:0:4c7d:5ec8:c517"},
		{"1.1.1.10.in-addr.arpa", "10.1.1.1"},
		{"1.1.1.10.in-addr.arpa.", "10.1.1.1"},
	}

	for _, pair := range TestsReverse {
		v := ExtractAddressFromReverse(pair.arpa)
		if v != pair.cidr {
			t.Error(
				"for", pair.arpa,
				"expected", pair.cidr,
				"got", v,
			)
		}
	}
}
