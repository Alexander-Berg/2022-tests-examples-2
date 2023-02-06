package coordinator

import (
	"context"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"gopkg.in/yaml.v2"

	test "a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/testing"
	"a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/utils"
	"a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/vr"
	pb "a.yandex-team.ru/noc/virtual_lab/proto/grpc"
)

const (
	PortRangeStart = 12000
	MaxRetries     = 5
)

func initTests(t *testing.T, addresses []string) *Coordinator {
	c := NewCoordinator(utils.NewLogger())
	for _, addr := range addresses {
		c.RegisterAgent(addr)
	}
	return c
}

func generateAddresses(agentsCount, startPort int) []string {
	result := make([]string, agentsCount)
	for i := 0; i < agentsCount; i++ {
		result[i] = fmt.Sprintf("localhost:%d", startPort+i)
	}
	return result
}

func makeTest(t *testing.T, path string, agentsCount, portRangeStart int, configs []*test.AgentConfig, expectErr bool) []*test.Agent {
	addresses := generateAddresses(agentsCount, portRangeStart)
	stop, agents, err := test.StartServers(addresses, nil, nil, configs)
	assert.NoError(t, err)
	defer stop()
	c := initTests(t, addresses)
	ctx := context.Background()
	err = c.StartVRsFromFile(ctx, path, vr.Default, MaxRetries)
	if expectErr {
		assert.Error(t, err)
	} else {
		assert.NoError(t, err)
	}
	return agents
}

func TestCoordinator_SingleVR(t *testing.T) {
	const AgentsCount = 1
	configs := []*test.AgentConfig{{UUID: "1_", Capacity: 9}}
	agents := makeTest(t, "single_vr.yaml", AgentsCount, PortRangeStart, configs, false)
	assert.Equal(t, "vmx", agents[0].VRTypes[0])
	assert.Equal(t, 1, agents[0].VRCounter)
}

var ThreeVRsTypeToPorts = map[string]int{"vmx1": 7, "vmx2": 5, "vmx3": 8}

func TestCoordinator_ThreeVRs(t *testing.T) {
	const AgentsCount = 1
	configs := []*test.AgentConfig{{UUID: "1_", Capacity: 100}}
	agents := makeTest(t, "three_vrs.yaml", AgentsCount, PortRangeStart, configs, false)
	assert.Equal(t, 3, agents[0].VRCounter)
	unique := make(map[string]struct{})
	for _, VR := range agents[0].Allocations {
		assert.Equal(t, ThreeVRsTypeToPorts[VR.Type], len(VR.Ports))
		unique[VR.Type] = struct{}{}
	}
	assert.Equal(t, 3, len(unique))
}

func TestCoordinator_ThreeVRsThreeAgents(t *testing.T) {
	const AgentsCount = 3
	configs := []*test.AgentConfig{
		{UUID: "1_", Capacity: int32(ThreeVRsTypeToPorts["vmx2"])},
		{UUID: "2_", Capacity: int32(ThreeVRsTypeToPorts["vmx1"])},
		{UUID: "3_", Capacity: int32(ThreeVRsTypeToPorts["vmx3"])}}
	agents := makeTest(t, "three_vrs.yaml", AgentsCount, PortRangeStart, configs, false)
	for _, a := range agents {
		assert.Equal(t, 1, len(a.VRTypes))
		for _, VR := range a.Allocations {
			assert.Equal(t, ThreeVRsTypeToPorts[VR.Type], len(VR.Ports))
		}
	}
}

func TestCoordinator_AllocationTimeout(t *testing.T) {
	const AgentsCount = 3
	configs := []*test.AgentConfig{
		{UUID: "1_", Capacity: 12},
		{UUID: "2_", Capacity: 8},
		{UUID: "3_", Capacity: 20}}
	addresses := generateAddresses(AgentsCount, PortRangeStart)
	stop, agents, err := test.StartServers(addresses[:len(addresses)-1], nil, nil, configs[:len(addresses)-1])
	assert.NoError(t, err)
	defer stop()
	stopLast, lastAgent, err := test.StartServers(addresses[len(addresses)-1:],
		func(_ context.Context, _ *pb.AllocationRequest) (*pb.AllocationInfo, error) {
			time.Sleep(1100 * time.Millisecond)
			return &pb.AllocationInfo{AllocationUuid: "123"}, nil
		}, nil, configs[len(addresses)-1:])
	assert.NoError(t, err)
	defer stopLast()
	c := initTests(t, addresses)
	ctx := context.Background()
	err = c.StartVRsFromFile(ctx, "five_vrs.yaml", vr.Default, MaxRetries)
	assert.Error(t, err)
	for _, a := range agents {
		assert.Equal(t, a.VRCounter, a.CancelCounter)
	}
	assert.Equal(t, 0, lastAgent[0].VRCounter)
}

func TestCoordinator_NotEnoughResources(t *testing.T) {
	const AgentsCount = 3
	configs := []*test.AgentConfig{
		{UUID: "1_", Capacity: 12},
		{UUID: "2_", Capacity: 8},
		{UUID: "3_", Capacity: 4}}
	agents := makeTest(t, "five_vrs.yaml", AgentsCount, PortRangeStart, configs, true)
	for _, a := range agents {
		assert.Equal(t, a.VRCounter, a.CancelCounter)
	}
}

func TestCoordinator_StartFailure(t *testing.T) {
	const AgentsCount = 3
	configs := []*test.AgentConfig{
		{UUID: "1_", Capacity: 12},
		{UUID: "2_", Capacity: 8},
		{UUID: "3_", Capacity: 20}}
	addresses := generateAddresses(AgentsCount, PortRangeStart)
	stop, agents, err := test.StartServers(addresses[:len(addresses)-1], nil, nil, configs[:len(addresses)-1])
	assert.NoError(t, err)
	defer stop()
	startsCounter := 2
	stopLast, lastAgent, err := test.StartServers(addresses[len(addresses)-1:],
		nil,
		func(_ context.Context, _ *pb.DefaultVMRequest) (*pb.RequestStatus, error) {
			if startsCounter == 0 {
				return &pb.RequestStatus{Status: "Success"}, nil
			}
			startsCounter--
			return &pb.RequestStatus{Exception: "failure"}, nil
		}, configs[len(addresses)-1:])
	assert.NoError(t, err)
	defer stopLast()
	c := initTests(t, addresses)
	ctx := context.Background()
	err = c.StartVRsFromFile(ctx, "five_vrs.yaml", vr.Default, MaxRetries)
	assert.NoError(t, err)
	startedVRs := 0
	for _, a := range agents {
		assert.Equal(t, 0, a.CancelCounter)
		startedVRs += len(a.Allocations)
	}
	assert.Equal(t, 3, startedVRs)
	assert.Equal(t, 2, len(lastAgent[0].Allocations))
}

func makeVRs(connections []map[string]int, typesCount int) []*vr.VR {
	result := make([]*vr.VR, len(connections))
	for i := 0; i < len(connections); i++ {
		t := i % typesCount
		typeStr := strconv.Itoa(t)
		name := strconv.Itoa(i)
		result[i] = vr.New(typeStr, "0", name, "", connections[i])
	}
	return result
}

func makeConfigs(agentsCount, capacity int) []*test.AgentConfig {
	result := make([]*test.AgentConfig, agentsCount)
	for i := 0; i < agentsCount; i++ {
		result[i] = &test.AgentConfig{
			UUID:     fmt.Sprintf("%d_", i),
			Capacity: int32(capacity),
		}
	}
	return result
}

func marshalVRs(path string, vrs []*vr.VR) error {
	config := vr.Config{VRs: vrs}
	data, err := yaml.Marshal(&config)
	if err != nil {
		return err
	}
	err = ioutil.WriteFile(path, data, 0777)
	return err
}

func TestCoordinator_Stress(t *testing.T) {
	const (
		RoutersCount     = 100
		ConnectionsCount = 20
		TypesCount       = 10
		AgentsCount      = 10
		Capacity         = 5000
		PortRangeStart   = 5000
		TestPath         = "/tmp/stress.yaml"
	)
	connections := test.MakeStressConnections(RoutersCount, ConnectionsCount)
	vrs := makeVRs(connections, TypesCount)
	configs := makeConfigs(AgentsCount, Capacity)
	err := marshalVRs(TestPath, vrs)
	defer func() {
		_ = os.Remove(TestPath)
	}()
	assert.NoError(t, err)
	agents := makeTest(t, TestPath, AgentsCount, PortRangeStart, configs, false)
	vrsCounter := 0
	for _, a := range agents {
		vrsCounter += len(a.Allocations)
	}
	assert.Equal(t, RoutersCount, vrsCounter)
}
