package bgp

import (
	"testing"

	"github.com/stretchr/testify/suite"
)

// TopologyTestSuite contains test cases for topology
type TopologyTestSuite struct {
	suite.Suite

	topology            Topology
	fullLink            Link
	localPartLink       Link
	remotePartLink      Link
	missPartsLink       Link
	missPartsLinkUnique Link
}

// TestTopologyTestSuite runs TopologyTestSuite
func TestTopologyTestSuite(t *testing.T) {
	suite.Run(t, new(TopologyTestSuite))
}

func (suite *TopologyTestSuite) SetupSuite() {
	suite.fullLink = Link{
		LocalRouterID:    "local-id",
		RemoteRouterID:   "remote-id",
		InterfaceAddress: "local-address",
		NeighborAddress:  "remote-address",
	}

	suite.localPartLink = Link{
		LocalRouterID:    "local-id",
		RemoteRouterID:   "remote-id",
		InterfaceAddress: "local-address",
		NeighborAddress:  "",
	}

	suite.remotePartLink = Link{
		LocalRouterID:    "local-id",
		RemoteRouterID:   "remote-id",
		InterfaceAddress: "",
		NeighborAddress:  "remote-address",
	}

	suite.missPartsLink = Link{
		LocalRouterID:    "local-id",
		RemoteRouterID:   "remote-id",
		InterfaceAddress: "",
		NeighborAddress:  "",
	}

	suite.missPartsLinkUnique = Link{
		LocalRouterID:    "unique local-id",
		RemoteRouterID:   "unique remote-id",
		InterfaceAddress: "",
		NeighborAddress:  "",
	}
}

func (suite *TopologyTestSuite) SetupTest() {
	suite.topology = Topology{
		Nodes:                make(map[string]Node),
		Links:                make(map[string]Link),
		PrefixIPv4s:          make(map[string]map[uint32]PrefixIPv4),
		linksByLocalAddress:  make(map[string]string),
		linksByRemoteAddress: make(map[string]string),
	}
}

// TestLinkID checks formatting id() by link
func (suite *TopologyTestSuite) TestLinkID() {
	suite.Require().Equal("local-id->remote-id:local-address->remote-address", suite.fullLink.id())
	suite.Require().Equal("local-id->remote-id:local-address->", suite.localPartLink.id())
	suite.Require().Equal("local-id->remote-id:->remote-address", suite.remotePartLink.id())
	suite.Require().Equal("local-id->remote-id:->", suite.missPartsLink.id())
}

// TestDeduplicationPartAfterFull checks adding part filled links after a full link
func (suite *TopologyTestSuite) TestDeduplicationPartAfterFull() {
	suite.topology.addLink(suite.fullLink)
	suite.Require().Len(suite.topology.Links, 1)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)

	// Check that adding full copy will be ignored
	suite.topology.addLink(suite.fullLink)
	suite.Require().Len(suite.topology.Links, 1)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)

	// Check that adding link that duplicates full link but has remoteAddress missed will be ignored
	suite.topology.addLink(suite.localPartLink)
	suite.Require().Len(suite.topology.Links, 1)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)

	// Check that adding link that duplicates full link but has localAddress missed will be ignored
	suite.topology.addLink(suite.remotePartLink)
	suite.Require().Len(suite.topology.Links, 1)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)
}

// TestDeduplicationFullAfterPart checks adding a full link after adding different part filled links
func (suite *TopologyTestSuite) TestDeduplicationFullAfterPart() {
	// Check that adding part link with only local address will be added to links and index by local address
	suite.topology.addLink(suite.localPartLink)
	suite.Require().Len(suite.topology.Links, 1)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 0)

	// Check that adding part link with only remote address will be also added to links and index by remotes address
	suite.topology.addLink(suite.remotePartLink)
	suite.Require().Len(suite.topology.Links, 2)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)

	// Check that full link will replace both previously added links
	suite.topology.addLink(suite.fullLink)
	suite.Require().Len(suite.topology.Links, 1)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)
}

// TestMissDeduplicationForMissLink checks that deduplication passes links with both missed local and remotes addresses
func (suite *TopologyTestSuite) TestMissDeduplicationForMissLink() {
	// Check that link without local and remote addresses will be added to links and not added to any indexes
	suite.topology.addLink(suite.missPartsLink)
	suite.Require().Len(suite.topology.Links, 1)
	suite.Require().Len(suite.topology.linksByLocalAddress, 0)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 0)

	// Check that adding part link with only local address will be added to links and index by local address
	suite.topology.addLink(suite.localPartLink)
	suite.Require().Len(suite.topology.Links, 2)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 0)

	// Check that adding part link with only remote address will be also added to links and index by remotes address
	suite.topology.addLink(suite.remotePartLink)
	suite.Require().Len(suite.topology.Links, 3)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)

	// Check that full link will replace both previously added links
	suite.topology.addLink(suite.fullLink)
	suite.Require().Len(suite.topology.Links, 2)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)

	// Check that links without local and remote addresses are deduplicated between each other
	suite.topology.addLink(suite.missPartsLink)
	suite.Require().Len(suite.topology.Links, 2)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)

	// Check that links without local and remote addresses but with different local and remote routers id
	// are not deduplicated between each other
	suite.topology.addLink(suite.missPartsLinkUnique)
	suite.Require().Len(suite.topology.Links, 3)
	suite.Require().Len(suite.topology.linksByLocalAddress, 1)
	suite.Require().Len(suite.topology.linksByRemoteAddress, 1)
}
