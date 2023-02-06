package routing

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strconv"
)

type TestGatesInfo struct {
	gates map[uint64]*GateEntry
}

type TestFallbacksInfo struct{}

func NewTestGatesInfo(filename string) (*TestGatesInfo, error) {
	type RawData struct {
		Gates [][3]string `json:"gates"`
	}

	buff, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	rawData := &RawData{}
	err = json.Unmarshal(buff, rawData)
	if err != nil {
		return nil, fmt.Errorf("invalid test data format: %s", err.Error())
	}

	gates := make(map[uint64]*GateEntry)
	for _, raw := range rawData.Gates {
		id, err := strconv.ParseUint(raw[0], 10, 64)
		if err != nil {
			return nil, fmt.Errorf("gateid must be uint, got: %s", raw[0])
		}

		gate := &GateEntry{
			ID:   id,
			SmsC: raw[1],
			From: raw[2],
		}

		gates[gate.ID] = gate
	}

	return &TestGatesInfo{
		gates: gates,
	}, nil
}

func (info *TestGatesInfo) GateEntry(id uint64) *GateEntry {
	gate, exists := info.gates[id]
	if !exists {
		return nil
	}

	return gate
}

func (info *TestFallbacksInfo) Fallbacks(from, smsc string) []*FallbackEntry {
	return nil
}
