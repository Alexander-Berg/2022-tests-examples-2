package cvs

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParse(t *testing.T) {
	c := NewCvsClient()
	input := "yandex.ru 2a02:6b8:a::a XXX XXXX\nq.yandex.ru 2a02:6b8::242 YYY YYYY\n"
	targets := c.parseDNSCache(input)
	require.Equal(t, 2, len(targets))
	require.Equal(t, "2a02:6b8:a::a", targets[0].IP.String())
	require.Equal(t, "yandex.ru", *targets[0].FQDN)
	require.Equal(t, "2a02:6b8::242", targets[1].IP.String())
	require.Equal(t, "q.yandex.ru", *targets[1].FQDN)
}
