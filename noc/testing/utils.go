package testing

import (
	"context"
	"strconv"
	"strings"

	"google.golang.org/grpc"

	"a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/agent"
	"a.yandex-team.ru/noc/virtual_lab/coordinator/pkg/vr"
	pb "a.yandex-team.ru/noc/virtual_lab/proto/grpc"
)

func MakeVR(t, version, name string, connCount int) *vr.VR {
	conns := make(map[string]int, connCount)
	for i := 0; i < connCount; i++ {
		conns[strconv.Itoa(i)] = 1
	}
	return vr.New(t, version, name, "", conns)
}

func GetAddresses(agents []*agent.Agent) []string {
	result := make([]string, len(agents))
	for i, a := range agents {
		result[i] = a.Addr
	}
	return result
}

func StartServers(addresses []string,
	allocateFunc func(context.Context, *pb.AllocationRequest) (*pb.AllocationInfo, error),
	startFunc func(context.Context, *pb.DefaultVMRequest) (*pb.RequestStatus, error),
	configs []*AgentConfig) (func(), []*Agent, error) {
	servers := make([]*grpc.Server, len(addresses))
	makeStop := func(servers []*grpc.Server) func() {
		return func() {
			for _, server := range servers {
				server.GracefulStop()
			}
		}
	}
	testAgents := make([]*Agent, len(addresses))
	for i, a := range addresses {
		port, err := strconv.Atoi(strings.Split(a, ":")[1])
		if err != nil {
			makeStop(servers)()
			return nil, nil, err
		}
		var testAgent *Agent
		if allocateFunc != nil {
			testAgent = NewAgent(nil, allocateFunc, startFunc)
		} else {
			testAgent = NewAgent(configs[i], allocateFunc, startFunc)
		}
		servers[i], err = StartServer(port, testAgent)
		testAgents[i] = testAgent
		if err != nil {
			makeStop(servers)()
			return nil, nil, err
		}
	}
	return makeStop(servers), testAgents, nil
}

// MakeStressConnections creates list of connections for routersCount routers.
// Used only for testing.
func MakeStressConnections(routersCount, connectionsCount int) []map[string]int {
	connections := make([]map[string]int, routersCount)
	for i := 0; i < routersCount; i++ {
		if connections[i] == nil {
			connections[i] = make(map[string]int)
		}
		for j := 0; j < connectionsCount; j++ {
			rhs := (i + j) % routersCount
			rhsName := strconv.Itoa(rhs)
			lhsName := strconv.Itoa(i)
			connections[i][rhsName] = j
			if connections[rhs] == nil {
				connections[rhs] = make(map[string]int)
			}
			connections[rhs][lhsName] = j
		}
	}
	return connections
}
