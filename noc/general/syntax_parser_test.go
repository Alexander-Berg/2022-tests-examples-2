package snmp

import (
	"testing"

	"github.com/armon/go-radix"
	g "github.com/soniah/gosnmp"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/go/metrics"
)

func encodeTrap(oidVal string, pdus []g.SnmpPDU) ([]byte, error) {
	g.Default.Target = "127.0.0.1"
	g.Default.Port = 162
	g.Default.Version = g.Version2c
	g.Default.Community = "public"
	logger := zap.Must(zap.StandardConfig("console", log.DebugLevel))
	g.Default.Logger = NewLogger(logger)
	err := g.Default.Connect()
	if err != nil {
		return nil, err
	}
	defer g.Default.Conn.Close()

	tpdu := g.SnmpPDU{
		Name:  SnmpTrapUptime,
		Type:  g.TimeTicks,
		Value: uint32(0),
	}

	pdu := g.SnmpPDU{
		Name:  SnmpTrapOID,
		Type:  g.ObjectIdentifier,
		Value: oidVal,
	}
	vars := []g.SnmpPDU{tpdu, pdu}
	vars = append(vars, pdus...)
	trap := g.SnmpTrap{Variables: vars}
	f := g.SnmpPacket{
		Version:   g.Version2c,
		Community: "public",
		//MsgFlags:           x.MsgFlags,
		//SecurityModel:      x.SecurityModel,
		//SecurityParameters: newSecParams,
		//ContextEngineID:    x.ContextEngineID,
		//ContextName:        x.ContextName,
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

func decode(t *testing.T, testOidMap OidMap, packet []byte) ResolvedOidMap {
	as := assert.New(t)
	logger := zap.Must(zap.StandardConfig("console", log.DebugLevel)) // TODO: use fake logger
	met, err := metrics.New(nil, logger.WithName("metrics"))
	as.NoError(err)

	rad := radix.New()
	for oid, val := range testOidMap {
		rad.Insert(oid, val)
	}

	c := NewSNMPTrap(rad, logger, met.Registry(""), NewSNMPSyntax(logger))
	a, err := c.DecodeTrapMsg(packet)
	as.NoError(err)
	return *a
}

func TestSyntaxParserEnum(t *testing.T) {
	as := assert.New(t)
	type inputSyntax struct {
		syntax string
		val    []byte
	}
	var tests = []struct {
		input  inputSyntax
		exp    string
		expErr string
	}{
		{inputSyntax{`INTEGER {
			other(1),
			regular1822(2),
			hdh1822(3)}`, []byte{1}}, "other", ""},
		{inputSyntax{`BITS {A(0),B(1),C(2),D(3),E(4)}`, []byte{0b00010101}}, "A,C,E", ""},
	}
	logger := zap.Must(zap.StandardConfig("console", log.DebugLevel))

	s := NewSNMPSyntax(logger)

	for _, test := range tests {
		res, err := s.ResolveSyntaxValue(test.input.syntax, test.input.val)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.input)
		} else {
			as.NoError(err, "test %s", test.input)
		}
		as.Equal(res, test.exp, "test %s", test.input)
	}
}

func TestIndex1(t *testing.T) {
	as := assert.New(t)
	pdu := g.SnmpPDU{
		Name:  ".1.3.6.1.4.1.30065.3.22.1.1.1.9.12.85.110.100.101.114.108.97.121.69.99.109.112.0.0",
		Type:  g.OctetString,
		Value: []byte{50, 51, 52, 53},
	}
	testOidMap := OidMap{
		SnmpTrapOID:                  OIDParams{Name: SnmpTrapOIDName},
		SnmpTrapUptime:               OIDParams{Name: SnmpTrapOIDUptime},
		"1.3.6.1.4.1.30065.3.22.0.1": OIDParams{Name: "aristaHardwareUtilizationAlert"},
		"1.3.6.1.4.1.30065.3.22.1.1.1.9": OIDParams{
			Name:  "aristaHardwareUtilizationHighWatermarkTime",
			Index: []string{"OCTET STRING (0..35)", "OCTET STRING (0..35)", "OCTET STRING (0..35)"}},
	}
	pkt, err := encodeTrap("1.3.6.1.4.1.30065.3.22.0.1", []g.SnmpPDU{pdu})
	as.NoError(err)
	resMap := decode(t, testOidMap, pkt)
	exp := NewResolvedOidMapWithData("aristaHardwareUtilizationAlert", 0, map[string]interface{}{
		"aristaHardwareUtilizationHighWatermarkTime.UnderlayEcmp..": "2345"})
	as.Equal(exp, resMap)
}

func TestDateAndTime(t *testing.T) {
	as := assert.New(t)
	var tests = []struct {
		input  []byte
		exp    string
		expErr string
	}{
		{[]byte{0x07, 0xD2, 0x09, 0x03, 0x0C, 0x14, 0x20, 0x03, 0x2B, 0x07, 0x00}, "2002-09-03T12:20:32 +0700", ""},
		{[]byte{0x07, 0xD2, 0x09, 0x03, 0x0C, 0x14, 0x20, 0x03}, "2002-09-03T12:20:32 +0000", ""},
		{[]byte{0x07, 0xD2, 0x09, 0x03, 0x0C, 0x14, 0x20}, "", "unexpected DateAndTime len 7"},
	}
	logger := zap.Must(zap.StandardConfig("console", log.DebugLevel))

	s := NewSNMPSyntax(logger)

	for _, test := range tests {
		res, err := s.ResolveSyntaxValue(ConventionDateAndTime, test.input)
		if len(test.expErr) > 0 {
			as.EqualError(err, test.expErr, "test %s", test.input)
		} else {
			as.NoError(err, "test %s", test.input)
		}
		as.Equal(res, test.exp, "test %s", test.input)
	}
}

func TestIPAddressValue(t *testing.T) {
	as := assert.New(t)
	pdu := g.SnmpPDU{
		Name:  ".1.3.6.1.4.1.2636.5.3.1.1.2.1.14.5612",
		Type:  g.OctetString,
		Value: []byte{1, 2, 3, 4},
	}
	testOidMap := OidMap{
		"1.3.6.1.6.3.1.1.4.1.0":           OIDParams{Name: "snmpTrapOID"},
		"1.3.6.1.2.1.1.3.0":               OIDParams{Name: "uptime"},
		"1.3.6.1.4.1.2636.5.3.1.1.2.1.14": OIDParams{Name: "bfdSessAddr", Syntax: "InetAddress"},
	}
	pkt, err := encodeTrap("1.3.6.1.4.1.30065.3.12.0.1", []g.SnmpPDU{pdu})
	as.NoError(err)
	resMap := decode(t, testOidMap, pkt)
	exp := NewResolvedOidMapWithData("1.3.6.1.4.1.30065.3.12.0.1", 0, map[string]interface{}{
		"bfdSessAddr.5612": "1.2.3.4"})
	as.Equal(exp, resMap)
}

func TestMacTrapMacInfoSyntax(t *testing.T) {
	// example from https://support.huawei.com/enterprise/ru/doc/EDOC1100065666/82700987/huawei-switch-l2mam-ext-mib
	as := assert.New(t)
	trapOID := "1.3.6.1.4.1.2011.5.25.315.3.1"
	trapName := "hwMacTrapAlarm"
	testOID := "1.3.6.1.4.1.2011.5.25.315.2.2"
	testOIDName := "hwMacTrapMacInfo"
	testOidMap := MakeBaseOIDMapWithOid(trapOID, trapName, testOID, testOIDName, HMSyntaxMacTrapMacInfo)
	pdu := g.SnmpPDU{
		Name:  testOID,
		Type:  g.OctetString,
		Value: []byte{0x02, 0x00, 0x00, 0x00, 0x06, 0x01, 0x03, 0xe8, 0x00, 0x01, 0x11, 0x10, 0x5e, 0xe},
	}

	pkt, err := encodeTrap(trapOID, []g.SnmpPDU{pdu})
	as.NoError(err)
	resMap := decode(t, testOidMap, pkt)
	exp := NewResolvedOidMapWithData(trapName, 0, map[string]interface{}{
		testOIDName: "2.6.1.1000.00:01:11:10:5e:0e"})
	as.Equal(exp, resMap)
	// test MAC learning variant
	pdu = g.SnmpPDU{
		Name:  testOID,
		Type:  g.OctetString,
		Value: []byte("MAC learning"),
	}

	pkt, err = encodeTrap(trapOID, []g.SnmpPDU{pdu})
	as.NoError(err)
	resMap = decode(t, testOidMap, pkt)
	exp = NewResolvedOidMapWithData(trapName, 0, map[string]interface{}{
		testOIDName: "MAC learning"})
	as.Equal(exp, resMap)

	// test string in octet string MAC learning variant
	pdu = g.SnmpPDU{
		Name: testOID,
		Type: g.OctetString,
		//01 00 00 00 32 1 03 e7 00 09 f5 20 8e 74
		//               ^ no leading zero for some reason
		Value: []byte{48, 49, 48, 48, 48, 48, 48, 48, 51, 50, 49, 48, 51, 101, 55, 48, 48, 48, 57, 102, 53, 50, 48, 56, 101, 55, 52},
	}

	pkt, err = encodeTrap(trapOID, []g.SnmpPDU{pdu})
	as.NoError(err)
	resMap = decode(t, testOidMap, pkt)
	exp = NewResolvedOidMapWithData(trapName, 0, map[string]interface{}{
		testOIDName: "1.50.1.999.00:09:f5:20:8e:74"})
	as.Equal(exp, resMap)
	// test two string in octet string MAC learning variant
	pdu = g.SnmpPDU{
		Name: testOID,
		Type: g.OctetString,
		Value: []byte{48, 49, 48, 48, 48, 48, 48, 48, 50, 53, 49, 48, 57, 55, 55, 97, 99, 53, 102, 51, 101, 53, 100, 97,
			100, 101, 57, 48, 49, 48, 48, 48, 48, 48, 48, 50, 53, 49, 48, 57, 55, 55, 54, 99, 99, 52, 57, 102, 99, 52,
			48, 52, 56, 101},
	}

	pkt, err = encodeTrap(trapOID, []g.SnmpPDU{pdu})
	as.NoError(err)
	resMap = decode(t, testOidMap, pkt)
	exp = NewResolvedOidMapWithData(trapName, 0, map[string]interface{}{
		testOIDName: "1.37.1.2423.ac:5f:3e:5d:ad:e9|1.37.1.2423.6c:c4:9f:c4:04:8e"})
	as.Equal(exp, resMap)
}
