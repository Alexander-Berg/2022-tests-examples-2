package core

import (
	"context"
	"errors"
	"fmt"
	"net"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/openconfig/gnmi/proto/gnmi"
	"github.com/stretchr/testify/assert"
	zzap "go.uber.org/zap"
	"go.uber.org/zap/zaptest/observer"
	"golang.org/x/sync/errgroup"
	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"

	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/go/metrics"
	"a.yandex-team.ru/noc/go/xcfg"
	"a.yandex-team.ru/noc/metridat/internal/container"
	"a.yandex-team.ru/noc/metridat/internal/pipeline"
)

const (
	USERNAME = ""
	PASSWORD = ""
)

type MockServer struct {
	SubscribeF func(gnmi.GNMI_SubscribeServer) error
	GRPCServer *grpc.Server
}

func (s *MockServer) Capabilities(context.Context, *gnmi.CapabilityRequest) (*gnmi.CapabilityResponse, error) {
	return nil, nil
}

func (s *MockServer) Get(context.Context, *gnmi.GetRequest) (*gnmi.GetResponse, error) {
	return nil, nil
}

func (s *MockServer) Set(context.Context, *gnmi.SetRequest) (*gnmi.SetResponse, error) {
	return nil, nil
}

func (s *MockServer) Subscribe(server gnmi.GNMI_SubscribeServer) error {
	return s.SubscribeF(server)
}

type GNMITestWorker struct {
	gnmi         *gNMIWorker
	observedLogs *observer.ObservedLogs
	listener     net.Listener
}

func newGNMITestInstance(t *testing.T, username, password string, subscription []*gnmi.Subscription) *GNMITestWorker {
	zlcore, logged := observer.New(zzap.ErrorLevel)
	zl := zap.NewWithCore(zlcore)
	slist := gnmi.SubscriptionList{}
	slist.Subscription = append(slist.Subscription, subscription...)
	request := gnmi.SubscribeRequest{
		Request: &gnmi.SubscribeRequest_Subscribe{
			Subscribe: &slist,
		},
	}
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		panic(err)
	}

	mConf := metrics.Config{Pull: &metrics.Pull{Enabled: true}}
	metricsIns, err := metrics.New(&mConf, zl)
	assert.NoError(t, err)
	reg := metricsIns.Registry("")
	//app := GNMIApp{log: zl, metrics: &reg}
	split := strings.SplitN(listener.Addr().String(), ":", 2)
	target := Target{fqdn: "fqdn", host: "host", ips: []string{split[0]}}
	port, err := strconv.Atoi(split[1])
	assert.NoError(t, err)
	// (target *Target, mreg *slmn.Registry, trans map[string]transform, pipe map[string]pipeline.Pipeline,
	// rawChan *rawDataChannel, request *gnmi.SubscribeRequest,
	//	port int, username string, password xcfg.Secret, name string, logger log.Logger)
	worker := newGNMIWorker(&target, &reg, map[string]transform{}, map[string]pipeline.Pipeline{},
		newRawDataChannel(), &request,
		port, username, xcfg.Secret(password), "", 1999999999*time.Second, 5*time.Second, zl)
	gl := GNMITestWorker{gnmi: worker, observedLogs: logged, listener: listener}

	return &gl
}

func newGNMITest(t *testing.T, gnmiServer *MockServer, instance *GNMITestWorker) ([]RawData, error) {
	grpcServer := grpc.NewServer()
	gnmiServer.GRPCServer = grpcServer
	gnmi.RegisterGNMIServer(grpcServer, gnmiServer)
	ctx := context.Background()

	serverCtx, serverCancel := context.WithTimeout(ctx, 3*time.Second)
	defer serverCancel()
	eg, ctx := errgroup.WithContext(serverCtx)
	eg.Go(func() error {
		err := grpcServer.Serve(instance.listener)
		return err
	})
	time.Sleep(1000 * time.Millisecond)
	eg.Go(func() error {
		<-ctx.Done()
		grpcServer.Stop()
		return ctx.Err()
	})

	runErr := instance.gnmi.run(serverCtx)

	var rawData []RawData
	for {
		select {
		case f := <-instance.gnmi.rawChan.rawChan:
			rawData = append(rawData, f)
		case <-time.After(11 * time.Second):
			goto End
		}
	}
End:

	err := eg.Wait()
	assert.Error(t, err)

	return rawData, runErr
}

func TestWaitError(t *testing.T) {
	gnmiServer := &MockServer{
		SubscribeF: func(server gnmi.GNMI_SubscribeServer) error {
			return fmt.Errorf("testerror")
		},
	}
	instance := newGNMITestInstance(t, USERNAME, PASSWORD, []*gnmi.Subscription{})
	assert.NotNil(t, instance)
	res, runErr := newGNMITest(t, gnmiServer, instance)

	assert.EqualError(t, runErr, "aborted gNMI subscription: rpc error: code = Unknown desc = testerror")

	allLogs := instance.observedLogs.All()
	assert.Equal(t, 0, len(allLogs))
	assert.Equal(t, []RawData([]RawData(nil)), res)
}

func TestUsernamePassword(t *testing.T) {
	gnmiServer := &MockServer{
		SubscribeF: func(server gnmi.GNMI_SubscribeServer) error {
			metaData, ok := metadata.FromIncomingContext(server.Context())
			if !ok {
				return errors.New("failed to get metadata")
			}

			username := metaData.Get("username")
			if len(username) != 1 || username[0] != "theusername" {
				return errors.New("wrong username")
			}

			password := metaData.Get("password")
			if len(password) != 1 || password[0] != "thepassword" {
				return errors.New("wrong password")
			}

			return errors.New("success")
		},
	}
	instance := newGNMITestInstance(t, "theusername", "thepassword", []*gnmi.Subscription{})
	assert.NotNil(t, instance)
	res, runErr := newGNMITest(t, gnmiServer, instance)
	assert.EqualError(t, runErr, "aborted gNMI subscription: rpc error: code = Unknown desc = success")

	assert.Equal(t, []RawData([]RawData(nil)), res)
	allLogs := instance.observedLogs.All()
	assert.Equal(t, 0, len(allLogs))
}

func mockGNMINotification() *gnmi.Notification {
	return &gnmi.Notification{
		Timestamp: 1543236572000000000,
		Prefix: &gnmi.Path{
			Origin: "type",
			Elem: []*gnmi.PathElem{
				{
					Name: "model",
					Key:  map[string]string{"foo": "bar"},
				},
			},
			Target: "subscription",
		},
		Update: []*gnmi.Update{
			{
				Path: &gnmi.Path{
					Elem: []*gnmi.PathElem{
						{Name: "some"},
						{
							Name: "path",
							Key:  map[string]string{"name": "str", "uint64": "1234"}},
					},
				},
				Val: &gnmi.TypedValue{Value: &gnmi.TypedValue_IntVal{IntVal: 5678}},
			},
			{
				Path: &gnmi.Path{
					Elem: []*gnmi.PathElem{
						{Name: "other"},
						{Name: "path"},
					},
				},
				Val: &gnmi.TypedValue{Value: &gnmi.TypedValue_StringVal{StringVal: "foobar"}},
			},
			{
				Path: &gnmi.Path{
					Elem: []*gnmi.PathElem{
						{Name: "other"},
						{Name: "this"},
					},
				},
				Val: &gnmi.TypedValue{Value: &gnmi.TypedValue_StringVal{StringVal: "that"}},
			},
		},
	}
}

func TestNotification(t *testing.T) {
	t.Skip("Skipping")
	tests := []struct {
		name        string
		ins         *GNMITestWorker
		server      *MockServer
		expected    []RawData
		expectedStr []string
	}{
		{
			name: "multiple metrics",
			ins: newGNMITestInstance(t, USERNAME, PASSWORD, []*gnmi.Subscription{{
				Path: &gnmi.Path{Origin: "type", Elem: []*gnmi.PathElem{{Name: "/model"}}},
				Mode: gnmi.SubscriptionMode_SAMPLE}}),
			server: &MockServer{
				SubscribeF: func(server gnmi.GNMI_SubscribeServer) error {
					notification := mockGNMINotification()
					err := server.Send(&gnmi.SubscribeResponse{Response: &gnmi.SubscribeResponse_Update{Update: notification}})
					assert.NoError(t, err)
					err = server.Send(&gnmi.SubscribeResponse{Response: &gnmi.SubscribeResponse_SyncResponse{SyncResponse: true}})
					assert.NoError(t, err)
					notification.Prefix.Elem[0].Key["foo"] = "bar2"
					notification.Update[0].Path.Elem[1].Key["name"] = "str2"
					notification.Update[0].Val = &gnmi.TypedValue{Value: &gnmi.TypedValue_JsonVal{JsonVal: []byte{'"', '1', '2', '3', '"'}}}
					err = server.Send(&gnmi.SubscribeResponse{Response: &gnmi.SubscribeResponse_Update{Update: notification}})
					assert.NoError(t, err)
					return nil
				},
			},
			expectedStr: []string{"[{map[type:/model/foo:bar2] map[type:/model/other/path:[type.googleapis.com/google.protobuf.StringValue]:{value:\"foobar\"} type:/model/other/this:[type.googleapis.com/google.protobuf.StringValue]:{value:\"that\"}] 1543236572000 type:/model} {map[/some/path/name:str /some/path/uint64:1234 type:/model/foo:bar] map[type:/model/some/path:[type.googleapis.com/google.protobuf.Int64Value]:{value:5678}] 1543236572000 type:/model} {map[type:/model/foo:bar] map[type:/model/other/path:[type.googleapis.com/google.protobuf.StringValue]:{value:\"foobar\"} type:/model/other/this:[type.googleapis.com/google.protobuf.StringValue]:{value:\"that\"}] 1543236572000 type:/model} {map[/some/path/name:str2 /some/path/uint64:1234 type:/model/foo:bar2] map[type:/model/some/path:[type.googleapis.com/google.protobuf.UInt64Value]:{value:123}] 1543236572000 type:/model}]"},
			expected: []RawData{*newRawData(
				int64(1648482303182782000),
				&net.TCPAddr{IP: net.IPv4(127, 0, 0, 1).To4(), Port: 0, Zone: ""},
				[]container.Container{
					container.NewContainerFull(
						TestSeries,
						container.Tags{"/some/path/name": "str2", "/some/path/uint64": "1234", "type:/model/foo": "bar2"},
						container.Values{"type:/model/some/path": container.UIntToAny(123)},
						1613302662000),
					container.NewContainerFull(
						TestSeries,
						container.Tags{"/some/path/name": "str2", "/some/path/uint64": "1234", "type:/model/foo": "bar2"},
						container.Values{"type:/model/some/path": container.UIntToAny(123)},
						1613302662000),
					container.NewContainerFull(
						TestSeries,
						container.Tags{"/some/path/name": "str2", "/some/path/uint64": "1234", "type:/model/foo": "bar2"},
						container.Values{"type:/model/some/path": container.UIntToAny(123)},
						1613302662000),
					container.NewContainerFull(
						TestSeries,
						container.Tags{"/some/path/name": "str2", "/some/path/uint64": "1234", "type:/model/foo": "bar2"},
						container.Values{"type:/model/some/path": container.UIntToAny(123)},
						1613302662000),
				},
				map[string]string{"host": "host"},
				HuaweiPoller{},
			)},
		},
	}
	//recvTS := time.Now().UnixNano()
	//// TODO: set correct addr
	//ip := &net.TCPAddr{IP: net.ParseIP("127.0.0.1"), Port: 0}
	//
	//var targetMeta = map[string]string{"host": m.target.host}
	//data := newRawData(recvTS, ip, contsBufMerged, targetMeta, m)
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			res, runErr := newGNMITest(t, tt.server, tt.ins)
			assert.NoError(t, runErr)
			//spew.Dump(res)
			//fmt.Printf("%v", res)
			//assert.Equal(t, tt.expectedStr, rawDatToStr(res))
			assert.Equal(t, tt.expected, res)
		})
	}
}

func TestParsePath(t *testing.T) {
	type testCase struct {
		pref      string
		aliasPath string
		tags      map[string]string
		last      string
	}
	tests := []struct {
		name     string
		ins      *GNMITestWorker
		path     *gnmi.Path
		expected testCase
	}{
		{
			name: "with keys",
			ins: newGNMITestInstance(t, USERNAME, PASSWORD, []*gnmi.Subscription{{
				Path: &gnmi.Path{Origin: "type", Elem: []*gnmi.PathElem{{Name: "/model"}}},
				Mode: gnmi.SubscriptionMode_SAMPLE}}),
			path: &gnmi.Path{
				Elem: []*gnmi.PathElem{
					{Name: "some"},
					{Name: "path", Key: map[string]string{"name": "str", "uint64": "1234"}},
				}},
			expected: testCase{
				pref:      "/some/path",
				aliasPath: "",
				tags:      map[string]string{"/some/path/name": "str", "/some/path/uint64": "1234"},
				last:      "path",
			},
		},
		{
			name: "with keys2",
			ins: newGNMITestInstance(t, USERNAME, PASSWORD, []*gnmi.Subscription{{
				Path: &gnmi.Path{Origin: "type", Elem: []*gnmi.PathElem{{Name: "/model"}}},
				Mode: gnmi.SubscriptionMode_SAMPLE}}),
			path: &gnmi.Path{
				Elem: []*gnmi.PathElem{
					{Name: "network-instances"},
					{Name: "network-instances", Key: map[string]string{"name": "def"}},
					{Name: "protocol"},
					{Name: "protocol", Key: map[string]string{"identifier": "BGP", "name": "BGP"}},
					{Name: "afi-safi-name"},
				},
			},
			expected: testCase{
				pref:      "/network-instances/protocol/afi-safi-name",
				aliasPath: "",
				tags:      map[string]string{"/network-instances/name": "def", "/network-instances/protocol/identifier": "BGP", "/network-instances/protocol/name": "BGP"},
				last:      "afi-safi-name",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			resPrefix, tags := tt.ins.gnmi.parsePath(tt.path)
			assert.Equal(t, tt.expected.pref, resPrefix)
			assert.Equal(t, tt.expected.tags, tags)
		})
	}
}

func TestStringToPathElem(t *testing.T) {
	inValue := `/state/port[port-id=*]/`
	exp := []*gnmi.PathElem{
		{Name: "state"},
		{Name: "port", Key: map[string]string{"port-id": "*"}},
	}
	res, err := StringToPathElem(inValue)
	assert.NoError(t, err)
	assert.Equal(t, exp, res)
	inValue2 := `/interfaces/interface[name=eth0]/state/ifindex`
	exp2 := []*gnmi.PathElem{
		{Name: "interfaces"},
		{Name: "interface", Key: map[string]string{"name": "eth0"}},
		{Name: "state"},
		{Name: "ifindex"},
	}
	res2, err := StringToPathElem(inValue2)
	assert.NoError(t, err)
	assert.Equal(t, exp2, res2)
}
