package pcep

import (
	"testing"

	"github.com/stretchr/testify/suite"
)

type ciscoPolicyColorTLVSuite struct {
	suite.Suite

	value CiscoPolicyColorTLV
}

func TestCiscoPolicyColorTLVSuite(t *testing.T) {
	suite.Run(t, new(ciscoPolicyColorTLVSuite))
}

func (suite *ciscoPolicyColorTLVSuite) SetupTest() {
	suite.value = CiscoPolicyColorTLV{}
}

func (suite *ciscoPolicyColorTLVSuite) TestParse() {
	suite.Require().NoError(suite.value.Parse([]byte{0x00, 0x01, 0x00, 0x04, 0x00, 0x00, 0x01, 0xc2}))
	suite.Equal(uint32(450), suite.value.Color)
}

func (suite *ciscoPolicyColorTLVSuite) TestParseError() {
	suite.Error(suite.value.Parse(nil))
	suite.Error(suite.value.Parse([]byte{0x00, 0x01, 0x00, 0x00}))
	suite.Error(suite.value.Parse([]byte{0x00, 0x02, 0x00, 0x04, 0x00, 0x00, 0x01, 0xc2}))
}

func (suite *ciscoPolicyColorTLVSuite) TestSerialize() {
	suite.value = CiscoPolicyColorTLV{
		Color: 450,
	}

	raw, err := suite.value.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x00, 0x01, 0x00, 0x04, 0x00, 0x00, 0x01, 0xc2},
		raw,
	)
}

type ciscoPolicyNameTLVSuite struct {
	suite.Suite

	value CiscoPolicyNameTLV
}

func TestCiscoPolicyNameTLVSuite(t *testing.T) {
	suite.Run(t, new(ciscoPolicyNameTLVSuite))
}

func (suite *ciscoPolicyNameTLVSuite) SetupTest() {
	suite.value = CiscoPolicyNameTLV{}
}

func (suite *ciscoPolicyNameTLVSuite) TestParseEmpty() {
	suite.Require().NoError(suite.value.Parse([]byte{0x00, 0x02, 0x00, 0x00}))
	suite.Empty(suite.value.Name)
}

func (suite *ciscoPolicyNameTLVSuite) TestParse() {
	suite.Require().NoError(suite.value.Parse([]byte{
		0x00, 0x02, 0x00, 0x1d, 0x73, 0x72, 0x74, 0x65, 0x5f, 0x63, 0x5f, 0x35, 0x30, 0x30, 0x5f, 0x65,
		0x70, 0x5f, 0x38, 0x37, 0x2e, 0x32, 0x35, 0x30, 0x2e, 0x32, 0x33, 0x34, 0x2e, 0x31, 0x37, 0x33,
		0x00, 0x00, 0x00, 0x00,
	}))
	suite.Equal("srte_c_500_ep_87.250.234.173\x00", suite.value.Name)
}

func (suite *ciscoPolicyNameTLVSuite) TestParseError() {
	suite.Error(suite.value.Parse(nil))
	suite.Error(suite.value.Parse([]byte{
		0x00, 0x01, 0x00, 0x1d, 0x73, 0x72, 0x74, 0x65, 0x5f, 0x63, 0x5f, 0x35, 0x30, 0x30, 0x5f, 0x65,
		0x70, 0x5f, 0x38, 0x37, 0x2e, 0x32, 0x35, 0x30, 0x2e, 0x32, 0x33, 0x34, 0x2e, 0x31, 0x37, 0x33,
		0x00, 0x00, 0x00, 0x00,
	}))
}

func (suite *ciscoPolicyNameTLVSuite) TestSerialize() {
	suite.value = CiscoPolicyNameTLV{
		Name: "srte_c_500_ep_87.250.234.173\x00",
	}

	raw, err := suite.value.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x00, 0x02, 0x00, 0x1d, 0x73, 0x72, 0x74, 0x65, 0x5f, 0x63, 0x5f, 0x35, 0x30, 0x30, 0x5f, 0x65,
			0x70, 0x5f, 0x38, 0x37, 0x2e, 0x32, 0x35, 0x30, 0x2e, 0x32, 0x33, 0x34, 0x2e, 0x31, 0x37, 0x33,
			0x00, 0x00, 0x00, 0x00,
		},
		raw,
	)
}

type ciscoCandidatePathPreferenceTLVSuite struct {
	suite.Suite

	value CiscoCandidatePathPreferenceTLV
}

func TestCiscoUnknown3TLVSuite(t *testing.T) {
	suite.Run(t, new(ciscoCandidatePathPreferenceTLVSuite))
}

func (suite *ciscoCandidatePathPreferenceTLVSuite) SetupTest() {
	suite.value = CiscoCandidatePathPreferenceTLV{}
}

func (suite *ciscoCandidatePathPreferenceTLVSuite) TestParse() {
	suite.Require().NoError(suite.value.Parse([]byte{0x00, 0x03, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64}))
	suite.Equal(uint32(100), suite.value.Preference)
}

func (suite *ciscoCandidatePathPreferenceTLVSuite) TestParseError() {
	suite.Error(suite.value.Parse(nil))
	suite.Error(suite.value.Parse([]byte{0x00, 0x03, 0x00, 0x00}))
	suite.Error(suite.value.Parse([]byte{0x00, 0x02, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64}))
}

func (suite *ciscoCandidatePathPreferenceTLVSuite) TestSerialize() {
	suite.value = CiscoCandidatePathPreferenceTLV{
		Preference: 100,
	}

	raw, err := suite.value.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x00, 0x03, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64},
		raw,
	)
}

type ciscoProtectionConstraintTLVSuite struct {
	suite.Suite

	value CiscoProtectionConstraintTLV
}

func TestCiscoUnknown10TLVSuite(t *testing.T) {
	suite.Run(t, new(ciscoProtectionConstraintTLVSuite))
}

func (suite *ciscoProtectionConstraintTLVSuite) SetupTest() {
	suite.value = CiscoProtectionConstraintTLV{}
}

func (suite *ciscoProtectionConstraintTLVSuite) TestParse() {
	suite.Require().NoError(suite.value.Parse([]byte{0x00, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01}))
	suite.Equal(CiscoProtectionConstraintTypeUnprotected, suite.value.Type)
}

func (suite *ciscoProtectionConstraintTLVSuite) TestParseError() {
	suite.Error(suite.value.Parse(nil))
	suite.Error(suite.value.Parse([]byte{0x00, 0x0a, 0x00, 0x00}))
	suite.Error(suite.value.Parse([]byte{0x00, 0x0b, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01}))
}

func (suite *ciscoProtectionConstraintTLVSuite) TestSerialize() {
	suite.value = CiscoProtectionConstraintTLV{Type: CiscoProtectionConstraintTypeUnprotected}

	raw, err := suite.value.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{0x00, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01},
		raw,
	)
}

type ciscoEnterpriseSpecificInformationSuite struct {
	suite.Suite

	info CiscoEnterpriseSpecificInformation
}

func TestCiscoEnterpriseSpecificInformationSuite(t *testing.T) {
	suite.Run(t, new(ciscoEnterpriseSpecificInformationSuite))
}

func (suite *ciscoEnterpriseSpecificInformationSuite) SetupTest() {
	suite.info = CiscoEnterpriseSpecificInformation{}
}

func (suite *ciscoEnterpriseSpecificInformationSuite) TestParse() {
	suite.NoError(suite.info.Parse([]byte{
		0x00, 0x02, 0x00, 0x1d, 0x73, 0x72, 0x74, 0x65, 0x5f, 0x63, 0x5f, 0x35, 0x30, 0x30, 0x5f, 0x65,
		0x70, 0x5f, 0x38, 0x37, 0x2e, 0x32, 0x35, 0x30, 0x2e, 0x32, 0x33, 0x34, 0x2e, 0x31, 0x37, 0x33,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x04, 0x00, 0x00, 0x01, 0xf4, 0x00, 0x03, 0x00, 0x04,
		0x00, 0x00, 0x00, 0x64, 0x00, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
	}))
	suite.Require().NotNil(suite.info.PolicyColor)
	suite.Equal(uint32(500), suite.info.PolicyColor.Color)
	suite.Require().NotNil(suite.info.PolicyName)
	suite.Equal("srte_c_500_ep_87.250.234.173\x00", suite.info.PolicyName.Name)
	suite.Require().NotNil(suite.info.CandidatePathPreference)
	suite.Equal(uint32(100), suite.info.CandidatePathPreference.Preference)
	suite.Require().NotNil(suite.info.ProtectionConstraint)
	suite.Equal(CiscoProtectionConstraintTypeUnprotected, suite.info.ProtectionConstraint.Type)
}

func (suite *ciscoEnterpriseSpecificInformationSuite) TestSerialize() {
	suite.info = CiscoEnterpriseSpecificInformation{
		PolicyColor:             &CiscoPolicyColorTLV{Color: 100},
		PolicyName:              &CiscoPolicyNameTLV{Name: "srte_c_500_ep_87.250.234.173\x00"},
		CandidatePathPreference: &CiscoCandidatePathPreferenceTLV{Preference: 100},
		ProtectionConstraint:    &CiscoProtectionConstraintTLV{Type: CiscoProtectionConstraintTypeUnprotected},
	}
	raw, err := suite.info.Serialize()
	suite.NoError(err)
	suite.Equal(
		[]byte{
			0x00, 0x01, 0x00, 0x04, 0x00, 0x00, 0x00, 0x64, 0x00, 0x02, 0x00, 0x1d, 0x73, 0x72, 0x74, 0x65,
			0x5f, 0x63, 0x5f, 0x35, 0x30, 0x30, 0x5f, 0x65, 0x70, 0x5f, 0x38, 0x37, 0x2e, 0x32, 0x35, 0x30,
			0x2e, 0x32, 0x33, 0x34, 0x2e, 0x31, 0x37, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x04,
			0x00, 0x00, 0x00, 0x64, 0x00, 0x0a, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
		},
		raw,
	)
}
