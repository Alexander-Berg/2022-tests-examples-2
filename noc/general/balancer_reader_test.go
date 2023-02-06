package slbcloghandler

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

var balancerReaderDump, _ = ioutil.ReadFile("balancer_reader_dump.json")

func TestParseQuorumUp(t *testing.T) {
	count, ip, err := ParseQuorumUp("/etc/keepalived/quorum-handler2.sh up 2a02:6b8::193,b-100,2")
	assert.NoError(t, err)
	assert.Equal(t, count, 2)
	assert.Equal(t, ip, "2a02:6b8::193")
}

func TestParseQuorumUp2(t *testing.T) {
	count, ip, err := ParseQuorumUp("/etc/keepalived/quorum-handler2.sh up   93.158.157.159,443/TCP,b-100,5")
	assert.NoError(t, err)
	assert.Equal(t, count, 5)
	assert.Equal(t, ip, "93.158.157.159")
}

func TestParse(t *testing.T) {
	file, err := os.Open("balancer_reader_dump.json")
	if err != nil {
		t.Error(err)
	}
	content, err := ioutil.ReadAll(file)
	if err != nil {
		t.Error(err)
	}
	defer file.Close()
	result, err := Parse(content)
	assert.NoError(t, err)

	expected := BalancerStat{Server: Sta{TS: 1601768350, Conf: []Conf{{Vip: "2a02:6b8:0:3400::3:21", Protocol: "TCP", Af: "INET6", Fwmark: 0, Port: 443, QuorumState: 1, QuorumUp: "", Quorum: 0, QuorumIP: "", Transitions: 0x0, Rs: []Rs{{IP: "2a02:6b8:c1d:2c12:0:4f22:6895:0", Port: 443, Alive: 1, Transitions: 0x3, Key: ""}, {IP: "2a02:6b8:c0f:1f:0:4f22:8100:0", Port: 443, Alive: 1, Transitions: 0x3, Key: ""}}, Key: "", ServiceNames: []serviceName(nil)}, {Vip: "2a02:6b8:0:3400::3:21", Protocol: "TCP", Af: "INET6", Fwmark: 0, Port: 80, QuorumState: 1, QuorumUp: "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400::3:21,b-100,1", Quorum: 0, QuorumIP: "", Transitions: 0x0, Rs: []Rs{{IP: "2a02:6b8:c1d:2c12:0:4f22:6895:0", Port: 80, Alive: 1, Transitions: 0x3, Key: ""}, {IP: "2a02:6b8:c0f:1f:0:4f22:8100:0", Port: 80, Alive: 1, Transitions: 0x3, Key: ""}}, Key: "", ServiceNames: []serviceName(nil)}, {Vip: "2a02:6b8:0:3400:0:2ba:0:c", Protocol: "TCP", Af: "INET6", Fwmark: 0, Port: 443, QuorumState: 1, QuorumUp: "/etc/keepalived/quorum-handler2.sh up 2a02:6b8:0:3400:0:2ba:0:c,b-100,2", Quorum: 0, QuorumIP: "", Transitions: 0x0, Rs: []Rs{{IP: "2a02:6b8:c0d:2206:0:410e:ac7d:446d", Port: 443, Alive: 1, Transitions: 0x3, Key: ""}}, Key: "", ServiceNames: []serviceName(nil)}}}, Addrs: map[string][]string{"dummy100": {"2a02:6b8:0:3400:0:7bb:0:3/128", "2a02:6b8:0:3400:0:7bb:0:a/128", "fe80::4862:4bff:fe66:5f9/64"}, "dummy254": {"10.0.0.1/32", "fdef::1/128", "fe80::1c55:eeff:fe2e:adce/64"}, "eth2": {"fe80::ec4:7aff:fedb:2202/64"}, "lo": {"127.0.0.1/8", "::1/128"}}, Host: "vla1-4lb17b-25d", Status: "ok"}
	assert.Equal(t, result, expected)
	c := BalancerStat{}
	err = json.Unmarshal(content, &c)
	if err != nil {
		t.Error(err)
	}
	assert.Equal(t, result, expected)
}

func BenchmarkParseStandard(b *testing.B) {
	for n := 0; n < b.N; n++ {
		res := BalancerStat{}
		err := json.Unmarshal(balancerReaderDump, &res)
		if err != nil {
			b.Error(err)
		}
	}
}
func BenchmarkParseEasyJson(b *testing.B) {
	for n := 0; n < b.N; n++ {
		res := BalancerStat{}
		err := res.UnmarshalJSON(balancerReaderDump)
		if err != nil {
			b.Error(err)
		}
	}
}
