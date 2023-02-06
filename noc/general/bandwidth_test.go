package bw_test

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/bw"
)

type Data struct {
	Bandwidth *bw.BandwidthString `json:"bandwidth"`
}

func TestBandwidthIn_UnmarshalJSON_1(t *testing.T) {
	var data Data
	err := json.Unmarshal([]byte("{\"bandwidth\": 100}"), &data)
	require.NoError(t, err)
	require.Equal(t, *data.Bandwidth, bw.BandwidthString("100"))
}

func TestBandwidthIn_UnmarshalJSON_2(t *testing.T) {
	var data Data
	err := json.Unmarshal([]byte("{\"bandwidth\": \"100 Gbps\"}"), &data)
	require.NoError(t, err)
	require.Equal(t, *data.Bandwidth, bw.BandwidthString("100 Gbps"))
}

func TestParseBandwidth_b1(t *testing.T) {
	b, err := bw.BandwidthString("1000").Int64()
	require.NoError(t, err)
	assert.Equal(t, ptr.Int64(1000), b)
}

func TestParseBandwidth_g1(t *testing.T) {
	b, err := bw.BandwidthString("10 Gbps").Int64()
	require.NoError(t, err)
	assert.Equal(t, ptr.Int64(10000000000), b)
}

func TestParseBandwidth_g2(t *testing.T) {
	b, err := bw.BandwidthString("20 GE").Int64()
	require.NoError(t, err)
	assert.Equal(t, ptr.Int64(20000000000), b)
}

func TestParseBandwidth_g3(t *testing.T) {
	b, err := bw.BandwidthString("30g").Int64()
	require.NoError(t, err)
	assert.Equal(t, ptr.Int64(30000000000), b)
}

func TestParseBandwidth_m1(t *testing.T) {
	b, err := bw.BandwidthString("10 Mbps").Int64()
	require.NoError(t, err)
	assert.Equal(t, ptr.Int64(10000000), b)
}

func TestParseBandwidth_m2(t *testing.T) {
	b, err := bw.BandwidthString("20m").Int64()
	require.NoError(t, err)
	assert.Equal(t, ptr.Int64(20000000), b)
}
