package xnetip

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"inet.af/netaddr"
)

func Test_ParseIPNetIPv4(t *testing.T) {
	net, err := ParseIPNet("93.158.134.158")
	require.NoError(t, err)
	assert.Equal(t, IPNet{addr: netaddr.MustParseIP("93.158.134.158"), mask: netaddr.MustParseIP("255.255.255.255")}, net)
}

func Test_ParseIPNetIPv4CIDR(t *testing.T) {
	net, err := ParseIPNet("127.0.0.1/23")
	require.NoError(t, err)
	assert.Equal(t, IPNet{addr: netaddr.MustParseIP("127.0.0.0"), mask: netaddr.MustParseIP("255.255.254.0")}, net)
}

func Test_ParseIPNetIPv4ExplicitMask(t *testing.T) {
	net, err := ParseIPNet("127.0.0.1/255.255.254.0")
	require.NoError(t, err)
	assert.Equal(t, IPNet{addr: netaddr.MustParseIP("127.0.0.0"), mask: netaddr.MustParseIP("255.255.254.0")}, net)
}

func Test_ParseIPNetIPv4ExplicitWildcardMask(t *testing.T) {
	net, err := ParseIPNet("127.0.1.1/255.255.0.255")
	require.NoError(t, err)
	assert.Equal(t, IPNet{addr: netaddr.MustParseIP("127.0.0.1"), mask: netaddr.MustParseIP("255.255.0.255")}, net)
}

func Test_ParseIPNetIPv6(t *testing.T) {
	net, err := ParseIPNet("2a02:6b8:0:3400::3:147")
	require.NoError(t, err)
	assert.Equal(t, IPNet{
		addr: netaddr.MustParseIP("2a02:6b8:0:3400::3:147"),
		mask: IPv6Ones,
	}, net)
}

func Test_ParseIPNetIPv6LongSegment(t *testing.T) {
	net, err := ParseIPNet("2a02:ffff0003:0:3400::3:147")
	require.Error(t, err)
	assert.Equal(t, IPNet{}, net)
}

func Test_ParseIPNetIPv4Mapped(t *testing.T) {
	net, err := ParseIPNet("::ffff:a9db:0d85")
	require.NoError(t, err)
	assert.Equal(t, IPNet{
		addr: netaddr.MustParseIP("::ffff:a9db:0d85"),
		mask: IPv6Ones,
	}, net)
}

func Test_ParseIPNetIPv6CIDR(t *testing.T) {
	net, err := ParseIPNet("2a02:6b8:0:3400::3:147/64")
	require.NoError(t, err)
	assert.Equal(t, IPNet{
		addr: netaddr.MustParseIP("2a02:6b8:0:3400::"),
		mask: netaddr.MustParseIP("ffff:ffff:ffff:ffff::"),
	}, net)
}

func Test_ParseIPNetIPv6ExplicitMask(t *testing.T) {
	net, err := ParseIPNet("2a02:6b8:0:3400::3:147/ffff:ffff:ffff:ffff::")
	require.NoError(t, err)
	assert.Equal(t, IPNet{
		addr: netaddr.MustParseIP("2a02:6b8:0:3400::"),
		mask: netaddr.MustParseIP("ffff:ffff:ffff:ffff::"),
	}, net)
}

func Test_ParseIPNetIPv6ExplicitWildcardMask(t *testing.T) {
	net, err := ParseIPNet("::badc:ab1e/::ffff:ffff")
	require.NoError(t, err)
	assert.Equal(t, IPNet{
		addr: netaddr.MustParseIP("::badc:ab1e"),
		mask: netaddr.MustParseIP("::ffff:ffff"),
	}, net)
}

func Test_ParseIPNetProjectIDSyntax(t *testing.T) {
	net, err := ParseIPNet("41b9@2a02:6b8:c00::/40")
	require.NoError(t, err)
	assert.Equal(t, IPNet{
		addr: netaddr.MustParseIP("2a02:6b8:c00:0:0:41b9::"),
		mask: netaddr.MustParseIP("ffff:ffff:ff00:0:ffff:ffff::"),
	}, net)
}

func Test_ParseIPNetProjectIDRangeSyntax(t *testing.T) {
	net, err := ParseIPNet("41b9/29@2a02:6b8:c00::/40")
	require.NoError(t, err)
	assert.Equal(t, IPNet{
		addr: netaddr.MustParseIP("2a02:6b8:c00:0:0:41b8::"),
		mask: netaddr.MustParseIP("ffff:ffff:ff00:0:ffff:fff8::"),
	}, net)
}

func Test_ParseIPNet_Empty(t *testing.T) {
	net, err := ParseIPNet("")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_ParseIPNet_OnlyProjectID(t *testing.T) {
	net, err := ParseIPNet("41b9")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_ParseIPNet_Malformed(t *testing.T) {
	net, err := ParseIPNet("41b9@41b9@2a02:6b8:c00::/40")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_ParseIPNet_InvalidProjectID(t *testing.T) {
	net, err := ParseIPNet("41b912345@2a02:6b8:c00::/40")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_ParseIPNet_InvalidProjectIDRangeCIDR(t *testing.T) {
	net, err := ParseIPNet("41b9/33@2a02:6b8:c00::/40")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_ParseIPNet_InvalidAddr(t *testing.T) {
	net, err := ParseIPNet("41b9@2a02:6b8:cZZZ::/40")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_ParseIPNet_MixedV4V6(t *testing.T) {
	net, err := ParseIPNet("93.158.134.158/2a02:6b8:c0::")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_ParseIPNet_MixedV6V4(t *testing.T) {
	net, err := ParseIPNet("2a02:6b8:c0::/93.158.134.158")
	require.Error(t, err)
	require.Equal(t, IPNet{}, net)
}

func Test_IPNetIPv4String(t *testing.T) {
	net, err := ParseIPNet("93.158.134.158")
	require.NoError(t, err)
	assert.Equal(t, "93.158.134.158", net.String())
}

func Test_IPNetIPv4CIDRString(t *testing.T) {
	{
		net, err := ParseIPNet("93.158.134.158/31")
		require.NoError(t, err)
		assert.Equal(t, "93.158.134.158/31", net.String())
	}
	{
		net, err := ParseIPNet("93.158.134.158/16")
		require.NoError(t, err)
		assert.Equal(t, "93.158.0.0/16", net.String())
	}
	{
		net, err := ParseIPNet("93.158.134.158/0")
		require.NoError(t, err)
		assert.Equal(t, "0.0.0.0/0", net.String())
	}
}

func Test_IPNetIPv4NonContinuousString(t *testing.T) {
	net, err := ParseIPNet("93.158.134.158/255.255.0.255")
	require.NoError(t, err)
	assert.Equal(t, "93.158.0.158/255.255.0.255", net.String())
}

func Test_IPNetIPv6String(t *testing.T) {
	net, err := ParseIPNet("2a02:6b8:0:3400::3:147")
	require.NoError(t, err)
	assert.Equal(t, "2a02:6b8:0:3400::3:147", net.String())
}

func Test_IPNetIPv6CIDRString(t *testing.T) {
	{
		net, err := ParseIPNet("2a02:6b8:0:3400::3:147/127")
		require.NoError(t, err)
		assert.Equal(t, "2a02:6b8:0:3400::3:146/127", net.String())
	}
	{
		net, err := ParseIPNet("2a02:6b8:0:3400::3:147/32")
		require.NoError(t, err)
		assert.Equal(t, "2a02:6b8::/32", net.String())
	}
	{
		net, err := ParseIPNet("2a02:6b8:0:3400::3:147/0")
		require.NoError(t, err)
		assert.Equal(t, "::/0", net.String())
	}
}

func Test_IPNetIPv6NonContinuousString(t *testing.T) {
	{
		net, err := ParseIPNet("2a02:6b8:0:0:1234:5678:3:147/ffff:ffff:0:0:ffff:ffff::")
		require.NoError(t, err)
		assert.Equal(t, "2a02:6b8::1234:5678:0:0/ffff:ffff::ffff:ffff:0:0", net.String())
	}

	{
		net, err := ParseIPNet("2a02:6b8:0:0:1234:5678:3:147/ffff:ffff:0:0:ffff:fff8::")
		require.NoError(t, err)
		assert.Equal(t, "2a02:6b8::1234:5678:0:0/ffff:ffff::ffff:fff8:0:0", net.String())
	}

	{
		net, err := ParseIPNet("2a02:6b8:0:0:1234:5678:3:147/ffff:ffff:0:0:ffff:fff0::")
		require.NoError(t, err)
		assert.Equal(t, "2a02:6b8::1234:5670:0:0/ffff:ffff::ffff:fff0:0:0", net.String())
	}
}

func Test_IPNetIPv6StringMaybeProjectID(t *testing.T) {
	net, err := ParseIPNet("2a02:6b8:c00:3400::3:147")
	require.NoError(t, err)
	assert.Equal(t, "2a02:6b8:c00:3400::3:147", net.StringMaybeProjectID())
}

func Test_IPNetIPv6NonContinuousStringMaybeProjectID(t *testing.T) {
	{
		net, err := ParseIPNet("2a02:6b8:c00:0:1234:5678:3:147/ffff:ffff:ff00:0:ffff:ffff::")
		require.NoError(t, err)
		assert.Equal(t, "12345678@2a02:6b8:c00::/40", net.StringMaybeProjectID())
	}

	{
		net, err := ParseIPNet("2a02:6b8:c00:0:1234:5678:3:147/ffff:ffff:ff00:0:ffff:fff8::")
		require.NoError(t, err)
		assert.Equal(t, "12345678/29@2a02:6b8:c00::/40", net.StringMaybeProjectID())
	}

	{
		net, err := ParseIPNet("2a02:6b8:c00:0:1234:5678:3:147/ffff:ffff:ff00:0:ffff:fff0::")
		require.NoError(t, err)
		assert.Equal(t, "12345670/28@2a02:6b8:c00::/40", net.StringMaybeProjectID())
	}

	{
		net, err := ParseIPNet("5670/28@2a02:6b8:c00::/40")
		require.NoError(t, err)
		assert.Equal(t, "5670/28@2a02:6b8:c00::/40", net.StringMaybeProjectID())
	}

	{
		// Fastbone.
		net, err := ParseIPNet("1234@2a02:6b8:fc00::/40")
		require.NoError(t, err)
		assert.Equal(t, "1234@2a02:6b8:fc00::/40", net.StringMaybeProjectID())
	}
}

func Benchmark_ParseIPv4(b *testing.B) {
	buf := "93.158.134.158"
	for i := 0; i < b.N; i++ {
		_, _ = ParseIPNetExt(buf)
	}

	b.SetBytes(int64(len(buf)))
	b.ReportAllocs()
}

func Benchmark_ParseIPv6(b *testing.B) {
	buf := "2a02:6b8:0:3400::3:147"
	for i := 0; i < b.N; i++ {
		_, _ = ParseIPNetExt(buf)
	}

	b.SetBytes(int64(len(buf)))
	b.ReportAllocs()
}

func Benchmark_ParseIPv6WithProjectID(b *testing.B) {
	buf := "41b9@2a02:6b8:c00::/40"
	for i := 0; i < b.N; i++ {
		_, _ = ParseIPNetExt(buf)
	}

	b.SetBytes(int64(len(buf)))
	b.ReportAllocs()
}
