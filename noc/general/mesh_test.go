package racktables

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/valyala/fastjson"
)

func TestMeshUnmarshal(t *testing.T) {
	j, err := fastjson.Parse(`
	{
		"lab-vla-1s1": {
			"sessions": [
					{
							"local": {
									"asnum": "65100.64001",
									"bfd": true,
									"device": "lab-vla-1s1",
									"export_policy": "TOR_EXPORT_S1",
									"ifname": "100GE1/0/1",
									"import_policy": "TOR_IMPORT_S1",
									"ll": "fe80::e1:d1",
									"module": 64,
									"name": "TOR",
									"parallel_count": 1,
									"peers_min": 2,
									"portname": "100GE1/0/1",
									"router_id": "172.24.212.122",
									"send_community": true,
									"upstream": false,
									"vrf": ""
							},
							"remote": {
									"advertise_inactive": true,
									"asnum": "65100.65001",
									"bfd": true,
									"device": "lab-vla-1d1",
									"export_policy": "S1_EXPORT_TOR",
									"ifname": "Ethernet2/1",
									"import_policy": "S1_IMPORT_TOR",
									"ll": "fe80::1:c1",
									"name": "S1",
									"parallel_count": 1,
									"passive": true,
									"portname": "Ethernet2/1",
									"router_id": "1.0.1.1",
									"send_community": true,
									"uniq_pod": true,
									"upstream": true,
									"vrf": ""
							}
					},
					{
							"local": {
									"asnum": "65100.64001",
									"bfd": true,
									"device": "lab-vla-1s1",
									"export_policy": "TOR_EXPORT_S1",
									"ifname": "100GE1/0/2",
									"import_policy": "TOR_IMPORT_S1",
									"ll": "fe80::e1:d2",
									"module": 64,
									"name": "TOR",
									"parallel_count": 1,
									"peers_min": 2,
									"portname": "100GE1/0/2",
									"router_id": "172.24.212.122",
									"send_community": true,
									"upstream": false,
									"vrf": ""
							},
							"remote": {
									"advertise_inactive": true,
									"asnum": "65100.65001",
									"bfd": true,
									"device": "lab-vla-1d2",
									"export_policy": "S1_EXPORT_TOR",
									"ifname": "100GE1/0/2",
									"import_policy": "S1_IMPORT_TOR",
									"ll": "fe80::1:c2",
									"name": "S1",
									"parallel_count": 1,
									"passive": true,
									"portname": "100GE1/0/2",
									"router_id": "1.0.1.2",
									"send_community": true,
									"uniq_pod": true,
									"upstream": true,
									"vrf": ""
							}
					}
			]
		}
	}
	`)
	assert.NoError(t, err, "Failed to parse testcase json")
	actual, err := meshDevicesUnmarshal(j)
	assert.NoError(t, err, "Failed to unmarshall testcase json %v", err)
	assert.Equal(t, MeshDevices{
		"lab-vla-1s1": MeshSessions{
			Sessions: []MeshPair{
				{
					Local: MeshPeer{
						Asnum:         "65100.64001",
						Bfd:           true,
						Device:        "lab-vla-1s1",
						Ifname:        "100GE1/0/1",
						ImportPolicy:  "TOR_IMPORT_S1",
						ExportPolicy:  "TOR_EXPORT_S1",
						LL:            "fe80::e1:d1",
						Module:        64,
						Name:          "TOR",
						ParallelCount: 1,
						PeersMin:      2,
						Portname:      "100GE1/0/1",
						RouterID:      "172.24.212.122",
						SendCommunity: true,
						Upstream:      false,
						Vrf:           "",
					},
					Remote: MeshPeer{
						Asnum:             "65100.65001",
						Bfd:               true,
						Device:            "lab-vla-1d1",
						ExportPolicy:      "S1_EXPORT_TOR",
						Ifname:            "Ethernet2/1",
						ImportPolicy:      "S1_IMPORT_TOR",
						LL:                "fe80::1:c1",
						Name:              "S1",
						ParallelCount:     1,
						Portname:          "Ethernet2/1",
						RouterID:          "1.0.1.1",
						SendCommunity:     true,
						UniqPod:           true,
						Passive:           true,
						AdvertiseInactive: true,
						Upstream:          true,
						Vrf:               "",
					},
				},
				{
					Local: MeshPeer{
						Asnum:         "65100.64001",
						Bfd:           true,
						Device:        "lab-vla-1s1",
						Ifname:        "100GE1/0/2",
						ImportPolicy:  "TOR_IMPORT_S1",
						ExportPolicy:  "TOR_EXPORT_S1",
						LL:            "fe80::e1:d2",
						Module:        64,
						Name:          "TOR",
						ParallelCount: 1,
						PeersMin:      2,
						Portname:      "100GE1/0/2",
						RouterID:      "172.24.212.122",
						SendCommunity: true,
						Upstream:      false,
						Vrf:           "",
					},
					Remote: MeshPeer{
						Asnum:             "65100.65001",
						Bfd:               true,
						Device:            "lab-vla-1d2",
						ExportPolicy:      "S1_EXPORT_TOR",
						Ifname:            "100GE1/0/2",
						ImportPolicy:      "S1_IMPORT_TOR",
						LL:                "fe80::1:c2",
						Name:              "S1",
						ParallelCount:     1,
						Portname:          "100GE1/0/2",
						RouterID:          "1.0.1.2",
						SendCommunity:     true,
						UniqPod:           true,
						Passive:           true,
						AdvertiseInactive: true,
						Upstream:          true,
						Vrf:               "",
					},
				},
			},
		},
	}, actual)
}

func TestMeshErrorUnmarshal(t *testing.T) {
	j, err := fastjson.Parse(`
	{
		"lab-vla-1s1": {
			"sessions": [
					{
					}
			]
		}
	}
	`)
	assert.NoError(t, err, "Failed to parse testcase json")
	_, err = meshDevicesUnmarshal(j)
	assert.Error(t, err, "failed to find 'local' for key 'lab-vla-1s1' in element '0'")
}
