package syslogparsing

import (
	"net"
	"testing"
	"time"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/osquery/osquery-sender/config"
	"a.yandex-team.ru/security/osquery/osquery-sender/parser"
	"a.yandex-team.ru/security/osquery/osquery-sender/syslogparsing/parsers"
)

func TestServerUdpConfig(t *testing.T) {
	testServerConfig(t, false, "localhost:1234", sendMessageUDP)
}

func TestServerTcpConfig(t *testing.T) {
	testServerConfig(t, true, "localhost:1235", sendMessageTCP)
}

func testServerConfig(t *testing.T, useTCP bool, address string, sendMessage func(string, string)) {
	// The format we use (Cumulus) is not important, we could have chosen any other.
	var logParser = "Cumulus"
	var logLine1 = "2021-01-19T14:32:57.349974+02:00 netlab-myt-1ct253 zebra[5313]: old speed: 0 new speed: 4294967295"
	var logLine2 = "2021-01-27T15:55:17.479480+02:00 netlab-myt-1 watchfrr[20984]: bgpd state -> up : connect succeeded"

	conf := &config.SyslogServerConfig{
		Name:    "TestServer",
		Address: address,
		Parser:  logParser,
		UseTCP:  useTCP,
	}

	channel := make(EventChannel, 2)
	handler := &EventChannelHandler{channel: channel}

	server, _ := StartSysLogServer(conf, handler)

	time.Sleep(1000 * time.Millisecond) // I saw 100ms in the go-syslog.v2 tests, but our CI machines might need more
	sendMessage(logLine1, conf.Address)
	sendMessage(logLine2, conf.Address)
	time.Sleep(100 * time.Millisecond)
	_ = server.Kill()

	expectedEvent1 := &parser.ParsedEvent{
		Host:    "127.0.0.1",
		LogType: DefaultLogType,
		Name:    "TestServer",
		Data: map[string]interface{}{
			"action": DefaultAction,
			"name":   "TestServer",
			parsers.ColumnsDataKey: map[string]interface{}{
				"process":  "zebra",
				"proc_id":  "5313",
				"time":     parseLogTime("2021-01-19T14:32:57.349974+02:00"),
				"hostname": "netlab-myt-1ct253",
				"message":  "old speed: 0 new speed: 4294967295",
			},
		},
	}

	expectedEvent2 := &parser.ParsedEvent{
		Host:    "127.0.0.1",
		LogType: DefaultLogType,
		Name:    "TestServer",
		Data: map[string]interface{}{
			"action": DefaultAction,
			"name":   "TestServer",
			parsers.ColumnsDataKey: map[string]interface{}{
				"process":  "watchfrr",
				"proc_id":  "20984",
				"time":     parseLogTime("2021-01-27T15:55:17.479480+02:00"),
				"hostname": "netlab-myt-1",
				"message":  "bgpd state -> up : connect succeeded",
			},
		},
	}

	event1 := <-channel
	event2 := <-channel

	require.Equal(t, expectedEvent1, event1)
	require.Equal(t, expectedEvent2, event2)

	select {
	case <-channel:
		require.FailNow(t, "Unexpected event")
	default:
		// ok
	}
}

func sendMessageUDP(logLine string, address string) {
	serverAddr, _ := net.ResolveUDPAddr("udp", address)
	con, _ := net.DialUDP("udp", nil, serverAddr)
	_, _ = con.Write([]byte(logLine))
	_ = con.Close()
}

func sendMessageTCP(logLine string, address string) {
	serverAddr, _ := net.ResolveTCPAddr("tcp", address)
	con, _ := net.DialTCP("tcp", nil, serverAddr)
	_, _ = con.Write([]byte(logLine))
	_ = con.Close()
}

// returns the time in the format expected for the parser.ParsedEvent
func parseLogTime(timeStr string) float64 {
	t, _ := time.Parse("2006-01-02T15:04:05.000000-07:00", timeStr)
	return float64(t.Unix())
}

type EventChannel chan *parser.ParsedEvent

type EventChannelHandler struct {
	channel EventChannel
}

func (h *EventChannelHandler) Handle(event *parser.ParsedEvent) {
	h.channel <- event
}
