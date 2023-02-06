package models

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestParseIPV4(t *testing.T) {
	target := Parse("192.168.1.1")
	require.NotNil(t, target.IP)
	require.Equal(t, "192.168.1.1", target.IP.String())
}

func TestParseIPV6(t *testing.T) {
	target := Parse("2a02:6b8:a::a")
	require.NotNil(t, target.IP)
	require.Equal(t, "2a02:6b8:a::a", target.IP.String())
}

func TestParseIPV4NET(t *testing.T) {
	target := Parse("192.168.0.1/24")
	require.NotNil(t, target.NET)
	require.Equal(t, "192.168.0.0/24", target.NET.String())
}

func TestParseIPV6NET(t *testing.T) {
	target := Parse("2a02:6b8:a::a/48")
	require.NotNil(t, target.NET)
	require.Equal(t, "2a02:6b8:a::/48", target.NET.String())
}

func TestParseMTNNET(t *testing.T) {
	target := Parse("47a2@2a02:6b8:c00::/40")
	require.NotNil(t, target.NET)
	require.NotNil(t, target.ProjectID)
	require.Equal(t, "2a02:6b8:c00::/40", target.NET.String())
	require.Equal(t, "47a2", *target.ProjectID)
}

func TestParseFQDN(t *testing.T) {
	target := Parse("debby.sec.yandex-team.ru")
	require.Equal(t, "debby.sec.yandex-team.ru", *target.FQDN)
}

func TestParseDumps(t *testing.T) {
	tables := []struct {
		in  string
		out string
	}{
		{"192.168.0.1", "192.168.0.1"},
		{"2a02:6b8:a::a", "2a02:6b8:a::a"},
		{"192.168.0.1/24", "192.168.0.0/24"},
		{"2a02:6b8:a::a/48", "2a02:6b8:a::/48"},
		{"47a2@2a02:6b8:c00::/40", "47a2@2a02:6b8:c00::/40"},
		{"debby.sec.yandex-team.ru", "debby.sec.yandex-team.ru"},
	}

	for _, table := range tables {
		target := Parse(table.in)
		output := target.Dumps()
		require.Equal(t, table.out, output)
	}
}

func TestDumpsIPWithFQDN(t *testing.T) {
	ip := "2a02:6b8:a::a"
	fqdn := "yandex.ru"
	target := Parse(ip)
	target.FQDN = &fqdn
	out := target.Dumps()
	require.Equal(t, ip, out)
}
