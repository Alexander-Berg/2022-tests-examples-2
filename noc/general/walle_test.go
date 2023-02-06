package export

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/racktables/netmap/pkg/ports"
)

func TestGetWalleChunks(t *testing.T) {
	testCases := []struct {
		inputDeviceName  string
		outputDeviceName string
		chunks           []Formatter
	}{
		{
			inputDeviceName:  "avex-43a1-old",
			outputDeviceName: "avex-43a1",
		},
		{
			inputDeviceName:  "avex-43a1",
			outputDeviceName: "avex-43a1",
		},
	}
	for _, testCase := range testCases {
		mac := ports.Mac("0042.38c8.e7d1")
		vlan := ports.Vlan(2443)
		port := "gi1/0/4"
		ts := int64(1629480007)

		storage := &ports.MacStorage{
			Macs: map[ports.Mac]*ports.MacData{
				mac: {
					ConnectionCfg: &ports.MacConnectionCfg{
						Port:      ports.MakePortName(testCase.inputDeviceName, port),
						Vlans:     []ports.Vlan{vlan},
						Timestamp: ts,
					},
				},
			},
		}
		chunks := []Formatter{
			&macConnectedVlanTSFormatter{
				mac,
				vlan,
				ports.MakePortName(testCase.outputDeviceName, port),
				ts,
			},
		}

		assert.Equal(t, chunks, getWalleChunks(storage))
	}
}
