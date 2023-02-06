package pcep

import (
	"math"
	"net"
	"testing"

	"github.com/stretchr/testify/suite"
)

var (
	closeObject = []byte{
		0x0f, 0x10, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x03,
	}
	huaweiOpenObject = []byte{
		0x01, 0x10, 0x00, 0x2c,
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
		0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
		0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	}
	associationObject = []byte{
		0x28, 0x10, 0x00, 0x5c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, 0x01, 0x57, 0xfa, 0xea, 0xae,
		0x00, 0x1f, 0x00, 0x08, 0x00, 0x00, 0x01, 0x2c, 0x57, 0xfa, 0xea, 0xad, 0x00, 0x38, 0x00, 0x06,
		0x33, 0x32, 0x7a, 0x31, 0x5f, 0x31, 0x00, 0x00, 0x00, 0x39, 0x00, 0x1c, 0x0a, 0x00, 0x00, 0x00,
		0xfa, 0x56, 0xea, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff,
		0xac, 0x10, 0x05, 0x06, 0x00, 0x00, 0x00, 0x02, 0x00, 0x3a, 0x00, 0x06, 0x6a, 0x75, 0x6e, 0x31,
		0x5f, 0x31, 0x00, 0x00, 0x00, 0x3b, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64,
	}

	ciscoLSPObject = []byte{
		0x20, 0x10, 0x00, 0x34, 0x00, 0x00, 0x00, 0x89, 0x00, 0x11, 0x00, 0x0a, 0x4a, 0x55, 0x4e, 0x31,
		0x30, 0x37, 0x5f, 0x50, 0x4f, 0x4c, 0x00, 0x00, 0xff, 0xe1, 0x00, 0x06, 0x00, 0x00, 0xf4, 0x24,
		0x50, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x09, 0x00, 0x03, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x01,
	}

	juniperPTXRRO = []byte{
		0x08, 0x10, 0x00, 0x94, 0x01, 0x08, 0xd5, 0xb4, 0xd5, 0xd5, 0x20, 0x40, 0x03, 0x08, 0x01, 0x01,
		0x00, 0x00, 0x00, 0xb3, 0x01, 0x08, 0x57, 0xfa, 0xe4, 0x1c, 0x20, 0x20, 0x03, 0x08, 0x01, 0x01,
		0x00, 0x00, 0x00, 0xb3, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x4f, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x4e, 0x20, 0x00, 0x03, 0x08, 0x01, 0x01, 0x00, 0x02, 0x13, 0x7a, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x8a, 0x20, 0x40, 0x03, 0x08, 0x01, 0x01, 0x00, 0x00, 0x33, 0x94, 0x01, 0x08, 0x57, 0xfa,
		0xea, 0x02, 0x20, 0x20, 0x03, 0x08, 0x01, 0x01, 0x00, 0x00, 0x33, 0x94, 0x01, 0x08, 0xd5, 0xb4,
		0xd5, 0x20, 0x20, 0x00, 0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x21, 0x20, 0x00, 0x03, 0x08, 0x01, 0x01,
		0x00, 0x0e, 0xa8, 0x38, 0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x5d, 0x20, 0x40, 0x03, 0x08, 0x01, 0x01,
		0x00, 0x00, 0x00, 0x03, 0x01, 0x08, 0x8d, 0x08, 0x88, 0xef, 0x20, 0x20, 0x03, 0x08, 0x01, 0x01,
		0x00, 0x00, 0x00, 0x03,
	}
)

type objectHeaderSuite struct {
	suite.Suite

	header ObjectHeader
}

func TestObjectHeaderSuite(t *testing.T) {
	suite.Run(t, new(objectHeaderSuite))
}

func (suite *objectHeaderSuite) SetupTest() {
	suite.header = ObjectHeader{}
}

func (suite *objectHeaderSuite) TestDecode() {
	suite.Require().NoError(suite.header.decode([]byte{0x01, 0x10, 0x00, 0x2c}))
	suite.Equal(ObjectClassOpen, suite.header.Class)
	suite.Equal(uint8(1), suite.header.Type)
	suite.False(suite.header.ProcessingRule)
	suite.False(suite.header.Ignore)
	suite.Equal(uint16(44), suite.header.Length)
}

func (suite *objectHeaderSuite) TestDecodeError() {
	suite.Error(suite.header.decode(nil))
}

func (suite *objectHeaderSuite) TestParse() {
	body, err := suite.header.Parse([]byte{
		0x01, 0x10, 0x00, 0x2c,
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
		0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
		0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	})
	suite.Require().NoError(err)
	suite.NotNil(body)
	suite.Len(body, 40) // body doesn't include header
	suite.Equal(ObjectClassOpen, suite.header.Class)
	suite.Equal(uint8(1), suite.header.Type)
	suite.False(suite.header.ProcessingRule)
	suite.False(suite.header.Ignore)
	suite.Equal(uint16(44), suite.header.Length) // length does include header
}

func (suite *objectHeaderSuite) TestParseError() {
	body, err := suite.header.Parse([]byte{})
	suite.Error(err)
	suite.Nil(body)

	body, err = suite.header.Parse([]byte{0x01, 0x10, 0x00, 0x2c})
	suite.Error(err)
	suite.Nil(body)
}

func (suite *objectHeaderSuite) TestSerialize() {
	suite.header = ObjectHeader{
		Class:          ObjectClassOpen,
		Type:           1,
		ProcessingRule: true,
		Ignore:         true,
		Length:         40,
	}

	raw, err := suite.header.Serialize([]byte{
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
		0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
		0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	})
	suite.Require().NoError(err)
	suite.Require().Equal(
		[]byte{
			0x01, 0x13, 0x00, 0x2c,
			0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
			0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
			0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

func (suite *objectHeaderSuite) TestSerializeError() {
	suite.header = ObjectHeader{
		Class:  ObjectClassOpen,
		Type:   1,
		Length: 1,
	}
	raw, err := suite.header.Serialize(nil)
	suite.Error(err)
	suite.Nil(raw)
}

type openObjectSuite struct {
	suite.Suite

	object OpenObject
}

func TestOpenObjectSuite(t *testing.T) {
	suite.Run(t, new(openObjectSuite))
}

func (suite *openObjectSuite) SetupTest() {
	suite.object = OpenObject{}
}

func (suite *openObjectSuite) ParseHuawei() {
	suite.Require().NoError(suite.object.Parse(huaweiOpenObject))

	suite.Equal(ObjectClassOpen, suite.object.Class)
	suite.Equal(uint8(1), suite.object.Type)
	suite.False(suite.object.ProcessingRule)
	suite.False(suite.object.Ignore)
	suite.Equal(uint16(44), suite.object.Length)

	suite.Equal(uint8(30), suite.object.Keepalive)
	suite.Equal(uint8(120), suite.object.DeadTimer)
	suite.Equal(uint8(29), suite.object.SID)

	suite.Require().NotNil(suite.object.StatefulCapability)
	suite.True(suite.object.StatefulCapability.LSPUpdateCapability)
	suite.True(suite.object.StatefulCapability.IncludeDBVersion)
	suite.True(suite.object.StatefulCapability.LSPInstantiationCapability)
	suite.True(suite.object.StatefulCapability.TriggeredResync)
	suite.False(suite.object.StatefulCapability.DeltaLSPSyncCapability)
	suite.False(suite.object.StatefulCapability.TriggeredInitialSync)
	suite.False(suite.object.StatefulCapability.P2MPCapability)
	suite.False(suite.object.StatefulCapability.P2MPLSPUpdateCapability)
	suite.False(suite.object.StatefulCapability.P2MPLSPInstantiationCapability)
	suite.False(suite.object.StatefulCapability.LSPSchedulingCapability)
	suite.False(suite.object.StatefulCapability.PDLSPCapability)

	suite.Require().NotNil(suite.object.SRCapability)
	suite.False(suite.object.SRCapability.NAIToSidResolvingCapability)
	suite.False(suite.object.SRCapability.MSDNoLimit)
	suite.Equal(uint8(10), suite.object.SRCapability.MSD)

	suite.Nil(suite.object.PathSetupTypeCapability)
	suite.Nil(suite.object.AssociationTypeList)

	suite.Require().NotNil(suite.object.LSPDBVersion)
	suite.Equal(uint64(1), suite.object.LSPDBVersion.LSPStateDBVersionNumber)

	suite.Nil(suite.object.AutoBandwidthCapability)

	// TODO: check TLVTypeDomainID
}

func (suite *openObjectSuite) TestParseError() {
	suite.Require().Error(suite.object.Parse(nil))
	suite.Require().Error(suite.object.Parse(closeObject))
	suite.Require().Error(suite.object.Parse([]byte{
		0x01, 0x20, 0x00, 0x2c,
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
		0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
		0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	}))
	suite.Require().Error(suite.object.Parse([]byte{
		0x01, 0x10, 0x00, 0x2c,
		0x40, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
		0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
		0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	}))
}

func (suite *openObjectSuite) TestSerializeParse() {
	object := OpenObject{
		Keepalive: 10,
		DeadTimer: 20,
		SID:       30,
		StatefulCapability: &StatefulCapabilityTLV{
			LSPUpdateCapability:            true,
			IncludeDBVersion:               false,
			LSPInstantiationCapability:     true,
			TriggeredResync:                true,
			DeltaLSPSyncCapability:         false,
			TriggeredInitialSync:           false,
			P2MPCapability:                 true,
			P2MPLSPUpdateCapability:        true,
			P2MPLSPInstantiationCapability: true,
			LSPSchedulingCapability:        false,
			PDLSPCapability:                false,
		},
		SRCapability: &SRCapabilityTLV{
			NAIToSidResolvingCapability: true,
			MSDNoLimit:                  false,
			MSD:                         53,
		},
		PathSetupTypeCapability: &PathSetupTypeCapabilityTLV{
			Types: []PathSetupType{PathSetupTypeRSVP, PathSetupTypeSR, PathSetupTypeCentralController},
			SRCapability: &SRCapabilityTLV{
				NAIToSidResolvingCapability: true,
				MSDNoLimit:                  false,
				MSD:                         53,
			},
			PCECCCapability: &PCECCCapabilityTLV{
				Label: true,
			},
		},
		AssociationTypeList: &AssociationTypeListTLV{
			Types: []AssociationType{AssociationTypePolicy, AssociationTypePolicy, AssociationTypePathProtection},
		},
		LSPDBVersion: &LSPDBVersionTLV{
			LSPStateDBVersionNumber: 77,
		},
		AutoBandwidthCapability: &AutoBandwidthCapabilityTLV{},
	}

	raw, err := object.Serialize()
	suite.Require().NoError(err)
	suite.Require().NotNil(raw)

	suite.Require().NoError(suite.object.Parse(raw))
	suite.Equal(uint8(10), suite.object.Keepalive)
	suite.Equal(uint8(20), suite.object.DeadTimer)
	suite.Equal(uint8(30), suite.object.SID)

	suite.Require().NotNil(suite.object.StatefulCapability)
	suite.True(suite.object.StatefulCapability.LSPUpdateCapability)
	suite.False(suite.object.StatefulCapability.IncludeDBVersion)
	suite.True(suite.object.StatefulCapability.LSPInstantiationCapability)
	suite.True(suite.object.StatefulCapability.TriggeredResync)
	suite.False(suite.object.StatefulCapability.DeltaLSPSyncCapability)
	suite.True(suite.object.StatefulCapability.P2MPCapability)
	suite.True(suite.object.StatefulCapability.P2MPLSPUpdateCapability)
	suite.True(suite.object.StatefulCapability.P2MPLSPInstantiationCapability)
	suite.False(suite.object.StatefulCapability.LSPSchedulingCapability)
	suite.False(suite.object.StatefulCapability.PDLSPCapability)

	suite.Require().NotNil(suite.object.SRCapability)
	suite.True(suite.object.SRCapability.NAIToSidResolvingCapability)
	suite.False(suite.object.SRCapability.MSDNoLimit)
	suite.Equal(uint8(53), suite.object.SRCapability.MSD)

	suite.Require().NotNil(suite.object.PathSetupTypeCapability)
	suite.Equal(
		[]PathSetupType{PathSetupTypeRSVP, PathSetupTypeSR, PathSetupTypeCentralController},
		suite.object.PathSetupTypeCapability.Types,
	)
	suite.Require().NotNil(suite.object.PathSetupTypeCapability.SRCapability)
	suite.True(suite.object.PathSetupTypeCapability.SRCapability.NAIToSidResolvingCapability)
	suite.False(suite.object.PathSetupTypeCapability.SRCapability.MSDNoLimit)
	suite.Equal(uint8(53), suite.object.PathSetupTypeCapability.SRCapability.MSD)
	suite.Require().NotNil(suite.object.PathSetupTypeCapability.PCECCCapability)
	suite.True(suite.object.PathSetupTypeCapability.PCECCCapability.Label)

	suite.Require().NotNil(suite.object.AssociationTypeList)
	suite.Equal(
		[]AssociationType{AssociationTypePolicy, AssociationTypePolicy, AssociationTypePathProtection},
		suite.object.AssociationTypeList.Types,
	)

	suite.Require().NotNil(suite.object.LSPDBVersion)
	suite.Equal(uint64(77), suite.object.LSPDBVersion.LSPStateDBVersionNumber)

	suite.Require().NotNil(suite.object.AutoBandwidthCapability)
}

type endpointsObjectSuite struct {
	suite.Suite

	object EndpointsObject
}

func TestEndpointsObjectSuite(t *testing.T) {
	suite.Run(t, new(endpointsObjectSuite))
}

func (suite *endpointsObjectSuite) SetupTest() {
	suite.object = EndpointsObject{}
}

func (suite *endpointsObjectSuite) TestParseIPv4() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x04, 0x10, 0x00, 0x0c,
		0xac, 0x10, 0x06, 0x46, 0x57, 0xfa, 0xea, 0xad,
	}))
	suite.Equal(EndpointsTypeIPv4Addresses, suite.object.Type)
	suite.Equal(net.ParseIP("172.16.6.70").To4(), suite.object.Source)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), suite.object.Destination)
}

func (suite *endpointsObjectSuite) TestParseIPv6() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x04, 0x20, 0x00, 0x24,
		0xc3, 0x91, 0xa5, 0xdc, 0x79, 0xad, 0xe4, 0xac, 0xa7, 0x9a, 0x72, 0xa, 0x72, 0x8c, 0x22, 0xae,
		0xd1, 0xf1, 0xf2, 0x15, 0x5d, 0x47, 0x2b, 0xfb, 0xb4, 0xee, 0x54, 0xd, 0xd8, 0xa4, 0x78, 0xf8,
	}))
	suite.Equal(EndpointsTypeIPv6Addresses, suite.object.Type)
	suite.Equal(net.ParseIP("c391:a5dc:79ad:e4ac:a79a:720a:728c:22ae"), suite.object.Source)
	suite.Equal(net.ParseIP("d1f1:f215:5d47:2bfb:b4ee:540d:d8a4:78f8"), suite.object.Destination)
}

func (suite *endpointsObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{
		0x04, 0x10, 0x00, 0x24,
		0xc3, 0x91, 0xa5, 0xdc, 0x79, 0xad, 0xe4, 0xac, 0xa7, 0x9a, 0x72, 0xa, 0x72, 0x8c, 0x22, 0xae,
		0xd1, 0xf1, 0xf2, 0x15, 0x5d, 0x47, 0x2b, 0xfb, 0xb4, 0xee, 0x54, 0xd, 0xd8, 0xa4, 0x78, 0xf8,
	}))
	suite.Error(suite.object.Parse([]byte{
		0x04, 0x20, 0x00, 0x0c,
		0xac, 0x10, 0x06, 0x46, 0x57, 0xfa, 0xea, 0xad,
	}))
	suite.Error(suite.object.Parse([]byte{
		0x04, 0x30, 0x00, 0x0c,
		0xac, 0x10, 0x06, 0x46, 0x57, 0xfa, 0xea, 0xad,
	}))
}

func (suite *endpointsObjectSuite) TestSerializeIPv4() {
	suite.object = EndpointsObject{
		Type:        EndpointsTypeIPv4Addresses,
		Source:      net.ParseIP("172.16.6.70"),
		Destination: net.ParseIP("87.250.234.173"),
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x04, 0x10, 0x00, 0x0c,
			0xac, 0x10, 0x06, 0x46,
			0x57, 0xfa, 0xea, 0xad,
		},
		raw,
	)
}

func (suite *endpointsObjectSuite) TestSerializeIPv6() {
	suite.object = EndpointsObject{
		Type:        EndpointsTypeIPv6Addresses,
		Source:      net.ParseIP("c391:a5dc:79ad:e4ac:a79a:720a:728c:22ae"),
		Destination: net.ParseIP("d1f1:f215:5d47:2bfb:b4ee:540d:d8a4:78f8"),
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x04, 0x20, 0x00, 0x24,
			0xc3, 0x91, 0xa5, 0xdc, 0x79, 0xad, 0xe4, 0xac, 0xa7, 0x9a, 0x72, 0xa, 0x72, 0x8c, 0x22, 0xae,
			0xd1, 0xf1, 0xf2, 0x15, 0x5d, 0x47, 0x2b, 0xfb, 0xb4, 0xee, 0x54, 0xd, 0xd8, 0xa4, 0x78, 0xf8,
		},
		raw,
	)
}

func (suite *endpointsObjectSuite) TestSerializeError() {
	suite.object = EndpointsObject{Type: EndpointsTypeIPv4}
	raw, err := suite.object.Serialize()
	suite.Error(err)
	suite.Nil(raw)

	suite.object = EndpointsObject{
		Type:        EndpointsTypeIPv4Addresses,
		Source:      net.ParseIP("c391:a5dc:79ad:e4ac:a79a:720a:728c:22ae"),
		Destination: net.ParseIP("d1f1:f215:5d47:2bfb:b4ee:540d:d8a4:78f8"),
	}
	raw, err = suite.object.Serialize()
	suite.Error(err)
	suite.Nil(raw)

	suite.object = EndpointsObject{
		Type:        EndpointsTypeIPv4Addresses,
		Source:      net.ParseIP("172.16.6.70"),
		Destination: net.ParseIP("d1f1:f215:5d47:2bfb:b4ee:540d:d8a4:78f8"),
	}
	raw, err = suite.object.Serialize()
	suite.Error(err)
	suite.Nil(raw)
}

type bandwidthObjectSuite struct {
	suite.Suite

	object BandwidthObject
}

func TestBandwidthObjectSuite(t *testing.T) {
	suite.Run(t, new(bandwidthObjectSuite))
}

func (suite *bandwidthObjectSuite) SetupTest() {
	suite.object = BandwidthObject{}
}

func (suite *bandwidthObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x05, 0x20, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Equal(BandwidthTypeExisting, suite.object.Type)
	suite.Equal(uint32(0), suite.object.Bandwidth)
	suite.Empty(suite.object.SpecType)
	suite.Empty(suite.object.GeneralizedBandwidth)
	suite.Empty(suite.object.ReverseGeneralizedBandwidth)
}

func (suite *bandwidthObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{
		0x05, 0x20, 0x00, 0x0a,
		0x00, 0x00, 0x00, 0x00,
		0x00, 0x00,
	}))
}

func (suite *bandwidthObjectSuite) TestSerialize() {
	suite.object = BandwidthObject{
		Type:      BandwidthTypeExisting,
		Bandwidth: 0,
	}

	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x05, 0x20, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

func (suite *bandwidthObjectSuite) TestSerializeError() {
	suite.object = BandwidthObject{Type: BandwidthType(100)}
	raw, err := suite.object.Serialize()
	suite.Error(err)
	suite.Nil(raw)
}

type metricObjectSuite struct {
	suite.Suite

	object MetricObject
}

func TestMetricObjectSuite(t *testing.T) {
	suite.Run(t, new(metricObjectSuite))
}

func (suite *metricObjectSuite) SetupTest() {
	suite.object = MetricObject{}
}

func (suite *metricObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00,
	}))
	suite.False(suite.object.Bound)
	suite.False(suite.object.ComputedMetric)
	suite.Equal(MetricTypeTE, suite.object.Type)
	suite.Equal(float32(0), suite.object.Value)
}

func (suite *metricObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{
		0x06, 0x10, 0x00, 0x0d, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
	}))
}

func (suite *metricObjectSuite) TestSerialize() {
	suite.object = MetricObject{
		Bound:          true,
		ComputedMetric: true,
		Type:           MetricTypeTE,
		Value:          10,
	}

	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x03, 0x02, 0x41, 0x20, 0x00, 0x00},
		raw,
	)
}

type explicitRouteObjectSuite struct {
	suite.Suite

	object ExplicitRouteObject
}

func TestExplicitRouteObjectSuite(t *testing.T) {
	suite.Run(t, new(explicitRouteObjectSuite))
}

func (suite *explicitRouteObjectSuite) SetupTest() {
	suite.object = ExplicitRouteObject{}
}

func (suite *explicitRouteObjectSuite) TestParse() {
	suite.NoError(suite.object.Parse([]byte{
		0x07, 0x10, 0x00, 0x44, 0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x27, 0x20, 0x00, 0x01, 0x08, 0xd5, 0xb4,
		0xd5, 0x26, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x81, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x80, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x62, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x63, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x18, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x19, 0x20, 0x00,
	}))
	suite.Require().Len(suite.object.SubObjects, 8)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[0])
	ip := suite.object.SubObjects[0].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.39").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[1])
	ip = suite.object.SubObjects[1].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.38").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[2])
	ip = suite.object.SubObjects[2].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.129").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[3])
	ip = suite.object.SubObjects[3].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.128").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[4])
	ip = suite.object.SubObjects[4].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.98").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[5])
	ip = suite.object.SubObjects[5].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.99").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[6])
	ip = suite.object.SubObjects[6].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.24").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[7])
	ip = suite.object.SubObjects[7].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.25").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)
}

func (suite *explicitRouteObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x07, 0x20, 0x00, 0x04}))
	suite.Error(suite.object.Parse([]byte{0x07, 0x10, 0x00, 0x06, 0x00, 0x00}))
}

func (suite *explicitRouteObjectSuite) TestSerializeEmpty() {
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x07, 0x10, 0x00, 0x04},
		raw,
	)
}

func (suite *explicitRouteObjectSuite) TestSerializeIPv4() {
	suite.object = ExplicitRouteObject{
		SubObjects: []RouteSubObjectInterface{
			&RouteSubObjectIPv4{
				Loose:        true,
				Address:      net.ParseIP("127.0.0.1"),
				PrefixLength: 32,
			},
		},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x07, 0x10, 0x00, 0x0c, 0x81, 0x08, 0x7f, 0x00, 0x00, 0x01, 0x20, 0x00},
		raw,
	)
}

type recordRouteObjectSuite struct {
	suite.Suite

	object RecordRouteObject
}

func TestRecordRouteObjectSuite(t *testing.T) {
	suite.Run(t, new(recordRouteObjectSuite))
}

func (suite *recordRouteObjectSuite) SetupTest() {
	suite.object = RecordRouteObject{}
}

func (suite *recordRouteObjectSuite) TestParseIPv4Prefixes() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x08, 0x10, 0x00, 0x64, 0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x27, 0x20, 0x00, 0x01, 0x08, 0xd5, 0xb4,
		0xd5, 0x26, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xe4, 0xa8, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x81, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x80, 0x20, 0x00, 0x01, 0x08, 0x5f, 0x6c,
		0xed, 0xfd, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x62, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x63, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xe9, 0xe9, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x18, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x19, 0x20, 0x00, 0x01, 0x08, 0x8d, 0x08,
		0x88, 0xe3, 0x20, 0x00,
	}))
	suite.Require().Len(suite.object.SubObjects, 12)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[0])
	ip := suite.object.SubObjects[0].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.39").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[1])
	ip = suite.object.SubObjects[1].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.38").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[2])
	ip = suite.object.SubObjects[2].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.228.168").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[3])
	ip = suite.object.SubObjects[3].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.129").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[4])
	ip = suite.object.SubObjects[4].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.128").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[5])
	ip = suite.object.SubObjects[5].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("95.108.237.253").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[6])
	ip = suite.object.SubObjects[6].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.98").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[7])
	ip = suite.object.SubObjects[7].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.99").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[8])
	ip = suite.object.SubObjects[8].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.233.233").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[9])
	ip = suite.object.SubObjects[9].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.24").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[10])
	ip = suite.object.SubObjects[10].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.25").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[11])
	ip = suite.object.SubObjects[11].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("141.8.136.227").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)
}

func (suite *recordRouteObjectSuite) TestParseJuniperPTX() {
	suite.Require().NoError(suite.object.Parse(juniperPTXRRO))
	suite.Require().Len(suite.object.SubObjects, 18)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[0])
	ip := suite.object.SubObjects[0].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.213").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[1])
	label := suite.object.SubObjects[1].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x00, 0x00, 0xb3}, label.Label)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[2])
	ip = suite.object.SubObjects[2].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.228.28").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[3])
	label = suite.object.SubObjects[3].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x00, 0x00, 0xb3}, label.Label)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[4])
	ip = suite.object.SubObjects[4].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.79").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[5])
	ip = suite.object.SubObjects[5].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.78").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[6])
	label = suite.object.SubObjects[6].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x02, 0x13, 0x7a}, label.Label)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[7])
	ip = suite.object.SubObjects[7].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.138").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[8])
	label = suite.object.SubObjects[8].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x00, 0x33, 0x94}, label.Label)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[9])
	ip = suite.object.SubObjects[9].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.234.2").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[10])
	label = suite.object.SubObjects[10].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x00, 0x33, 0x94}, label.Label)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[11])
	ip = suite.object.SubObjects[11].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.32").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[12])
	ip = suite.object.SubObjects[12].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.33").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[13])
	label = suite.object.SubObjects[13].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x0e, 0xa8, 0x38}, label.Label)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[14])
	ip = suite.object.SubObjects[14].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("213.180.213.93").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[15])
	label = suite.object.SubObjects[15].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x00, 0x00, 0x03}, label.Label)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[16])
	ip = suite.object.SubObjects[16].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("141.8.136.239").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), suite.object.SubObjects[17])
	label = suite.object.SubObjects[17].(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x00, 0x00, 0x03}, label.Label)
}

func (suite *recordRouteObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x08, 0x20, 0x00, 0x04}))
	suite.Error(suite.object.Parse([]byte{0x08, 0x20, 0x00, 0x00}))
	suite.Error(suite.object.Parse([]byte{
		0x08, 0x10, 0x00, 0x64, 0x10, 0x08, 0xd5, 0xb4, 0xd5, 0x27, 0x20, 0x00, 0x01, 0x08, 0xd5, 0xb4,
		0xd5, 0x26, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xe4, 0xa8, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x81, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x80, 0x20, 0x00, 0x01, 0x08, 0x5f, 0x6c,
		0xed, 0xfd, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x62, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x63, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xe9, 0xe9, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x18, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x19, 0x20, 0x00, 0x01, 0x08, 0x8d, 0x08,
		0x88, 0xe3, 0x20, 0x00,
	}))
	suite.Error(suite.object.Parse([]byte{0x08, 0x10, 0x00, 0x06, 0x01, 0x02}))
	suite.Error(suite.object.Parse([]byte{0x08, 0x10, 0x00, 0x08, 0x01, 0x04, 0x00, 0x00}))
	suite.Error(suite.object.Parse([]byte{0x08, 0x10, 0x00, 0x08, 0x02, 0x04, 0x00, 0x00}))
	suite.Error(suite.object.Parse([]byte{0x08, 0x10, 0x00, 0x08, 0x04, 0x04, 0x00, 0x00}))
	suite.Error(suite.object.Parse([]byte{0x08, 0x10, 0x00, 0x08, 0x20, 0x04, 0x00, 0x00}))
}

func (suite *recordRouteObjectSuite) TestSerializeEmpty() {
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x08, 0x10, 0x00, 0x04},
		raw,
	)
}

func (suite *recordRouteObjectSuite) TestSerializeIPv4() {
	suite.object = RecordRouteObject{
		SubObjects: []RouteSubObjectInterface{
			&RouteSubObjectIPv4{
				Loose:        true,
				Address:      net.ParseIP("127.0.0.1"),
				PrefixLength: 32,
			},
		},
	}

	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x08, 0x10, 0x00, 0x0c, 0x81, 0x08, 0x7f, 0x00, 0x00, 0x01, 0x20, 0x00},
		raw,
	)
}

type lspAttributesObjectSuite struct {
	suite.Suite

	object LSPAttributesObject
}

func TestLSPAttributesObjectSuite(t *testing.T) {
	suite.Run(t, new(lspAttributesObjectSuite))
}

func (suite *lspAttributesObjectSuite) SetupTest() {
	suite.object = LSPAttributesObject{}
}

func (suite *lspAttributesObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x09, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Equal(uint32(0), suite.object.ExcludeAny)
	suite.Equal(uint32(0), suite.object.IncludeAny)
	suite.Equal(uint32(0), suite.object.IncludeAll)
	suite.Equal(uint8(0), suite.object.SetupPriority)
	suite.Equal(uint8(0), suite.object.HoldingPriority)
	suite.False(suite.object.LocalProtectionDesired)
}

func (suite *lspAttributesObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x09, 0x20, 0x00, 0x04}))
	suite.Error(suite.object.Parse([]byte{0x09, 0x10, 0x00, 0x04}))
}

func (suite *lspAttributesObjectSuite) TestSerialize() {
	suite.object = LSPAttributesObject{
		ExcludeAny:             1,
		IncludeAny:             2,
		IncludeAll:             3,
		SetupPriority:          4,
		HoldingPriority:        5,
		LocalProtectionDesired: true,
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x09, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00,
			0x03, 0x04, 0x05, 0x01, 0x00,
		},
		raw,
	)

	suite.object = LSPAttributesObject{}
	suite.Require().NoError(suite.object.Parse(raw))
	suite.Equal(uint32(1), suite.object.ExcludeAny)
	suite.Equal(uint32(2), suite.object.IncludeAny)
	suite.Equal(uint32(3), suite.object.IncludeAll)
	suite.Equal(uint8(4), suite.object.SetupPriority)
	suite.Equal(uint8(5), suite.object.HoldingPriority)
	suite.True(suite.object.LocalProtectionDesired)
}

type includeRouteObjectSuite struct {
	suite.Suite

	object IncludeRouteObject
}

func TestIncludeRouteObjectSuite(t *testing.T) {
	suite.Run(t, new(includeRouteObjectSuite))
}

func (suite *includeRouteObjectSuite) SetupTest() {
	suite.object = IncludeRouteObject{}
}

func (suite *includeRouteObjectSuite) TestParseEmpty() {
	suite.Require().NoError(suite.object.Parse([]byte{0x0a, 0x10, 0x00, 0x04}))
	suite.Require().Empty(suite.object.SubObjects)
}

func (suite *includeRouteObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x0a, 0x10, 0x00, 0x1c, 0x81, 0x08, 0x57, 0xfa, 0xe9, 0xe9, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x19, 0x20, 0x00, 0x01, 0x08, 0x8d, 0x08, 0x88, 0xe3, 0x20, 0x00,
	}))
	suite.Require().Len(suite.object.SubObjects, 3)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[0])
	ip := suite.object.SubObjects[0].(*RouteSubObjectIPv4)
	suite.True(ip.Loose)
	suite.Equal(net.ParseIP("87.250.233.233").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[1])
	ip = suite.object.SubObjects[1].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("87.250.239.25").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), suite.object.SubObjects[2])
	ip = suite.object.SubObjects[2].(*RouteSubObjectIPv4)
	suite.False(ip.Loose)
	suite.Equal(net.ParseIP("141.8.136.227").To4(), ip.Address)
	suite.Equal(uint8(32), ip.PrefixLength)
}

func (suite *includeRouteObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x0a, 0x20, 0x00, 0x04}))
}

func (suite *includeRouteObjectSuite) TestSerialize() {
	suite.object = IncludeRouteObject{
		SubObjects: []RouteSubObjectInterface{
			&RouteSubObjectIPv4{
				Loose:        true,
				Address:      net.ParseIP("87.250.233.233"),
				PrefixLength: 32,
			},
			&RouteSubObjectIPv4{
				Address:      net.ParseIP("87.250.239.25"),
				PrefixLength: 32,
			},
			&RouteSubObjectIPv4{
				Address:      net.ParseIP("141.8.136.227"),
				PrefixLength: 32,
			},
		},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x0a, 0x10, 0x00, 0x1c, 0x81, 0x08, 0x57, 0xfa, 0xe9, 0xe9, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
			0xef, 0x19, 0x20, 0x00, 0x01, 0x08, 0x8d, 0x08, 0x88, 0xe3, 0x20, 0x00,
		},
		raw,
	)
}

type errorObjectSuite struct {
	suite.Suite

	object ErrorObject
}

func TestErrorObjectSuite(t *testing.T) {
	suite.Run(t, new(errorObjectSuite))
}

func (suite *errorObjectSuite) SetupTest() {
	suite.object = ErrorObject{}
}

func (suite *errorObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x0d, 0x00, 0x00, 0x08,
		0x00, 0x00, 0x02, 0x00,
	}))

	suite.Equal(ErrorTypeCapabilityNotSupported, suite.object.Type)
	suite.Equal(ErrorValue(0), suite.object.Value)
}

func (suite *errorObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
}

func (suite *errorObjectSuite) TestSerialize() {
	suite.object = ErrorObject{
		Type:  ErrorTypeBadParameterValue,
		Value: ErrorValueRROMissing,
	}

	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x0d, 0x00, 0x00, 0x08,
			0x00, 0x00, 0x17, 0x02,
		},
		raw,
	)
}

type closeObjectSuite struct {
	suite.Suite

	object CloseObject
}

func TestCloseObjectSuite(t *testing.T) {
	suite.Run(t, new(closeObjectSuite))
}

func (suite *closeObjectSuite) SetupTest() {
	suite.object = CloseObject{}
}

func (suite *closeObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse(closeObject))
	suite.Equal(CloseReasonMalformedPCEPMessage, suite.object.Reason)
}

func (suite *closeObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(huaweiOpenObject))
	suite.Error(suite.object.Parse([]byte{0x0f, 0x20, 0x00, 0x08, 0x00, 0x00, 0x00, 0x03}))
	suite.Error(suite.object.Parse([]byte{0x0f, 0x10, 0x00, 0x04}))
}

func (suite *closeObjectSuite) TestSerialize() {
	suite.object = CloseObject{Reason: CloseReasonDeadTimerExpired}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x0f, 0x10, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x02,
		},
		raw,
	)
}

type lspObjectSuite struct {
	suite.Suite

	object LSPObject
}

func TestLSPObjectSuite(t *testing.T) {
	suite.Run(t, new(lspObjectSuite))
}

func (suite *lspObjectSuite) SetupTest() {
	suite.object = LSPObject{}
}

func (suite *lspObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x20, 0x10, 0x00, 0x3c, 0x00, 0x4a, 0x50, 0x0a, 0x00, 0x11, 0x00, 0x1c, 0x73, 0x74, 0x61, 0x74,
		0x69, 0x63, 0x5f, 0x6c, 0x73, 0x70, 0x5f, 0x70, 0x61, 0x74, 0x68, 0x5f, 0x31, 0x2f, 0x73, 0x74,
		0x61, 0x74, 0x69, 0x63, 0x5f, 0x6c, 0x73, 0x70, 0x00, 0x12, 0x00, 0x10, 0x0a, 0xff, 0x00, 0x17,
		0x00, 0x00, 0x04, 0x63, 0x0a, 0xff, 0x00, 0x17, 0x57, 0xfa, 0xea, 0xad,
	}))
	suite.Equal(uint32(1189), suite.object.ID)
	suite.False(suite.object.Delegate)
	suite.True(suite.object.Sync)
	suite.False(suite.object.Remove)
	suite.True(suite.object.Administrative)
	suite.Equal(LSPOperationalDown, suite.object.Operational)
	suite.False(suite.object.Create)
	suite.False(suite.object.P2MP)
	suite.False(suite.object.Fragmentation)
	suite.False(suite.object.EROCompression)
	suite.False(suite.object.AllocatedBindingLabelSID)
	suite.Require().NotNil(suite.object.IPv4Identifiers)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), suite.object.IPv4Identifiers.TunnelSenderAddress)
	suite.Equal(uint16(0), suite.object.IPv4Identifiers.LSPID)
	suite.Equal(uint16(1123), suite.object.IPv4Identifiers.TunnelID)
	suite.Equal(uint32(184483863), suite.object.IPv4Identifiers.ExtendedTunnelID)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), suite.object.IPv4Identifiers.TunnelEndpointAddress)
	suite.Nil(suite.object.IPv6Identifiers)
	suite.Require().NotNil(suite.object.SymbolicPathName)
	suite.Equal("static_lsp_path_1/static_lsp", suite.object.SymbolicPathName.Name)
	suite.Nil(suite.object.LSPErrorCode)
	suite.Nil(suite.object.PathBinding)
}

func (suite *lspObjectSuite) TestParseCisco() {
	suite.Require().NoError(suite.object.Parse(ciscoLSPObject))
	suite.Equal(uint32(0), suite.object.ID)
	suite.True(suite.object.Delegate)
	suite.False(suite.object.Sync)
	suite.False(suite.object.Remove)
	suite.True(suite.object.Administrative)
	suite.Equal(LSPOperationalDown, suite.object.Operational)
	suite.True(suite.object.Create)
	suite.False(suite.object.P2MP)
	suite.False(suite.object.Fragmentation)
	suite.False(suite.object.EROCompression)
	suite.False(suite.object.AllocatedBindingLabelSID)
	suite.Nil(suite.object.IPv4Identifiers)
	suite.Nil(suite.object.IPv6Identifiers)
	suite.Require().NotNil(suite.object.SymbolicPathName)
	suite.Equal("JUN107_POL", suite.object.SymbolicPathName.Name)
	suite.Nil(suite.object.LSPErrorCode)
	suite.Nil(suite.object.PathBinding)
	suite.Require().NotNil(suite.object.CiscoBSID)
	suite.Equal(uint32(1000005), suite.object.CiscoBSID.Label)
}

func (suite *lspObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x20, 0x20, 0x00, 0x04}))
	suite.Error(suite.object.Parse([]byte{0x20, 0x10, 0x00, 0x04}))
}

func (suite *lspObjectSuite) TestSerialize() {
	suite.object = LSPObject{
		ID:             1189,
		Sync:           true,
		Administrative: true,
		IPv4Identifiers: &IPv4LSPIdentifiersTLV{
			TunnelSenderAddress:   net.ParseIP("10.255.0.23"),
			TunnelID:              1123,
			ExtendedTunnelID:      184483863,
			TunnelEndpointAddress: net.ParseIP("87.250.234.173"),
		},
		SymbolicPathName: &SymbolicPathNameTLV{Name: "static_lsp_path_1/static_lsp"},
		CiscoBSID:        &CiscoBindingSIDTLV{Label: 100500},
		VendorInformation: &VendorInformationTLV{
			EnterpriseNumber:              10,
			EnterpriseSpecificInformation: []byte{0x01, 0x02, 0x03, 0x04},
		},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x10, 0x00, 0x54, 0x00, 0x4a, 0x50, 0x0a, 0x00, 0x12, 0x00, 0x10, 0x0a, 0xff, 0x00, 0x17,
			0x00, 0x00, 0x04, 0x63, 0x0a, 0xff, 0x00, 0x17, 0x57, 0xfa, 0xea, 0xad, 0x00, 0x11, 0x00, 0x1c,
			0x73, 0x74, 0x61, 0x74, 0x69, 0x63, 0x5f, 0x6c, 0x73, 0x70, 0x5f, 0x70, 0x61, 0x74, 0x68, 0x5f,
			0x31, 0x2f, 0x73, 0x74, 0x61, 0x74, 0x69, 0x63, 0x5f, 0x6c, 0x73, 0x70, 0xff, 0xe1, 0x00, 0x06,
			0x00, 0x00, 0x18, 0x89, 0x40, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00, 0x08, 0x00, 0x00, 0x00, 0x0a,
			0x01, 0x02, 0x03, 0x04,
		},
		raw,
	)
}

type srpObjectSuite struct {
	suite.Suite

	object SRPObject
}

func TestSRPObjectSuite(t *testing.T) {
	suite.Run(t, new(srpObjectSuite))
}

func (suite *srpObjectSuite) SetupTest() {
	suite.object = SRPObject{}
}

func (suite *srpObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{
		0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1c, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x01,
	}))
	suite.False(suite.object.Remove)
	suite.Equal(uint32(0), suite.object.ID)
	suite.Require().NotNil(suite.object.PathSetupType)
	suite.Equal(PathSetupTypeSR, suite.object.PathSetupType.Type)
}

func (suite *srpObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x21, 0x20, 0x00, 0x04}))
	suite.Error(suite.object.Parse([]byte{0x21, 0x10, 0x00, 0x04}))
}

func (suite *srpObjectSuite) TestSerialize() {
	suite.object = SRPObject{
		Remove: true,
		ID:     100,
		PathSetupType: &PathSetupTypeTLV{
			Type: PathSetupTypeRSVP,
		},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x64, 0x00, 0x1c, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

type vendorInformationObjectSuite struct {
	suite.Suite

	object VendorInformationObject
}

func TestVendorInformationObjectSuite(t *testing.T) {
	suite.Run(t, new(vendorInformationObjectSuite))
}

func (suite *vendorInformationObjectSuite) SetupTest() {
	suite.object = VendorInformationObject{}
}

func (suite *vendorInformationObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse([]byte{0x22, 0x10, 0x00, 0x0b, 0x00, 0x01, 0x88, 0x94, 0x00, 0x01, 0x02}))
	suite.Equal(VendorEnterpriseNumber(100500), suite.object.EnterpriseNumber)
	suite.Equal([]byte{0x00, 0x01, 0x02}, suite.object.EnterpriseSpecificInformation)
}

func (suite *vendorInformationObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x22, 0x20, 0x00, 0x04}))
	suite.Error(suite.object.Parse([]byte{0x22, 0x10, 0x00, 0x04}))
}

func (suite *vendorInformationObjectSuite) TestSerialize() {
	suite.object = VendorInformationObject{
		EnterpriseNumber:              100500,
		EnterpriseSpecificInformation: []byte{0x00, 0x01, 0x02},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x22, 0x10, 0x00, 0x0b, 0x00, 0x01, 0x88, 0x94, 0x00, 0x01, 0x02},
		raw,
	)
}

type associationObjectSuite struct {
	suite.Suite

	object AssociationObject
}

func TestAssociationObjectSuite(t *testing.T) {
	suite.Run(t, new(associationObjectSuite))
}

func (suite *associationObjectSuite) SetupTest() {
	suite.object = AssociationObject{}
}

func (suite *associationObjectSuite) TestParse() {
	suite.Require().NoError(suite.object.Parse(associationObject))
	suite.Equal(AssociationObjectTypeIPv4, suite.object.Type)
	suite.False(suite.object.Removal)
	suite.Equal(AssociationTypeSRPolicy, suite.object.AssociationType)
	suite.Equal(uint16(1), suite.object.ID)
	suite.Equal(net.ParseIP("87.250.234.174").To4(), suite.object.Source)
	suite.Nil(suite.object.GlobalSource)
	suite.Nil(suite.object.ExtendedID)
	suite.Require().NotNil(suite.object.SRExtendedID)
	suite.Equal(uint32(300), suite.object.SRExtendedID.Color)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), suite.object.SRExtendedID.Endpoint)
	suite.Nil(suite.object.JuniperSRPolicyID)
	suite.Require().NotNil(suite.object.SRPolicyName)
	suite.Equal("32z1_1", suite.object.SRPolicyName.Name)
	suite.Require().NotNil(suite.object.SRPolicyCandidatePathID)
	suite.Equal(uint8(10), suite.object.SRPolicyCandidatePathID.ProtocolOrigin)
	suite.Equal(uint32(4200000002), suite.object.SRPolicyCandidatePathID.OriginatorASN)
	suite.Equal(net.ParseIP("172.16.5.6"), suite.object.SRPolicyCandidatePathID.OriginatorAddress)
	suite.Equal(uint32(2), suite.object.SRPolicyCandidatePathID.Discriminator)
	suite.Require().NotNil(suite.object.SRPolicyCandidatePathName)
	suite.Equal("jun1_1", suite.object.SRPolicyCandidatePathName.Name)
	suite.Require().NotNil(suite.object.SRPolicyCandidatePathPreference)
	suite.Equal(uint32(100), suite.object.SRPolicyCandidatePathPreference.Preference)
}

func (suite *associationObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
	suite.Error(suite.object.Parse(closeObject))
	suite.Error(suite.object.Parse([]byte{0x28, 0x10, 0x00, 0x04}))
	suite.Error(suite.object.Parse([]byte{
		0x28, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00,
	}))
}

func (suite *associationObjectSuite) TestSerialize() {
	suite.object = AssociationObject{
		Type:            AssociationObjectTypeIPv4,
		Removal:         false,
		AssociationType: AssociationTypeSRPolicy,
		ID:              1,
		Source:          net.ParseIP("87.250.234.174"),
		SRExtendedID: &SRExtendedAssociationIDTLV{
			Color:    300,
			Endpoint: net.ParseIP("87.250.234.173"),
		},
		SRPolicyName: &SRPolicyNameTLV{
			Name: "32z1_1",
		},
		SRPolicyCandidatePathID: &SRPolicyCandidatePathIDTLV{
			ProtocolOrigin:    10,
			OriginatorASN:     4200000002,
			OriginatorAddress: net.ParseIP("172.16.5.6"),
			Discriminator:     2,
		},
		SRPolicyCandidatePathName: &SRPolicyCandidatePathNameTLV{
			Name: "jun1_1",
		},
		SRPolicyCandidatePathPreference: &SRPolicyCandidatePathPreferenceTLV{
			Preference: 100,
		},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(
		associationObject,
		raw,
	)
}

type unknownObjectSuite struct {
	suite.Suite

	object UnknownObject
}

func TestUnknownObjectSuite(t *testing.T) {
	suite.Run(t, new(unknownObjectSuite))
}

func (suite *unknownObjectSuite) SetupTest() {
	suite.object = UnknownObject{}
}

func (suite *unknownObjectSuite) TestParseOpen() {
	suite.Require().NoError(suite.object.Parse(huaweiOpenObject))
	suite.Equal(
		[]byte{
			0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
			0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
			0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
		},
		suite.object.Data,
	)
}

func (suite *unknownObjectSuite) TestParseClose() {
	suite.Require().NoError(suite.object.Parse(closeObject))
	suite.Equal(
		[]byte{0x00, 0x00, 0x00, 0x03},
		suite.object.Data,
	)
}

func (suite *unknownObjectSuite) TestParseError() {
	suite.Error(suite.object.Parse(nil))
}

func (suite *unknownObjectSuite) TestSerializeOpen() {
	suite.object = UnknownObject{
		ObjectHeader: ObjectHeader{
			Class: ObjectClassOpen,
			Type:  1,
		},
		Data: []byte{
			0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
			0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0a,
			0x00, 0x17, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x01, 0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
		},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(huaweiOpenObject, raw)
}

func (suite *unknownObjectSuite) TestSerializeClose() {

	suite.object = UnknownObject{
		ObjectHeader: ObjectHeader{
			Class: ObjectClassClose,
			Type:  1,
		},
		Data: []byte{0x00, 0x00, 0x00, 0x03},
	}
	raw, err := suite.object.Serialize()
	suite.NoError(err)
	suite.Equal(closeObject, raw)
}

func (suite *unknownObjectSuite) TestSerializeError() {
	raw, err := suite.object.Serialize()
	suite.Error(err)
	suite.Nil(raw)

	suite.object = UnknownObject{
		ObjectHeader: ObjectHeader{Class: ObjectClassOpen},
	}
	raw, err = suite.object.Serialize()
	suite.Error(err)
	suite.Nil(raw)

	suite.object = UnknownObject{
		ObjectHeader: ObjectHeader{
			Class: ObjectClassOpen,
			Type:  1,
		},
		Data: make([]byte, math.MaxUint16+1),
	}
	raw, err = suite.object.Serialize()
	suite.Error(err)
	suite.Nil(raw)
}

type routeSubObjectSuite struct {
	suite.Suite
}

func TestRouteSubObjectSuite(t *testing.T) {
	suite.Run(t, new(routeSubObjectSuite))
}

func (suite *routeSubObjectSuite) TestParseIPv4Prefix() {
	object, err := ParseRouteSubObject([]byte{0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x27, 0x20, 0x00})
	suite.Require().NoError(err)
	suite.Require().NotNil(object)
	suite.Require().IsType((*RouteSubObjectIPv4)(nil), object)
	prefix := object.(*RouteSubObjectIPv4)
	suite.False(prefix.Loose)
	suite.Equal(net.ParseIP("213.180.213.39").To4(), prefix.Address)
	suite.Equal(uint8(32), prefix.PrefixLength)
}

func (suite *routeSubObjectSuite) TestParseLabelControl() {
	object, err := ParseRouteSubObject([]byte{0x03, 0x08, 0x01, 0x01, 0x00, 0x00, 0x00, 0xb3})
	suite.Require().NoError(err)
	suite.Require().NotNil(object)
	suite.Require().IsType((*RouteSubObjectLabelControl)(nil), object)
	label := object.(*RouteSubObjectLabelControl)
	suite.Equal(LabelDirectionDownstream, label.Direction)
	suite.True(label.GlobalLabel)
	suite.Equal(uint8(1), label.CType)
	suite.Equal([]byte{0x00, 0x00, 0x00, 0xb3}, label.Label)
}

func (suite *routeSubObjectSuite) TestParseSR() {
	object, err := ParseRouteSubObject([]byte{0x24, 0x08, 0x00, 0x09, 0x25, 0xdd, 0x20, 0x00})
	suite.Require().NoError(err)
	suite.Require().NotNil(object)
	suite.Require().IsType((*RouteSubObjectSR)(nil), object)
	sr := object.(*RouteSubObjectSR)
	suite.False(sr.Loose)
	suite.Equal(NAITypeAbsent, sr.NT)
	suite.True(sr.M)
	suite.False(sr.C)
	suite.False(sr.S)
	suite.True(sr.F)
	suite.Nil(sr.SIDIndex)
	suite.Require().NotNil(sr.SIDEntry)
	suite.Equal(uint32(155090), sr.SIDEntry.Label)
	suite.Equal(uint8(0), sr.SIDEntry.TC)
	suite.False(sr.SIDEntry.S)
	suite.Equal(uint8(0), sr.SIDEntry.TTL)
}

func (suite *routeSubObjectSuite) TestSerializeIPv4Prefix() {
	object := RouteSubObjectIPv4{
		Loose:        false,
		Address:      net.ParseIP("213.180.213.39"),
		PrefixLength: 32,
	}

	raw, err := object.Serialize()
	suite.NoError(err)
	suite.Equal([]byte{0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x27, 0x20, 0x00}, raw)
}

func (suite *routeSubObjectSuite) TestSerializeLabelControl() {
	object := RouteSubObjectLabelControl{
		Direction:   LabelDirectionUpstream,
		GlobalLabel: false,
		CType:       2,
		Label:       []byte{0x00, 0x00, 0x00, 0xb3},
	}

	raw, err := object.Serialize()
	suite.NoError(err)
	suite.Equal([]byte{0x03, 0x08, 0x80, 0x02, 0x00, 0x00, 0x00, 0xb3}, raw)
}

func (suite *routeSubObjectSuite) TestSerializeSR() {
	object := RouteSubObjectSR{
		M:        true,
		F:        true,
		SIDEntry: &MPLSLabelStackEntry{Label: 155090},
	}

	raw, err := object.Serialize()
	suite.NoError(err)
	suite.Equal([]byte{0x24, 0x08, 0x00, 0x09, 0x25, 0xdd, 0x20, 0x00}, raw)
}
