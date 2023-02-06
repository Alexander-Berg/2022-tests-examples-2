package scheduler

import (
	"context"
	"fmt"
	"strconv"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"google.golang.org/grpc"

	"a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/agent"
	test "a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/testing"
	"a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/utils"
	"a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/vr"
	pb "a.yandex-team.ru/noc/virtual_lab/proto/grpc"
)

type simpleTest struct {
	s         *AllocateScheduler
	a         *agent.Agent
	testAgent *test.Agent
	VR        *vr.VR
	server    *grpc.Server
}

func makeSimpleAllocateTest(t *testing.T, port int, f func(context.Context, *pb.AllocationRequest) (*pb.AllocationInfo, error)) *simpleTest {
	addr := fmt.Sprintf("localhost:%d", port)
	a := test.NewAgent(nil, f, nil)
	ag := agent.New(addr)
	server, err := test.StartServer(port, a)
	assert.NoError(t, err)
	s := NewScheduler(utils.NewLogger())
	assert.NoError(t, err)
	VR := vr.New("type", "version", "name", "", map[string]int{"1": 1, "2": 2, "3": 3})
	return &simpleTest{s, ag, a, VR, server}
}

func runAllocateTest(tests *simpleTest) error {
	defer tests.server.GracefulStop()
	ctx := context.Background()
	err := tests.s.TryAllocate(ctx, tests.VR, tests.a, 200*time.Millisecond)
	return err
}

func TestTryAllocate_Simple(t *testing.T) {
	uuid := "uuid"
	f := func(ctx context.Context, req *pb.AllocationRequest) (*pb.AllocationInfo, error) {
		return &pb.AllocationInfo{AllocationUuid: uuid, Exception: ""}, nil
	}
	tests := makeSimpleAllocateTest(t, 5000, f)
	err := runAllocateTest(tests)
	assert.NoError(t, err)
	assert.Equal(t, uuid, tests.VR.Allocation.AllocationUuid)
	assert.Equal(t, tests.a, tests.VR.VRAgent)
}

func TestTryAllocate_Timeout(t *testing.T) {
	f := func(ctx context.Context, req *pb.AllocationRequest) (*pb.AllocationInfo, error) {
		time.Sleep(250 * time.Millisecond)
		return &pb.AllocationInfo{}, nil
	}
	tests := makeSimpleAllocateTest(t, 5000, f)
	err := runAllocateTest(tests)
	assert.Error(t, err)
}

func TestTryAllocate_Exception(t *testing.T) {
	f := func(ctx context.Context, req *pb.AllocationRequest) (*pb.AllocationInfo, error) {
		return &pb.AllocationInfo{Exception: "exception"}, nil
	}
	tests := makeSimpleAllocateTest(t, 5000, f)
	err := runAllocateTest(tests)
	assert.Error(t, err)
	assert.Equal(t, err.Error(), "exception")
}

func MakeSchedulerWithAgents(agentsCount, startPort int) (*AllocateScheduler, []*agent.Agent) {
	s := NewScheduler(utils.NewLogger())
	agents := make([]*agent.Agent, agentsCount)
	for i := 0; i < agentsCount; i++ {
		agents[i] = agent.New(fmt.Sprintf("localhost:%d", startPort+i))
		s.RegisterAgent(agents[i])
	}
	return s, agents
}

func initTests(t *testing.T, VRsCount, VRsConnections, agentsCount, portRangeStart int, vrTypes []string) (s *AllocateScheduler, agents []*agent.Agent, vrs []*vr.VR) {
	vrs = make([]*vr.VR, VRsCount)
	for i := 0; i < VRsCount; i++ {
		vrType := "type"
		if vrTypes != nil {
			vrType = vrTypes[i]
		}
		vrs[i] = test.MakeVR(vrType, "version", strconv.Itoa(i), VRsConnections)
	}
	s, agents = MakeSchedulerWithAgents(agentsCount, portRangeStart)
	err := s.ScheduleAllocations(vrs)
	assert.NoError(t, err)
	return
}

func makeAllocations(t *testing.T, s *AllocateScheduler, VRsCount int, vrs []*vr.VR) {
	ctx := context.Background()
AllocationsLoop:
	for i := 0; i < VRsCount; i++ {
		VR, err := s.MakeAllocation(ctx, time.Second)
		assert.NoError(t, err)
		assert.NotNil(t, VR.Allocation)
		assert.NotNil(t, VR.VRAgent)
		for j, v := range vrs {
			if v == VR {
				vrs[j], vrs[len(vrs)-1] = vrs[len(vrs)-1], vrs[j]
				vrs = vrs[:len(vrs)-1]
				continue AllocationsLoop
			}
		}
		assert.Fail(t, "no vr")
	}
}

func expectErrorAllocation(t *testing.T, s *AllocateScheduler, errorNumber int) {
	ctx := context.Background()
	for i := 0; i+1 < errorNumber; i++ {
		VR, err := s.MakeAllocation(ctx, time.Second)
		assert.NoError(t, err)
		assert.NotNil(t, VR.Allocation)
		assert.NotNil(t, VR.VRAgent)
	}
	_, err := s.MakeAllocation(ctx, time.Second)
	assert.Error(t, err)
}

func TestMakeAllocation_Simple(t *testing.T) {
	const (
		VRsCount       = 3
		VRsConnections = 3
		AgentsCount    = 1
		PortRangeStart = 5000
	)
	s, agents, vrs := initTests(t, VRsCount, VRsConnections, AgentsCount, PortRangeStart, nil)
	counter := 0
	f := func(ctx context.Context, req *pb.AllocationRequest) (*pb.AllocationInfo, error) {
		counter++
		return &pb.AllocationInfo{AllocationUuid: strconv.Itoa(counter), Exception: ""}, nil
	}
	stop, _, err := test.StartServers(test.GetAddresses(agents), f, nil, nil)
	assert.NoError(t, err)
	defer stop()
	makeAllocations(t, s, VRsCount, vrs)
	assert.Equal(t, counter, VRsCount)
}

func TestMakeAllocation_AgentsWithPortCapacity(t *testing.T) {
	const (
		VRsCount       = 10
		VRsConnections = 3
		AgentsCount    = 3
		PortRangeStart = 5000
	)
	s, agents, vrs := initTests(t, VRsCount, VRsConnections, AgentsCount, PortRangeStart, nil)
	configs := []*test.AgentConfig{{UUID: "1_", Capacity: 3}, {UUID: "2_", Capacity: 3}, {UUID: "3_", Capacity: 100}}
	stop, testAgents, err := test.StartServers(test.GetAddresses(agents), nil, nil, configs)
	assert.NoError(t, err)
	defer stop()
	makeAllocations(t, s, VRsCount, vrs)
	assert.Equal(t, 1, testAgents[0].VRCounter)
	assert.Equal(t, 1, testAgents[1].VRCounter)
	assert.Equal(t, 8, testAgents[2].VRCounter)
}

func TestMakeAllocation_NotEnoughPorts(t *testing.T) {
	const (
		VRsCount       = 10
		VRsConnections = 3
		AgentsCount    = 3
		PortRangeStart = 5000
	)
	s, agents, _ := initTests(t, VRsCount, VRsConnections, AgentsCount, PortRangeStart, nil)
	configs := []*test.AgentConfig{{UUID: "1_", Capacity: 3}, {UUID: "2_", Capacity: 3}, {UUID: "3_", Capacity: 3}}
	stop, _, err := test.StartServers(test.GetAddresses(agents), nil, nil, configs)
	assert.NoError(t, err)
	defer stop()
	expectErrorAllocation(t, s, 4)
}

func TestMakeAllocation_DifferentVRTypes(t *testing.T) {
	const (
		VRsCount       = 9
		VRsConnections = 3
		AgentsCount    = 3
		PortRangeStart = 5000
	)
	vrTypes := []string{"1", "2", "3", "1", "1", "1", "2", "2", "3"}
	s, agents, vrs := initTests(t, VRsCount, VRsConnections, AgentsCount, PortRangeStart, vrTypes)
	configs := []*test.AgentConfig{{UUID: "1_", Capacity: 9}, {UUID: "2_", Capacity: 9}, {UUID: "3_", Capacity: 9}}
	stop, testAgents, err := test.StartServers(test.GetAddresses(agents), nil, nil, configs)
	assert.NoError(t, err)
	defer stop()
	makeAllocations(t, s, VRsCount, vrs)
	multipleTypesCounter := 0
	for _, a := range testAgents {
		assert.Equal(t, 3, len(a.VRTypes))
		types := make(map[string]struct{})
		for _, vrType := range a.VRTypes {
			types[vrType] = struct{}{}
		}
		if len(types) > 1 {
			multipleTypesCounter++
		}
	}
	assert.Equal(t, 1, multipleTypesCounter)
}
