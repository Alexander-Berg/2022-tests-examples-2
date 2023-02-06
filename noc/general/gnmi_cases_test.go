package core

import (
	"testing"

	"github.com/golang/protobuf/proto"
	"github.com/openconfig/gnmi/proto/gnmi"
	"github.com/stretchr/testify/assert"
)

func TestUpdateDecode(t *testing.T) {
	tests := []struct {
		name     string
		data     []byte
		expected string
	}{
		{
			name: "juniper /interfaces/interface json",
			data: []uint8{8, 192, 205, 247, 193, 229, 205, 247, 215, 22, 18, 90, 26, 12, 10, 10, 105, 110, 116, 101,
				114, 102, 97, 99, 101, 115, 26, 29, 10, 9, 105, 110, 116, 101, 114, 102, 97, 99, 101, 18, 16, 10, 4,
				110, 97, 109, 101, 18, 8, 101, 116, 45, 48, 47, 48, 47, 49, 26, 15, 10, 13, 115, 117, 98, 105, 110,
				116, 101, 114, 102, 97, 99, 101, 115, 26, 26, 10, 12, 115, 117, 98, 105, 110, 116, 101, 114, 102, 97,
				99, 101, 18, 10, 10, 5, 105, 110, 100, 101, 120, 18, 1, 49, 34, 29, 10, 13, 26, 11, 10, 9, 105, 110,
				105, 116, 45, 116, 105, 109, 101, 26, 12, 82, 10, 49, 54, 51, 49, 56, 55, 56, 57, 49, 52, 34, 42, 10,
				27, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 16, 10, 14, 112, 97, 114, 101, 110, 116, 45, 97, 101, 45,
				110, 97, 109, 101, 26, 11, 82, 9, 34, 97, 101, 49, 48, 49, 46, 49, 34, 34, 56, 10, 35, 26, 7, 10, 5,
				115, 116, 97, 116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 12, 10, 10, 111, 117,
				116, 45, 111, 99, 116, 101, 116, 115, 26, 17, 82, 15, 49, 48, 51, 57, 52, 48, 53, 49, 53, 51, 49, 51,
				52, 57, 53, 34, 50, 10, 33, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116,
				101, 114, 115, 26, 10, 10, 8, 111, 117, 116, 45, 112, 107, 116, 115, 26, 13, 82, 11, 49, 52, 55, 56, 55,
				51, 48, 51, 50, 55, 57, 34, 48, 10, 41, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10, 10, 8, 99, 111,
				117, 110, 116, 101, 114, 115, 26, 18, 10, 16, 111, 117, 116, 45, 117, 110, 105, 99, 97, 115, 116, 45,
				112, 107, 116, 115, 26, 3, 82, 1, 48, 34, 50, 10, 43, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10, 10,
				8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 20, 10, 18, 111, 117, 116, 45, 109, 117, 108, 116, 105,
				99, 97, 115, 116, 45, 112, 107, 116, 115, 26, 3, 82, 1, 48, 34, 55, 10, 34, 26, 7, 10, 5, 115, 116, 97,
				116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 11, 10, 9, 105, 110, 45, 111, 99,
				116, 101, 116, 115, 26, 17, 82, 15, 49, 50, 48, 53, 55, 54, 53, 56, 51, 56, 52, 57, 48, 51, 55, 34, 49,
				10, 32, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26,
				9, 10, 7, 105, 110, 45, 112, 107, 116, 115, 26, 13, 82, 11, 49, 54, 51, 53, 57, 56, 51, 54, 53, 49, 55,
				34, 47, 10, 40, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114,
				115, 26, 17, 10, 15, 105, 110, 45, 117, 110, 105, 99, 97, 115, 116, 45, 112, 107, 116, 115, 26, 3, 82,
				1, 48, 34, 49, 10, 42, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101,
				114, 115, 26, 19, 10, 17, 105, 110, 45, 109, 117, 108, 116, 105, 99, 97, 115, 116, 45, 112, 107, 116,
				115, 26, 3, 82, 1, 48},
			expected: `
[
  {
    "series": "/interfaces/interface/subinterfaces/subinterface",
    "ts": 1634769755267,
    "tags": {
      "/interfaces/interface/name": "et-0/0/1",
      "/interfaces/interface/subinterfaces/subinterface/index": "1"
    },
    "values": {
      "/interfaces/interface/subinterfaces/subinterface/init-time": 1631878914,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-multicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-octets": 120576583849037,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-pkts": 16359836517,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-unicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-multicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-octets": 103940515313495,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-pkts": 14787303279,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-unicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/parent-ae-name": "ae101.1"
    }
  }
]`,
		}, {
			name: "juniper /interfaces/interface proto",
			data: []uint8{8, 128, 216, 210, 245, 209, 235, 129, 216, 22, 18, 90, 26, 12, 10, 10, 105, 110, 116, 101,
				114, 102, 97, 99, 101, 115, 26, 29, 10, 9, 105, 110, 116, 101, 114, 102, 97, 99, 101, 18, 16, 10, 4,
				110, 97, 109, 101, 18, 8, 101, 116, 45, 48, 47, 48, 47, 49, 26, 15, 10, 13, 115, 117, 98, 105, 110, 116,
				101, 114, 102, 97, 99, 101, 115, 26, 26, 10, 12, 115, 117, 98, 105, 110, 116, 101, 114, 102, 97, 99,
				101, 18, 10, 10, 5, 105, 110, 100, 101, 120, 18, 1, 49, 34, 23, 10, 13, 26, 11, 10, 9, 105, 110, 105,
				116, 45, 116, 105, 109, 101, 26, 6, 24, 130, 254, 145, 138, 6, 34, 40, 10, 27, 26, 7, 10, 5, 115, 116,
				97, 116, 101, 26, 16, 10, 14, 112, 97, 114, 101, 110, 116, 45, 97, 101, 45, 110, 97, 109, 101, 26, 9,
				10, 7, 97, 101, 49, 48, 49, 46, 49, 34, 47, 10, 35, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10, 10,
				8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 12, 10, 10, 111, 117, 116, 45, 111, 99, 116, 101, 116,
				115, 26, 8, 24, 144, 172, 180, 217, 228, 135, 24, 34, 43, 10, 33, 26, 7, 10, 5, 115, 116, 97, 116, 101,
				26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 10, 10, 8, 111, 117, 116, 45, 112, 107, 116,
				115, 26, 6, 24, 241, 237, 199, 130, 56, 34, 47, 10, 41, 26, 7, 10, 5, 115, 116, 97, 116, 101, 26, 10,
				10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 18, 10, 16, 111, 117, 116, 45, 117, 110, 105, 99, 97,
				115, 116, 45, 112, 107, 116, 115, 26, 2, 24, 0, 34, 49, 10, 43, 26, 7, 10, 5, 115, 116, 97, 116, 101,
				26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 20, 10, 18, 111, 117, 116, 45, 109, 117, 108,
				116, 105, 99, 97, 115, 116, 45, 112, 107, 116, 115, 26, 2, 24, 0, 34, 46, 10, 34, 26, 7, 10, 5, 115,
				116, 97, 116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 11, 10, 9, 105, 110, 45,
				111, 99, 116, 101, 116, 115, 26, 8, 24, 131, 178, 130, 170, 154, 238, 27, 34, 42, 10, 32, 26, 7, 10, 5,
				115, 116, 97, 116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 9, 10, 7, 105, 110,
				45, 112, 107, 116, 115, 26, 6, 24, 231, 249, 169, 247, 61, 34, 46, 10, 40, 26, 7, 10, 5, 115, 116, 97,
				116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 17, 10, 15, 105, 110, 45, 117, 110,
				105, 99, 97, 115, 116, 45, 112, 107, 116, 115, 26, 2, 24, 0, 34, 48, 10, 42, 26, 7, 10, 5, 115, 116, 97,
				116, 101, 26, 10, 10, 8, 99, 111, 117, 110, 116, 101, 114, 115, 26, 19, 10, 17, 105, 110, 45, 109, 117,
				108, 116, 105, 99, 97, 115, 116, 45, 112, 107, 116, 115, 26, 2, 24, 0},
			expected: `
[
  {
    "series": "/interfaces/interface/subinterfaces/subinterface",
    "ts": 1634814761264,
    "tags": {
      "/interfaces/interface/name": "et-0/0/1",
      "/interfaces/interface/subinterfaces/subinterface/index": "1"
    },
    "values": {
      "/interfaces/interface/subinterfaces/subinterface/init-time": 1631878914,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-multicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-octets": 122533894461699,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-pkts": 16624811239,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/in-unicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-multicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-octets": 105820665484816,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-pkts": 15037757169,
      "/interfaces/interface/subinterfaces/subinterface/state/counters/out-unicast-pkts": 0,
      "/interfaces/interface/subinterfaces/subinterface/state/parent-ae-name": "ae101.1"
    }
  }
]
`,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var response gnmi.Notification
			err := proto.Unmarshal(tt.data, &response)
			assert.NoError(t, err, tt.name)
			conn := newGNMITestInstance(t, USERNAME, PASSWORD, []*gnmi.Subscription{})
			res, _, err := conn.gnmi.decodeGnmiUpdate(&response)
			assert.NoError(t, err, tt.name)
			resJSON, err := res.FormatJSON()
			assert.NoError(t, err, tt.name)
			assert.JSONEq(t, resJSON, tt.expected, tt.name)
		})
	}
}
