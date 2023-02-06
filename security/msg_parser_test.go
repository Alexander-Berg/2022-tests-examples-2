package parser

import (
	"bytes"
	"net"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestParseRuleset(t *testing.T) {
	cases := []struct {
		in   string
		rule Rule
	}{
		{
			in: "i172.28.122.143;1645803989;asinamati;wireless",
			rule: Rule{
				Timestamp:  1645803989,
				Kind:       RuleKindIPv4,
				Entrypoint: EntrypointWireless,
				Username:   "asinamati",
				IP:         net.ParseIP("172.28.122.143"),
			},
		},
		{
			in: "m88:e9:fe:60:d8:a9;1645807160;forx;wireless",
			rule: Rule{
				Timestamp:  1645807160,
				Kind:       RuleKindMAC,
				Entrypoint: EntrypointWireless,
				Username:   "forx",
				MAC:        []byte{0x88, 0xe9, 0xfe, 0x60, 0xd8, 0xa9},
			},
		},
		{
			in: "i2a02:6b8:0:402:5861:3b8:cb1e:9a31;1645810672;alisasnooki;vpn",
			rule: Rule{
				Timestamp:  1645810672,
				Kind:       RuleKindIPv6,
				Entrypoint: EntrypointVPN,
				Username:   "alisasnooki",
				IP:         net.ParseIP("2a02:6b8:0:402:5861:3b8:cb1e:9a31"),
			},
		},
	}

	for _, tc := range cases {
		t.Run(tc.in, func(t *testing.T) {
			ts := time.Now().Unix()
			in := strings.NewReader(tc.in)
			ruleset, err := parseRuleset(ts, in)
			require.NoError(t, err)
			require.Equal(t, ts, ruleset.Timestamp)
			require.Len(t, ruleset.Rules, 1)
			require.Equal(t, tc.rule, ruleset.Rules[0])
		})
	}

	t.Run("whole", func(t *testing.T) {
		var whole bytes.Buffer
		for _, tc := range cases {
			whole.WriteString(tc.in)
			whole.WriteByte('\n')
		}

		ts := time.Now().Unix()
		ruleset, err := parseRuleset(ts, bytes.NewReader(whole.Bytes()))
		require.NoError(t, err)
		require.Equal(t, ts, ruleset.Timestamp)
		require.Len(t, ruleset.Rules, len(cases))
		for i, tc := range cases {
			require.Equal(t, tc.rule, ruleset.Rules[i])
		}
	})

}
