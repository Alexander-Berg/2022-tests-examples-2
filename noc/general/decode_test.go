package internal

import (
	"bytes"
	"fmt"
	"net"
	"testing"

	g "github.com/soniah/gosnmp"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/go/metrics"
	"a.yandex-team.ru/noc/snmptrapper/internal/snmp"
)

type TestResolver struct {
	cache map[string]string
}

func (m TestResolver) Lookup(ip string) (string, error) {
	res, ok := m.cache[ip]
	if ok {
		return res, nil
	}
	return "", fmt.Errorf("not resolved %v", ip)
}

func newTestResolver(cache map[string]string) *TestResolver {
	return &TestResolver{cache: cache}
}

func TestDecode(t *testing.T) {
	testOidMap := snmp.OidMap{
		"1.3.6.1.6.3.1.1.4.1.0": snmp.OIDParams{Name: "snmpTrapOID"},
		"1.3.6.1.2.1.1.3.0":     snmp.OIDParams{Name: "uptime"},
		"1.3.6.1.4.1.13238.2":   snmp.OIDParams{Name: "linuxCommitAPI"},
		"1.3.6.1.4.1.13238.2.1": snmp.OIDParams{Name: "yandexConfigUser"},
		"1.3.6.1.4.1.13238.2.2": snmp.OIDParams{Name: "yandexConfigCounter"},
	}
	packet := []byte{48, 100, 2, 1, 1, 4, 2, 84, 122, 167, 91, 2, 4, 117, 111, 168, 203, 2, 1, 0, 2, 1, 0, 48, 77, 48,
		16, 6, 8, 43, 6, 1, 2, 1, 1, 3, 0, 67, 4, 13, 157, 195, 85, 48, 22, 6, 10, 43, 6, 1, 6, 3, 1, 1, 4, 1, 0, 6, 8,
		43, 6, 1, 4, 1, 231, 54, 2, 48, 17, 6, 9, 43, 6, 1, 4, 1, 231, 54, 2, 1, 4, 4, 114, 111, 111, 116, 48, 14, 6,
		9, 43, 6, 1, 4, 1, 231, 54, 2, 2, 2, 1, 2}
	expected := []byte("snmpTrapOID=linuxCommitAPI uptime=228442965 yandexConfigCounter=2 yandexConfigUser=root")
	assertDecoded(t, testOidMap, packet, expected)
}

func assertDecoded(t *testing.T, testOidMap snmp.OidMap, packet []byte, expected []byte) {
	as := assert.New(t)
	logger := zap.Must(zap.StandardConfig("console", log.DebugLevel)) // TODO: use fake logger
	met, err := metrics.New(nil, logger.WithName("metrics"))
	as.NoError(err)
	resolver := newTestResolver(map[string]string{"127.0.0.1": "localhost"})
	app := NewSNMPTrapDecoder(testOidMap, resolver, met.Registry(""), logger)

	ip, err := net.ResolveTCPAddr("tcp", "127.0.0.1:12345")
	as.NoError(err)
	tp := NewTrapPacket(packet, ip)
	fmtRes, err := app.Decode(tp)
	as.NoError(err)
	res, err := fmtRes.Format(SyslogText)
	as.NoError(err)
	res = bytes.Split(res, []byte("snmptrapper: "))[1]
	as.Equal(string(expected), string(res))
}

func TestDecodeMACAddress(t *testing.T) {
	testOidMap := snmp.OidMap{
		"1.3.6.1.6.3.1.1.4.1.0":              snmp.OIDParams{Name: "snmpTrapOID"},
		"1.3.6.1.2.1.1.3.0":                  snmp.OIDParams{Name: "uptime"},
		"1.3.6.1.2.1.2.2.1.2":                snmp.OIDParams{Name: "ifDescr"},
		"1.3.6.1.4.1.2011.5.25.315.2.2":      snmp.OIDParams{Name: "hwMacTrapMacInfo"},
		"1.3.6.1.4.1.2011.5.25.42.2.1.2.1.2": snmp.OIDParams{Name: "hwCfgFdbVlanId"},
		"1.3.6.1.4.1.2011.5.25.42.2.1.2.1.1": snmp.OIDParams{Name: "hwCfgFdbMac", Syntax: "MacAddress"},
		"1.3.6.1.4.1.2011.5.25.315.3.5":      snmp.OIDParams{Name: "hwMacTrapPortCfgAlarm"},
	}
	packet := []byte{
		0x30, 0x81, 0xd0, 0x02, 0x01, 0x01, 0x04, 0x05, 0x54, 0x7a, 0x56, 0x5a, 0x38, 0xa7, 0x81, 0xc3,
		0x02, 0x03, 0x12, 0x4e, 0xf3, 0x02, 0x01, 0x00, 0x02, 0x01, 0x00, 0x30, 0x81, 0xb5, 0x30, 0x10,
		0x06, 0x08, 0x2b, 0x06, 0x01, 0x02, 0x01, 0x01, 0x03, 0x00, 0x43, 0x04, 0x08, 0x6b, 0x52, 0x2c,
		0x30, 0x1b, 0x06, 0x0a, 0x2b, 0x06, 0x01, 0x06, 0x03, 0x01, 0x01, 0x04, 0x01, 0x00, 0x06, 0x0d,
		0x2b, 0x06, 0x01, 0x04, 0x01, 0x8f, 0x5b, 0x05, 0x19, 0x82, 0x3b, 0x03, 0x05, 0x30, 0x1e, 0x06,
		0x0e, 0x2b, 0x06, 0x01, 0x04, 0x01, 0x8f, 0x5b, 0x05, 0x19, 0x82, 0x3b, 0x02, 0x02, 0x00, 0x04,
		0x0c, 0x4d, 0x41, 0x43, 0x20, 0x6c, 0x65, 0x61, 0x72, 0x6e, 0x69, 0x6e, 0x67, 0x30, 0x26, 0x06,
		0x1c, 0x2b, 0x06, 0x01, 0x04, 0x01, 0x8f, 0x5b, 0x05, 0x19, 0x2a, 0x02, 0x01, 0x02, 0x01, 0x01,
		0x02, 0x81, 0x5d, 0x81, 0x5d, 0x5f, 0x81, 0x78, 0x36, 0x82, 0x4d, 0x01, 0x2d, 0x04, 0x06, 0x02,
		0xdd, 0xdd, 0x5f, 0xf8, 0x36, 0x30, 0x22, 0x06, 0x1c, 0x2b, 0x06, 0x01, 0x04, 0x01, 0x8f, 0x5b,
		0x05, 0x19, 0x2a, 0x02, 0x01, 0x02, 0x01, 0x02, 0x02, 0x81, 0x5d, 0x81, 0x5d, 0x5f, 0x81, 0x78,
		0x36, 0x82, 0x4d, 0x01, 0x2d, 0x42, 0x02, 0x01, 0x4d, 0x30, 0x18, 0x06, 0x0a, 0x2b, 0x06, 0x01,
		0x02, 0x01, 0x02, 0x02, 0x01, 0x02, 0x1d, 0x04, 0x0a, 0x32, 0x35, 0x47, 0x45, 0x31, 0x2f, 0x30,
		0x2f, 0x31, 0x37,
	}
	expected := []byte("snmpTrapOID=hwMacTrapPortCfgAlarm uptime=141251116 hwCfgFdbMac.2.221.221.95.248.54.333.1.45=02:dd:dd:5f:f8:36 hwCfgFdbVlanId.2.221.221.95.248.54.333.1.45=333 hwMacTrapMacInfo.0=MAC learning ifDescr.29=25GE1/0/17")
	assertDecoded(t, testOidMap, packet, expected)
}

func encodeTrap(oidVal string, pdus []g.SnmpPDU) ([]byte, error) {
	g.Default.Target = "127.0.0.1"
	g.Default.Port = 162
	g.Default.Version = g.Version2c
	g.Default.Community = "public"
	logger := zap.Must(zap.StandardConfig("console", log.DebugLevel))
	g.Default.Logger = snmp.NewLogger(logger)
	err := g.Default.Connect()
	if err != nil {
		return nil, err
	}
	defer g.Default.Conn.Close()

	tpdu := g.SnmpPDU{
		Name:  snmp.SnmpTrapUptime,
		Type:  g.TimeTicks,
		Value: uint32(0),
	}

	pdu := g.SnmpPDU{
		Name:  snmp.SnmpTrapOID,
		Type:  g.ObjectIdentifier,
		Value: oidVal,
	}
	vars := []g.SnmpPDU{tpdu, pdu}
	vars = append(vars, pdus...)
	trap := g.SnmpTrap{Variables: vars}
	f := g.SnmpPacket{
		Version:        g.Version2c,
		Community:      "public",
		Error:          0,
		ErrorIndex:     0,
		PDUType:        g.SNMPv2Trap,
		NonRepeaters:   0,
		MaxRepetitions: 0,
		Variables:      trap.Variables,
	}
	r, err := f.MarshalMsg()
	return r, err
}

func TestSyntaxBit(t *testing.T) {
	as := assert.New(t)
	pdu := g.SnmpPDU{
		Name:  ".1.3.6.1.2.1.131.1.1.1.5", //entStateAlarm
		Type:  g.OctetString,
		Value: []byte{2},
	}

	testOidMap := snmp.OidMap{
		"1.3.6.1.6.3.1.1.4.1.0":      snmp.OIDParams{Name: "snmpTrapOID"},
		"1.3.6.1.2.1.1.3.0":          snmp.OIDParams{Name: "uptime"},
		"1.3.6.1.4.1.30065.3.12.0.1": snmp.OIDParams{Name: "aristaEntSensorAlarm"},
		"1.3.6.1.2.1.131.1.1.1.5": snmp.OIDParams{
			Name:   "entStateAlarm",
			Syntax: "BITS {unknown(0), underRepair(1), critical(2), major(3), minor(4), warning(5), indeterminate(6)}"},
	}

	pkt, err := encodeTrap("1.3.6.1.4.1.30065.3.12.0.1", []g.SnmpPDU{pdu})
	as.NoError(err)
	expected := []byte("snmpTrapOID=aristaEntSensorAlarm uptime=0 entStateAlarm=underRepair")
	assertDecoded(t, testOidMap, pkt, expected)
}

func TestSyntaxDateAndTime(t *testing.T) {
	as := assert.New(t)
	trapOID := "1.3.6.1.4.1.2636.4.5.0.1"
	testOID := "1.3.6.1.4.1.2636.3.18.1.7.1.3"
	pdu := g.SnmpPDU{
		Name:  testOID,
		Type:  g.OctetString,
		Value: []byte{0x07, 0xD2, 0x09, 0x03, 0x0C, 0x14, 0x20, 0x03, 0x2B, 0x07, 0x00},
	}

	testOidMap := snmp.MakeBaseOIDMap(trapOID, "jnxCmCfgChange")
	testOidMap[testOID] = snmp.OIDParams{
		Name:   "jnxCmCfgChgEventDate",
		Syntax: "DateAndTime",
	}

	pkt, err := encodeTrap(trapOID, []g.SnmpPDU{pdu})
	as.NoError(err)
	expected := []byte("snmpTrapOID=jnxCmCfgChange uptime=0 jnxCmCfgChgEventDate=2002-09-03T12:20:32 +0700")
	assertDecoded(t, testOidMap, pkt, expected)
}

func TestIndex(t *testing.T) {
	as := assert.New(t)
	pdu := g.SnmpPDU{
		Name:  "1.3.6.1.4.1.30065.4.1.1.3.1.1.1.2.16.12.12.0.0.11.12.0.0.0.0.0.0.0.4.0.12",
		Type:  g.OctetString,
		Value: []byte{'3'},
	}

	testOidMap := snmp.OidMap{
		"1.3.6.1.6.3.1.1.4.1.0":     snmp.OIDParams{Name: "snmpTrapOID"},
		"1.3.6.1.2.1.1.3.0":         snmp.OIDParams{Name: "uptime"},
		"1.3.6.1.4.1.30065.4.1.0.2": snmp.OIDParams{Name: "aristaBgp4V2BackwardTransitionNotification"},
		"1.3.6.1.4.1.30065.4.1.1.3.1.1": snmp.OIDParams{
			Name: "aristaBgp4V2PeerLastErrorSentData",
			Index: []string{
				"Unsigned32 (1..4294967295)",
				"InetAddressType",
				"InetAddress"},
		},
	}

	pkt, err := encodeTrap("1.3.6.1.4.1.30065.4.1.0.2", []g.SnmpPDU{pdu})
	as.NoError(err)
	expected := []byte("snmpTrapOID=aristaBgp4V2BackwardTransitionNotification uptime=0 aristaBgp4V2PeerLastErrorSentData.1.ipv6.c0c:0:b0c::4:c=3")
	assertDecoded(t, testOidMap, pkt, expected)
}

func TestMacAddressIndex(t *testing.T) {
	as := assert.New(t)
	pdu := g.SnmpPDU{
		Name:  "1.3.6.1.4.1.2011.5.25.42.2.1.2.1.2.224.213.94.25.73.156.333.1.45",
		Type:  g.OctetString,
		Value: []byte{'3'},
	}
	testOidMap := snmp.OidMap{
		"1.3.6.1.6.3.1.1.4.1.0":     snmp.OIDParams{Name: "snmpTrapOID"},
		"1.3.6.1.2.1.1.3.0":         snmp.OIDParams{Name: "uptime"},
		"1.3.6.1.4.1.30065.4.1.0.2": snmp.OIDParams{Name: "aristaBgp4V2BackwardTransitionNotification"},
		"1.3.6.1.4.1.2011.5.25.42.2.1.2.1.2": snmp.OIDParams{
			Name: "hwCfgFdbVlanId",
			//{ hwCfgFdbMac, hwCfgFdbVlanId, hwCfgFdbVsiName }
			Index: []string{"MacAddress", "Unsigned32", "OCTET STRING (SIZE (0..32))"},
		},
	}

	pkt, err := encodeTrap("1.3.6.1.4.1.30065.4.1.0.2", []g.SnmpPDU{pdu})
	as.NoError(err)
	expected := []byte("snmpTrapOID=aristaBgp4V2BackwardTransitionNotification uptime=0 hwCfgFdbVlanId.e0:d5:5e:19:49:9c.333.-=3")
	assertDecoded(t, testOidMap, pkt, expected)
}

func TestIndex2(t *testing.T) {
	as := assert.New(t)
	pdu := g.SnmpPDU{
		Name:  "1.3.6.1.4.1.2011.5.25.32.4.1.36.1.1.2.7.71.69.49.47.48.47.57.0.1.49",
		Type:  g.OctetString,
		Value: []byte{'3'},
	}
	testOidMap := snmp.OidMap{
		"1.3.6.1.6.3.1.1.4.1.0":           snmp.OIDParams{Name: "snmpTrapOID"},
		"1.3.6.1.2.1.1.3.0":               snmp.OIDParams{Name: "uptime"},
		"1.3.6.1.4.1.2011.5.25.32.4.1.11": snmp.OIDParams{Name: "hwXQoSNotifications"},
		"1.3.6.1.4.1.2011.5.25.32.4.1.36.1.1.2": snmp.OIDParams{
			Name: "hwXQoSPacketsDropInterfaceAlarmQueueId",
			// hwXQoSPacketsDropInterfaceAlarmIfName - OCTET STRING
			// hwXQoSPacketsDropInterfaceAlarmQueueId - Integer32
			// hwXQoSPacketsDropInterfaceAlarmSlotId - OCTET STRING
			Index:  []string{"OCTET STRING", "Integer32", "OCTET STRING"},
			Syntax: "Integer32",
		},
	}

	pkt, err := encodeTrap("1.3.6.1.4.1.2011.5.25.32.4.1.11.51", []g.SnmpPDU{pdu})
	as.NoError(err)
	expected := []byte("snmpTrapOID=hwXQoSNotifications.51 uptime=0 hwXQoSPacketsDropInterfaceAlarmQueueId.GE1/0/9.0.1=3")
	assertDecoded(t, testOidMap, pkt, expected)
}
