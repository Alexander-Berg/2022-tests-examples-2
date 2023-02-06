package pcep

import (
	"net"
	"testing"

	"github.com/stretchr/testify/suite"
)

type messageHeaderSuite struct {
	suite.Suite

	header MessageHeader
}

func TestMessageHeaderSuite(t *testing.T) {
	suite.Run(t, new(messageHeaderSuite))
}

func (suite *messageHeaderSuite) SetupTest() {
	suite.header = MessageHeader{}
}

func (suite *messageHeaderSuite) TestDecode() {
	suite.NoError(suite.header.decode([]byte{0x20, 0x01, 0x00, 0x30}))
	suite.Equal(MessageTypeOpen, suite.header.Type)
	suite.Equal(uint16(48), suite.header.Length)
}

func (suite *messageHeaderSuite) TestDecodeError() {
	suite.Error(suite.header.decode(nil))
	suite.Error(suite.header.decode([]byte{}))
	suite.Error(suite.header.decode([]byte{0x00, 0x00, 0x01}))
	suite.Error(suite.header.decode([]byte{0x40, 0x00, 0x00, 0x00}))
}

func (suite *messageHeaderSuite) TestParse() {
	body, err := suite.header.Parse([]byte{
		0x20, 0x01, 0x00, 0x30,
		0x01, 0x10, 0x00, 0x2c,
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0a, 0x00, 0x17, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
		0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	})
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x01, 0x10, 0x00, 0x2c,
			0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x0a, 0x00, 0x17, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
			0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
		},
		body,
	)
	suite.Equal(MessageTypeOpen, suite.header.Type)
	suite.Equal(uint16(48), suite.header.Length)
}

func (suite *messageHeaderSuite) TestParseError() {
	body, err := suite.header.Parse(nil)
	suite.Error(err)
	suite.Nil(body)

	body, err = suite.header.Parse([]byte{})
	suite.Error(err)
	suite.Nil(body)

	body, err = suite.header.Parse([]byte{0x00, 0x00, 0x00})
	suite.Error(err)
	suite.Nil(body)

	body, err = suite.header.Parse([]byte{0x20, 0x01, 0x00, 0x01})
	suite.Error(err)
	suite.Nil(body)

	body, err = suite.header.Parse([]byte{0x20, 0x01, 0x00, 0x05})
	suite.Error(err)
	suite.Nil(body)
}

func (suite *messageHeaderSuite) TestSerialize() {
	suite.header = MessageHeader{
		Type:   MessageTypeKeepalive,
		Length: 0,
	}
	raw, err := suite.header.Serialize(nil)
	suite.NoError(err)
	suite.Equal(
		[]byte{0x20, 0x02, 0x00, 0x04},
		raw,
	)

	suite.header = MessageHeader{
		Type:   MessageTypeOpen,
		Length: 44,
	}
	raw, err = suite.header.Serialize([]byte{
		0x01, 0x10, 0x00, 0x2c,
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0a, 0x00, 0x17, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
		0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	})
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x01, 0x00, 0x30,
			0x01, 0x10, 0x00, 0x2c,
			0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x0a, 0x00, 0x17, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
			0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

func (suite *messageHeaderSuite) TestSerializeError() {
	suite.header = MessageHeader{
		Type:   MessageTypeKeepalive,
		Length: 0,
	}
	raw, err := suite.header.Serialize([]byte{0x00})
	suite.Error(err)
	suite.Nil(raw)

	suite.header = MessageHeader{
		Type:   MessageTypeKeepalive,
		Length: 1,
	}
	raw, err = suite.header.Serialize(nil)
	suite.Error(err)
	suite.Nil(raw)
}

type openMessageSuite struct {
	suite.Suite

	huaweiData  []byte
	ciscoData   []byte
	juniperData []byte

	message OpenMessage
}

func TestOpenMessageSuite(t *testing.T) {
	suite.Run(t, new(openMessageSuite))
}

func (suite *openMessageSuite) SetupSuite() {
	suite.huaweiData = []byte{
		0x20, 0x01, 0x00, 0x30,
		0x01, 0x10, 0x00, 0x2c,
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0a, 0x00, 0x17, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
		0x00, 0x0e, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
	}
	suite.ciscoData = []byte{
		0x20, 0x01, 0x00, 0x24,
		0x01, 0x10, 0x00, 0x20,
		0x20, 0x1e, 0x78, 0x01, 0x00, 0x10, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x05, 0x00, 0x1a, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x09, 0x00, 0x23, 0x00, 0x02,
		0x00, 0x14, 0x00, 0x00,
	}
	suite.juniperData = []byte{
		0x20, 0x01, 0x00, 0x1c,
		0x01, 0x10, 0x00, 0x18,
		0x20, 0x1e, 0x78, 0x13, 0x00, 0x10, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x05, 0x00, 0x23, 0x00, 0x02,
		0x00, 0x01, 0x00, 0x00,
	}
}

func (suite *openMessageSuite) SetupTest() {
	suite.message = OpenMessage{}
}

func (suite *openMessageSuite) TestHuawei() {
	suite.Require().NoError(suite.message.Parse(suite.huaweiData))
	suite.Equal(MessageTypeOpen, suite.message.Type)
	suite.Equal(uint16(48), suite.message.Length)

	suite.Equal(ObjectClassOpen, suite.message.Open.Class)
	suite.Equal(uint8(1), suite.message.Open.Type)
	suite.False(suite.message.Open.ProcessingRule)
	suite.False(suite.message.Open.Ignore)
	suite.Equal(uint16(44), suite.message.Open.Length)

	suite.Equal(uint8(30), suite.message.Open.Keepalive)
	suite.Equal(uint8(120), suite.message.Open.DeadTimer)
	suite.Equal(uint8(29), suite.message.Open.SID)

	suite.Require().NotNil(suite.message.Open.StatefulCapability)
	suite.True(suite.message.Open.StatefulCapability.LSPUpdateCapability)
	suite.True(suite.message.Open.StatefulCapability.IncludeDBVersion)
	suite.True(suite.message.Open.StatefulCapability.LSPInstantiationCapability)
	suite.True(suite.message.Open.StatefulCapability.TriggeredResync)
	suite.False(suite.message.Open.StatefulCapability.DeltaLSPSyncCapability)
	suite.False(suite.message.Open.StatefulCapability.TriggeredInitialSync)
	suite.False(suite.message.Open.StatefulCapability.P2MPCapability)
	suite.False(suite.message.Open.StatefulCapability.P2MPLSPUpdateCapability)
	suite.False(suite.message.Open.StatefulCapability.P2MPLSPInstantiationCapability)
	suite.False(suite.message.Open.StatefulCapability.LSPSchedulingCapability)
	suite.False(suite.message.Open.StatefulCapability.PDLSPCapability)

	suite.Require().NotNil(suite.message.Open.SRCapability)
	suite.False(suite.message.Open.SRCapability.NAIToSidResolvingCapability)
	suite.False(suite.message.Open.SRCapability.MSDNoLimit)
	suite.Equal(uint8(10), suite.message.Open.SRCapability.MSD)

	suite.Nil(suite.message.Open.PathSetupTypeCapability)
	suite.Nil(suite.message.Open.AssociationTypeList)

	suite.Require().NotNil(suite.message.Open.LSPDBVersion)
	suite.Equal(uint64(1), suite.message.Open.LSPDBVersion.LSPStateDBVersionNumber)

	suite.Nil(suite.message.Open.AutoBandwidthCapability)

	// TODO: check TLVTypeDomainID
}

func (suite *openMessageSuite) TestCisco() {
	suite.Require().NoError(suite.message.Parse(suite.ciscoData))
	suite.Equal(MessageTypeOpen, suite.message.Type)
	suite.Equal(uint16(36), suite.message.Length)

	suite.Equal(ObjectClassOpen, suite.message.Open.Class)
	suite.Equal(uint8(1), suite.message.Open.Type)
	suite.False(suite.message.Open.ProcessingRule)
	suite.False(suite.message.Open.Ignore)
	suite.Equal(uint16(32), suite.message.Open.Length)

	suite.Equal(uint8(30), suite.message.Open.Keepalive)
	suite.Equal(uint8(120), suite.message.Open.DeadTimer)
	suite.Equal(uint8(1), suite.message.Open.SID)

	suite.Require().NotNil(suite.message.Open.StatefulCapability)
	suite.True(suite.message.Open.StatefulCapability.LSPUpdateCapability)
	suite.False(suite.message.Open.StatefulCapability.IncludeDBVersion)
	suite.True(suite.message.Open.StatefulCapability.LSPInstantiationCapability)
	suite.False(suite.message.Open.StatefulCapability.TriggeredResync)
	suite.False(suite.message.Open.StatefulCapability.DeltaLSPSyncCapability)
	suite.False(suite.message.Open.StatefulCapability.TriggeredInitialSync)
	suite.False(suite.message.Open.StatefulCapability.P2MPCapability)
	suite.False(suite.message.Open.StatefulCapability.P2MPLSPUpdateCapability)
	suite.False(suite.message.Open.StatefulCapability.P2MPLSPInstantiationCapability)
	suite.False(suite.message.Open.StatefulCapability.LSPSchedulingCapability)
	suite.False(suite.message.Open.StatefulCapability.PDLSPCapability)

	suite.Require().NotNil(suite.message.Open.SRCapability)
	suite.False(suite.message.Open.SRCapability.NAIToSidResolvingCapability)
	suite.False(suite.message.Open.SRCapability.MSDNoLimit)
	suite.Equal(uint8(9), suite.message.Open.SRCapability.MSD)

	suite.Nil(suite.message.Open.PathSetupTypeCapability)

	suite.Require().NotNil(suite.message.Open.AssociationTypeList)
	suite.Require().Len(suite.message.Open.AssociationTypeList.Types, 1)
	suite.Equal(AssociationType(20), suite.message.Open.AssociationTypeList.Types[0])

	suite.Nil(suite.message.Open.LSPDBVersion)
	suite.Nil(suite.message.Open.AutoBandwidthCapability)
}

func (suite *openMessageSuite) TestJuniper() {
	suite.Require().NoError(suite.message.Parse(suite.juniperData))
	suite.Equal(MessageTypeOpen, suite.message.Type)
	suite.Equal(uint16(28), suite.message.Length)

	suite.Equal(ObjectClassOpen, suite.message.Open.Class)
	suite.Equal(uint8(1), suite.message.Open.Type)
	suite.False(suite.message.Open.ProcessingRule)
	suite.False(suite.message.Open.Ignore)
	suite.Equal(uint16(24), suite.message.Open.Length)

	suite.Equal(uint8(30), suite.message.Open.Keepalive)
	suite.Equal(uint8(120), suite.message.Open.DeadTimer)
	suite.Equal(uint8(19), suite.message.Open.SID)

	suite.Require().NotNil(suite.message.Open.StatefulCapability)
	suite.True(suite.message.Open.StatefulCapability.LSPUpdateCapability)
	suite.False(suite.message.Open.StatefulCapability.IncludeDBVersion)
	suite.True(suite.message.Open.StatefulCapability.LSPInstantiationCapability)
	suite.False(suite.message.Open.StatefulCapability.TriggeredResync)
	suite.False(suite.message.Open.StatefulCapability.DeltaLSPSyncCapability)
	suite.False(suite.message.Open.StatefulCapability.TriggeredInitialSync)
	suite.False(suite.message.Open.StatefulCapability.P2MPCapability)
	suite.False(suite.message.Open.StatefulCapability.P2MPLSPUpdateCapability)
	suite.False(suite.message.Open.StatefulCapability.P2MPLSPInstantiationCapability)
	suite.False(suite.message.Open.StatefulCapability.LSPSchedulingCapability)
	suite.False(suite.message.Open.StatefulCapability.PDLSPCapability)

	suite.Nil(suite.message.Open.SRCapability)
	suite.Nil(suite.message.Open.PathSetupTypeCapability)

	suite.Require().NotNil(suite.message.Open.AssociationTypeList)
	suite.Require().Len(suite.message.Open.AssociationTypeList.Types, 1)
	suite.Equal(AssociationTypePathProtection, suite.message.Open.AssociationTypeList.Types[0])

	suite.Nil(suite.message.Open.LSPDBVersion)
	suite.Nil(suite.message.Open.AutoBandwidthCapability)

	// TODO: check TLVTypeDomainID
}

func (suite *openMessageSuite) TestSerialize() {
	raw, err := NewOpenMessage(10, 20, 30).Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x01, 0x00, 0x44,
			0x01, 0x10, 0x00, 0x40,
			0x20, 0x14, 0x1e, 0x0a, 0x00, 0x10, 0x00, 0x04, 0x00, 0x00,
			0x00, 0x05, 0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x01, 0x00,
			0x00, 0x22, 0x00, 0x18, 0x00, 0x00, 0x00, 0x03, 0x00, 0x01,
			0x02, 0x00, 0x00, 0x01, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
			0x00, 0x1a, 0x00, 0x04, 0x00, 0x00, 0x03, 0x00, 0x00, 0x23,
			0x00, 0x06, 0x00, 0x01, 0x00, 0x06, 0xff, 0xe1, 0x00, 0x00,
		},
		raw,
	)
}

type keepaliveMessageSuite struct {
	suite.Suite

	message KeepaliveMessage
}

func TestKeepaliveMessageSuite(t *testing.T) {
	suite.Run(t, new(keepaliveMessageSuite))
}

func (suite *keepaliveMessageSuite) SetupTest() {
	suite.message = KeepaliveMessage{}
}

func (suite *keepaliveMessageSuite) TestParse() {
	suite.Require().NoError(suite.message.Parse([]byte{0x20, 0x02, 0x00, 0x04}))
}

func (suite *keepaliveMessageSuite) TestSerialize() {
	raw, err := suite.message.Serialize()
	suite.NoError(err)
	suite.Equal([]byte{0x20, 0x02, 0x00, 0x04}, raw)
}

type errorMessageSuite struct {
	suite.Suite

	message ErrorMessage
}

func TestErrorMessageSuite(t *testing.T) {
	suite.Run(t, new(errorMessageSuite))
}

func (suite *errorMessageSuite) SetupTest() {
	suite.message = ErrorMessage{}
}

func (suite *errorMessageSuite) TestParse() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x06, 0x00, 0x0c,
		0x0d, 0x10, 0x00, 0x08, 0x00, 0x00, 0x02, 0x00,
	}))

	suite.Require().Len(suite.message.Errors, 1)

	obj := suite.message.Errors[0]
	suite.Equal(ErrorTypeCapabilityNotSupported, obj.Type)
	suite.Equal(ErrorValue(0), obj.Value)
}

type closeMessageSuite struct {
	suite.Suite

	message CloseMessage
}

func TestCloseMessageSuite(t *testing.T) {
	suite.Run(t, new(closeMessageSuite))
}

func (suite *closeMessageSuite) SetupTest() {
	suite.message = CloseMessage{}
}

func (suite *closeMessageSuite) TestParse() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x07, 0x00, 0x0c,
		0x0f, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x03,
	}))

	suite.Equal(CloseReasonMalformedPCEPMessage, suite.message.Close.Reason)
}

func (suite *closeMessageSuite) TestSerialize() {
	suite.message = CloseMessage{Close: CloseObject{Reason: CloseReasonDeadTimerExpired}}

	raw, err := suite.message.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x07, 0x00, 0x0c,
			0x0f, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x02,
		},
		raw,
	)
}

type reportMessageSuite struct {
	suite.Suite

	message ReportMessage
}

func TestReportMessageSuite(t *testing.T) {
	suite.Run(t, new(reportMessageSuite))
}

func (suite *reportMessageSuite) SetupTest() {
	suite.message = ReportMessage{}
}

func (suite *reportMessageSuite) TestParse() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x0a, 0x02, 0x60, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x3c, 0x00, 0x4a, 0x50, 0x0a,
		0x00, 0x11, 0x00, 0x1c, 0x73, 0x74, 0x61, 0x74, 0x69, 0x63, 0x5f, 0x6c, 0x73, 0x70, 0x5f, 0x70,
		0x61, 0x74, 0x68, 0x5f, 0x31, 0x2f, 0x73, 0x74, 0x61, 0x74, 0x69, 0x63, 0x5f, 0x6c, 0x73, 0x70,
		0x00, 0x12, 0x00, 0x10, 0x0a, 0xff, 0x00, 0x17, 0x00, 0x00, 0x04, 0x63, 0x0a, 0xff, 0x00, 0x17,
		0x57, 0xfa, 0xea, 0xad, 0x07, 0x10, 0x00, 0x04, 0x05, 0x20, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00,
		0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x09, 0x10, 0x00, 0x14,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x05, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x60,
		0x00, 0x62, 0x30, 0x0b, 0x00, 0x11, 0x00, 0x34, 0x73, 0x75, 0x73, 0x61, 0x6e, 0x69, 0x6e, 0x5f,
		0x73, 0x72, 0x5f, 0x70, 0x6f, 0x6c, 0x69, 0x63, 0x79, 0x5f, 0x66, 0x6f, 0x72, 0x5f, 0x70, 0x74,
		0x78, 0x5f, 0x61, 0x6e, 0x64, 0x5f, 0x6a, 0x75, 0x6e, 0x31, 0x2f, 0x74, 0x6f, 0x5f, 0x6a, 0x75,
		0x6e, 0x31, 0x5f, 0x63, 0x6f, 0x6c, 0x6f, 0x72, 0x5f, 0x33, 0x30, 0x30, 0x00, 0x12, 0x00, 0x10,
		0x0a, 0xff, 0x00, 0x17, 0x00, 0x00, 0x05, 0xde, 0x0a, 0xff, 0x00, 0x17, 0x57, 0xfa, 0xea, 0xad,
		0x00, 0x3c, 0x00, 0x06, 0x00, 0x00, 0xf4, 0x24, 0x00, 0x00, 0x00, 0x00, 0x07, 0x10, 0x00, 0x04,
		0x05, 0x20, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x02,
		0x00, 0x00, 0x00, 0x00, 0x09, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00,
		0x28, 0x10, 0x00, 0x44, 0x00, 0x00, 0x00, 0x00, 0xff, 0xe1, 0x00, 0x08, 0x0a, 0xff, 0x00, 0x17,
		0xff, 0xe3, 0x00, 0x08, 0x00, 0x00, 0x01, 0x2c, 0x57, 0xfa, 0xea, 0xad, 0xff, 0xe4, 0x00, 0x1c,
		0x1e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xe5, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x64, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x60, 0x00, 0x62, 0x30, 0x0b,
		0x00, 0x11, 0x00, 0x34, 0x73, 0x75, 0x73, 0x61, 0x6e, 0x69, 0x6e, 0x5f, 0x73, 0x72, 0x5f, 0x70,
		0x6f, 0x6c, 0x69, 0x63, 0x79, 0x5f, 0x66, 0x6f, 0x72, 0x5f, 0x70, 0x74, 0x78, 0x5f, 0x61, 0x6e,
		0x64, 0x5f, 0x6a, 0x75, 0x6e, 0x31, 0x2f, 0x74, 0x6f, 0x5f, 0x6a, 0x75, 0x6e, 0x31, 0x5f, 0x63,
		0x6f, 0x6c, 0x6f, 0x72, 0x5f, 0x33, 0x30, 0x30, 0x00, 0x12, 0x00, 0x10, 0x0a, 0xff, 0x00, 0x17,
		0x00, 0x00, 0x05, 0xde, 0x0a, 0xff, 0x00, 0x17, 0x57, 0xfa, 0xea, 0xad, 0x00, 0x3c, 0x00, 0x06,
		0x00, 0x00, 0xf4, 0x24, 0x00, 0x00, 0x00, 0x00, 0x07, 0x10, 0x00, 0x04, 0x05, 0x20, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00, 0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00,
		0x09, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x05, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x28, 0x10, 0x00, 0x44,
		0x00, 0x00, 0x00, 0x00, 0xff, 0xe1, 0x00, 0x08, 0x0a, 0xff, 0x00, 0x17, 0xff, 0xe3, 0x00, 0x08,
		0x00, 0x00, 0x01, 0x2c, 0x57, 0xfa, 0xea, 0xad, 0xff, 0xe4, 0x00, 0x1c, 0x1e, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xe5, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64,
	}))
	suite.Require().Len(suite.message.Reports, 3)

	srp := suite.message.Reports[0].SRP
	suite.Equal(uint32(0), srp.ID)
	suite.Require().NotNil(srp.PathSetupType)
	suite.Equal(PathSetupTypeSR, srp.PathSetupType.Type)

	lsp := suite.message.Reports[0].LSP
	suite.Equal(uint32(1189), lsp.ID)
	suite.False(lsp.Delegate)
	suite.True(lsp.Sync)
	suite.False(lsp.Remove)
	suite.True(lsp.Administrative)
	suite.Equal(LSPOperationalDown, lsp.Operational)
	suite.False(lsp.Create)
	suite.False(lsp.P2MP)
	suite.False(lsp.Fragmentation)
	suite.False(lsp.EROCompression)
	suite.False(lsp.AllocatedBindingLabelSID)

	suite.Require().NotNil(lsp.IPv4Identifiers)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), lsp.IPv4Identifiers.TunnelSenderAddress)
	suite.Equal(uint16(0), lsp.IPv4Identifiers.LSPID)
	suite.Equal(uint16(1123), lsp.IPv4Identifiers.TunnelID)
	suite.Equal(uint32(184483863), lsp.IPv4Identifiers.ExtendedTunnelID)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), lsp.IPv4Identifiers.TunnelEndpointAddress)

	suite.Nil(lsp.IPv6Identifiers)

	suite.Require().NotNil(lsp.SymbolicPathName)
	suite.Equal("static_lsp_path_1/static_lsp", lsp.SymbolicPathName.Name)

	suite.Nil(lsp.LSPErrorCode)
	suite.Nil(lsp.PathBinding)

	ero := suite.message.Reports[0].ERO
	suite.Require().NotNil(ero)
	suite.Empty(ero.SubObjects)

	suite.Require().Len(suite.message.Reports[0].Bandwidths, 2)
	bandwidth := suite.message.Reports[0].Bandwidths[0]
	suite.Equal(BandwidthTypeExisting, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	bandwidth = suite.message.Reports[0].Bandwidths[1]
	suite.Equal(BandwidthTypeRequested, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	suite.Require().Len(suite.message.Reports[0].Metrics, 1)
	metric := suite.message.Reports[0].Metrics[0]
	suite.False(metric.Bound)
	suite.False(metric.ComputedMetric)
	suite.Equal(MetricTypeTE, metric.Type)
	suite.Equal(float32(0), metric.Value)

	lspa := suite.message.Reports[0].LSPA
	suite.Require().NotNil(lspa)
	suite.Equal(uint32(0), lspa.ExcludeAny)
	suite.Equal(uint32(0), lspa.IncludeAny)
	suite.Equal(uint32(0), lspa.IncludeAll)
	suite.Equal(uint8(0), lspa.SetupPriority)
	suite.Equal(uint8(0), lspa.HoldingPriority)
	suite.False(lspa.LocalProtectionDesired)

	suite.Nil(suite.message.Reports[0].RRO)
	suite.Nil(suite.message.Reports[0].IRO)
	suite.Nil(suite.message.Reports[0].Association)
	suite.Nil(suite.message.Reports[0].VendorInformation)

	srp = suite.message.Reports[1].SRP
	suite.Equal(uint32(0), srp.ID)
	suite.Require().NotNil(srp.PathSetupType)
	suite.Equal(PathSetupTypeSR, srp.PathSetupType.Type)

	lsp = suite.message.Reports[1].LSP
	suite.Equal(uint32(1571), lsp.ID)
	suite.True(lsp.Delegate)
	suite.True(lsp.Sync)
	suite.False(lsp.Remove)
	suite.True(lsp.Administrative)
	suite.Equal(LSPOperationalDown, lsp.Operational)
	suite.False(lsp.Create)
	suite.False(lsp.P2MP)
	suite.False(lsp.Fragmentation)
	suite.False(lsp.EROCompression)
	suite.False(lsp.AllocatedBindingLabelSID)
	suite.Require().NotNil(lsp.IPv4Identifiers)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), lsp.IPv4Identifiers.TunnelSenderAddress)
	suite.Equal(uint16(0), lsp.IPv4Identifiers.LSPID)
	suite.Equal(uint16(1502), lsp.IPv4Identifiers.TunnelID)
	suite.Equal(uint32(184483863), lsp.IPv4Identifiers.ExtendedTunnelID)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), lsp.IPv4Identifiers.TunnelEndpointAddress)
	suite.Nil(lsp.IPv6Identifiers)
	suite.Require().NotNil(lsp.SymbolicPathName)
	suite.Equal("susanin_sr_policy_for_ptx_and_jun1/to_jun1_color_300", lsp.SymbolicPathName.Name)
	suite.Nil(lsp.LSPErrorCode)
	suite.Nil(lsp.PathBinding)

	ero = suite.message.Reports[1].ERO
	suite.Require().NotNil(ero)
	suite.Empty(ero.SubObjects)

	suite.Require().Len(suite.message.Reports[1].Bandwidths, 2)
	bandwidth = suite.message.Reports[1].Bandwidths[0]
	suite.Equal(BandwidthTypeExisting, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	bandwidth = suite.message.Reports[1].Bandwidths[1]
	suite.Equal(BandwidthTypeRequested, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	suite.Require().Len(suite.message.Reports[1].Metrics, 1)
	metric = suite.message.Reports[1].Metrics[0]
	suite.False(metric.Bound)
	suite.False(metric.ComputedMetric)
	suite.Equal(MetricTypeTE, metric.Type)
	suite.Equal(float32(0), metric.Value)

	lspa = suite.message.Reports[1].LSPA
	suite.Require().NotNil(lspa)
	suite.Equal(uint32(0), lspa.ExcludeAny)
	suite.Equal(uint32(0), lspa.IncludeAny)
	suite.Equal(uint32(0), lspa.IncludeAll)
	suite.Equal(uint8(0), lspa.SetupPriority)
	suite.Equal(uint8(0), lspa.HoldingPriority)
	suite.False(lspa.LocalProtectionDesired)

	suite.Nil(suite.message.Reports[1].RRO)
	suite.Nil(suite.message.Reports[1].IRO)

	association := suite.message.Reports[1].Association
	suite.Require().NotNil(association)
	suite.Equal(AssociationObjectTypeIPv4, association.Type)
	suite.False(association.Removal)
	suite.Equal(AssociationTypeJuniperSRPolicy, association.AssociationType)
	suite.Equal(uint16(8), association.ID)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), association.Source)
	suite.Nil(association.GlobalSource)
	suite.Nil(association.ExtendedID)

	suite.Nil(association.SRExtendedID)
	suite.Nil(association.SRPolicyName)
	suite.Nil(association.SRPolicyCandidatePathID)
	suite.Nil(association.SRPolicyCandidatePathName)
	suite.Nil(association.SRPolicyCandidatePathPreference)

	suite.Require().NotNil(association.JuniperSRPolicyID)
	suite.Equal(uint32(300), association.JuniperSRPolicyID.Color)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), association.JuniperSRPolicyID.Endpoint)
	suite.Require().NotNil(association.JuniperSRPolicyCandidatePathID)
	suite.Equal(uint8(30), association.JuniperSRPolicyCandidatePathID.ProtocolOrigin)
	suite.Equal(uint32(0), association.JuniperSRPolicyCandidatePathID.OriginatorASN)
	suite.Equal(net.ParseIP("::"), association.JuniperSRPolicyCandidatePathID.OriginatorAddress)
	suite.Equal(uint32(0), association.JuniperSRPolicyCandidatePathID.Discriminator)
	suite.Require().NotNil(association.JuniperSRPolicyCandidatePathPreference)
	suite.Equal(uint32(100), association.JuniperSRPolicyCandidatePathPreference.Preference)

	suite.Nil(suite.message.Reports[1].VendorInformation)

	srp = suite.message.Reports[2].SRP
	suite.Equal(uint32(0), srp.ID)
	suite.Require().NotNil(srp.PathSetupType)
	suite.Equal(PathSetupTypeSR, srp.PathSetupType.Type)

	lsp = suite.message.Reports[2].LSP
	suite.Equal(uint32(1571), lsp.ID)
	suite.True(lsp.Delegate)
	suite.True(lsp.Sync)
	suite.False(lsp.Remove)
	suite.True(lsp.Administrative)
	suite.Equal(LSPOperationalDown, lsp.Operational)
	suite.False(lsp.Create)
	suite.False(lsp.P2MP)
	suite.False(lsp.Fragmentation)
	suite.False(lsp.EROCompression)
	suite.False(lsp.AllocatedBindingLabelSID)
	suite.Require().NotNil(lsp.IPv4Identifiers)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), lsp.IPv4Identifiers.TunnelSenderAddress)
	suite.Equal(uint16(0), lsp.IPv4Identifiers.LSPID)
	suite.Equal(uint16(1502), lsp.IPv4Identifiers.TunnelID)
	suite.Equal(uint32(184483863), lsp.IPv4Identifiers.ExtendedTunnelID)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), lsp.IPv4Identifiers.TunnelEndpointAddress)
	suite.Nil(lsp.IPv6Identifiers)
	suite.Require().NotNil(lsp.SymbolicPathName)
	suite.Equal("susanin_sr_policy_for_ptx_and_jun1/to_jun1_color_300", lsp.SymbolicPathName.Name)
	suite.Nil(lsp.LSPErrorCode)
	suite.Nil(lsp.PathBinding)

	ero = suite.message.Reports[2].ERO
	suite.Require().NotNil(ero)
	suite.Empty(ero.SubObjects)

	suite.Require().Len(suite.message.Reports[2].Bandwidths, 2)
	bandwidth = suite.message.Reports[2].Bandwidths[0]
	suite.Equal(BandwidthTypeExisting, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	bandwidth = suite.message.Reports[2].Bandwidths[1]
	suite.Equal(BandwidthTypeRequested, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	suite.Require().Len(suite.message.Reports[2].Metrics, 1)
	metric = suite.message.Reports[2].Metrics[0]
	suite.False(metric.Bound)
	suite.False(metric.ComputedMetric)
	suite.Equal(MetricTypeTE, metric.Type)
	suite.Equal(float32(0), metric.Value)

	lspa = suite.message.Reports[2].LSPA
	suite.Require().NotNil(lspa)
	suite.Equal(uint32(0), lspa.ExcludeAny)
	suite.Equal(uint32(0), lspa.IncludeAny)
	suite.Equal(uint32(0), lspa.IncludeAll)
	suite.Equal(uint8(0), lspa.SetupPriority)
	suite.Equal(uint8(0), lspa.HoldingPriority)
	suite.False(lspa.LocalProtectionDesired)

	suite.Nil(suite.message.Reports[2].RRO)
	suite.Nil(suite.message.Reports[2].IRO)

	association = suite.message.Reports[2].Association
	suite.Require().NotNil(association)
	suite.Equal(AssociationObjectTypeIPv4, association.Type)
	suite.False(association.Removal)
	suite.Equal(AssociationTypeJuniperSRPolicy, association.AssociationType)
	suite.Equal(uint16(8), association.ID)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), association.Source)
	suite.Nil(association.GlobalSource)
	suite.Nil(association.ExtendedID)
	suite.Nil(association.SRExtendedID)

	suite.Nil(association.SRExtendedID)
	suite.Nil(association.SRPolicyName)
	suite.Nil(association.SRPolicyCandidatePathID)
	suite.Nil(association.SRPolicyCandidatePathName)
	suite.Nil(association.SRPolicyCandidatePathPreference)

	suite.Require().NotNil(association.JuniperSRPolicyID)
	suite.Equal(uint32(300), association.JuniperSRPolicyID.Color)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), association.JuniperSRPolicyID.Endpoint)
	suite.Nil(association.SRPolicyName)
	suite.Require().NotNil(association.JuniperSRPolicyCandidatePathID)
	suite.Equal(uint8(30), association.JuniperSRPolicyCandidatePathID.ProtocolOrigin)
	suite.Equal(uint32(0), association.JuniperSRPolicyCandidatePathID.OriginatorASN)
	suite.Equal(net.ParseIP("::"), association.JuniperSRPolicyCandidatePathID.OriginatorAddress)
	suite.Equal(uint32(0), association.JuniperSRPolicyCandidatePathID.Discriminator)
	suite.Require().NotNil(association.JuniperSRPolicyCandidatePathPreference)
	suite.Equal(uint32(100), association.JuniperSRPolicyCandidatePathPreference.Preference)

	suite.Nil(suite.message.Reports[2].VendorInformation)
}

func (suite *reportMessageSuite) TestParseWithIRO() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x0a, 0x00, 0xe4, 0x21, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x20, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x04, 0x07, 0x10, 0x00, 0x44, 0x01, 0x08, 0xd5, 0xb4,
		0xd5, 0x27, 0x20, 0x00, 0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x26, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x81, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x80, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x62, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x63, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa,
		0xef, 0x18, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x19, 0x20, 0x00, 0x08, 0x10, 0x00, 0x64,
		0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x27, 0x20, 0x00, 0x01, 0x08, 0xd5, 0xb4, 0xd5, 0x26, 0x20, 0x00,
		0x01, 0x08, 0x57, 0xfa, 0xe4, 0xa8, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x81, 0x20, 0x00,
		0x01, 0x08, 0x57, 0xfa, 0xef, 0x80, 0x20, 0x00, 0x01, 0x08, 0x5f, 0x6c, 0xed, 0xfd, 0x20, 0x00,
		0x01, 0x08, 0x57, 0xfa, 0xef, 0x62, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x63, 0x20, 0x00,
		0x01, 0x08, 0x57, 0xfa, 0xe9, 0xe9, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x18, 0x20, 0x00,
		0x01, 0x08, 0x57, 0xfa, 0xef, 0x19, 0x20, 0x00, 0x01, 0x08, 0x8d, 0x08, 0x88, 0xe3, 0x20, 0x00,
		0x05, 0x20, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x0a, 0x10, 0x00, 0x1c, 0x81, 0x08, 0x57, 0xfa,
		0xe9, 0xe9, 0x20, 0x00, 0x01, 0x08, 0x57, 0xfa, 0xef, 0x19, 0x20, 0x00, 0x01, 0x08, 0x8d, 0x08,
		0x88, 0xe3, 0x20, 0x00,
	}))
	suite.Require().Len(suite.message.Reports, 1)

	srp := suite.message.Reports[0].SRP
	suite.Equal(uint32(0), srp.ID)
	suite.Nil(srp.PathSetupType)

	lsp := suite.message.Reports[0].LSP
	suite.Equal(uint32(0), lsp.ID)
	suite.False(lsp.Delegate)
	suite.False(lsp.Sync)
	suite.True(lsp.Remove)
	suite.False(lsp.Administrative)
	suite.Equal(LSPOperationalDown, lsp.Operational)
	suite.False(lsp.Create)
	suite.False(lsp.P2MP)
	suite.False(lsp.Fragmentation)
	suite.False(lsp.EROCompression)
	suite.False(lsp.AllocatedBindingLabelSID)
	suite.Nil(lsp.IPv4Identifiers)
	suite.Nil(lsp.IPv6Identifiers)
	suite.Nil(lsp.SymbolicPathName)
	suite.Nil(lsp.LSPErrorCode)
	suite.Nil(lsp.PathBinding)

	ero := suite.message.Reports[0].ERO
	suite.Require().Len(ero.SubObjects, 8)

	suite.Require().Len(suite.message.Reports[0].Bandwidths, 1)
	bandwidth := suite.message.Reports[0].Bandwidths[0]
	suite.Equal(BandwidthTypeExisting, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	suite.Nil(suite.message.Reports[0].Metrics)
	suite.Nil(suite.message.Reports[0].LSPA)

	rro := suite.message.Reports[0].RRO
	suite.Require().NotNil(rro)
	suite.Require().Len(rro.SubObjects, 12)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[0])
	ipv4 := rro.SubObjects[0].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("213.180.213.39").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[1])
	ipv4 = rro.SubObjects[1].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("213.180.213.38").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[2])
	ipv4 = rro.SubObjects[2].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.228.168").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[3])
	ipv4 = rro.SubObjects[3].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.239.129").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[4])
	ipv4 = rro.SubObjects[4].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.239.128").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[5])
	ipv4 = rro.SubObjects[5].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("95.108.237.253").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[6])
	ipv4 = rro.SubObjects[6].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.239.98").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[7])
	ipv4 = rro.SubObjects[7].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.239.99").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[8])
	ipv4 = rro.SubObjects[8].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.233.233").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[9])
	ipv4 = rro.SubObjects[9].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.239.24").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[10])
	ipv4 = rro.SubObjects[10].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.239.25").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), rro.SubObjects[11])
	ipv4 = rro.SubObjects[11].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("141.8.136.227").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	iro := suite.message.Reports[0].IRO
	suite.Require().NotNil(iro)
	suite.Require().Len(iro.SubObjects, 3)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), iro.SubObjects[0])
	ipv4 = iro.SubObjects[0].(*RouteSubObjectIPv4)
	suite.True(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.233.233").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), iro.SubObjects[1])
	ipv4 = iro.SubObjects[1].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("87.250.239.25").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)

	suite.Require().IsType((*RouteSubObjectIPv4)(nil), iro.SubObjects[2])
	ipv4 = iro.SubObjects[2].(*RouteSubObjectIPv4)
	suite.False(ipv4.Loose)
	suite.Equal(net.ParseIP("141.8.136.227").To4(), ipv4.Address)
	suite.Equal(uint8(32), ipv4.PrefixLength)
	suite.Nil(suite.message.Reports[0].Association)
	suite.Nil(suite.message.Reports[0].VendorInformation)
}

func (suite *reportMessageSuite) TestParseCisco() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x0a, 0x00, 0xc8, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x28, 0x00, 0x08, 0x00, 0x89,
		0x00, 0x12, 0x00, 0x10, 0x57, 0xfa, 0xea, 0xae, 0x00, 0x00, 0x00, 0x80, 0x57, 0xfa, 0xea, 0xae,
		0x57, 0xfa, 0xea, 0xad, 0x00, 0x11, 0x00, 0x05, 0x53, 0x4c, 0x5f, 0x31, 0x00, 0x00, 0x00, 0x00,
		0x07, 0x10, 0x00, 0x04, 0x09, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x07, 0x07, 0x00, 0x00, 0x05, 0x12, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00,
		0x05, 0x52, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x02,
		0x00, 0x00, 0x00, 0x00, 0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x01, 0x0b, 0x41, 0x10, 0x00, 0x00,
		0x22, 0x10, 0x00, 0x48, 0x00, 0x00, 0x00, 0x09, 0x00, 0x02, 0x00, 0x24, 0x73, 0x72, 0x74, 0x65,
		0x5f, 0x63, 0x5f, 0x34, 0x32, 0x39, 0x34, 0x39, 0x36, 0x37, 0x32, 0x39, 0x35, 0x5f, 0x65, 0x70,
		0x5f, 0x38, 0x37, 0x2e, 0x32, 0x35, 0x30, 0x2e, 0x32, 0x33, 0x34, 0x2e, 0x31, 0x37, 0x33, 0x00,
		0x00, 0x01, 0x00, 0x04, 0xff, 0xff, 0xff, 0xff, 0x00, 0x03, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64,
		0x00, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
	}))
	suite.Require().Len(suite.message.Reports, 1)

	srp := suite.message.Reports[0].SRP
	suite.Equal(uint32(0), srp.ID)
	suite.Require().NotNil(srp.PathSetupType)
	suite.Equal(PathSetupTypeSR, srp.PathSetupType.Type)

	lsp := suite.message.Reports[0].LSP
	suite.Equal(uint32(128), lsp.ID)
	suite.True(lsp.Delegate)
	suite.False(lsp.Sync)
	suite.False(lsp.Remove)
	suite.True(lsp.Administrative)
	suite.Equal(LSPOperationalDown, lsp.Operational)
	suite.True(lsp.Create)
	suite.False(lsp.P2MP)
	suite.False(lsp.Fragmentation)
	suite.False(lsp.EROCompression)
	suite.False(lsp.AllocatedBindingLabelSID)

	suite.Require().NotNil(lsp.IPv4Identifiers)
	suite.Equal(net.ParseIP("87.250.234.174").To4(), lsp.IPv4Identifiers.TunnelSenderAddress)
	suite.Equal(uint16(0), lsp.IPv4Identifiers.LSPID)
	suite.Equal(uint16(128), lsp.IPv4Identifiers.TunnelID)
	suite.Equal(uint32(1476061870), lsp.IPv4Identifiers.ExtendedTunnelID)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), lsp.IPv4Identifiers.TunnelEndpointAddress)

	suite.Nil(lsp.IPv6Identifiers)

	suite.Require().NotNil(lsp.SymbolicPathName)
	suite.Equal("SL_1\x00", lsp.SymbolicPathName.Name)

	suite.Nil(lsp.LSPErrorCode)
	suite.Nil(lsp.PathBinding)
	suite.Nil(lsp.CiscoBSID)
	suite.Nil(lsp.VendorInformation)

	ero := suite.message.Reports[0].ERO
	suite.Nil(ero.SubObjects)

	lspa := suite.message.Reports[0].LSPA
	suite.Require().NotNil(lspa)
	suite.Require().NotNil(lspa)
	suite.Equal(uint32(0), lspa.ExcludeAny)
	suite.Equal(uint32(0), lspa.IncludeAny)
	suite.Equal(uint32(0), lspa.IncludeAll)
	suite.Equal(uint8(7), lspa.SetupPriority)
	suite.Equal(uint8(7), lspa.HoldingPriority)
	suite.False(lspa.LocalProtectionDesired)

	suite.Require().Len(suite.message.Reports[0].Bandwidths, 2)
	bandwidth := suite.message.Reports[0].Bandwidths[0]
	suite.Equal(BandwidthTypeRequested, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	bandwidth = suite.message.Reports[0].Bandwidths[1]
	suite.Equal(BandwidthTypeCiscoRequested, bandwidth.Type)
	suite.Equal(uint32(0), bandwidth.Bandwidth)
	suite.Empty(bandwidth.SpecType)
	suite.Nil(bandwidth.GeneralizedBandwidth)
	suite.Nil(bandwidth.ReverseGeneralizedBandwidth)

	suite.Require().Len(suite.message.Reports[0].Metrics, 2)
	metric := suite.message.Reports[0].Metrics[0]
	suite.False(metric.Bound)
	suite.False(metric.ComputedMetric)
	suite.Equal(MetricTypeTE, metric.Type)
	suite.Equal(float32(0), metric.Value)

	metric = suite.message.Reports[0].Metrics[1]
	suite.True(metric.Bound)
	suite.False(metric.ComputedMetric)
	suite.Equal(MetricTypeSegmentIDDepth, metric.Type)
	suite.Equal(float32(9), metric.Value)

	suite.Equal(len(suite.message.Reports[0].VendorInformation), 1)
	vendorInformation := suite.message.Reports[0].VendorInformation[0]
	suite.Require().NotNil(vendorInformation)
	suite.Equal(VendorEnterpriseNumberCisco, vendorInformation.EnterpriseNumber)
	suite.Nil(vendorInformation.EnterpriseSpecificInformation)

	suite.Require().NotNil(vendorInformation.Cisco)

	suite.Require().NotNil(vendorInformation.Cisco.PolicyColor)
	suite.Equal(uint32(0xffffffff), vendorInformation.Cisco.PolicyColor.Color)

	suite.Require().NotNil(vendorInformation.Cisco.PolicyName)
	suite.Equal("srte_c_4294967295_ep_87.250.234.173\x00", vendorInformation.Cisco.PolicyName.Name)

	suite.Require().NotNil(vendorInformation.Cisco.CandidatePathPreference)
	suite.Equal(uint32(100), vendorInformation.Cisco.CandidatePathPreference.Preference)

	suite.Require().NotNil(vendorInformation.Cisco.ProtectionConstraint)
	suite.Equal(CiscoProtectionConstraintTypeUnprotected, vendorInformation.Cisco.ProtectionConstraint.Type)
}

func (suite *reportMessageSuite) TestSerialize() {
	suite.message = ReportMessage{
		Reports: []LSPReport{
			{
				SRP: &SRPObject{
					ID:            0,
					PathSetupType: &PathSetupTypeTLV{Type: PathSetupTypeSR},
				},
				LSP: LSPObject{
					ID:             1189,
					Sync:           true,
					Administrative: true,
					Operational:    LSPOperationalDown,
					IPv4Identifiers: &IPv4LSPIdentifiersTLV{
						TunnelSenderAddress:   net.ParseIP("10.255.0.23"),
						TunnelID:              1123,
						ExtendedTunnelID:      184483863,
						TunnelEndpointAddress: net.ParseIP("87.250.234.173"),
					},
					SymbolicPathName: &SymbolicPathNameTLV{Name: "static_lsp_path_1/static_lsp"},
				},
				ERO: &ExplicitRouteObject{},
				Bandwidths: []BandwidthObject{
					{Type: BandwidthTypeExisting},
					{Type: BandwidthTypeRequested},
				},
				Metrics: []MetricObject{{Type: MetricTypeTE}},
				LSPA:    &LSPAttributesObject{},
			},
			{
				SRP: &SRPObject{
					ID:            0,
					PathSetupType: &PathSetupTypeTLV{Type: PathSetupTypeSR},
				},
				LSP: LSPObject{
					ID:             1571,
					Delegate:       true,
					Sync:           true,
					Administrative: true,
					Operational:    LSPOperationalDown,
					IPv4Identifiers: &IPv4LSPIdentifiersTLV{
						TunnelSenderAddress:   net.ParseIP("10.255.0.23"),
						TunnelID:              1502,
						ExtendedTunnelID:      184483863,
						TunnelEndpointAddress: net.ParseIP("87.250.234.173"),
					},
					SymbolicPathName: &SymbolicPathNameTLV{Name: "susanin_sr_policy_for_ptx_and_jun1/to_jun1_color_300"},
				},
				ERO: &ExplicitRouteObject{},
				Bandwidths: []BandwidthObject{
					{Type: BandwidthTypeExisting},
					{Type: BandwidthTypeRequested},
				},
				Metrics: []MetricObject{{Type: MetricTypeTE}},
				LSPA:    &LSPAttributesObject{},
				Association: &AssociationObject{
					Type:            AssociationObjectTypeIPv4,
					AssociationType: AssociationTypeJuniperSRPolicy,
					ID:              uint16(8),
					Source:          net.ParseIP("10.255.0.23"),
					JuniperSRPolicyID: &JuniperSRPolicyIDTLV{
						Color:    300,
						Endpoint: net.ParseIP("87.250.234.173"),
					},
					SRPolicyCandidatePathID: &SRPolicyCandidatePathIDTLV{
						ProtocolOrigin:    30,
						OriginatorASN:     0,
						OriginatorAddress: net.ParseIP("::"),
						Discriminator:     0,
					},
					SRPolicyCandidatePathPreference: &SRPolicyCandidatePathPreferenceTLV{
						Preference: 100,
					},
				},
			},
			{
				SRP: &SRPObject{
					ID:            0,
					PathSetupType: &PathSetupTypeTLV{Type: PathSetupTypeSR},
				},
				LSP: LSPObject{
					ID:             1571,
					Delegate:       true,
					Sync:           true,
					Administrative: true,
					Operational:    LSPOperationalDown,
					IPv4Identifiers: &IPv4LSPIdentifiersTLV{
						TunnelSenderAddress:   net.ParseIP("10.255.0.23"),
						TunnelID:              1571,
						ExtendedTunnelID:      184483863,
						TunnelEndpointAddress: net.ParseIP("87.250.234.173"),
					},
					SymbolicPathName: &SymbolicPathNameTLV{Name: "susanin_sr_policy_for_ptx_and_jun1/to_jun1_color_300"},
				},
				ERO: &ExplicitRouteObject{},
				Bandwidths: []BandwidthObject{
					{Type: BandwidthTypeExisting},
					{Type: BandwidthTypeRequested},
				},
				Metrics: []MetricObject{{Type: MetricTypeTE}},
				LSPA:    &LSPAttributesObject{},
				Association: &AssociationObject{
					Type:            AssociationObjectTypeIPv4,
					AssociationType: AssociationTypeJuniperSRPolicy,
					ID:              uint16(8),
					Source:          net.ParseIP("10.255.0.23"),
					JuniperSRPolicyID: &JuniperSRPolicyIDTLV{
						Color:    300,
						Endpoint: net.ParseIP("87.250.234.173"),
					},
					SRPolicyCandidatePathID: &SRPolicyCandidatePathIDTLV{
						ProtocolOrigin:    30,
						OriginatorASN:     0,
						OriginatorAddress: net.ParseIP("::"),
						Discriminator:     0,
					},
					SRPolicyCandidatePathPreference: &SRPolicyCandidatePathPreferenceTLV{
						Preference: 100,
					},
				},
			},
		},
	}

	raw, err := suite.message.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x0a, 0x02, 0x0c, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x3c, 0x00, 0x4a, 0x50, 0x0a,
			0x00, 0x12, 0x00, 0x10, 0x0a, 0xff, 0x00, 0x17, 0x00, 0x00, 0x04, 0x63, 0x0a, 0xff, 0x00, 0x17,
			0x57, 0xfa, 0xea, 0xad, 0x00, 0x11, 0x00, 0x1c, 0x73, 0x74, 0x61, 0x74, 0x69, 0x63, 0x5f, 0x6c,
			0x73, 0x70, 0x5f, 0x70, 0x61, 0x74, 0x68, 0x5f, 0x31, 0x2f, 0x73, 0x74, 0x61, 0x74, 0x69, 0x63,
			0x5f, 0x6c, 0x73, 0x70, 0x07, 0x10, 0x00, 0x04, 0x05, 0x20, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00,
			0x05, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x02,
			0x00, 0x00, 0x00, 0x00, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x54, 0x00, 0x62, 0x30, 0x0b,
			0x00, 0x12, 0x00, 0x10, 0x0a, 0xff, 0x00, 0x17, 0x00, 0x00, 0x05, 0xde, 0x0a, 0xff, 0x00, 0x17,
			0x57, 0xfa, 0xea, 0xad, 0x00, 0x11, 0x00, 0x34, 0x73, 0x75, 0x73, 0x61, 0x6e, 0x69, 0x6e, 0x5f,
			0x73, 0x72, 0x5f, 0x70, 0x6f, 0x6c, 0x69, 0x63, 0x79, 0x5f, 0x66, 0x6f, 0x72, 0x5f, 0x70, 0x74,
			0x78, 0x5f, 0x61, 0x6e, 0x64, 0x5f, 0x6a, 0x75, 0x6e, 0x31, 0x2f, 0x74, 0x6f, 0x5f, 0x6a, 0x75,
			0x6e, 0x31, 0x5f, 0x63, 0x6f, 0x6c, 0x6f, 0x72, 0x5f, 0x33, 0x30, 0x30, 0x07, 0x10, 0x00, 0x04,
			0x05, 0x20, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x05, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00,
			0x06, 0x10, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x28, 0x10, 0x00, 0x44,
			0x00, 0x00, 0x00, 0x00, 0xff, 0xe1, 0x00, 0x08, 0x0a, 0xff, 0x00, 0x17, 0xff, 0xe3, 0x00, 0x08,
			0x00, 0x00, 0x01, 0x2c, 0x57, 0xfa, 0xea, 0xad, 0x00, 0x39, 0x00, 0x1c, 0x1e, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x3b, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64,
			0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1c, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x54, 0x00, 0x62, 0x30, 0x0b, 0x00, 0x12, 0x00, 0x10,
			0x0a, 0xff, 0x00, 0x17, 0x00, 0x00, 0x06, 0x23, 0x0a, 0xff, 0x00, 0x17, 0x57, 0xfa, 0xea, 0xad,
			0x00, 0x11, 0x00, 0x34, 0x73, 0x75, 0x73, 0x61, 0x6e, 0x69, 0x6e, 0x5f, 0x73, 0x72, 0x5f, 0x70,
			0x6f, 0x6c, 0x69, 0x63, 0x79, 0x5f, 0x66, 0x6f, 0x72, 0x5f, 0x70, 0x74, 0x78, 0x5f, 0x61, 0x6e,
			0x64, 0x5f, 0x6a, 0x75, 0x6e, 0x31, 0x2f, 0x74, 0x6f, 0x5f, 0x6a, 0x75, 0x6e, 0x31, 0x5f, 0x63,
			0x6f, 0x6c, 0x6f, 0x72, 0x5f, 0x33, 0x30, 0x30, 0x07, 0x10, 0x00, 0x04, 0x05, 0x20, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x00, 0x05, 0x10, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x06, 0x10, 0x00, 0x0c,
			0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x28, 0x10, 0x00, 0x44, 0x00, 0x00, 0x00, 0x00,
			0xff, 0xe1, 0x00, 0x08, 0x0a, 0xff, 0x00, 0x17, 0xff, 0xe3, 0x00, 0x08, 0x00, 0x00, 0x01, 0x2c,
			0x57, 0xfa, 0xea, 0xad, 0x00, 0x39, 0x00, 0x1c, 0x1e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x3b, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64,
		},
		raw,
	)
}

type updateMessageSuite struct {
	suite.Suite

	message UpdateMessage
}

func TestUpdateMessageSuite(t *testing.T) {
	suite.Run(t, new(updateMessageSuite))
}

func (suite *updateMessageSuite) SetupTest() {
	suite.message = UpdateMessage{}
}

func (suite *updateMessageSuite) TestParse() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x0b, 0x00, 0x50, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
		0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x24, 0x00, 0x07, 0xb0, 0x2b,
		0x00, 0x11, 0x00, 0x09, 0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65, 0x00, 0x00, 0x00,
		0x00, 0x37, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x18, 0x89, 0x40, 0x00, 0x07, 0x10, 0x00, 0x14,
		0x24, 0x08, 0x00, 0x09, 0x00, 0x3e, 0x90, 0x00, 0x24, 0x08, 0x00, 0x09, 0x00, 0x3e, 0xa0, 0x00,
	}))

	suite.Require().Len(suite.message.Updates, 1)

	srp := suite.message.Updates[0].SRP
	suite.Equal(uint32(1), srp.ID)
	suite.Require().NotNil(srp.PathSetupType)
	suite.Assert().Equal(PathSetupTypeSR, srp.PathSetupType.Type)

	lsp := suite.message.Updates[0].LSP
	suite.Equal(uint32(123), lsp.ID)
	suite.True(lsp.Delegate)
	suite.True(lsp.Sync)
	suite.False(lsp.Remove)
	suite.True(lsp.Administrative)
	suite.Equal(LSPOperationalActive, lsp.Operational)
	suite.False(lsp.Create)
	suite.False(lsp.P2MP)
	suite.False(lsp.Fragmentation)
	suite.False(lsp.EROCompression)
	suite.False(lsp.AllocatedBindingLabelSID)
	suite.Nil(lsp.IPv4Identifiers)
	suite.Nil(lsp.IPv6Identifiers)
	suite.Require().NotNil(lsp.SymbolicPathName)
	suite.Equal("test name", lsp.SymbolicPathName.Name)
	suite.Nil(lsp.LSPErrorCode)
	suite.Require().NotNil(lsp.PathBinding)
	suite.Equal(BindingTypeMPLSLabel, lsp.PathBinding.BindingType)
	suite.Require().NotNil(lsp.PathBinding.MPLSLabel)
	suite.Equal(uint32(100500), *lsp.PathBinding.MPLSLabel)
	suite.Nil(lsp.PathBinding.MPLSStack)
	suite.Nil(lsp.PathBinding.SRv6SID)
	suite.Nil(lsp.PathBinding.SRv6SIDWithEndpointBehavior)

	ero := suite.message.Updates[0].ERO
	suite.Require().NotNil(ero)
	suite.Require().Len(ero.SubObjects, 2)

	suite.Require().IsType((*RouteSubObjectSR)(nil), ero.SubObjects[0])
	sr := ero.SubObjects[0].(*RouteSubObjectSR)
	suite.False(sr.Loose)
	suite.Empty(sr.NT)
	suite.True(sr.M)
	suite.False(sr.C)
	suite.False(sr.S)
	suite.True(sr.F)
	suite.Nil(sr.SIDIndex)
	suite.Require().NotNil(sr.SIDEntry)
	suite.Equal(uint32(1001), sr.SIDEntry.Label)
	suite.Equal(uint8(0), sr.SIDEntry.TC)
	suite.False(sr.SIDEntry.S)
	suite.Equal(uint8(0), sr.SIDEntry.TTL)

	suite.Require().IsType((*RouteSubObjectSR)(nil), ero.SubObjects[1])
	sr = ero.SubObjects[1].(*RouteSubObjectSR)
	suite.False(sr.Loose)
	suite.Empty(sr.NT)
	suite.True(sr.M)
	suite.False(sr.C)
	suite.False(sr.S)
	suite.True(sr.F)
	suite.Nil(sr.SIDIndex)
	suite.Require().NotNil(sr.SIDEntry)
	suite.Equal(uint32(1002), sr.SIDEntry.Label)
	suite.Equal(uint8(0), sr.SIDEntry.TC)
	suite.False(sr.SIDEntry.S)
	suite.Equal(uint8(0), sr.SIDEntry.TTL)

	suite.Nil(suite.message.Updates[0].Association)
	suite.Nil(suite.message.Updates[0].VendorInformation)
}

func (suite *updateMessageSuite) TestSerialize() {
	label := uint32(100500)
	suite.message = UpdateMessage{
		Updates: []LSPUpdate{{
			SRP: SRPObject{
				ID:            1,
				PathSetupType: &PathSetupTypeTLV{Type: PathSetupTypeSR},
			},
			LSP: LSPObject{
				ID:               123,
				Delegate:         true,
				Sync:             true,
				Administrative:   true,
				Operational:      LSPOperationalActive,
				SymbolicPathName: &SymbolicPathNameTLV{Name: "test name"},
				PathBinding: &PathBindingTLV{
					BindingType: BindingTypeMPLSLabel,
					MPLSLabel:   &label,
				},
			},
			ERO: &ExplicitRouteObject{
				SubObjects: []RouteSubObjectInterface{
					&RouteSubObjectSR{
						M:        true,
						F:        true,
						SIDEntry: &MPLSLabelStackEntry{Label: 1001},
					},
					&RouteSubObjectSR{
						M:        true,
						F:        true,
						SIDEntry: &MPLSLabelStackEntry{Label: 1002},
					},
				},
			},
		}},
	}

	raw, err := suite.message.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x0b, 0x00, 0x50, 0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
			0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0x20, 0x10, 0x00, 0x24, 0x00, 0x07, 0xb0, 0x2b,
			0x00, 0x11, 0x00, 0x09, 0x74, 0x65, 0x73, 0x74, 0x20, 0x6e, 0x61, 0x6d, 0x65, 0x00, 0x00, 0x00,
			0x00, 0x37, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x18, 0x89, 0x40, 0x00, 0x07, 0x10, 0x00, 0x14,
			0x24, 0x08, 0x00, 0x09, 0x00, 0x3e, 0x90, 0x00, 0x24, 0x08, 0x00, 0x09, 0x00, 0x3e, 0xa0, 0x00,
		},
		raw,
	)
}

type initiateMessageSuite struct {
	suite.Suite

	message InitiateMessage
}

func TestInitiateMessageSuite(t *testing.T) {
	suite.Run(t, new(initiateMessageSuite))
}

func (suite *initiateMessageSuite) SetupTest() {
	suite.message = InitiateMessage{}
}

func (suite *initiateMessageSuite) TestParse() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x0c, 0x00, 0xbc,
		0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x01, 0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
		0x20, 0x10, 0x00, 0x24, 0x00, 0x00, 0x10, 0x9b, 0x00, 0x11,
		0x00, 0x16, 0x63, 0x61, 0x6e, 0x64, 0x69, 0x64, 0x61, 0x74,
		0x65, 0x5f, 0x70, 0x61, 0x74, 0x68, 0x5f, 0x31, 0x5f, 0x6c,
		0x73, 0x70, 0x5f, 0x31, 0x00, 0x00, 0x04, 0x10, 0x00, 0x0c,
		0x0a, 0xff, 0x00, 0x17, 0x57, 0xfa, 0xea, 0xad, 0x07, 0x10,
		0x00, 0x1c, 0x24, 0x08, 0x00, 0x09, 0x25, 0xdd, 0x20, 0x00,
		0x24, 0x08, 0x00, 0x09, 0x25, 0xdd, 0x30, 0x00, 0x24, 0x08,
		0x00, 0x09, 0x25, 0x1c, 0x10, 0x00, 0x28, 0x10, 0x00, 0x58,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x0a, 0xff,
		0x00, 0x17, 0x00, 0x1f, 0x00, 0x08, 0x00, 0x00, 0x01, 0x2c,
		0x57, 0xfa, 0xea, 0xad, 0x00, 0x38, 0x00, 0x22, 0x73, 0x75,
		0x73, 0x61, 0x6e, 0x69, 0x6e, 0x5f, 0x73, 0x72, 0x5f, 0x70,
		0x6f, 0x6c, 0x69, 0x63, 0x79, 0x5f, 0x66, 0x6f, 0x72, 0x5f,
		0x70, 0x74, 0x78, 0x5f, 0x61, 0x6e, 0x64, 0x5f, 0x6a, 0x75,
		0x6e, 0x31, 0x00, 0x00, 0x00, 0x3a, 0x00, 0x10, 0x63, 0x61,
		0x6e, 0x64, 0x69, 0x64, 0x61, 0x74, 0x65, 0x5f, 0x70, 0x61,
		0x74, 0x68, 0x5f, 0x31,
	}))

	suite.Require().Len(suite.message.Initiates, 1)

	srp := suite.message.Initiates[0].SRP
	suite.Equal(uint32(1), srp.ID)
	suite.Require().NotNil(srp.PathSetupType)
	suite.Equal(PathSetupTypeSR, srp.PathSetupType.Type)

	lsp := suite.message.Initiates[0].LSP
	suite.Equal(uint32(1), lsp.ID)
	suite.True(lsp.Delegate)
	suite.True(lsp.Sync)
	suite.False(lsp.Remove)
	suite.True(lsp.Administrative)
	suite.Equal(LSPOperationalUp, lsp.Operational)
	suite.True(lsp.Create)
	suite.Nil(lsp.IPv4Identifiers)
	suite.Nil(lsp.IPv6Identifiers)
	suite.Require().NotNil(lsp.SymbolicPathName)
	suite.Equal("candidate_path_1_lsp_1", lsp.SymbolicPathName.Name)
	suite.Nil(lsp.LSPErrorCode)
	suite.Nil(lsp.PathBinding)

	endpoints := suite.message.Initiates[0].Endpoints
	suite.Require().NotNil(endpoints)
	suite.Equal(EndpointsTypeIPv4Addresses, endpoints.Type)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), endpoints.Source)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), endpoints.Destination)

	ero := suite.message.Initiates[0].ERO
	suite.Require().NotNil(ero)
	suite.Require().Len(ero.SubObjects, 3)

	suite.Require().IsType((*RouteSubObjectSR)(nil), ero.SubObjects[0])
	sr := ero.SubObjects[0].(*RouteSubObjectSR)
	suite.False(sr.Loose)
	suite.Require().Equal(NAITypeAbsent, sr.NT)
	suite.True(sr.M)
	suite.False(sr.C)
	suite.False(sr.S)
	suite.True(sr.F)
	suite.Nil(sr.SIDIndex)
	suite.NotNil(sr.SIDEntry)
	suite.Equal(uint32(155090), sr.SIDEntry.Label)
	suite.Equal(uint8(0), sr.SIDEntry.TC)
	suite.False(sr.SIDEntry.S)
	suite.Equal(uint8(0), sr.SIDEntry.TTL)

	suite.Require().IsType((*RouteSubObjectSR)(nil), ero.SubObjects[1])
	sr = ero.SubObjects[1].(*RouteSubObjectSR)
	suite.False(sr.Loose)
	suite.Equal(NAITypeAbsent, sr.NT)
	suite.True(sr.M)
	suite.False(sr.C)
	suite.False(sr.S)
	suite.True(sr.F)
	suite.Nil(sr.SIDIndex)
	suite.NotNil(sr.SIDEntry)
	suite.Equal(uint32(155091), sr.SIDEntry.Label)
	suite.Equal(uint8(0), sr.SIDEntry.TC)
	suite.False(sr.SIDEntry.S)
	suite.Equal(uint8(0), sr.SIDEntry.TTL)

	suite.Require().IsType((*RouteSubObjectSR)(nil), ero.SubObjects[2])
	sr = ero.SubObjects[2].(*RouteSubObjectSR)
	suite.False(sr.Loose)
	suite.Equal(NAITypeAbsent, sr.NT)
	suite.True(sr.M)
	suite.False(sr.C)
	suite.False(sr.S)
	suite.True(sr.F)
	suite.Nil(sr.SIDIndex)
	suite.NotNil(sr.SIDEntry)
	suite.Equal(uint32(152001), sr.SIDEntry.Label)
	suite.Equal(uint8(0), sr.SIDEntry.TC)
	suite.False(sr.SIDEntry.S)
	suite.Equal(uint8(0), sr.SIDEntry.TTL)

	association := suite.message.Initiates[0].Association
	suite.Require().NotNil(association)
	suite.Equal(AssociationObjectTypeIPv4, association.Type)
	suite.False(association.Removal)
	suite.Equal(AssociationTypePolicy, association.AssociationType)
	suite.Equal(uint16(1), association.ID)
	suite.Equal(net.ParseIP("10.255.0.23").To4(), association.Source)
	suite.Nil(association.GlobalSource)
	suite.Nil(association.ExtendedID)
	suite.Require().NotNil(association.SRExtendedID)
	suite.Equal(uint32(300), association.SRExtendedID.Color)
	suite.Equal(net.ParseIP("87.250.234.173").To4(), association.SRExtendedID.Endpoint)
	suite.Nil(association.JuniperSRPolicyID)
	suite.Require().NotNil(association.SRPolicyName)
	suite.Equal("susanin_sr_policy_for_ptx_and_jun1", association.SRPolicyName.Name)
	suite.Nil(association.SRPolicyCandidatePathID)
	suite.Require().NotNil(association.SRPolicyCandidatePathName)
	suite.Equal("candidate_path_1", association.SRPolicyCandidatePathName.Name)
	suite.Nil(association.SRPolicyCandidatePathPreference)

	suite.Nil(suite.message.Initiates[0].VendorInformation)
}

func (suite *initiateMessageSuite) TestSerialize() {
	suite.message = InitiateMessage{
		Initiates: []LSPInitiate{{
			SRP: SRPObject{
				ID:            1,
				PathSetupType: &PathSetupTypeTLV{Type: PathSetupTypeSR},
			},
			LSP: LSPObject{
				ID:                       1,
				Delegate:                 true,
				Sync:                     true,
				Remove:                   false,
				Administrative:           true,
				Operational:              LSPOperationalUp,
				Create:                   true,
				P2MP:                     false,
				Fragmentation:            false,
				EROCompression:           false,
				AllocatedBindingLabelSID: false,
				SymbolicPathName:         &SymbolicPathNameTLV{Name: "candidate_path_1_lsp_1"},
			},
			Endpoints: &EndpointsObject{
				Type:        EndpointsTypeIPv4Addresses,
				Source:      net.ParseIP("10.255.0.23"),
				Destination: net.ParseIP("87.250.234.173"),
			},
			ERO: &ExplicitRouteObject{
				SubObjects: []RouteSubObjectInterface{
					&RouteSubObjectSR{
						M: true,
						F: true,
						SIDEntry: &MPLSLabelStackEntry{
							Label: 155090,
						},
					},
					&RouteSubObjectSR{
						M: true,
						F: true,
						SIDEntry: &MPLSLabelStackEntry{
							Label: 155091,
						},
					},
					&RouteSubObjectSR{
						M: true,
						F: true,
						SIDEntry: &MPLSLabelStackEntry{
							Label: 152001,
						},
					},
				},
			},
			Association: &AssociationObject{
				Type:            AssociationObjectTypeIPv4,
				AssociationType: AssociationTypePolicy,
				ID:              1,
				Source:          net.ParseIP("10.255.0.23"),
				SRExtendedID: &SRExtendedAssociationIDTLV{
					Color:    300,
					Endpoint: net.ParseIP("87.250.234.173"),
				},
				SRPolicyName:              &SRPolicyNameTLV{Name: "susanin_sr_policy_for_ptx_and_jun1"},
				SRPolicyCandidatePathName: &SRPolicyCandidatePathNameTLV{Name: "candidate_path_1"},
			},
		}},
	}
	raw, err := suite.message.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x0c, 0x00, 0xbc,
			0x21, 0x10, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
			0x00, 0x01, 0x00, 0x1c, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
			0x20, 0x10, 0x00, 0x24, 0x00, 0x00, 0x10, 0x9b, 0x00, 0x11,
			0x00, 0x16, 0x63, 0x61, 0x6e, 0x64, 0x69, 0x64, 0x61, 0x74,
			0x65, 0x5f, 0x70, 0x61, 0x74, 0x68, 0x5f, 0x31, 0x5f, 0x6c,
			0x73, 0x70, 0x5f, 0x31, 0x00, 0x00, 0x04, 0x10, 0x00, 0x0c,
			0x0a, 0xff, 0x00, 0x17, 0x57, 0xfa, 0xea, 0xad, 0x07, 0x10,
			0x00, 0x1c, 0x24, 0x08, 0x00, 0x09, 0x25, 0xdd, 0x20, 0x00,
			0x24, 0x08, 0x00, 0x09, 0x25, 0xdd, 0x30, 0x00, 0x24, 0x08,
			0x00, 0x09, 0x25, 0x1c, 0x10, 0x00, 0x28, 0x10, 0x00, 0x58,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x01, 0x0a, 0xff,
			0x00, 0x17, 0x00, 0x1f, 0x00, 0x08, 0x00, 0x00, 0x01, 0x2c,
			0x57, 0xfa, 0xea, 0xad, 0x00, 0x38, 0x00, 0x22, 0x73, 0x75,
			0x73, 0x61, 0x6e, 0x69, 0x6e, 0x5f, 0x73, 0x72, 0x5f, 0x70,
			0x6f, 0x6c, 0x69, 0x63, 0x79, 0x5f, 0x66, 0x6f, 0x72, 0x5f,
			0x70, 0x74, 0x78, 0x5f, 0x61, 0x6e, 0x64, 0x5f, 0x6a, 0x75,
			0x6e, 0x31, 0x00, 0x00, 0x00, 0x3a, 0x00, 0x10, 0x63, 0x61,
			0x6e, 0x64, 0x69, 0x64, 0x61, 0x74, 0x65, 0x5f, 0x70, 0x61,
			0x74, 0x68, 0x5f, 0x31,
		},
		raw,
	)
}

type unknownMessageSuite struct {
	suite.Suite

	message UnknownMessage
}

func TestUnknownMessageSuite(t *testing.T) {
	suite.Run(t, new(unknownMessageSuite))
}

func (suite *unknownMessageSuite) SetupTest() {
	suite.message = UnknownMessage{}
}

func (suite *unknownMessageSuite) TestParseKeepalive() {
	suite.Require().NoError(suite.message.Parse([]byte{0x20, 0x02, 0x00, 0x04}))
	suite.Equal(MessageTypeKeepalive, suite.message.Type)
	suite.Nil(suite.message.Objects)
}

func (suite *unknownMessageSuite) TestParseOpen() {
	suite.Require().NoError(suite.message.Parse([]byte{
		0x20, 0x01, 0x00, 0x28,
		0x01, 0x10, 0x00, 0x24,
		0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x0a, 0x00, 0x17, 0x00, 0x08,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
	}))
	suite.Equal(MessageTypeOpen, suite.message.Type)
	suite.Require().Len(suite.message.Objects, 1)
	suite.Require().IsType((*OpenObject)(nil), suite.message.Objects[0])
}

func (suite *unknownMessageSuite) TestSerializeKeepalive() {
	suite.message = UnknownMessage{
		MessageHeader: MessageHeader{Type: MessageTypeKeepalive},
	}

	raw, err := suite.message.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x20, 0x02, 0x00, 0x04},
		raw,
	)
}

func (suite *unknownMessageSuite) TestSerializeOpen() {
	suite.message = UnknownMessage{
		MessageHeader: MessageHeader{Type: MessageTypeOpen},
		Objects: []ObjectInterface{
			&OpenObject{
				Keepalive: 30,
				DeadTimer: 120,
				SID:       29,
				StatefulCapability: &StatefulCapabilityTLV{
					LSPUpdateCapability:            true,
					IncludeDBVersion:               true,
					LSPInstantiationCapability:     true,
					TriggeredResync:                true,
					DeltaLSPSyncCapability:         false,
					TriggeredInitialSync:           false,
					P2MPCapability:                 false,
					P2MPLSPUpdateCapability:        false,
					P2MPLSPInstantiationCapability: false,
					LSPSchedulingCapability:        false,
					PDLSPCapability:                false,
				},
				SRCapability: &SRCapabilityTLV{
					NAIToSidResolvingCapability: false,
					MSDNoLimit:                  false,
					MSD:                         10,
				},
				LSPDBVersion: &LSPDBVersionTLV{
					LSPStateDBVersionNumber: 1,
				},
			},
		},
	}

	raw, err := suite.message.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x20, 0x01, 0x00, 0x28,
			0x01, 0x10, 0x00, 0x24,
			0x20, 0x1e, 0x78, 0x1d, 0x00, 0x10, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x0f, 0x00, 0x1a, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x0a, 0x00, 0x17, 0x00, 0x08,
			0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
		},
		raw,
	)
}
