package core

import (
	"testing"

	"github.com/stretchr/testify/assert"
	zzap "go.uber.org/zap"
	"go.uber.org/zap/zaptest/observer"
	"google.golang.org/protobuf/encoding/protojson"

	"a.yandex-team.ru/library/go/core/log/zap"
	tt "a.yandex-team.ru/noc/metridat/internal/protos/telemetry_top"
)

const pkt1 = "\x0a\x14\x73\x74\x79\x72\x69\x3a\x38\x37\x2e\x32\x35\x30\x2e\x32" +
	"\x33\x34\x2e\x31\x32\x31\x10\x07\x22\x71\x6c\x6f\x67\x69\x63\x61" +
	"\x6c\x5f\x69\x66\x61\x63\x65\x3a\x2f\x6a\x75\x6e\x6f\x73\x2f\x73" +
	"\x79\x73\x74\x65\x6d\x2f\x6c\x69\x6e\x65\x63\x61\x72\x64\x2f\x69" +
	"\x6e\x74\x65\x72\x66\x61\x63\x65\x2f\x6c\x6f\x67\x69\x63\x61\x6c" +
	"\x2f\x75\x73\x61\x67\x65\x2f\x3a\x2f\x6a\x75\x6e\x6f\x73\x2f\x73" +
	"\x79\x73\x74\x65\x6d\x2f\x6c\x69\x6e\x65\x63\x61\x72\x64\x2f\x69" +
	"\x6e\x74\x65\x72\x66\x61\x63\x65\x2f\x6c\x6f\x67\x69\x63\x61\x6c" +
	"\x2f\x75\x73\x61\x67\x65\x2f\x3a\x50\x46\x45\x28\xa0\xd8\x86\x07" +
	"\x30\xb4\xc4\xc9\xf3\xea\x2e\x38\x01\x40\x01\xaa\x06\xbe\x02\xe2" +
	"\xa4\x01\xb9\x02\x3a\xb6\x02\x0a\x24\x0a\x07\x69\x72\x62\x2e\x35" +
	"\x36\x32\x10\xa2\xbf\x98\xf1\x05\x18\x8d\x08\x2a\x04\x08\x00\x10" +
	"\x00\x32\x04\x08\x00\x10\x00\x3a\x04\x0a\x02\x75\x70\x0a\x24\x0a" +
	"\x07\x69\x72\x62\x2e\x35\x38\x34\x10\xa2\xbf\x98\xf1\x05\x18\x97" +
	"\x08\x2a\x04\x08\x00\x10\x00\x32\x04\x08\x00\x10\x00\x3a\x04\x0a" +
	"\x02\x75\x70\x0a\x24\x0a\x07\x69\x72\x62\x2e\x36\x30\x31\x10\xa2" +
	"\xbf\x98\xf1\x05\x18\xf1\x04\x2a\x04\x08\x00\x10\x00\x32\x04\x08" +
	"\x00\x10\x00\x3a\x04\x0a\x02\x75\x70\x0a\x60\x0a\x0a\x65\x74\x2d" +
	"\x37\x2f\x31\x2f\x30\x2e\x30\x10\x9e\xc0\x98\xf1\x05\x18\xc6\x08" +
	"\x22\x05\x61\x65\x31\x2e\x30\x2a\x1f\x08\x91\x8f\x8e\xad\xf3\xc4" +
	"\x13\x10\xdd\xe3\xc9\xab\xd0\xe2\xe7\xaf\x01\x18\xfd\xab\xb1\xa5" +
	"\xf3\xc4\x13\x20\x94\xe3\xdc\x07\x32\x1b\x08\xfe\xde\xc2\x98\x94" +
	"\x99\x13\x10\xfc\x94\x8e\x85\xa0\xb2\xdc\x67\x18\xfe\xde\xc2\x98" +
	"\x94\x99\x13\x20\x00\x3a\x04\x0a\x02\x75\x70\x0a\x60\x0a\x0a\x65" +
	"\x74\x2d\x37\x2f\x33\x2f\x30\x2e\x30\x10\xad\xc0\x98\xf1\x05\x18" +
	"\xc7\x08\x22\x05\x61\x65\x30\x2e\x30\x2a\x1f\x08\xe2\x8d\xc6\xcb" +
	"\x9b\x9d\x13\x10\x8c\x81\x83\xba\xca\xe0\xab\xad\x01\x18\xa5\xeb" +
	"\xcc\xc8\x9b\x9d\x13\x20\xbd\xa2\xf9\x02\x32\x1b\x08\xb6\x83\xd4" +
	"\xd7\xa2\xc3\x13\x10\xa8\x93\x9d\xba\x96\xa2\xcd\x68\x18\xb6\x83" +
	"\xd4\xd7\xa2\xc3\x13\x20\x00\x3a\x04\x0a\x02\x75\x70"

var pkt1Json = `{
  "systemId":  "styri:87.250.234.121",
  "componentId":  7,
  "sensorName":  "logical_iface:/junos/system/linecard/interface/logical/usage/:/junos/system/linecard/interface/logical/usage/:PFE",
  "sequenceNumber":  14789664,
  "timestamp":  "1609244500532",
  "versionMajor":  1,
  "versionMinor":  1,
  "enterprise":  {
    "[juniperNetworks]":  {
      "[jnprLogicalInterfaceExt]":  {
        "interfaceInfo":  [
          {
            "ifName":  "irb.562",
            "initTime":  "1579556770",
            "snmpIfIndex":  1037,
            "ingressStats":  {
              "ifPackets":  "0",
              "ifOctets":  "0"
            },
            "egressStats":  {
              "ifPackets":  "0",
              "ifOctets":  "0"
            },
            "opState":  {
              "operationalStatus":  "up"
            }
          },
          {
            "ifName":  "irb.584",
            "initTime":  "1579556770",
            "snmpIfIndex":  1047,
            "ingressStats":  {
              "ifPackets":  "0",
              "ifOctets":  "0"
            },
            "egressStats":  {
              "ifPackets":  "0",
              "ifOctets":  "0"
            },
            "opState":  {
              "operationalStatus":  "up"
            }
          },
          {
            "ifName":  "irb.601",
            "initTime":  "1579556770",
            "snmpIfIndex":  625,
            "ingressStats":  {
              "ifPackets":  "0",
              "ifOctets":  "0"
            },
            "egressStats":  {
              "ifPackets":  "0",
              "ifOctets":  "0"
            },
            "opState":  {
              "operationalStatus":  "up"
            }
          },
          {
            "ifName":  "et-7/1/0.0",
            "initTime":  "1579556894",
            "snmpIfIndex":  1094,
            "parentAeName":  "ae1.0",
            "ingressStats":  {
              "ifPackets":  "85930310600593",
              "ifOctets":  "98972629459956189",
              "ifUcastPackets":  "85930294400509",
              "ifMcastPackets":  "16200084"
            },
            "egressStats":  {
              "ifPackets":  "84427297304446",
              "ifOctets":  "58390192068987516",
              "ifUcastPackets":  "84427297304446",
              "ifMcastPackets":  "0"
            },
            "opState":  {
              "operationalStatus":  "up"
            }
          },
          {
            "ifName":  "et-7/3/0.0",
            "initTime":  "1579556909",
            "snmpIfIndex":  1095,
            "parentAeName":  "ae0.0",
            "ingressStats":  {
              "ifPackets":  "84566722316002",
              "ifOctets":  "97582776462655628",
              "ifUcastPackets":  "84566716134821",
              "ifMcastPackets":  "6181181"
            },
            "egressStats":  {
              "ifPackets":  "85874296816054",
              "ifOctets":  "58886618995968424",
              "ifUcastPackets":  "85874296816054",
              "ifMcastPackets":  "0"
            },
            "opState":  {
              "operationalStatus":  "up"
            }
          }
        ]
      }
    }
  }
}`

const pkt2 = "\x0a\x13\x73\x61\x73\x2d\x62\x33\x3a\x31\x37\x32\x2e\x32\x34\x2e" +
	"\x39\x32\x2e\x34\x30\x10\x00\x22\x4d\x69\x66\x61\x63\x65\x3a\x2f" +
	"\x6a\x75\x6e\x6f\x73\x2f\x73\x79\x73\x74\x65\x6d\x2f\x6c\x69\x6e" +
	"\x65\x63\x61\x72\x64\x2f\x69\x6e\x74\x65\x72\x66\x61\x63\x65\x2f" +
	"\x3a\x2f\x6a\x75\x6e\x6f\x73\x2f\x73\x79\x73\x74\x65\x6d\x2f\x6c" +
	"\x69\x6e\x65\x63\x61\x72\x64\x2f\x69\x6e\x74\x65\x72\x66\x61\x63" +
	"\x65\x2f\x3a\x50\x46\x45\x28\xe7\x3c\x30\xb6\x8c\xdf\x9d\xeb\x2e" +
	"\x38\x01\x40\x01\xaa\x06\xad\x0b\xe2\xa4\x01\xa8\x0b\x1a\xa5\x0b" +
	"\x0a\xb3\x02\x0a\x08\x67\x72\x2d\x30\x2f\x30\x2f\x30\x10\x9e\xbe" +
	"\xd4\xfd\x05\x18\xf7\x03\x2a\x18\x08\x00\x10\x00\x18\x00\x20\x00" +
	"\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00" +
	"\x2a\x18\x08\x01\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00" +
	"\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18\x08\x02\x10\x00" +
	"\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00" +
	"\x58\x00\x60\x00\x2a\x18\x08\x03\x10\x00\x18\x00\x20\x00\x28\x00" +
	"\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18" +
	"\x08\x04\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00" +
	"\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18\x08\x05\x10\x00\x18\x00" +
	"\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00" +
	"\x60\x00\x2a\x18\x08\x06\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00" +
	"\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18\x08\x07" +
	"\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00" +
	"\x50\x00\x58\x00\x60\x00\x3a\x12\x08\x00\x10\x00\x18\x00\x20\x00" +
	"\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x42\x12\x08\x00\x10\x00" +
	"\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x4a\x14" +
	"\x08\x00\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00" +
	"\x48\x00\x50\x00\x5a\x02\x55\x50\x68\x00\x70\x00\x78\xa0\x06\x82" +
	"\x01\x04\x08\x00\x10\x00\x0a\xf0\x02\x0a\x08\x65\x74\x2d\x30\x2f" +
	"\x30\x2f\x30\x10\xb5\xbe\xd4\xfd\x05\x18\xff\x03\x22\x03\x61\x65" +
	"\x31\x2a\x1f\x08\x00\x10\xf9\x9f\xd7\x15\x18\x9e\xd1\x99\xda\x10" +
	"\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00" +
	"\x60\x00\x2a\x18\x08\x01\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00" +
	"\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x21\x08\x02" +
	"\x10\x97\xaf\xa8\x8c\x02\x18\xd9\x86\x93\x9c\xec\x06\x20\x00\x28" +
	"\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a" +
	"\x1f\x08\x03\x10\xe7\xcd\xd4\x02\x18\xf3\xa2\xb1\xfa\x02\x20\x00" +
	"\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00" +
	"\x2a\x18\x08\x04\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00" +
	"\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18\x08\x05\x10\x00" +
	"\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00" +
	"\x58\x00\x60\x00\x2a\x18\x08\x06\x10\x00\x18\x00\x20\x00\x28\x00" +
	"\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18" +
	"\x08\x07\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00" +
	"\x48\x00\x50\x00\x58\x00\x60\x00\x3a\x1c\x08\x9b\x8d\x70\x10\xcd" +
	"\xa1\xde\x75\x18\x00\x20\x00\x28\xa7\xea\x03\x30\xc1\xb0\xb0\x02" +
	"\x38\x02\x40\x00\x48\x00\x42\x26\x08\x9e\xea\x96\xa3\x02\x10\xa3" +
	"\xc0\xc3\xfe\xa9\x06\x18\xf4\x11\x20\xe0\xd4\x30\x28\x86\xd5\xa1" +
	"\xa2\x02\x30\x9f\xc3\xb2\x02\x38\xbc\x0a\x40\x00\x48\x00\x4a\x14" +
	"\x08\x00\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00" +
	"\x48\x00\x50\x00\x5a\x02\x55\x50\x68\x01\x70\xea\x99\x0c\x78\xa0" +
	"\x8d\x06\x82\x01\x04\x08\x00\x10\x00\x0a\xfa\x02\x0a\x08\x65\x74" +
	"\x2d\x30\x2f\x30\x2f\x31\x10\xb6\xbe\xd4\xfd\x05\x18\x80\x04\x22" +
	"\x03\x61\x65\x32\x2a\x1f\x08\x00\x10\xcd\xf5\xaa\x16\x18\xfc\xe8" +
	"\xda\x9a\x10\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50" +
	"\x00\x58\x00\x60\x00\x2a\x18\x08\x01\x10\x00\x18\x00\x20\x00\x28" +
	"\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a" +
	"\x22\x08\x02\x10\xcc\x83\x94\xfc\x01\x18\x92\xcf\xce\xe6\x94\x06" +
	"\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\xf2" +
	"\x7c\x60\x00\x2a\x1f\x08\x03\x10\x88\x9e\xd7\x02\x18\xfa\xa2\xcb" +
	"\xf4\x02\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00" +
	"\x58\x00\x60\x00\x2a\x18\x08\x04\x10\x00\x18\x00\x20\x00\x28\x00" +
	"\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18" +
	"\x08\x05\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00" +
	"\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18\x08\x06\x10\x00\x18\x00" +
	"\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00" +
	"\x60\x00\x2a\x18\x08\x07\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00" +
	"\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x3a\x25\x08\xf6" +
	"\x89\xcc\xf6\x15\x10\xf0\x90\xa3\xbf\xf4\x26\x18\xe7\x25\x20\xf8" +
	"\xf3\x31\x28\xea\xdc\xe0\xf5\x15\x30\xc3\xc6\xaf\x02\x38\x00\x40" +
	"\x00\x48\x00\x42\x26\x08\xd9\xef\xd8\x93\x02\x10\xc4\xe6\xa6\xc7" +
	"\xd6\x05\x18\xdd\x12\x20\xb1\x9c\x37\x28\xa0\x87\xe3\x92\x02\x30" +
	"\xa6\x8c\xb3\x02\x38\x98\x0a\x40\x00\x48\x00\x4a\x14\x08\x00\x10" +
	"\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50" +
	"\x00\x5a\x02\x55\x50\x68\x01\x70\x91\xb1\x0c\x78\xa0\x8d\x06\x82" +
	"\x01\x04\x08\x00\x10\x00\x0a\xfc\x02\x0a\x08\x65\x74\x2d\x30\x2f" +
	"\x30\x2f\x32\x10\xb9\xbe\xd4\xfd\x05\x18\x81\x04\x22\x04\x61\x65" +
	"\x31\x30\x2a\x1d\x08\x00\x10\xfa\xa3\x12\x18\xce\xec\xc9\x0e\x20" +
	"\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60" +
	"\x00\x2a\x18\x08\x01\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38" +
	"\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x23\x08\x02\x10" +
	"\x8d\x9a\xec\xc2\x15\x18\x8a\xc6\xfa\x9e\xf7\x2b\x20\x00\x28\x00" +
	"\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\xd6\xf6\x02\x60\x00" +
	"\x2a\x1f\x08\x03\x10\xed\x9f\xd3\x01\x18\xfa\xec\x82\xf6\x01\x20" +
	"\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60" +
	"\x00\x2a\x18\x08\x04\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38" +
	"\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a\x18\x08\x05\x10" +
	"\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50" +
	"\x00\x58\x00\x60\x00\x2a\x18\x08\x06\x10\x00\x18\x00\x20\x00\x28" +
	"\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x58\x00\x60\x00\x2a" +
	"\x18\x08\x07\x10\x00\x18\x00\x20\x00\x28\x00\x30\x00\x38\x00\x40" +
	"\x00\x48\x00\x50\x00\x58\x00\x60\x00\x3a\x24\x08\xd3\xa9\xbe\x88" +
	"\x04\x10\xac\xb4\xc5\xa3\xd6\x0b\x18\xce\x24\x20\x9b\xf1\x66\x28" +
	"\xf4\xbd\xbe\x88\x04\x30\xbe\xa2\x6c\x38\x11\x40\x00\x48\x00\x42" +
	"\x27\x08\xef\xdf\xb8\xc3\x15\x10\xe7\xda\xbf\xe9\xef\x24\x18\xeb" +
	"\x25\x20\xb9\xd1\x30\x28\xbe\xcc\x8f\xc3\x15\x30\x8f\xe3\xbb\x01" +
	"\x38\xf8\xba\x06\x40\x00\x48\x00\x4a\x14\x08\x00\x10\x00\x18\x00" +
	"\x20\x00\x28\x00\x30\x00\x38\x00\x40\x00\x48\x00\x50\x00\x5a\x02" +
	"\x55\x50\x68\x67\x70\xea\xf5\xcf\x91\x04\x78\xa0\x8d\x06\x82\x01" +
	"\x04\x08\x00\x10\x00"

var pkt2Json = `{
  "systemId": "sas-b3:172.24.92.40",
  "componentId": 0,
  "sensorName": "iface:/junos/system/linecard/interface/:/junos/system/linecard/interface/:PFE",
  "sequenceNumber": 7783,
  "timestamp": "1609332934198",
  "versionMajor": 1,
  "versionMinor": 1,
  "enterprise": {
    "[juniperNetworks]": {
      "[jnpr_interface_ext]": {
        "interfaceStats": [
          {
            "ifName": "gr-0/0/0",
            "initTime": "1605705502",
            "snmpIfIndex": 503,
            "egressQueueInfo": [
              {
                "queueNumber": 0,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 1,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 2,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 3,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 4,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 5,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 6,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 7,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              }
            ],
            "ingressStats": {
              "ifPkts": "0",
              "ifOctets": "0",
              "if1secPkts": "0",
              "if1secOctets": "0",
              "ifUcPkts": "0",
              "ifMcPkts": "0",
              "ifBcPkts": "0",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "egressStats": {
              "ifPkts": "0",
              "ifOctets": "0",
              "if1secPkts": "0",
              "if1secOctets": "0",
              "ifUcPkts": "0",
              "ifMcPkts": "0",
              "ifBcPkts": "0",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "ingressErrors": {
              "ifErrors": "0",
              "ifInQdrops": "0",
              "ifInFrameErrors": "0",
              "ifDiscards": "0",
              "ifInRunts": "0",
              "ifInL3Incompletes": "0",
              "ifInL2chanErrors": "0",
              "ifInL2MismatchTimeouts": "0",
              "ifInFifoErrors": "0",
              "ifInResourceErrors": "0"
            },
            "ifOperationalStatus": "UP",
            "ifTransitions": "0",
            "ifLastChange": 0,
            "ifHighSpeed": 800,
            "egressErrors": {
              "ifErrors": "0",
              "ifDiscards": "0"
            }
          },
          {
            "ifName": "et-0/0/0",
            "initTime": "1605705525",
            "snmpIfIndex": 511,
            "parentAeName": "ae1",
            "egressQueueInfo": [
              {
                "queueNumber": 0,
                "packets": "45469689",
                "bytes": "4484130974",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 1,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 2,
                "packets": "562698135",
                "bytes": "235208491865",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 3,
                "packets": "5580519",
                "bytes": "793530739",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 4,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 5,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 6,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 7,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              }
            ],
            "ingressStats": {
              "ifPkts": "1836699",
              "ifOctets": "246911181",
              "if1secPkts": "0",
              "if1secOctets": "0",
              "ifUcPkts": "62759",
              "ifMcPkts": "4986945",
              "ifBcPkts": "2",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "egressStats": {
              "ifPkts": "610645278",
              "ifOctets": "217429631011",
              "if1secPkts": "2292",
              "if1secOctets": "797280",
              "ifUcPkts": "608725638",
              "ifMcPkts": "5022111",
              "ifBcPkts": "1340",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "ingressErrors": {
              "ifErrors": "0",
              "ifInQdrops": "0",
              "ifInFrameErrors": "0",
              "ifDiscards": "0",
              "ifInRunts": "0",
              "ifInL3Incompletes": "0",
              "ifInL2chanErrors": "0",
              "ifInL2MismatchTimeouts": "0",
              "ifInFifoErrors": "0",
              "ifInResourceErrors": "0"
            },
            "ifOperationalStatus": "UP",
            "ifTransitions": "1",
            "ifLastChange": 199914,
            "ifHighSpeed": 100000,
            "egressErrors": {
              "ifErrors": "0",
              "ifDiscards": "0"
            }
          },
          {
            "ifName": "et-0/0/1",
            "initTime": "1605705526",
            "snmpIfIndex": 512,
            "parentAeName": "ae2",
            "egressQueueInfo": [
              {
                "queueNumber": 0,
                "packets": "46840525",
                "bytes": "4350981244",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 1,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 2,
                "packets": "528810444",
                "bytes": "211742336914",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "15986",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 3,
                "packets": "5623560",
                "bytes": "781373818",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 4,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 5,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 6,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 7,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              }
            ],
            "ingressStats": {
              "ifPkts": "5885854966",
              "ifOctets": "1336941267056",
              "if1secPkts": "4839",
              "if1secOctets": "817656",
              "ifUcPkts": "5884096106",
              "ifMcPkts": "4973379",
              "ifBcPkts": "0",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "egressStats": {
              "ifPkts": "578172889",
              "ifOctets": "195033674564",
              "if1secPkts": "2397",
              "if1secOctets": "904753",
              "ifUcPkts": "576242592",
              "ifMcPkts": "5031462",
              "ifBcPkts": "1304",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "ingressErrors": {
              "ifErrors": "0",
              "ifInQdrops": "0",
              "ifInFrameErrors": "0",
              "ifDiscards": "0",
              "ifInRunts": "0",
              "ifInL3Incompletes": "0",
              "ifInL2chanErrors": "0",
              "ifInL2MismatchTimeouts": "0",
              "ifInFifoErrors": "0",
              "ifInResourceErrors": "0"
            },
            "ifOperationalStatus": "UP",
            "ifTransitions": "1",
            "ifLastChange": 202897,
            "ifHighSpeed": 100000,
            "egressErrors": {
              "ifErrors": "0",
              "ifDiscards": "0"
            }
          },
          {
            "ifName": "et-0/0/2",
            "initTime": "1605705529",
            "snmpIfIndex": 513,
            "parentAeName": "ae10",
            "egressQueueInfo": [
              {
                "queueNumber": 0,
                "packets": "299514",
                "bytes": "30570062",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 1,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 2,
                "packets": "5777329421",
                "bytes": "1509477491466",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "47958",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 3,
                "packets": "3461101",
                "bytes": "515946106",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 4,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 5,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 6,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              },
              {
                "queueNumber": 7,
                "packets": "0",
                "bytes": "0",
                "tailDropPackets": "0",
                "rlDropPackets": "0",
                "rlDropBytes": "0",
                "redDropPackets": "0",
                "redDropBytes": "0",
                "avgBufferOccupancy": "0",
                "curBufferOccupancy": "0",
                "peakBufferOccupancy": "0",
                "allocatedBufferSize": "0"
              }
            ],
            "ingressStats": {
              "ifPkts": "1091540179",
              "ifOctets": "401117108780",
              "if1secPkts": "4686",
              "if1secOctets": "1685659",
              "ifUcPkts": "1091542772",
              "ifMcPkts": "1773886",
              "ifBcPkts": "17",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "egressStats": {
              "ifPkts": "5778583535",
              "ifOctets": "1266968161639",
              "if1secPkts": "4843",
              "if1secOctets": "796857",
              "ifUcPkts": "5777909310",
              "ifMcPkts": "3076495",
              "ifBcPkts": "105848",
              "ifError": "0",
              "ifPausePkts": "0"
            },
            "ingressErrors": {
              "ifErrors": "0",
              "ifInQdrops": "0",
              "ifInFrameErrors": "0",
              "ifDiscards": "0",
              "ifInRunts": "0",
              "ifInL3Incompletes": "0",
              "ifInL2chanErrors": "0",
              "ifInL2MismatchTimeouts": "0",
              "ifInFifoErrors": "0",
              "ifInResourceErrors": "0"
            },
            "ifOperationalStatus": "UP",
            "ifTransitions": "103",
            "ifLastChange": 1110702826,
            "ifHighSpeed": 100000,
            "egressErrors": {
              "ifErrors": "0",
              "ifDiscards": "0"
            }
          }
        ]
      }
    }
  }
}`

type jtiAppTest struct {
	jtiApp *JTIPoller
	olog   *observer.ObservedLogs
}

func newTestJTIApp() *jtiAppTest {
	zlcore, logged := observer.New(zzap.ErrorLevel)
	logger := zap.NewWithCore(zlcore)
	poller := &JTIPoller{log: logger}
	return &jtiAppTest{jtiApp: poller, olog: logged}
}

func TestJTILogicalIface(t *testing.T) {
	buffer := []byte(pkt1)
	jtiTestApp := newTestJTIApp()
	tsInt, _, err := jtiTestApp.jtiApp.Decode(RawData{Data: buffer})
	if tsInt == nil {
		t.FailNow()
	}
	ts := (*tsInt).(*tt.TelemetryStream)
	assert.NoError(t, err)
	q := protojson.Format(ts)
	assert.JSONEq(t, q, pkt1Json)
}

func TestJTIPort(t *testing.T) {
	buffer := []byte(pkt1)
	jtiTestApp := newTestJTIApp()
	tsInt, _, err := jtiTestApp.jtiApp.Decode(RawData{Data: buffer})
	if tsInt == nil {
		t.FailNow()
	}
	ts := (*tsInt).(*tt.TelemetryStream)
	assert.NoError(t, err)
	q := protojson.MarshalOptions{Multiline: true, EmitUnpopulated: false}.Format(ts)
	assert.JSONEq(t, q, pkt1Json)
}

func TestJTILogicPort(t *testing.T) {
	buffer := []byte(pkt2)
	jtiTestApp := newTestJTIApp()
	tsInt, cont, err := jtiTestApp.jtiApp.Decode(RawData{Data: buffer})
	if tsInt == nil {
		t.FailNow()
	}
	ts := (*tsInt).(*tt.TelemetryStream)
	assert.NoError(t, err)
	q := protojson.MarshalOptions{Multiline: true, EmitUnpopulated: false}.Format(ts)
	assert.JSONEq(t, q, pkt2Json)
	assert.Len(t, cont, 40)
}
