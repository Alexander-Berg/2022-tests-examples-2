package testing

import (
	"context"
	"fmt"
	"net"
	"strconv"
	"sync"

	"google.golang.org/grpc"

	pb "a.yandex-team.ru/noc/virtual_lab/proto/grpc"
)

type VR struct {
	UUID  string
	Type  string
	Ports []uint32
}

type AgentConfig struct {
	UUID     string
	Capacity int32
}

type Agent struct {
	UUID          string
	Capacity      int32
	VRCounter     int
	CancelCounter int
	CurrentPort   uint32
	VRTypes       []string
	Allocations   map[string]VR
	AllocateFunc  func(context.Context, *pb.AllocationRequest) (*pb.AllocationInfo, error)
	StartFunc     func(context.Context, *pb.DefaultVMRequest) (*pb.RequestStatus, error)
	mu            sync.Mutex
}

func NewAgent(config *AgentConfig,
	allocateFunc func(context.Context, *pb.AllocationRequest) (*pb.AllocationInfo, error),
	startFunc func(context.Context, *pb.DefaultVMRequest) (*pb.RequestStatus, error)) *Agent {
	if config == nil {
		return &Agent{
			Allocations:  make(map[string]VR),
			AllocateFunc: allocateFunc,
			StartFunc:    startFunc,
			mu:           sync.Mutex{}}
	}
	return &Agent{
		UUID:          config.UUID,
		Capacity:      config.Capacity,
		VRCounter:     0,
		CurrentPort:   0,
		CancelCounter: 0,
		Allocations:   make(map[string]VR),
		AllocateFunc:  allocateFunc,
		StartFunc:     startFunc,
		mu:            sync.Mutex{}}
}

func (a *Agent) StartDefaultModeVM(ctx context.Context, request *pb.DefaultVMRequest) (*pb.RequestStatus, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.StartFunc != nil {
		return a.StartFunc(ctx, request)
	}
	if _, ok := a.Allocations[request.AllocationUuid]; !ok {
		return &pb.RequestStatus{Exception: "no allocation"}, nil
	}
	if a.Allocations[request.AllocationUuid].Type != request.VmType {
		return &pb.RequestStatus{Exception: "incorrect vm type"}, nil
	}
	return &pb.RequestStatus{Status: "Success", VmUuid: a.Allocations[request.AllocationUuid].UUID}, nil
}

func (a *Agent) StartControlModeVM(ctx context.Context, request *pb.ControlVMRequest) (*pb.RequestStatus, error) {
	return nil, nil
}

func (a *Agent) StartLinuxControlVM(ctx context.Context, request *pb.LinuxControlVMRequest) (*pb.RequestStatus, error) {
	return nil, nil
}

func (a *Agent) StopVM(ctx context.Context, request *pb.StopRequest) (*pb.RequestStatus, error) {
	return &pb.RequestStatus{
		Status: "Success",
	}, nil
}

func (a *Agent) GetVMInfo(ctx context.Context, request *pb.InfoRequest) (*pb.VMInfo, error) {
	return nil, nil
}

func (a *Agent) GetVMsList(ctx context.Context, request *pb.VMsListRequest) (*pb.VMsList, error) {
	return nil, nil
}

func (a *Agent) Allocate(ctx context.Context, request *pb.AllocationRequest) (*pb.AllocationInfo, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.AllocateFunc != nil {
		return a.AllocateFunc(ctx, request)
	}
	if a.VRTypes == nil {
		a.VRTypes = make([]string, 0)
	}
	if a.Capacity < request.PortsNumber {
		return &pb.AllocationInfo{Exception: "not enough ports"}, nil
	}
	a.Capacity -= request.PortsNumber
	a.VRTypes = append(a.VRTypes, request.VmType)
	ports := make([]uint32, request.PortsNumber)
	for i := int32(0); i < request.PortsNumber; i++ {
		ports[i] = a.CurrentPort
		a.CurrentPort++
	}
	a.VRCounter++
	uuid := a.UUID + strconv.Itoa(a.VRCounter)
	a.Allocations[uuid] = VR{UUID: uuid, Type: request.VmType, Ports: ports}
	return &pb.AllocationInfo{
		AllocationUuid: uuid,
		ReservedPorts:  make([]uint32, 0),
		AvailablePorts: ports,
		Exception:      "",
	}, nil
}

func (a *Agent) GetAllocationsList(ctx context.Context, request *pb.AllocationsListRequest) (*pb.AllocationsList, error) {
	result := make([]*pb.AllocationInfo, 0)
	for _, allocation := range a.Allocations {
		result = append(result, &pb.AllocationInfo{AllocationUuid: allocation.UUID, AvailablePorts: allocation.Ports})
	}
	return &pb.AllocationsList{Allocations: result}, nil
}

func (a *Agent) ReleaseAllocation(ctx context.Context, request *pb.ReleaseAllocationRequest) (*pb.ReleaseStatus, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.CancelCounter++
	a.Capacity += int32(len(a.Allocations[request.AllocationUuid].Ports))
	delete(a.Allocations, request.AllocationUuid)
	return &pb.ReleaseStatus{Status: "Released"}, nil
}

func StartServer(port int, agent *Agent) (*grpc.Server, error) {
	lis, err := net.Listen("tcp", fmt.Sprintf("localhost:%d", port))
	if err != nil {
		return nil, err
	}
	server := grpc.NewServer()
	pb.RegisterVMAgentServer(server, agent)
	go func() {
		_ = server.Serve(lis)
	}()
	return server, nil
}
