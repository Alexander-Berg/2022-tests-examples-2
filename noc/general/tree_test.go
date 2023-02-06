package netutil

import (
	"math/rand"
	"net"
	"reflect"
	"sort"
	"testing"
)

func parseIPNet(s string) IPNet {
	ipnet, err := ParseIPNet(s)
	if err != nil {
		panic(err)
	}
	return ipnet
}

func TestGetIPNibble(t *testing.T) {
	buf := []byte("\x12\x34\x56\x78")
	tests := []struct {
		idx    int
		result byte
	}{
		{24, 0x1},
		{31, 0x8},
	}
	for _, test := range tests {
		r := getIPNibble(buf, test.idx)
		if r != test.result {
			t.Errorf("get nibble(%d) = %d, want %d", test.idx, r, test.result)
		}
	}

	buf4 := net.IP(buf).To4()
	buf6 := net.IP(buf).To16()
	for i := 0; i < 32; i++ {
		a := getIPNibble(buf4, i)
		b := getIPNibble(buf6, i)
		if a != b {
			t.Errorf("%d: %x != %x", i, a, b)
		}
	}
}

func TestGetMaskNibble(t *testing.T) {
	buf := []byte("\x12\x34\x56\x78")
	tests := []struct {
		idx    int
		result byte
	}{
		{24, 0x1},
		{31, 0x8},
	}
	for _, test := range tests {
		r := getMaskNibble(buf, test.idx)
		if r != test.result {
			t.Errorf("get nibble(%d) = %d, want %d", test.idx, r, test.result)
		}
	}

	parse := func(s string) *net.IPNet {
		_, ipnet, err := net.ParseCIDR(s)
		if err != nil {
			t.Fatal(err)
		}
		return ipnet
	}
	mask4 := parse("127.0.0.0/15").Mask
	mask6 := parse("::ffff:127.0.0.0/111").Mask
	if len(mask4) != net.IPv4len || len(mask6) != net.IPv6len {
		t.Fatal("bad masks:", mask4, mask6)
	}
	for i := 0; i < 32; i++ {
		a := getMaskNibble(mask4, i)
		b := getMaskNibble(mask6, i)
		if a != b {
			t.Errorf("%d: %x != %x", i, a, b)
		}
	}
}

func TestGetMaskSize(t *testing.T) {
	tests := []struct {
		buf    []byte
		result int
	}{
		{[]byte("\x00\x00\x00\x00"), 0},
		{[]byte("\x80\x00\x00\x00"), 2*12 + 1},
		{[]byte("\xff\xff\x00\x00"), 2*12 + 4},
		{[]byte("\xff\xff\x0f\x00"), 2*12 + 6},
		{[]byte("\xff\xff\xf0\x00"), 2*12 + 5},
		{[]byte("\x00\xff\xf8\x00"), 2*12 + 6},
		{[]byte("\xff\xff\x80\x00"), 2*12 + 5},
		{[]byte("\xff\xff\x80\x00"), 2*12 + 5},
		{[]byte("\xffUUUUUUUUUUUUU\x50\x00"), 29},
	}
	for _, test := range tests {
		r := getMaskSize(test.buf)
		if r != test.result {
			t.Errorf("mask size(% 02x) = %d, want %d", test.buf, r, test.result)
		}
	}
}

func TestTreeFind(t *testing.T) {
	var tree Tree
	tree.Insert(parseIPNet("127.0.1.0/255.0.255.0"), "a")
	tree.Insert(parseIPNet("4150::/5555::"), "b")
	tree.Insert(parseIPNet("abcd@::/0"), "c")
	tree.Insert(parseIPNet("f::abcd:0:0/128"), "d")
	tree.Insert(parseIPNet("f::/16"), "e")
	tree.Insert(parseIPNet("f:8000::/17"), "f")
	tree.Insert(parseIPNet("95.108.128.0/17"), "g")
	tree.Insert(parseIPNet("5.45.192.0/18"), "h")
	tree.Insert(parseIPNet("40dd@2a02:6b8:c00::/40"), "i")
	tree.Insert(parseIPNet("40dd@2a02:6b8:c00::/64"), "j")
	tree.Insert(parseIPNet("40dd@2a02:6b8:c00::/48"), "k")
	tree.Insert(parseIPNet("10bad43@2a02:6b8:c00::/40"), "GENCFG_MARKET_PROD") // GENCFG_IVA_MARKET_PREP_MARKET_GENERAL_MARKET
	tree.Insert(parseIPNet("10cdb29@2a02:6b8:c00::/40"), "GENCFG_MARKET_PROD") // GENCFG_IVA_MARKET_PREP_PARTNER_API
	tree.Insert(parseIPNet("10d1045@2a02:6b8:c00::/40"), "GENCFG_MARKET_PROD") // GENCFG_IVA_MARKET_PREP_PRICELABS_TMS
	tree.Insert(parseIPNet("10bc16d@2a02:6b8:c00::/40"), "GENCFG_MARKET_PROD") // GENCFG_MARKET_PROD
	tree.Insert(parseIPNet("10d1045@2a02:6b8:c00::/40"), "GENCFG_IVA_MARKET_PREP_PRICELABS_TMS")
	tree.Insert(parseIPNet("10cdb29@2a02:6b8:c00::/40"), "GENCFG_IVA_MARKET_PREP_PARTNER_API")
	tree.Insert(parseIPNet("10bad43@2a02:6b8:c00::/40"), "GENCFG_IVA_MARKET_PREP_MARKET_GENERAL_MARKET")

	tests := []struct {
		query  []string
		result []string
	}{
		{
			query:  []string{"127.0.1.0/24"},
			result: []string{"a"},
		},
		{
			query:  []string{"127.0.0.0/8"},
			result: nil,
		},
		{
			query:  []string{"4150::/5555::"},
			result: []string{"b"},
		},
		{
			query:  []string{"c9d8::/ffff::"},
			result: []string{"b"},
		},
		{
			query:  []string{"20ab:2:3:4:0:abcd:5:6/128"},
			result: []string{"c"},
		},
		{
			query:  []string{"f::abcd:0:0/128"},
			result: []string{"c", "d", "e"},
		},
		{
			query:  []string{"f:8000::/18"},
			result: []string{"e", "f"},
		},
		{
			query:  []string{"95.108.156.96/27"},
			result: []string{"g"},
		},
		{
			query:  []string{"2a02:6b8:c06::40dd:777d:8da/128"},
			result: []string{"i"},
		},
		{
			query:  []string{"2a02:6b8:c00::40dd:777d:8da/128"},
			result: []string{"i", "j", "k"},
		},
		{
			query:  []string{"10bad43@2a02:6b8:c00::/40"},
			result: []string{"GENCFG_IVA_MARKET_PREP_MARKET_GENERAL_MARKET", "GENCFG_MARKET_PROD"},
		},
		{
			query:  []string{"10cdb29@2a02:6b8:c00::/40"},
			result: []string{"GENCFG_IVA_MARKET_PREP_PARTNER_API", "GENCFG_MARKET_PROD"},
		},
		{
			query:  []string{"10d1045@2a02:6b8:c00::/40"},
			result: []string{"GENCFG_IVA_MARKET_PREP_PRICELABS_TMS", "GENCFG_MARKET_PROD"},
		},
		{
			query:  []string{"10d1045@2a02:6b8:c00::/40", "10cdb29@2a02:6b8:c00::/40", "10bad43@2a02:6b8:c00::/40"},
			result: []string{"GENCFG_MARKET_PROD"},
		},
		{
			query:  []string{"10d1045@2a02:6b8:c00::/40", "10cdb29@2a02:6b8:c00::/40", "10bc16d@2a02:6b8:c00::/40"},
			result: []string{"GENCFG_MARKET_PROD"},
		},
		{
			query:  []string{"10d1045@2a02:6b8:c00::/60", "2a02:6b8:c00::40dd:777d:8da/128"},
			result: nil,
		},
	}

	for _, test := range tests {
		nets := make([]IPNet, 0)
		for _, q := range test.query {
			nets = append(nets, parseIPNet(q))
		}
		v := tree.Find(nets...)
		sort.Strings(v)
		if !reflect.DeepEqual(v, test.result) {
			t.Errorf("query(%s) = %v, want %v", test.query, v, test.result)
		}
	}
}

func TestTreeInsertDup(t *testing.T) {
	var tree Tree
	tests := []struct {
		name   string
		net    IPNet
		result bool
	}{
		{"_LOOPBACK_", parseIPNet("127.0.0.1/32"), true},
		{"_LOCALHOST_", parseIPNet("127.0.0.1/32"), true},
		{"_LOOPBACK_", parseIPNet("::1/128"), true},
		{"_10_NET_", parseIPNet("10.0.0.0/8"), true},
		{"_LOOPBACK_", parseIPNet("127.0.0.1/32"), false},
		{"_10_NET_", parseIPNet("10.0.2.0/24"), true},
		{"_LOOPBACK_", parseIPNet("::1/128"), false},
	}
	for _, test := range tests {
		result := tree.Insert(test.net, test.name)
		if result != test.result {
			t.Errorf("insert (%s, %v): got %t, want %t", test.name, test.net, result, test.result)
		}
	}
}

func generateSubnets(rnd *rand.Rand, ip net.IP, bits int, out func(IPNet)) {
	var p float64
	switch {
	case bits >= 30:
		p = 1
	case bits >= 29:
		p = 0.95
	case bits >= 28:
		p = 0.6
	case bits >= 23:
		p = 0.3
	case bits >= 19:
		p = 0.2
	}
	if rnd.Float64() < p {
		outip := make(net.IP, len(ip))
		copy(outip, ip)
		out(IPNet{&net.IPNet{
			IP:   outip,
			Mask: net.CIDRMask(bits, 8*len(outip)),
		}})
		return
	}
	if bits == 8*(len(ip)) {
		panic("it have to stop on /30 or /64 subnet, but something went wrong")
	}

	generateSubnets(rnd, ip, bits+1, out)

	ip[bits/8] |= (0x80 >> (uint(bits) % 8))
	generateSubnets(rnd, ip, bits+1, out)
}

func generateTree() Tree {
	rnd := rand.New(rand.NewSource(1))
	NetA17 := net.ParseIP("95.108.128.0").To4()
	NetB18 := net.ParseIP("5.45.192.0").To4()
	var tree Tree
	generateSubnets(rnd, NetA17, 17, func(ipnet IPNet) {
		tree.Insert(ipnet, ipnet.String())
	})
	generateSubnets(rnd, NetB18, 18, func(ipnet IPNet) {
		tree.Insert(ipnet, ipnet.String())
	})
	return tree
}

func BenchmarkBigTree(b *testing.B) {
	tree := generateTree()
	b.ResetTimer()

	ipnet := parseIPNet("95.108.156.96/27")
	for i := 0; i < b.N; i++ {
		output := tree.Find(ipnet)
		if len(output) != 1 {
			b.Fatal(output)
		}
	}
}

func BenchmarkSmallTree(b *testing.B) {
	var tree Tree
	tree.Insert(parseIPNet("95.108.159.248/21"), "a")

	ipnet := parseIPNet("95.108.156.96/27")
	for i := 0; i < b.N; i++ {
		output := tree.Find(ipnet)
		if len(output) != 1 {
			b.Fatal(output)
		}
	}
}

func BenchmarkBadTree(b *testing.B) {
	var tree Tree
	nets := []string{
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/128",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/f000::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/ff00::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/fff0::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/ffff::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/ffff:f000::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/ffff:ff00::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/ffff:fff0::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/ffff:ffff::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/0f00::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/f0::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/f::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/0:f000::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/0:0f00::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/0:f0::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/0:f::1",
		"1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/::1",
	}
	for _, ipnet := range nets {
		tree.Insert(parseIPNet(ipnet), ipnet)
	}

	ipnet := parseIPNet("1111:2222:3333:4444:aaaa:bbbb:cccc:dddd/128")
	for i := 0; i < b.N; i++ {
		output := tree.Find(ipnet)
		if len(output) != len(nets) {
			b.Fatal(output)
		}
	}
}
