package models

import (
	"net"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBGPPeer_Equal(t *testing.T) {
	peer := &BGPPeer{"hostname", "hostname.example.com", net.ParseIP("192.0.2.1"), "MOON"}
	samePeer := &BGPPeer{"hostname", "hostname.example.com", net.ParseIP("192.0.2.1"), "MOON"}
	peerButDifferentIP := &BGPPeer{"hostname", "hostname.example.com", net.ParseIP("192.0.2.2"), "MOON"}
	peerButDifferentDC := &BGPPeer{"hostname", "hostname.example.com", net.ParseIP("192.0.2.1"), "PLUTO"}
	differentPeerButSameIP := &BGPPeer{"host", "host.example.com", net.ParseIP("192.0.2.1"), "PLUTO"}

	assert.True(t, peer.Equal(samePeer))
	assert.True(t, samePeer.Equal(peer))
	assert.False(t, peer.Equal(peerButDifferentIP))
	assert.False(t, peer.Equal(peerButDifferentDC))
	assert.False(t, peer.Equal(differentPeerButSameIP))
}

func TestBGPPeerCatalog_DiffWith(t *testing.T) {
	peer1 := &BGPPeer{"peer1", "peer1.example.com", net.ParseIP("192.0.2.1"), "MOON"}
	peer2 := &BGPPeer{"peer2", "peer2.example.com", net.ParseIP("192.0.2.2"), "MOON"}
	peer3 := &BGPPeer{"peer3", "peer3.example.com", net.ParseIP("192.0.2.3"), "MOON"}
	peer4 := &BGPPeer{"peer4", "peer4.example.com", net.ParseIP("192.0.2.4"), "MOON"}
	peer5 := &BGPPeer{"peer5", "peer5.example.com", net.ParseIP("192.0.2.5"), "MOON"}

	oldCatalog := &BGPPeerCatalog{}
	newCatalog := &BGPPeerCatalog{}
	sameOldCatalog := &BGPPeerCatalog{}

	oldCatalog.Add(peer1)
	oldCatalog.Add(peer3)
	oldCatalog.Add(peer5)

	sameOldCatalog.Add(peer1)
	sameOldCatalog.Add(peer3)
	sameOldCatalog.Add(peer5)

	newCatalog.Add(peer1)
	newCatalog.Add(peer2)
	newCatalog.Add(peer4)
	newCatalog.Add(peer5)

	added, removed := newCatalog.DiffWith(oldCatalog)
	sameAdded, sameRemoved := oldCatalog.DiffWith(sameOldCatalog)

	assert.Len(t, added, 2)
	assert.Len(t, removed, 1)

	assert.Len(t, sameAdded, 0)
	assert.Len(t, sameRemoved, 0)
}
