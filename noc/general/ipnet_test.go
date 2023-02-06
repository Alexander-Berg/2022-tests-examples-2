package netutil

import (
	"fmt"
	"net"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseIPNet(t *testing.T) {
	tests := []struct {
		input  string
		result string
	}{
		{
			input:  "10.0.0.0/8",
			result: "10.0.0.0/8",
		},
		{
			input:  "10.0.0.0/08",
			result: "10.0.0.0/8",
		},
		{
			input:  "5.45.192.0/18",
			result: "5.45.192.0/18",
		},
		{
			input:  "2620:10f:d000::/44",
			result: "2620:10f:d000::/44",
		},
		{
			input:  "::ffff:0:0/96",
			result: "0.0.0.0/0",
		},
		{
			input:  "2a02:6b8:c06::40dd:777d:8da/128",
			result: "2a02:6b8:c06::40dd:777d:8da/128",
		},
		{
			input:  "40dd@2a02:6b8:c00::/40",
			result: "40dd@2a02:6b8:c00::/40",
		},
		{
			input:  "f800/21@2a02:6b8:c00::/40",
			result: "f800/21@2a02:6b8:c00::/40",
		},
		{
			input:  "f801/21@2a02:6b8:c00::/40",
			result: "f800/21@2a02:6b8:c00::/40",
		},
		{
			input:  "0644@2a02:6b8:c00::/40",
			result: "644@2a02:6b8:c00::/40",
		},
		{
			input:  "ffffffff@2a02:6b8:c00::/40",
			result: "ffffffff@2a02:6b8:c00::/40",
		},
		{
			input:  "0@2a02:6b8:c00::/40",
			result: "0@2a02:6b8:c00::/40",
		},
		{
			input:  "::ffff:7f00:1/ffff:ffff:ffff:ffff:ffff:ffff:ff00:0",
			result: "127.0.0.0/8",
		},
		{
			input:  "::ffff:0:0/ffff:ffff:ffff:ffff:ffff:ffff:0:0",
			result: "0.0.0.0/0",
		},
		{
			input:  "::ffff:0.0.0.0/ffff:ffff:ffff:ffff:ffff:fffe:0:0",
			result: "::fffe:0:0/95",
		},
		{
			input:  "::ffff:0:0/::ffff:0:0",
			result: "::ffff:0:0/::ffff:0:0",
		},
		{
			input:  "::ffff:0:0/::ffff:ffff:0:0",
			result: "ffff@::/0",
		},
		{
			input:  "127.0.0.1/255.0.0.255",
			result: "127.0.0.1/255.0.0.255",
		},
		{
			input:  "::ffff:127.0.0.1/ffff:ffff:ffff:ffff:ffff:ffff:255.0.0.255",
			result: "127.0.0.1/255.0.0.255",
		},
		{
			input:  "a800::/f800::",
			result: "a800::/5",
		},
		{
			input:  "a800::/f900::",
			result: "a800::/f900::",
		},
		{
			input:  "2a02:6b8:c00::40dd:0:0/ffff:ffff:ff00:0:ffff:ffff::",
			result: "40dd@2a02:6b8:c00::/40",
		},
		{
			input:  "2a02:6b8:c00::40dd:0:0/ffff:ffff:ff00:1:ffff:ffff::",
			result: "2a02:6b8:c00::40dd:0:0/ffff:ffff:ff00:1:ffff:ffff::",
		},
		{
			input:  "2a02:6b8:c00::40dd:0:0/96",
			result: "2a02:6b8:c00::40dd:0:0/96",
		},
		{
			input:  "foo",
			result: "",
		},
		{
			input:  "10.0.0.0/",
			result: "",
		},
		{
			input:  "256.256.256.256/24",
			result: "",
		},
		{
			input:  "10.0.0.0/33",
			result: "",
		},
		{
			input:  "40dd@127.0.0.1/8",
			result: "",
		},
		{
			input:  "40dd@2a02:6b8:c00::/96",
			result: "",
		},
		{
			input:  "40dd@yandex.ru",
			result: "",
		},
		{
			input:  "foo@2a02:6b8:c00::/96",
			result: "",
		},
		{
			input:  "100000000@2a02:6b8:c00::/40",
			result: "",
		},
		{
			input:  "-1@2a02:6b8:c00::/40",
			result: "",
		},
		{
			input:  "0x40dd@2a02:6b8:c00::/40",
			result: "",
		},
		{
			input:  "02a02::/fffff::",
			result: "",
		},
	}
	for _, test := range tests {
		ipnet, err := ParseIPNet(test.input)
		if err != nil {
			if test.result != "" {
				t.Errorf("%s: got %s, want %s", test.input, err, test.result)
			}
			continue
		}
		if ipnet.String() != test.result {
			t.Errorf("%s: got %s, want %s", test.input, ipnet.String(), test.result)
		}
	}
}

func TestSingleAddressIPNet(t *testing.T) {
	parse := func(s string) IPNet {
		ipnet, err := ParseIPNet(s)
		if err != nil {
			t.Fatal(err)
		}
		return ipnet
	}

	a := SingleAddressIPNet(net.ParseIP("127.0.0.1").To4())
	b := parse("127.0.0.1/32")
	assert.Equal(t, a, b)
}

func TestContains(t *testing.T) {
	parse := func(s string) *net.IPNet {
		ipnet, err := ParseIPNet(s)
		if err != nil {
			t.Fatal(err)
		}
		return ipnet.IPNet
	}

	cases := []struct {
		net, subnet string
		result      bool
	}{
		{"127.0.0.1/8", "127.1.0.0/16", true},
		{"127.1.0.0/16", "127.0.0.0/8", false},
		{"127.0.0.0/8", "127.0.0.0/8", true},
		{"40dd@2a02:6b8:c00::/40", "2a02:6b8:c06::40dd:777d:8da/128", true},
		{"40dd@2a02:6b8:c00::/40", "2a02:6b8:c06::40ff:777d:8da/128", false},
		{"40dd@2a02:6b8:c00::/40", "2a02:6b8:f06::40dd:777d:8da/128", false},
		{"40dd@2a02:6b8:c00::/40", "2a02:6b8:c06::40dd:0:0/96", true},
		{"40dd@2a02:6b8:c00::/40", "2a02:6b8:c00::/40", false},
		{"40dd@2a02:6b8:c00::/40", "40dd@2a02:6b8:c00::/40", true},
		{"40dd@2a02:6b8:c00::/40", "40dd@2a02:6b8:c00::/56", true},
		{"40dd@2a02:6b8:c00::/40", "40dd@2a02:6b8:c00::/39", false},
		{"40dd@2a02:6b8:c00::/40", "40de@2a02:6b8:c00::/40", false},
		{"2a02:6b8::/32", "40dd@2a02:6b8:c00::/40", true},
		{"2a02:6b8::/32", "2a02:6b8::/32", true},
		{"2a02:6b8::/32", "2a02:6bf::/32", false},
		{"2a02:6b8::/40", "2a02:6b8::/32", false},
		{"::ffff:0:0/96", "127.0.0.1/32", true},
		{"::fffe:0:0/95", "127.0.0.1/32", false},
		{"::abcd:0:0/::ffff:0:0", "ffff::abcd:1:2/128", true},
		{"::abcd:0:0/::ffff:0:0", "ffff::abce:1:2/128", false},
		{"::ffff:127.0.0.0/104", "127.0.0.0/8", true},
		{"::ffff:127.0.0.0/::ffff:255.0.0.0", "127.0.0.0/8", false},
	}
	for _, c := range cases {
		if Contains(parse(c.net), parse(c.subnet)) != c.result {
			t.Errorf("%s contains %s: got %t, want %t", c.net, c.subnet, !c.result, c.result)
		}
	}
}

func TestContainsUnmasked(t *testing.T) {
	parse := func(s string) *net.IPNet {
		ipnet, err := ParseIPNet(s)
		if err != nil {
			t.Fatal(err)
		}
		return ipnet.IPNet
	}

	cases := []struct {
		net, subnet *net.IPNet
		result      bool
	}{
		{
			net: &net.IPNet{
				IP:   parse("95.108.159.248/32").IP,
				Mask: net.CIDRMask(21, 32),
			},
			subnet: &net.IPNet{
				IP:   parse("95.108.156.96/32").IP,
				Mask: net.CIDRMask(27, 32),
			},
			result: true,
		},
	}
	for _, c := range cases {
		if Contains(c.net, c.subnet) != c.result {
			t.Errorf("%s contains %s: got %t, want %t", c.net, c.subnet, !c.result, c.result)
		}
	}
}

func TestZeroBits(t *testing.T) {
	tests := []struct {
		input  string
		result int
	}{
		{
			input:  "10.0.0.0/8",
			result: 32 - 8,
		},
		{
			input:  "5.45.192.0/18",
			result: 32 - 18,
		},
		{
			input:  "2620:10f:d000::/44",
			result: 128 - 44,
		},
		{
			input:  "::ffff:0:0/96",
			result: 32,
		},
		{
			input:  "2a02:6b8:c06::40dd:777d:8da/128",
			result: 0,
		},
		{
			input:  "40dd@2a02:6b8:c00::/40",
			result: 128 - 40 - 32,
		},
		{
			input:  "::ffff:127.0.0.0/104",
			result: 24,
		},
		{
			input:  "127.0.0.1/255.0.0.255",
			result: 16,
		},
		{
			input:  "::/5a::",
			result: 128 - 4,
		},
	}
	for _, test := range tests {
		result := ZeroBits(parseIPNet(test.input))
		if result != test.result {
			t.Errorf("%s: got %d, want %d", test.input, result, test.result)
		}
	}
}

func TestIsIPContainProjectID(t *testing.T) {
	tests := []struct {
		macro  string
		id     string
		ip     IPNet
		result bool
	}{
		{
			macro:  "_GENCFG_MSK_MYT_PUNCHER_DEV_",
			id:     "10d5678",
			ip:     parseIPNet("2a02:6b8:c00:98e:10d:5678:0:4d72/128"),
			result: true,
		},
		{
			macro:  "_GENCFG_MSK_MYT_PUNCHER_DEV_",
			id:     "10d5678",
			ip:     parseIPNet("2a02:6b8:b000:a001:92e2:baff:fea1:65a4/128"),
			result: false,
		},
		{
			macro:  "_GENCFG_VLA_PUNCHER_DEV_",
			id:     "10d5677",
			ip:     parseIPNet("2a02:6b8:c0f:693:10d:5677::5152/128"),
			result: true,
		},
	}
	for i, test := range tests {
		result, err := IsIPFromProjectID(test.ip.IP, test.id)
		if err != nil {
			t.Errorf("got error while test: %d", i)
		}
		if result != test.result {
			t.Errorf("test %d faild", i)
		}
	}
}

func TestGetProjectIDFromIP(t *testing.T) {
	tests := []struct {
		ip       IPNet
		expected string
		err      error
	}{
		{
			ip:       parseIPNet("2a02:6b8:c00:98e:10d:5678:0:4d72/128"),
			expected: "10d5678",
		},
		{
			ip:       parseIPNet("2a02:6b8:c0f:693:10d:5677::5152/128"),
			expected: "10d5677",
		},
		{
			ip:  parseIPNet("127.0.0.1/32"),
			err: fmt.Errorf("127.0.0.1 is not ipv6"),
		},
		{
			ip:  parseIPNet("2a02:6b8:b010:6:1::1/128"),
			err: fmt.Errorf("2a02:6b8:b010:6:1::1 is not project id ip"),
		},
	}

	for _, test := range tests {
		actual, err := GetProjectIDFromIP(test.ip.IP)
		assert.Equal(t, test.expected, actual)
		assert.Equal(t, test.err, err)
	}
}
