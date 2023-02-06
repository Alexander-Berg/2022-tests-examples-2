package trigger_test

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"net/url"
	"runtime/debug"
	"strconv"
	"testing"

	"github.com/stretchr/testify/require"
	"gorm.io/gorm"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/library/go/ptr"
	"a.yandex-team.ru/noc/cmdb/pkg/auth"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapi"
	"a.yandex-team.ru/noc/cmdb/pkg/cmdbapitest"
	"a.yandex-team.ru/noc/cmdb/pkg/configuration"
	"a.yandex-team.ru/noc/cmdb/pkg/dbconn"
	"a.yandex-team.ru/noc/cmdb/pkg/httpjson"
	"a.yandex-team.ru/noc/cmdb/pkg/mur"
	"a.yandex-team.ru/noc/cmdb/pkg/rtmodel"
	"a.yandex-team.ru/noc/cmdb/pkg/types"
	"a.yandex-team.ru/strm/common/go/pkg/fn"
)

func TestWires(t *testing.T) {

	defer func() {
		if x := recover(); x != nil {
			if msg, ok := x.(string); ok {
				t.Logf("%s; stacktrace:\n%s", msg, string(debug.Stack()))
			}
			panic(x)
		}
	}()

	dbURI := cmdbapitest.DBURI()

	lg, _ := zap.New(zap.ConsoleConfig(log.DebugLevel))
	logger := fn.NewLogger(lg)
	db, err := dbconn.Database{
		URIRW:  dbURI,
		Logger: logger,
	}.Open()
	require.NoError(t, err)

	r, err := configuration.NewRouter{
		DB:                    db,
		Logger:                logger,
		IDMCheckServiceTicket: &auth.DoNotCheckServiceTicket{},
		CheckServiceTicket:    &auth.DoNotCheckServiceTicket{},
		CheckUserTicket:       &auth.TryCheckUserTicket{},
		NewSession:            mur.NewSession{Logger: logger, DebugHeader: configuration.XDebugCMDB},
	}.NewRouter()
	require.NoError(t, err)
	router := r.IntoChiMux(logger)
	server := &httpjson.Server{Server: httptest.NewServer(router), Client: http.DefaultClient}

	rw := db
	w := CreateTopology(t, rw, [][2]types.ObjectID{
		{1, 2}, {1, 3}, {3, 4}, {3, 5}, {6, 7},
		{10, 11}, {11, 12}, {10, 13}, {11, 13},
	})

	w1 := w[[2]types.ObjectID{1, 2}]
	w2 := w[[2]types.ObjectID{1, 3}]
	w3 := w[[2]types.ObjectID{3, 4}]
	w4 := w[[2]types.ObjectID{3, 5}]
	w5 := w[[2]types.ObjectID{6, 7}]
	w1011 := w[[2]types.ObjectID{10, 11}]
	w1112 := w[[2]types.ObjectID{11, 12}]
	w1013 := w[[2]types.ObjectID{10, 13}]
	w1113 := w[[2]types.ObjectID{11, 13}]

	obj := func(id types.ObjectID) cmdbapi.Object {
		name := strconv.FormatInt(id.Int64(), 10)
		return cmdbapi.Object{ID: id, Name: (*types.ObjectName)(&name)}
	}
	var wires []cmdbapi.WireExt

	server.Get(t, server.URL+"/api/wires", &wires)
	require.Equal(t, []cmdbapi.WireExt{w1, w2, w1011, w1013, w1112, w1113, w3, w4, w5}, wires)

	server.Get(t, server.URL+"/api/wires?object_id=1", &wires)
	require.Equal(t, []cmdbapi.WireExt{w1, w2}, wires)

	server.Get(t, server.URL+"/api/wires?object_id_pairs="+url.QueryEscape("[[1,2],[3,4]]"), &wires)
	require.Equal(t, []cmdbapi.WireExt{w1, w3}, wires)

	server.Get(t, server.URL+"/api/wires?path="+url.QueryEscape("[1,5]"), &wires)
	require.Equal(t, []cmdbapi.WireExt{w2, w4}, wires)

	var objects []cmdbapi.Object

	server.Get(t, server.URL+"/api/objects?connected_to=3", &objects)
	require.Equal(t, []cmdbapi.Object{obj(1), obj(2), obj(3), obj(4), obj(5)}, objects)

	server.Get(t, server.URL+"/api/objects?connected_to=6", &objects)
	require.Equal(t, []cmdbapi.Object{obj(6), obj(7)}, objects)

	server.Get(t, server.URL+"/api/graph?input_object=10&objects_terminate_bgp_session="+url.QueryEscape("[12,13]"), &wires)
	require.Equal(t, []cmdbapi.WireExt{w1011, w1013, w1112, w1113}, wires)
}

func CreateTopology(t *testing.T, rw *gorm.DB, objectPairs [][2]types.ObjectID) Wires {
	objects := NewUniqueObjects(objectPairs)
	for _, obj := range objects {
		require.NoError(t, rw.Create(&rtmodel.Object{ID: obj.ID, Name: &obj.Name}).Error)
	}
	ports, wires := NewWires(objects, objectPairs)
	for _, port := range ports {
		require.NoError(t, rw.Create(&rtmodel.Port{ID: port.ID, ObjectID: &port.ObjectID, Name: &port.Name, IIfName: ptr.String("hardwired")}).Error)
	}
	for _, wire := range wires {
		require.NoError(t, rw.Create(rtmodel.Wire{Port1ID: wire.Port1ID, Port2ID: wire.Port2ID}).Error)
	}
	return wires
}

func NewWires(objects Objects, pairs [][2]types.ObjectID) (Ports, Wires) {
	ports, wires := make(Ports), make(Wires)
	for _, pair := range pairs {
		obj1, obj2 := objects[pair[0]], objects[pair[1]]
		port1 := NewPort(obj1, obj2)
		ports[port1.ID] = port1
		port2 := NewPort(obj2, obj1)
		ports[port2.ID] = port2

		wires[pair] = cmdbapi.WireExt{
			Wire: cmdbapi.Wire{
				Port1ID: port1.ID,
				Port2ID: port2.ID,
			},

			Object1ID:   obj1.ID,
			Object1Name: obj1.Name,
			Port1Name:   port1.Name,

			Object2ID:   obj2.ID,
			Object2Name: obj2.Name,
			Port2Name:   port2.Name,
		}
	}
	return ports, wires
}

func NewPort(obj1, obj2 Object) Port {
	portName := types.PortName(fmt.Sprintf("%s-%s", obj1.Name, obj2.Name))
	portID := types.PortID(100*obj1.ID + obj2.ID)
	return Port{
		ID:       portID,
		Name:     portName,
		ObjectID: obj1.ID,
	}
}

type Port struct {
	ID       types.PortID
	Name     types.PortName
	ObjectID types.ObjectID
}

type Object struct {
	ID   types.ObjectID
	Name types.ObjectName
}

type (
	Objects map[types.ObjectID]Object
	Ports   map[types.PortID]Port
	Wires   map[[2]types.ObjectID]cmdbapi.WireExt
)

func NewUniqueObjects(pairs [][2]types.ObjectID) Objects {
	result := make(Objects)
	for _, pair := range pairs {
		for _, objectID := range pair {
			_, found := result[objectID]
			if found {
				continue
			}
			result[objectID] = Object{
				ID:   objectID,
				Name: types.ObjectName(fmt.Sprintf("%d", objectID.Int64())),
			}
		}
	}
	return result
}
