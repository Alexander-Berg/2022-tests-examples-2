package pcep

import (
	"math"
	"net"
	"testing"

	"github.com/stretchr/testify/suite"
)

type tlvHeaderSuite struct {
	suite.Suite

	header TLVHeader
}

func TestTLVHeaderSuite(t *testing.T) {
	suite.Run(t, new(tlvHeaderSuite))
}

func (suite *tlvHeaderSuite) SetupTest() {
	suite.header = TLVHeader{}
}

func (suite *tlvHeaderSuite) TestDecode() {
	suite.Require().NoError(suite.header.decode([]byte{0x00, 0x0e, 0x00, 0x18}))
	suite.Assert().Equal(TLVTypeDomainID, suite.header.Type)
	suite.Assert().Equal(uint16(24), suite.header.Length)
}

func (suite *tlvHeaderSuite) TestParse() {
	value, err := suite.header.Parse([]byte{0x00, 0x0e, 0x00, 0x00})
	suite.Require().NoError(err)
	suite.Require().Empty(value)
	suite.Assert().Equal(TLVTypeDomainID, suite.header.Type)
	suite.Assert().Equal(uint16(0), suite.header.Length)
}

func (suite *tlvHeaderSuite) TestDecodeError() {
	suite.Assert().Error(suite.header.decode([]byte{}))
	suite.Assert().Error(suite.header.decode([]byte{0x0}))
}

func (suite *tlvHeaderSuite) TestParseError() {
	_, err := suite.header.Parse([]byte{})
	suite.Assert().Error(err)
	_, err = suite.header.Parse([]byte{0x0})
	suite.Assert().Error(err)
}

func (suite *tlvHeaderSuite) TestSerialize() {
	suite.header = TLVHeader{
		Type:   TLVTypeSymbolicPathName,
		Length: 0,
	}
	raw, err := suite.header.Serialize(nil)
	suite.Require().NoError(err)
	suite.Assert().Equal([]byte{0x00, 0x11, 0x00, 0x00}, raw)

	suite.header = TLVHeader{
		Type:   TLVTypeSymbolicPathName,
		Length: 4,
	}
	raw, err = suite.header.Serialize([]byte{0x00, 0x01, 0x02, 0x03})
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x11, 0x00, 0x04,
			0x00, 0x01, 0x02, 0x03,
		},
		raw,
	)
}

func (suite *tlvHeaderSuite) TestSerializeError() {
	suite.header = TLVHeader{
		Type:   TLVTypeAutoBandwidthCapability,
		Length: 1,
	}
	raw, err := suite.header.Serialize(nil)
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)

	suite.header = TLVHeader{
		Type:   TLVTypeAutoBandwidthCapability,
		Length: 0,
	}
	raw, err = suite.header.Serialize([]byte{0x0})
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)
}

type statefulCapabilityTLVSuite struct {
	suite.Suite

	tlv StatefulCapabilityTLV
}

func TestStatefulCapabilityTLVSuite(t *testing.T) {
	suite.Run(t, new(statefulCapabilityTLVSuite))
}

func (suite *statefulCapabilityTLVSuite) SetupTest() {
	suite.tlv = StatefulCapabilityTLV{}
}

func (suite *statefulCapabilityTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *statefulCapabilityTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x10, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().False(suite.tlv.LSPUpdateCapability)
	suite.Assert().False(suite.tlv.IncludeDBVersion)
	suite.Assert().False(suite.tlv.LSPInstantiationCapability)
	suite.Assert().False(suite.tlv.TriggeredResync)
	suite.Assert().False(suite.tlv.DeltaLSPSyncCapability)
	suite.Assert().False(suite.tlv.TriggeredInitialSync)
	suite.Assert().False(suite.tlv.P2MPCapability)
	suite.Assert().False(suite.tlv.P2MPLSPUpdateCapability)
	suite.Assert().False(suite.tlv.P2MPLSPInstantiationCapability)
	suite.Assert().False(suite.tlv.LSPSchedulingCapability)
	suite.Assert().False(suite.tlv.PDLSPCapability)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x10, 0x00, 0x04,
		0xff, 0xff, 0xff, 0xff,
	}))
	suite.Assert().True(suite.tlv.LSPUpdateCapability)
	suite.Assert().True(suite.tlv.IncludeDBVersion)
	suite.Assert().True(suite.tlv.LSPInstantiationCapability)
	suite.Assert().True(suite.tlv.TriggeredResync)
	suite.Assert().True(suite.tlv.DeltaLSPSyncCapability)
	suite.Assert().True(suite.tlv.TriggeredInitialSync)
	suite.Assert().True(suite.tlv.P2MPCapability)
	suite.Assert().True(suite.tlv.P2MPLSPUpdateCapability)
	suite.Assert().True(suite.tlv.P2MPLSPInstantiationCapability)
	suite.Assert().True(suite.tlv.LSPSchedulingCapability)
	suite.Assert().True(suite.tlv.PDLSPCapability)
}

func (suite *statefulCapabilityTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x00, 0x04}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x10, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x10, 0x00, 0x05}))
}

func (suite *statefulCapabilityTLVSuite) TestSerialize() {
	suite.tlv = StatefulCapabilityTLV{
		LSPUpdateCapability:            true,
		IncludeDBVersion:               false,
		LSPInstantiationCapability:     true,
		TriggeredResync:                false,
		DeltaLSPSyncCapability:         true,
		TriggeredInitialSync:           false,
		P2MPCapability:                 true,
		P2MPLSPUpdateCapability:        false,
		P2MPLSPInstantiationCapability: true,
		LSPSchedulingCapability:        false,
		PDLSPCapability:                true,
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x10, 0x00, 0x04,
			0x00, 0x00, 0x05, 0x55,
		},
		raw,
	)
}

type srCapabilityTLVSuite struct {
	suite.Suite

	tlv SRCapabilityTLV
}

func TestSRCapabilityTLVSuite(t *testing.T) {
	suite.Run(t, new(srCapabilityTLVSuite))
}

func (suite *srCapabilityTLVSuite) SetupTest() {
	suite.tlv = SRCapabilityTLV{}
}

func (suite *srCapabilityTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *srCapabilityTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1a, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0a,
	}))
	suite.Assert().Equal(uint8(10), suite.tlv.MSD)
	suite.Assert().False(suite.tlv.NAIToSidResolvingCapability)
	suite.Assert().False(suite.tlv.MSDNoLimit)
}

func (suite *srCapabilityTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1a, 0x00, 0x04}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1a, 0x00, 0x05, 0x00, 0x00, 0x00, 0x0a, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1b, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a}))
}

func (suite *srCapabilityTLVSuite) TestSerialize() {
	suite.tlv = SRCapabilityTLV{
		NAIToSidResolvingCapability: true,
		MSDNoLimit:                  true,
		MSD:                         34,
	}

	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1a, 0x00, 0x04,
			0x00, 0x00, 0x03, 0x00,
		},
		raw,
	)
}

type pathSetupTypeTLVSuite struct {
	suite.Suite

	tlv PathSetupTypeTLV
}

func TestPathSetupTypeTLVSuite(t *testing.T) {
	suite.Run(t, new(pathSetupTypeTLVSuite))
}

func (suite *pathSetupTypeTLVSuite) SetupTest() {
	suite.tlv = PathSetupTypeTLV{}
}

func (suite *pathSetupTypeTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *pathSetupTypeTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1c, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().Equal(PathSetupTypeRSVP, suite.tlv.Type)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1c, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x01,
	}))
	suite.Assert().Equal(PathSetupTypeSR, suite.tlv.Type)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1c, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x02,
	}))
	suite.Assert().Equal(PathSetupTypeCentralController, suite.tlv.Type)
}

func (suite *pathSetupTypeTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1d, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1c, 0x00, 0x00}))
}

func (suite *pathSetupTypeTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1c, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = PathSetupTypeTLV{Type: PathSetupTypeSR}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1c, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x01,
		},
		raw,
	)

	suite.tlv = PathSetupTypeTLV{Type: PathSetupTypeCentralController}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal([]byte{
		0x00, 0x1c, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x02,
	},
		raw,
	)
}

type pathSetupTypeCapabilityTLVSuite struct {
	suite.Suite

	tlv PathSetupTypeCapabilityTLV
}

func TestPathSetupTypeCapabilityTLVSuite(t *testing.T) {
	suite.Run(t, new(pathSetupTypeCapabilityTLVSuite))
}

func (suite *pathSetupTypeCapabilityTLVSuite) SetupTest() {
	suite.tlv = PathSetupTypeCapabilityTLV{}
}

func (suite *pathSetupTypeCapabilityTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *pathSetupTypeCapabilityTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x22, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().Equal([]PathSetupType{PathSetupTypeRSVP}, suite.tlv.Types)
	suite.Assert().Nil(suite.tlv.SRCapability)
	suite.Assert().Nil(suite.tlv.PCECCCapability)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x22, 0x00, 0x18,
		0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x02, 0x00,
		0x00, 0x01, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
		0x00, 0x1a, 0x00, 0x4,
		0x00, 0x00, 0x01, 0xd5,
	}))
	suite.Assert().Equal([]PathSetupType{PathSetupTypeRSVP, PathSetupTypeSR, PathSetupTypeCentralController}, suite.tlv.Types)
	suite.Assert().NotNil(suite.tlv.SRCapability)
	suite.Assert().False(suite.tlv.SRCapability.NAIToSidResolvingCapability)
	suite.Assert().True(suite.tlv.SRCapability.MSDNoLimit)
	suite.Assert().Equal(uint8(0), suite.tlv.SRCapability.MSD)
	suite.Assert().NotNil(suite.tlv.PCECCCapability)
	suite.Assert().False(suite.tlv.PCECCCapability.Label)
}

func (suite *pathSetupTypeCapabilityTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x0, 0x1, 0x2}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x0, 0x0, 0x0, 0x0}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x0, 0x0, 0x0, 0x1}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x0, 0x0, 0x0, 0xa}))
}

func (suite *pathSetupTypeCapabilityTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x22, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = PathSetupTypeCapabilityTLV{
		Types:           []PathSetupType{PathSetupTypeRSVP},
		SRCapability:    nil,
		PCECCCapability: nil,
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x22, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = PathSetupTypeCapabilityTLV{
		Types: []PathSetupType{PathSetupTypeSR},
		SRCapability: &SRCapabilityTLV{
			NAIToSidResolvingCapability: true,
			MSDNoLimit:                  false,
			MSD:                         123,
		},
		PCECCCapability: nil,
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x22, 0x00, 0x10,
			0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00,
			0x00, 0x1a, 0x00, 0x04,
			0x00, 0x00, 0x02, 0x7b,
		},
		raw,
	)

	suite.tlv = PathSetupTypeCapabilityTLV{
		Types: []PathSetupType{PathSetupTypeRSVP, PathSetupTypeSR, PathSetupTypeCentralController},
		SRCapability: &SRCapabilityTLV{
			NAIToSidResolvingCapability: true,
			MSDNoLimit:                  false,
			MSD:                         123,
		},
		PCECCCapability: &PCECCCapabilityTLV{Label: true},
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x22, 0x00, 0x18,
			0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x02, 0x00,
			0x00, 0x01, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x01,
			0x00, 0x1a, 0x00, 0x04,
			0x00, 0x00, 0x02, 0x7b,
		},
		raw,
	)
}

type pceCCCapabilityTLVSuite struct {
	suite.Suite

	tlv PCECCCapabilityTLV
}

func TestPCECCCapabilityTLVSuite(t *testing.T) {
	suite.Run(t, new(pceCCCapabilityTLVSuite))
}

func (suite *pceCCCapabilityTLVSuite) SetupTest() {
	suite.tlv = PCECCCapabilityTLV{}
}

func (suite *pceCCCapabilityTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *pceCCCapabilityTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x01, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().False(suite.tlv.Label)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x01, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x01,
	}))
	suite.Assert().True(suite.tlv.Label)
}

func (suite *pceCCCapabilityTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x02, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00}))
}

func (suite *pceCCCapabilityTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x01, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = PCECCCapabilityTLV{Label: true}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x01, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x01,
		},
		raw,
	)
}

type ipv4LSPIdentifiersTLVSuite struct {
	suite.Suite

	tlv IPv4LSPIdentifiersTLV
}

func TestIPv4LSPIdentifiersTLVSuite(t *testing.T) {
	suite.Run(t, new(ipv4LSPIdentifiersTLVSuite))
}

func (suite *ipv4LSPIdentifiersTLVSuite) SetupTest() {
	suite.tlv = IPv4LSPIdentifiersTLV{}
}

func (suite *ipv4LSPIdentifiersTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *ipv4LSPIdentifiersTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x12, 0x00, 0x10,
		0x7f, 0x01, 0x02, 0x03, 0x00, 0x71, 0x00, 0x25, 0x00, 0x07, 0xa4, 0xa4, 0x7f, 0x03, 0x02, 0x01,
	}))
	suite.Assert().Equal(net.ParseIP("127.1.2.3").To4(), suite.tlv.TunnelSenderAddress)
	suite.Assert().Equal(uint16(113), suite.tlv.LSPID)
	suite.Assert().Equal(uint16(37), suite.tlv.TunnelID)
	suite.Assert().Equal(uint32(500900), suite.tlv.ExtendedTunnelID)
	suite.Assert().Equal(net.ParseIP("127.3.2.1").To4(), suite.tlv.TunnelEndpointAddress)
}

func (suite *ipv4LSPIdentifiersTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x0, 0x0, 0x0, 0x0}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x0, 0x12, 0x0, 0x0}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x11, 0x00, 0x10,
		0x7f, 0x01, 0x2, 0x03, 0x00, 0x71, 0x00, 0x25, 0x00, 0x07, 0xa4, 0xa4, 0x7f, 0x03, 0x02, 0x01,
	}))
}

func (suite *ipv4LSPIdentifiersTLVSuite) TestSerialize() {
	suite.tlv = IPv4LSPIdentifiersTLV{
		TunnelSenderAddress:   net.ParseIP("127.1.2.3"),
		LSPID:                 113,
		TunnelID:              37,
		ExtendedTunnelID:      500900,
		TunnelEndpointAddress: net.ParseIP("127.3.2.1"),
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x12, 0x00, 0x10,
			0x7f, 0x01, 0x02, 0x03, 0x00, 0x71, 0x00, 0x25, 0x00, 0x07, 0xa4, 0xa4, 0x7f, 0x03, 0x02, 0x01,
		},
		raw,
	)
}

func (suite *ipv4LSPIdentifiersTLVSuite) TestSerializeError() {
	raw, err := suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)

	suite.tlv = IPv4LSPIdentifiersTLV{
		TunnelSenderAddress: net.ParseIP("127.1.2.3"),
		LSPID:               113,
		TunnelID:            37,
		ExtendedTunnelID:    500900,
	}
	raw, err = suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)

	suite.tlv = IPv4LSPIdentifiersTLV{
		LSPID:                 113,
		TunnelID:              37,
		ExtendedTunnelID:      500900,
		TunnelEndpointAddress: net.ParseIP("127.3.2.1"),
	}
	raw, err = suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)
}

type ipv6LSPIdentifiersTLVSuite struct {
	suite.Suite

	tlv IPv6LSPIdentifiersTLV
}

func TestIPv6LSPIdentifiersTLVSuite(t *testing.T) {
	suite.Run(t, new(ipv6LSPIdentifiersTLVSuite))
}

func (suite *ipv6LSPIdentifiersTLVSuite) SetupTest() {
	suite.tlv = IPv6LSPIdentifiersTLV{}
}

func (suite *ipv6LSPIdentifiersTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *ipv6LSPIdentifiersTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x13, 0x00, 0x34,
		0x48, 0x2b, 0x52, 0x52, 0xd6, 0xe3, 0x9d, 0x5b, 0xab, 0x43,
		0x76, 0x12, 0x19, 0xb9, 0xf4, 0x74, 0x01, 0x8d, 0x02, 0x13,
		0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
		0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0xf2, 0x68, 0xb5, 0x6b,
		0x78, 0xfd, 0x4c, 0x00, 0x15, 0x7e, 0x54, 0xdd, 0xa6, 0x62,
		0x4, 0x45,
	}))

	suite.Assert().Equal(net.ParseIP("482b:5252:d6e3:9d5b:ab43:7612:19b9:f474"), suite.tlv.TunnelSenderAddress)
	suite.Assert().Equal(uint16(397), suite.tlv.LSPID)
	suite.Assert().Equal(uint16(531), suite.tlv.TunnelID)
	suite.Assert().Equal(
		[16]byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f},
		suite.tlv.ExtendedTunnelID,
	)
	suite.Assert().Equal(net.ParseIP("f268:b56b:78fd:4c00:157e:54dd:a662:0445"), suite.tlv.TunnelEndpointAddress)
}

func (suite *ipv6LSPIdentifiersTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x13, 0x00, 0x34}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x13, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x11, 0x00, 0x00}))
}

func (suite *ipv6LSPIdentifiersTLVSuite) TestSerialize() {
	suite.tlv = IPv6LSPIdentifiersTLV{
		TunnelSenderAddress: net.ParseIP("482b:5252:d6e3:9d5b:ab43:7612:19b9:f474"),
		LSPID:               397,
		TunnelID:            531,
		ExtendedTunnelID: [16]byte{
			0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
		},
		TunnelEndpointAddress: net.ParseIP("f268:b56b:78fd:4c00:157e:54dd:a662:0445"),
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x13, 0x00, 0x34,
			0x48, 0x2b, 0x52, 0x52, 0xd6, 0xe3, 0x9d, 0x5b, 0xab, 0x43,
			0x76, 0x12, 0x19, 0xb9, 0xf4, 0x74, 0x01, 0x8d, 0x02, 0x13,
			0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
			0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0xf2, 0x68, 0xb5, 0x6b,
			0x78, 0xfd, 0x4c, 0x00, 0x15, 0x7e, 0x54, 0xdd, 0xa6, 0x62,
			0x04, 0x45,
		},
		raw,
	)
}

func (suite *ipv6LSPIdentifiersTLVSuite) TestSerializeError() {
	raw, err := suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)

	suite.tlv = IPv6LSPIdentifiersTLV{
		TunnelSenderAddress: net.ParseIP("482b:5252:d6e3:9d5b:ab43:7612:19b9:f474"),
		LSPID:               397,
		TunnelID:            531,
		ExtendedTunnelID: [16]byte{
			0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
		},
	}
	raw, err = suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)

	suite.tlv = IPv6LSPIdentifiersTLV{
		LSPID:    397,
		TunnelID: 531,
		ExtendedTunnelID: [16]byte{
			0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
		},
		TunnelEndpointAddress: net.ParseIP("f268:b56b:78fd:4c00:157e:54dd:a662:0445"),
	}
	raw, err = suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)
}

type symbolicPathNameTLVSuite struct {
	suite.Suite

	tlv SymbolicPathNameTLV
}

func TestSymbolicPathNameTLVSuite(t *testing.T) {
	suite.Run(t, new(symbolicPathNameTLVSuite))
}

func (suite *symbolicPathNameTLVSuite) SetupTest() {
	suite.tlv = SymbolicPathNameTLV{}
}

func (suite *symbolicPathNameTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *symbolicPathNameTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{0x00, 0x11, 0x00, 0x00}))
	suite.Assert().Equal("", suite.tlv.Name)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x11, 0x00, 0x09,
		0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65,
	}))
	suite.Assert().Equal("test name", suite.tlv.Name)
}

func (suite *symbolicPathNameTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x10, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x11, 0x00, 0x01}))
}

func (suite *symbolicPathNameTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{0x00, 0x11, 0x00, 0x00},
		raw,
	)

	suite.tlv = SymbolicPathNameTLV{Name: "test name"}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x11, 0x00, 0x09,
			0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

type lspErrorCodeTLVSuite struct {
	suite.Suite

	tlv LSPErrorCodeTLV
}

func TestLSPErrorCodeTLVSuite(t *testing.T) {
	suite.Run(t, new(lspErrorCodeTLVSuite))
}

func (suite *lspErrorCodeTLVSuite) SetupTest() {
	suite.tlv = LSPErrorCodeTLV{}
}

func (suite *lspErrorCodeTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *lspErrorCodeTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x14, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x01,
	}))
	suite.Assert().Equal(LSPErrorCodeUnknownReason, suite.tlv.Code)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x14, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x08,
	}))
	suite.Assert().Equal(LSPErrorCodeLSPPreemptedRSVPSignalingError, suite.tlv.Code)
}

func (suite *lspErrorCodeTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x14, 0x00, 0x04}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x14, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x13, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x01,
	}))
}

func (suite *lspErrorCodeTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x14, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = LSPErrorCodeTLV{Code: LSPErrorCodeLimitReachedForPCEControlledLSPs}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x14, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x02,
		},
		raw,
	)

	suite.tlv = LSPErrorCodeTLV{Code: LSPErrorCodeLSPPreemptedRSVPSignalingError}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x14, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x08,
		},
		raw,
	)
}

type lspDBVersionTLVSuite struct {
	suite.Suite

	tlv LSPDBVersionTLV
}

func TestLSPDBVersionTLVSuite(t *testing.T) {
	suite.Run(t, new(lspDBVersionTLVSuite))
}

func (suite *lspDBVersionTLVSuite) SetupTest() {
	suite.tlv = LSPDBVersionTLV{}
}

func (suite *lspDBVersionTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *lspDBVersionTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x17, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x8a, 0xf8,
	}))

	suite.Assert().Equal(uint64(101112), suite.tlv.LSPStateDBVersionNumber)
}

func (suite *lspDBVersionTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x16, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x8a, 0xf8,
	}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x17, 0x00, 0x08}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x17, 0x00, 0x00}))
}

func (suite *lspDBVersionTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x17, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = LSPDBVersionTLV{LSPStateDBVersionNumber: 101112}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x17, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x8a, 0xf8,
		},
		raw,
	)
}

type associationTypeListTLVSuite struct {
	suite.Suite

	tlv AssociationTypeListTLV
}

func TestAssociationTypeListTLVSuite(t *testing.T) {
	suite.Run(t, new(associationTypeListTLVSuite))
}

func (suite *associationTypeListTLVSuite) SetupTest() {
	suite.tlv = AssociationTypeListTLV{}
}

func (suite *associationTypeListTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *associationTypeListTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{0x00, 0x23, 0x00, 0x00}))
	suite.Assert().Equal([]AssociationType{}, suite.tlv.Types)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x23, 0x00, 0x02,
		0x00, 0x01,
	}))
	suite.Assert().Equal([]AssociationType{AssociationTypePathProtection}, suite.tlv.Types)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x23, 0x00, 0x04,
		0x00, 0x03, 0x00, 0x06,
	}))
	suite.Assert().Equal([]AssociationType{AssociationTypePolicy, AssociationTypeSRPolicy}, suite.tlv.Types)
}

func (suite *associationTypeListTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x22, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x23, 0x00, 0x01}))
}

func (suite *associationTypeListTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{0x00, 0x23, 0x00, 0x00},
		raw,
	)

	suite.tlv = AssociationTypeListTLV{
		Types: []AssociationType{AssociationTypePathProtection},
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x23, 0x00, 0x02,
			0x00, 0x01, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = AssociationTypeListTLV{
		Types: []AssociationType{AssociationTypePolicy, AssociationTypeSRPolicy},
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x23, 0x00, 0x04,
			0x00, 0x03, 0x00, 0x06,
		},
		raw,
	)
}

type globalAssociationSourceTLVSuite struct {
	suite.Suite

	tlv GlobalAssociationSourceTLV
}

func TestGlobalAssociationSourceTLVSuite(t *testing.T) {
	suite.Run(t, new(globalAssociationSourceTLVSuite))
}

func (suite *globalAssociationSourceTLVSuite) SetupTest() {
	suite.tlv = GlobalAssociationSourceTLV{}
}

func (suite *globalAssociationSourceTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *globalAssociationSourceTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1e, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().Equal(uint32(0), suite.tlv.Source)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1e, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x71,
	}))
	suite.Assert().Equal(uint32(113), suite.tlv.Source)
}

func (suite *globalAssociationSourceTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1e, 0x00, 0x04}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1e, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x1d, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
}

func (suite *globalAssociationSourceTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1e, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = GlobalAssociationSourceTLV{Source: 113}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1e, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x71,
		},
		raw,
	)
}

type extendedAssociationIDTLVSuite struct {
	suite.Suite

	tlv ExtendedAssociationIDTLV
}

func TestExtendedAssociationIDTLVSuite(t *testing.T) {
	suite.Run(t, new(extendedAssociationIDTLVSuite))
}

func (suite *extendedAssociationIDTLVSuite) SetupTest() {
	suite.tlv = ExtendedAssociationIDTLV{}
}

func (suite *extendedAssociationIDTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *extendedAssociationIDTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{0x00, 0x1f, 0x00, 0x00}))
	suite.Assert().Empty(suite.tlv.ID)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1f, 0x00, 0x06,
		0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
	}))
	suite.Assert().Equal([]byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05}, suite.tlv.ID)
}

func (suite *extendedAssociationIDTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1f, 0x00, 0x01}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1e, 0x00, 0x00}))
}

func (suite *extendedAssociationIDTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{0x00, 0x1f, 0x00, 0x00},
		raw,
	)

	suite.tlv = ExtendedAssociationIDTLV{ID: []byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05}}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1f, 0x00, 0x06,
			0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x00, 0x00,
		},
		raw,
	)
}

type srExtendedAssociationIDTLVSuite struct {
	suite.Suite

	tlv SRExtendedAssociationIDTLV
}

func TestSRExtendedAssociationIDTLVSuite(t *testing.T) {
	suite.Run(t, new(srExtendedAssociationIDTLVSuite))
}

func (suite *srExtendedAssociationIDTLVSuite) SetupTest() {
	suite.tlv = SRExtendedAssociationIDTLV{}
}

func (suite *srExtendedAssociationIDTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *srExtendedAssociationIDTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1f, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x64, 0x7f, 0x00, 0x00, 0x01,
	}))
	suite.Assert().Equal(uint32(100), suite.tlv.Color)
	suite.Assert().Equal(net.ParseIP("127.0.0.1").To4(), suite.tlv.Endpoint)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x1f, 0x00, 0x14,
		0x00, 0x00, 0x00, 0xc8, 0x12, 0x05, 0x82, 0x6e, 0xb2, 0xee,
		0x39, 0x04, 0x73, 0x48, 0x8d, 0x19, 0x53, 0x1b, 0xca, 0x34,
	}))
	suite.Assert().Equal(uint32(200), suite.tlv.Color)
	suite.Assert().Equal(net.ParseIP("1205:826e:b2ee:3904:7348:8d19:531b:ca34"), suite.tlv.Endpoint)
}

func (suite *srExtendedAssociationIDTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1f, 0x00, 0x08}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x1f, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x1d, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x64, 0x7f, 0x00, 0x00, 0x01,
	}))
}

func (suite *srExtendedAssociationIDTLVSuite) TestSerialize() {
	suite.tlv = SRExtendedAssociationIDTLV{
		Color:    100,
		Endpoint: net.ParseIP("127.0.0.1"),
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1f, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x64, 0x7f, 0x00, 0x00, 0x01,
		},
		raw,
	)

	suite.tlv = SRExtendedAssociationIDTLV{
		Color:    200,
		Endpoint: net.ParseIP("1205:826e:b2ee:3904:7348:8d19:531b:ca34"),
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x1f, 0x00, 0x14,
			0x00, 0x00, 0x00, 0xc8, 0x12, 0x05, 0x82, 0x6e, 0xb2, 0xee,
			0x39, 0x04, 0x73, 0x48, 0x8d, 0x19, 0x53, 0x1b, 0xca, 0x34,
		},
		raw,
	)
}

func (suite *srExtendedAssociationIDTLVSuite) TestSerializeError() {
	raw, err := suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)
}

type srPolicyIDTLVSuite struct {
	suite.Suite

	tlv JuniperSRPolicyIDTLV
}

func TestSRPolicyIDTLVSuite(t *testing.T) {
	suite.Run(t, new(srPolicyIDTLVSuite))
}

func (suite *srPolicyIDTLVSuite) SetupTest() {
	suite.tlv = JuniperSRPolicyIDTLV{}
}

func (suite *srPolicyIDTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *srPolicyIDTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0xff, 0xe3, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x64, 0x7f, 0x00, 0x00, 0x01,
	}))
	suite.Assert().Equal(uint32(100), suite.tlv.Color)
	suite.Assert().Equal(net.ParseIP("127.0.0.1").To4(), suite.tlv.Endpoint)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0xff, 0xe3, 0x00, 0x14,
		0x00, 0x00, 0x00, 0xc8, 0x12, 0x05, 0x82, 0x6e, 0xb2, 0xee,
		0x39, 0x04, 0x73, 0x48, 0x8d, 0x19, 0x53, 0x1b, 0xca, 0x34,
	}))
	suite.Assert().Equal(uint32(200), suite.tlv.Color)
	suite.Assert().Equal(net.ParseIP("1205:826e:b2ee:3904:7348:8d19:531b:ca34"), suite.tlv.Endpoint)
}

func (suite *srPolicyIDTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0xff, 0xe3, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0xff, 0xe3, 0x00, 0x08}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x3f, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x64, 0x7f, 0x00, 0x00, 0x01,
	}))
}

func (suite *srPolicyIDTLVSuite) TestSerialize() {
	suite.tlv = JuniperSRPolicyIDTLV{
		Color:    100,
		Endpoint: net.ParseIP("127.0.0.1"),
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0xff, 0xe3, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x64, 0x7f, 0x00, 0x00, 0x01,
		},
		raw,
	)

	suite.tlv = JuniperSRPolicyIDTLV{
		Color:    200,
		Endpoint: net.ParseIP("1205:826e:b2ee:3904:7348:8d19:531b:ca34"),
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0xff, 0xe3, 0x00, 0x14,
			0x00, 0x00, 0x00, 0xc8, 0x12, 0x05, 0x82, 0x6e, 0xb2, 0xee,
			0x39, 0x04, 0x73, 0x48, 0x8d, 0x19, 0x53, 0x1b, 0xca, 0x34,
		},
		raw,
	)
}

func (suite *srPolicyIDTLVSuite) SerializeError() {
	raw, err := suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)
}

type srPolicyNameTLVSuite struct {
	suite.Suite

	tlv SRPolicyNameTLV
}

func TestSRPolicyNameTLVSuite(t *testing.T) {
	suite.Run(t, new(srPolicyNameTLVSuite))
}

func (suite *srPolicyNameTLVSuite) SetupTest() {
	suite.tlv = SRPolicyNameTLV{}
}

func (suite *srPolicyNameTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *srPolicyNameTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{0x00, 0x38, 0x00, 0x00}))
	suite.Assert().Equal("", suite.tlv.Name)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x38, 0x00, 0x09,
		0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65,
	}))
	suite.Assert().Equal("test name", suite.tlv.Name)
}

func (suite *srPolicyNameTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x38, 0x00, 0x01}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x37, 0x00, 0x00}))
}

func (suite *srPolicyNameTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{0x00, 0x38, 0x00, 0x00},
		raw,
	)

	suite.tlv = SRPolicyNameTLV{Name: "test name"}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x38, 0x00, 0x09,
			0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

type srPolicyCandidatePathIDTLVSuite struct {
	suite.Suite

	tlv SRPolicyCandidatePathIDTLV
}

func TestSRPolicyCandidatePathIDTLVSuite(t *testing.T) {
	suite.Run(t, new(srPolicyCandidatePathIDTLVSuite))
}

func (suite *srPolicyCandidatePathIDTLVSuite) SetupTest() {
	suite.tlv = SRPolicyCandidatePathIDTLV{}
}

func (suite *srPolicyCandidatePathIDTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *srPolicyCandidatePathIDTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x39, 0x00, 0x1c,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().Equal(uint8(0), suite.tlv.ProtocolOrigin)
	suite.Assert().Equal(uint32(0), suite.tlv.OriginatorASN)
	suite.Assert().Equal(net.ParseIP("::"), suite.tlv.OriginatorAddress)
	suite.Assert().Equal(uint32(0), suite.tlv.Discriminator)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x39, 0x00, 0x1c,
		0x0d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x35, 0xdc,
		0x35, 0x05, 0xf1, 0xa2, 0x3e, 0x12, 0x8a, 0x99, 0xbe,
		0x98, 0x52, 0xd5, 0x42, 0xa9, 0x79, 0x00, 0x00, 0x00,
		0x02,
	}))
	suite.Assert().Equal(uint8(13), suite.tlv.ProtocolOrigin)
	suite.Assert().Equal(uint32(53), suite.tlv.OriginatorASN)
	suite.Assert().Equal(net.ParseIP("dc35:05f1:a23e:128a:99be:9852:d542:a979"), suite.tlv.OriginatorAddress)
	suite.Assert().Equal(uint32(2), suite.tlv.Discriminator)
}

func (suite *srPolicyCandidatePathIDTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02, 0x03}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x39, 0x00, 0x1c}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x39, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x38, 0x00, 0x1c,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00,
	}))
}

func (suite *srPolicyCandidatePathIDTLVSuite) TestSerialize() {
	suite.tlv = SRPolicyCandidatePathIDTLV{
		OriginatorAddress: net.ParseIP("::"),
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x39, 0x00, 0x1c,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00,
		},
		raw,
	)

	suite.tlv = SRPolicyCandidatePathIDTLV{
		ProtocolOrigin:    13,
		OriginatorASN:     53,
		OriginatorAddress: net.ParseIP("dc35:05f1:a23e:128a:99be:9852:d542:a979"),
		Discriminator:     2,
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x39, 0x00, 0x1c,
			0x0d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x35, 0xdc,
			0x35, 0x05, 0xf1, 0xa2, 0x3e, 0x12, 0x8a, 0x99, 0xbe,
			0x98, 0x52, 0xd5, 0x42, 0xa9, 0x79, 0x00, 0x00, 0x00,
			0x2,
		},
		raw,
	)
}

func (suite *srPolicyCandidatePathIDTLVSuite) TestSerializeError() {
	raw, err := suite.tlv.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)
}

type srPolicyCandidatePathNameTLVSuite struct {
	suite.Suite

	tlv SRPolicyCandidatePathNameTLV
}

func TestSRPolicyCandidatePathNameTLVSuite(t *testing.T) {
	suite.Run(t, new(srPolicyCandidatePathNameTLVSuite))
}

func (suite *srPolicyCandidatePathNameTLVSuite) SetupTest() {
	suite.tlv = SRPolicyCandidatePathNameTLV{}
}

func (suite *srPolicyCandidatePathNameTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *srPolicyCandidatePathNameTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{0x00, 0x3a, 0x00, 0x00}))
	suite.Assert().Equal("", suite.tlv.Name)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x3a, 0x00, 0x09,
		0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65,
	}))
	suite.Assert().Equal("test name", suite.tlv.Name)
}

func (suite *srPolicyCandidatePathNameTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x3a, 0x00, 0x09}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x3b, 0x00, 0x00}))
}

func (suite *srPolicyCandidatePathNameTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{0x00, 0x3a, 0x00, 0x00},
		raw,
	)

	suite.tlv = SRPolicyCandidatePathNameTLV{Name: "test name"}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x3a, 0x00, 0x09,
			0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

type srPolicyCandidatePathPreferenceTLVSuite struct {
	suite.Suite

	tlv SRPolicyCandidatePathPreferenceTLV
}

func TestSRPolicyCandidatePathPreferenceTLVSuite(t *testing.T) {
	suite.Run(t, new(srPolicyCandidatePathPreferenceTLVSuite))
}

func (suite *srPolicyCandidatePathPreferenceTLVSuite) SetupTest() {
	suite.tlv = SRPolicyCandidatePathPreferenceTLV{}
}

func (suite *srPolicyCandidatePathPreferenceTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *srPolicyCandidatePathPreferenceTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x3b, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().Equal(uint32(0), suite.tlv.Preference)

	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x3b, 0x00, 0x04,
		0x00, 0x00, 0x01, 0xa1,
	}))
	suite.Assert().Equal(uint32(417), suite.tlv.Preference)
}

func (suite *srPolicyCandidatePathPreferenceTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x3b, 0x00, 0x04}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x3b, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x3c, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
}

func (suite *srPolicyCandidatePathPreferenceTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x3b, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.tlv = SRPolicyCandidatePathPreferenceTLV{Preference: 417}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x3b, 0x00, 0x04,
			0x00, 0x00, 0x01, 0xa1,
		},
		raw,
	)
}

type autoBandwidthCapabilityTLVSuite struct {
	suite.Suite

	tlv AutoBandwidthCapabilityTLV
}

func TestAutoBandwidthCapabilityTLVSuite(t *testing.T) {
	suite.Run(t, new(autoBandwidthCapabilityTLVSuite))
}

func (suite *autoBandwidthCapabilityTLVSuite) SetupTest() {
	suite.tlv = AutoBandwidthCapabilityTLV{}
}

func (suite *autoBandwidthCapabilityTLVSuite) TestImplements() {
	suite.Require().Implements((*TLVInterface)(nil), &suite.tlv)
}

func (suite *autoBandwidthCapabilityTLVSuite) TestParse() {
	suite.Require().NoError(suite.tlv.Parse([]byte{
		0x00, 0x24, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
}

func (suite *autoBandwidthCapabilityTLVSuite) TestParseError() {
	suite.Require().Error(suite.tlv.Parse([]byte{}))
	suite.Require().Error(suite.tlv.Parse([]byte{0x00, 0x01, 0x02}))
	suite.Require().Error(suite.tlv.Parse([]byte{
		0x00, 0x23, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Require().Error(suite.tlv.Parse([]byte{0x00, 0x24, 0x00, 0x00}))
}

func (suite *autoBandwidthCapabilityTLVSuite) TestSerialize() {
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x24, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

type pathBindingTLVSuite struct {
	suite.Suite

	tlv PathBindingTLV
}

func TestPathBindingTLVSuite(t *testing.T) {
	suite.Run(t, new(pathBindingTLVSuite))
}

func (suite *pathBindingTLVSuite) SetupTest() {
	suite.tlv = PathBindingTLV{}
}

func (suite *pathBindingTLVSuite) TestParseMPLSLabel() {
	suite.Require().NoError(suite.tlv.Parse(
		[]byte{
			0x00, 0x37, 0x00, 0x07,
			0x00, 0x01, 0x00, 0x00, 0x00, 0x03, 0x20, 0x00,
		},
	))

	suite.Assert().Equal(BindingTypeMPLSLabel, suite.tlv.BindingType)
	suite.Assert().True(suite.tlv.Removal)
	suite.Assert().Nil(suite.tlv.MPLSStack)
	suite.Assert().Nil(suite.tlv.SRv6SID)
	suite.Assert().Nil(suite.tlv.SRv6SIDWithEndpointBehavior)
	suite.Require().NotNil(suite.tlv.MPLSLabel)
	suite.Assert().Equal(uint32(50), *suite.tlv.MPLSLabel)
}

func (suite *pathBindingTLVSuite) TestParseMPLSStack() {
	suite.Require().NoError(suite.tlv.Parse(
		[]byte{
			0x00, 0x37, 0x00, 0x08,
			0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x95, 0x2c,
		},
	))

	suite.Assert().Equal(BindingTypeMPLSStack, suite.tlv.BindingType)
	suite.Assert().True(suite.tlv.Removal)
	suite.Assert().Nil(suite.tlv.MPLSLabel)
	suite.Assert().Nil(suite.tlv.SRv6SID)
	suite.Assert().Nil(suite.tlv.SRv6SIDWithEndpointBehavior)
	suite.Require().NotNil(suite.tlv.MPLSStack)
	suite.Assert().Equal(uint32(25), suite.tlv.MPLSStack.Label)
	suite.Assert().Equal(uint8(2), suite.tlv.MPLSStack.TC)
	suite.Assert().True(suite.tlv.MPLSStack.S)
	suite.Assert().Equal(uint8(44), suite.tlv.MPLSStack.TTL)
}

func (suite *pathBindingTLVSuite) TestParseSRv6() {
	suite.Require().NoError(suite.tlv.Parse(
		[]byte{
			0x00, 0x37, 0x00, 0x14,
			0x02, 0x00, 0x00, 0x00,
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
		},
	))

	suite.Assert().Equal(BindingTypeSRv6SID, suite.tlv.BindingType)
	suite.Assert().False(suite.tlv.Removal)
	suite.Assert().Nil(suite.tlv.MPLSLabel)
	suite.Assert().Nil(suite.tlv.MPLSStack)
	suite.Assert().Nil(suite.tlv.SRv6SIDWithEndpointBehavior)
	suite.Assert().Equal(net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"), suite.tlv.SRv6SID)
}

func (suite *pathBindingTLVSuite) TestParseSRv6WithEndpointBehavior() {
	suite.Require().NoError(suite.tlv.Parse(
		[]byte{
			0x00, 0x37, 0x00, 0x1c,
			0x03, 0x00, 0x00, 0x00,
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
			0x00, 0x00, 0x00, 0x01,
			0x02, 0x03, 0x04, 0x05,
		},
	))

	suite.Assert().Equal(BindingTypeSRv6SIDWithEndpointBehavior, suite.tlv.BindingType)
	suite.Assert().False(suite.tlv.Removal)
	suite.Assert().Nil(suite.tlv.MPLSLabel)
	suite.Assert().Nil(suite.tlv.MPLSStack)
	suite.Assert().Nil(suite.tlv.SRv6SID)
	suite.Require().NotNil(suite.tlv.SRv6SIDWithEndpointBehavior)
	suite.Assert().Equal(
		net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"),
		suite.tlv.SRv6SIDWithEndpointBehavior.SID,
	)
	suite.Assert().Equal(uint16(1), suite.tlv.SRv6SIDWithEndpointBehavior.EndpointBehavior)
	suite.Assert().Equal(uint8(2), suite.tlv.SRv6SIDWithEndpointBehavior.LocatorBlockLength)
	suite.Assert().Equal(uint8(3), suite.tlv.SRv6SIDWithEndpointBehavior.LocatorNodeLength)
	suite.Assert().Equal(uint8(4), suite.tlv.SRv6SIDWithEndpointBehavior.FunctionLength)
	suite.Assert().Equal(uint8(5), suite.tlv.SRv6SIDWithEndpointBehavior.ArgumentLength)
}

func (suite *pathBindingTLVSuite) TestParseError() {
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x37, 0x00, 0x00}))
	suite.Assert().Error(suite.tlv.Parse([]byte{0x00, 0x37, 0x00, 0x07}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x37, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Assert().Error(suite.tlv.Parse([]byte{
		0x00, 0x37, 0x00, 0x06,
		0xf0, 0x00, 0x00, 0x00,
		0x00, 0x00,
	}))
}

func (suite *pathBindingTLVSuite) TestSerializeMPLSLabel() {
	label := uint32(10)
	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeMPLSLabel,
		MPLSLabel:   &label,
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x07,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xa0, 0x00,
		},
		raw,
	)

	label = 50
	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeMPLSLabel,
		Removal:     true,
		MPLSLabel:   &label,
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x07,
			0x00, 0x01, 0x00, 0x00, 0x00, 0x03, 0x20, 0x00,
		},
		raw,
	)
}

func (suite *pathBindingTLVSuite) TestSerializeMPLSStack() {
	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeMPLSStack,
		MPLSStack: &MPLSLabelStackEntry{
			Label: 20,
			TC:    1,
			S:     false,
			TTL:   13,
		},
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x08,
			0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x42, 0x0d,
		},
		raw,
	)

	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeMPLSStack,
		Removal:     true,
		MPLSStack: &MPLSLabelStackEntry{
			Label: 25,
			TC:    2,
			S:     true,
			TTL:   44,
		},
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x08,
			0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x95, 0x2c,
		},
		raw,
	)
}

func (suite *pathBindingTLVSuite) TestSerializeSRv6() {
	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeSRv6SID,
		SRv6SID:     net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"),
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x14,
			0x02, 0x00, 0x00, 0x00,
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
		},
		raw,
	)

	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeSRv6SID,
		Removal:     true,
		SRv6SID:     net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"),
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x14,
			0x02, 0x01, 0x00, 0x00,
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
		},
		raw,
	)
}

func (suite *pathBindingTLVSuite) TestSerializeSRv6WithEndpointBehavior() {
	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeSRv6SIDWithEndpointBehavior,
		SRv6SIDWithEndpointBehavior: &SRv6SIDWithEndpointBehavior{
			SID:                net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"),
			EndpointBehavior:   uint16(1),
			LocatorBlockLength: uint8(2),
			LocatorNodeLength:  uint8(3),
			FunctionLength:     uint8(4),
			ArgumentLength:     uint8(5),
		},
	}
	raw, err := suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x1c,
			0x03, 0x00, 0x00, 0x00,
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
			0x00, 0x00, 0x00, 0x01,
			0x02, 0x03, 0x04, 0x05,
		},
		raw,
	)

	suite.tlv = PathBindingTLV{
		BindingType: BindingTypeSRv6SIDWithEndpointBehavior,
		Removal:     true,
		SRv6SIDWithEndpointBehavior: &SRv6SIDWithEndpointBehavior{
			SID:                net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"),
			EndpointBehavior:   uint16(1),
			LocatorBlockLength: uint8(2),
			LocatorNodeLength:  uint8(3),
			FunctionLength:     uint8(4),
			ArgumentLength:     uint8(5),
		},
	}
	raw, err = suite.tlv.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0x00, 0x37, 0x00, 0x1c,
			0x03, 0x01, 0x00, 0x00,
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
			0x00, 0x00, 0x00, 0x01,
			0x02, 0x03, 0x04, 0x05,
		},
		raw,
	)
}

func (suite *pathBindingTLVSuite) TestSerializeError() {
	var raw []byte
	var err error
	for _, t := range []BindingType{
		BindingTypeMPLSLabel,
		BindingTypeMPLSStack,
		BindingTypeSRv6SID,
		BindingTypeSRv6SIDWithEndpointBehavior,
		BindingType(255),
	} {
		suite.tlv = PathBindingTLV{BindingType: t}
		raw, err = suite.tlv.Serialize()
		suite.Assert().Error(err)
		suite.Assert().Nil(raw)
	}
}

type srv6SIDWithEndpointBehaviorSuite struct {
	suite.Suite

	value SRv6SIDWithEndpointBehavior
}

func TestSRv6SIDWithEndpointBehaviorSuite(t *testing.T) {
	suite.Run(t, new(srv6SIDWithEndpointBehaviorSuite))
}

func (suite *srv6SIDWithEndpointBehaviorSuite) SetupTest() {
	suite.value = SRv6SIDWithEndpointBehavior{}
}

func (suite *srv6SIDWithEndpointBehaviorSuite) TestParse() {
	suite.Require().NoError(suite.value.Parse([]byte{
		0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
		0x00, 0x00, 0x00, 0x01,
		0x02, 0x03, 0x04, 0x05,
	}))

	suite.Assert().Equal(net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"), suite.value.SID)
	suite.Assert().Equal(uint16(1), suite.value.EndpointBehavior)
	suite.Assert().Equal(uint8(2), suite.value.LocatorBlockLength)
	suite.Assert().Equal(uint8(3), suite.value.LocatorNodeLength)
	suite.Assert().Equal(uint8(4), suite.value.FunctionLength)
	suite.Assert().Equal(uint8(5), suite.value.ArgumentLength)
}

func (suite *srv6SIDWithEndpointBehaviorSuite) TestParseError() {
	suite.Assert().Error(suite.value.Parse(nil))
	suite.Assert().Error(suite.value.Parse([]byte{}))
	suite.Assert().Error(suite.value.Parse([]byte{0x00, 0x01, 0x02}))
}

func (suite *srv6SIDWithEndpointBehaviorSuite) TestSerialize() {
	suite.value = SRv6SIDWithEndpointBehavior{
		SID: net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"),
	}
	raw, err := suite.value.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
			0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)

	suite.value = SRv6SIDWithEndpointBehavior{
		SID:                net.ParseIP("eba5:2fe2:9cf9:f96e:392a:f996:7e99:812a"),
		EndpointBehavior:   uint16(1),
		LocatorBlockLength: uint8(2),
		LocatorNodeLength:  uint8(3),
		FunctionLength:     uint8(4),
		ArgumentLength:     uint8(5),
	}
	raw, err = suite.value.Serialize()
	suite.Require().NoError(err)
	suite.Assert().Equal(
		[]byte{
			0xeb, 0xa5, 0x2f, 0xe2, 0x9c, 0xf9, 0xf9, 0x6e, 0x39, 0x2a, 0xf9, 0x96, 0x7e, 0x99, 0x81, 0x2a,
			0x00, 0x00, 0x00, 0x01,
			0x02, 0x03, 0x04, 0x05,
		},
		raw,
	)
}

func (suite *srv6SIDWithEndpointBehaviorSuite) TestSerializeError() {
	raw, err := suite.value.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)

	suite.value = SRv6SIDWithEndpointBehavior{SID: []byte{0x0}}
	raw, err = suite.value.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)

	suite.value = SRv6SIDWithEndpointBehavior{SID: []byte{0x0}}
	raw, err = suite.value.Serialize()
	suite.Assert().Error(err)
	suite.Assert().Nil(raw)
}

type ciscoBindingSIDTlvSuite struct {
	suite.Suite

	value CiscoBindingSIDTLV
}

func TestCiscoBindingSIDTlvSuite(t *testing.T) {
	suite.Run(t, new(ciscoBindingSIDTlvSuite))
}

func (suite *ciscoBindingSIDTlvSuite) SetupTest() {
	suite.value = CiscoBindingSIDTLV{}
}

func (suite *ciscoBindingSIDTlvSuite) TestParse() {
	suite.Require().NoError(suite.value.Parse([]byte{
		0xff, 0xe1, 0x00, 0x06, 0x00, 0x00, 0xf4, 0x24, 0x50, 0x00, 0x00, 0x00,
	}))
	suite.Equal(uint32(1000005), suite.value.Label)
}

func (suite *ciscoBindingSIDTlvSuite) TestParseError() {
	suite.Error(suite.value.Parse(nil))
	suite.Error(suite.value.Parse([]byte{0xff, 0xe1, 0x00, 0x00}))
	suite.Error(suite.value.Parse([]byte{
		0xff, 0xe2, 0x00, 0x06, 0x00, 0x00, 0xf4, 0x24, 0x50, 0x00, 0x00, 0x00,
	}))
}

func (suite *ciscoBindingSIDTlvSuite) TestSerialize() {
	suite.value = CiscoBindingSIDTLV{Label: 1000005}
	raw, err := suite.value.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0xff, 0xe1, 0x00, 0x06, 0x00, 0x00, 0xf4, 0x24, 0x50, 0x00, 0x00, 0x00},
		raw,
	)
}

type vendorInformationTLVSuite struct {
	suite.Suite

	value VendorInformationTLV
}

func TestVendorInformationTLVSuite(t *testing.T) {
	suite.Run(t, new(vendorInformationTLVSuite))
}

func (suite *vendorInformationTLVSuite) SetupTest() {
	suite.value = VendorInformationTLV{}
}

func (suite *vendorInformationTLVSuite) TestParseCisco() {
	suite.Require().NoError(suite.value.Parse([]byte{
		0x00, 0x07, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
	}))
	suite.Equal(VendorEnterpriseNumberCisco, suite.value.EnterpriseNumber)
	suite.Nil(suite.value.EnterpriseSpecificInformation)
	suite.Require().NotNil(suite.value.Cisco)
	suite.Nil(suite.value.Cisco.PolicyColor)
	suite.Nil(suite.value.Cisco.PolicyName)
	suite.Require().NotNil(suite.value.Cisco.CandidatePathPreference)
	suite.Equal(uint32(1), suite.value.Cisco.CandidatePathPreference.Preference)
	suite.Nil(suite.value.Cisco.ProtectionConstraint)
}

func (suite *vendorInformationTLVSuite) TestParseError() {
	suite.Error(suite.value.Parse(nil))
	suite.Error(suite.value.Parse([]byte{0x00, 0x07, 0x00, 0x00}))
	suite.Error(suite.value.Parse([]byte{
		0x00, 0x08, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
	}))
}

func (suite *vendorInformationTLVSuite) TestSerialize() {
	suite.value = VendorInformationTLV{
		EnterpriseNumber: VendorEnterpriseNumberCisco,
		Cisco: &CiscoEnterpriseSpecificInformation{
			CandidatePathPreference: &CiscoCandidatePathPreferenceTLV{Preference: 1},
		},
	}
	raw, err := suite.value.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x00, 0x07, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01},
		raw,
	)
}

func (suite *vendorInformationTLVSuite) TestSerializeError() {
	suite.value = VendorInformationTLV{
		EnterpriseNumber:              VendorEnterpriseNumberCisco,
		EnterpriseSpecificInformation: make([]byte, math.MaxUint16+1),
	}
	raw, err := suite.value.Serialize()
	suite.Error(err)
	suite.Nil(raw)
}
