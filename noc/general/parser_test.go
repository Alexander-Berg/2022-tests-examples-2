package peersreport_test

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/peersreport"
)

func TestParsePeer_ParsePeerName(t *testing.T) {
	parse := peersreport.NewParsePeerString()
	name, err := parse.ParsePeerString("Ya.Cloud 20GE@MAR %peer% %NOC-16295%")
	require.NoError(t, err)
	assert.Equal(t, peersreport.PeerName{
		OperatorName: "Ya.Cloud",
		Bandwidth:    20 * 1e9,
		Location:     "MAR",
		LinkType:     ptr.String("peer"),
	}, *name)
}

func TestParsePeer_ParsePeerName2(t *testing.T) {
	parse := peersreport.NewParsePeerString()
	name, err := parse.ParsePeerString("CERN 10GE@FRA via Level3 %peer%")
	require.NoError(t, err)
	assert.Equal(t, peersreport.PeerName{
		OperatorName: "CERN",
		Bandwidth:    10 * 1e9,
		Location:     "FRA",
		LinkType:     ptr.String("peer"),
	}, *name)
}

func TestParsePeer_ParsePeerName3(t *testing.T) {
	parse := peersreport.NewParsePeerString()
	name, err := parse.ParsePeerString("Rascom 100GE@RAD %cdn_client%")
	require.NoError(t, err)
	assert.Equal(t, peersreport.PeerName{
		OperatorName: "Rascom",
		Bandwidth:    100 * 1e9,
		Location:     "RAD",
		LinkType:     ptr.String("cdn_client"),
	}, *name)
}

func TestParsePeer_ParsePeerName4(t *testing.T) {
	parse := peersreport.NewParsePeerString()
	name, err := parse.ParsePeerString("NetbyNet 10GE@SPBBM18 peer")
	require.NoError(t, err)
	assert.Equal(t, peersreport.PeerName{
		OperatorName: "NetbyNet",
		Bandwidth:    10 * 1e9,
		Location:     "SPBBM18",
		LinkType:     ptr.String("peer"),
	}, *name)
}

func TestParsePeer_ParsePeerName5(t *testing.T) {
	parse := peersreport.NewParsePeerString()
	name, err := parse.ParsePeerString("<operator> 20Gbps@HBRRT")
	require.NoError(t, err)
	assert.Equal(t, peersreport.PeerName{
		OperatorName: "<operator>",
		Bandwidth:    20 * 1e9,
		Location:     "HBRRT",
		LinkType:     nil,
	}, *name)
}

func TestParsePeer_ParsePeerName6(t *testing.T) {
	parse := peersreport.NewParsePeerString()
	name, err := parse.ParsePeerString("Seabone for CDN 100GE@AMS %strm_transit%")
	require.NoError(t, err)
	assert.Equal(t, peersreport.PeerName{
		OperatorName: "Seabone for CDN",
		Bandwidth:    100 * 1e9,
		Location:     "AMS",
		LinkType:     ptr.String("strm_transit"),
	}, *name)
}
