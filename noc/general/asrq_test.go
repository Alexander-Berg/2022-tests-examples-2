package asrq

import (
	"net"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/miekg/dns"
)

func AsrqServer(w dns.ResponseWriter, req *dns.Msg) {
	m := new(dns.Msg)
	m.SetReply(req)

	//m.Answer = make([]dns.RR, 1)

	// Filling Additional section

	m.Extra = make([]dns.RR, 1)
	switch req.Question[0].Qtype {
	case dns.TypeAAAA:
		var ASRQ ASRQ6
		ASRQ.AuthServerAddress = net.ParseIP("2a00:1450:4010:c0e::66")
		ASRQ.Quota = 101
		ASRQ.QuotaUsed = 80
		ASRQ.Throttling = 0

		m.Extra[0] = &dns.PrivateRR{
			Hdr:  dns.RR_Header{Name: m.Question[0].Name, Rrtype: TypeASRQ6, Class: dns.ClassINET, Ttl: 120},
			Data: &ASRQ,
		}
	case dns.TypeA:
		var ASRQ ASRQ4
		ASRQ.AuthServerAddress = net.ParseIP("74.125.131.101")
		ASRQ.Quota = 101
		ASRQ.QuotaUsed = 80
		ASRQ.Throttling = 0

		m.Extra[0] = &dns.PrivateRR{
			Hdr:  dns.RR_Header{Name: m.Question[0].Name, Rrtype: TypeASRQ4, Class: dns.ClassINET, Ttl: 120},
			Data: &ASRQ,
		}
	}

	w.WriteMsg(m)
}

// Based on miekg dns testing code
func RunLocalUDPServer(laddr string, opts ...func(*dns.Server)) (*dns.Server, string, chan error, error) {
	pc, err := net.ListenPacket("udp", laddr)
	if err != nil {
		return nil, "", nil, err
	}
	server := &dns.Server{PacketConn: pc, ReadTimeout: time.Hour, WriteTimeout: time.Hour}

	waitLock := sync.Mutex{}
	waitLock.Lock()
	server.NotifyStartedFunc = waitLock.Unlock

	for _, opt := range opts {
		opt(server)
	}

	// fin must be buffered so the goroutine below won't block
	// forever if fin is never read from. This always happens
	// if the channel is discarded and can happen in TestShutdownUDP.
	fin := make(chan error, 1)

	go func() {
		fin <- server.ActivateAndServe()
		pc.Close()
	}()

	waitLock.Lock()
	return server, pc.LocalAddr().String(), fin, nil
}

// Testing private RR generation and handling
func TestServePrivateAsrq(t *testing.T) {

	dns.HandleFunc("example.com.", AsrqServer)
	dns.PrivateHandle("ASRQ6", TypeASRQ6, NewASRQ6)
	dns.PrivateHandle("ASRQ4", TypeASRQ4, NewASRQ4)

	s, addrstr, _, err := RunLocalUDPServer(":0")
	if err != nil {
		t.Fatalf("unable to run test server: %v", err)
	}
	defer s.Shutdown()

	c := new(dns.Client)
	m := new(dns.Msg)

	// we expect that for AAAA question we will receive ASRQ6 response
	// for A corresponding ASRQ4

	types := []uint16{dns.TypeAAAA, dns.TypeA}

	for _, tt := range types {

		m.SetQuestion("example.com.", tt)
		r, _, err := c.Exchange(m, addrstr)

		t.Logf("\n%v\n", r)

		if err != nil {
			t.Fatal("failed to exchange example.com ", err)
		}
		if r.Rcode != dns.RcodeSuccess {
			t.Errorf("expected rcode %v, got %v", dns.RcodeSuccess, r.Rcode)
		}

		if len(r.Extra) != 1 {
			t.Fatalf("failed to get additional answers\n%v\n", r)
		}

		rr := r.Extra[0].(*dns.PrivateRR)
		if rr == nil {
			t.Errorf("invalid private RR response\n%v\n", rr)
		}

		// Parsing asrq to get structure
		var response string
		switch tt {
		case dns.TypeAAAA:
			data6 := rr.Data.(*ASRQ6)
			response = data6.String()
		case dns.TypeA:
			data4 := rr.Data.(*ASRQ4)
			response = data4.String()
		}

		t.Logf("\nresponsed and parsed as ASRQ:'%s'\n", response)
	}

}

var asrq4 = strings.Join([]string{"example.org.", "3600", "IN", "ASRQ4", "193.0.6.139", "333", "121", "0"}, "\t")
var asrq6 = strings.Join([]string{"example.org.", "3600", "IN", "ASRQ6", "2001:67c:2e8:22::c100:68b", "1312", "41", "0"}, "\t")

func TestPrivateAsqr4(t *testing.T) {
	dns.PrivateHandle("ASRQ4", TypeASRQ4, NewASRQ4)
	defer dns.PrivateHandleRemove(TypeASRQ4)

	rr, err := dns.NewRR(asrq4)
	if err != nil {
		t.Fatal(err)
	}
	if rr.String() != asrq4 {
		t.Errorf("record string representation did not match original %#v != %#v", rr.String(), asrq4)
	}
}

func TestPrivateAsqr6(t *testing.T) {

	ExamplePrivateHandleASRQ6()

	dns.PrivateHandle("ASRQ6", TypeASRQ6, NewASRQ6)
	defer dns.PrivateHandleRemove(TypeASRQ6)

	rr, err := dns.NewRR(asrq6)
	if err != nil {
		t.Fatal(err)
	}
	if rr.String() != asrq6 {
		t.Errorf("record string representation did not match original %#v != %#v", rr.String(), asrq6)
	}
}
