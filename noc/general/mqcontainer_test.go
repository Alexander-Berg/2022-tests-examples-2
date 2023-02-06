package core

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"

	"a.yandex-team.ru/noc/metridat/api/protos/mqcontainer"
	"a.yandex-team.ru/noc/metridat/internal/container"
)

const TestSeries = "test"
const TestSTsMs = 1611003344000
const TestSTs = 1611003344

var (
	pbFormat = protojson.MarshalOptions{
		Multiline:       false,
		Indent:          "  ",
		AllowPartial:    true,
		UseProtoNames:   false,
		UseEnumNumbers:  false,
		EmitUnpopulated: false,
		Resolver:        nil,
	}
)

func ProtoJSON(m proto.Message) (string, error) {
	jsonBytes, err := pbFormat.Marshal(m)
	if err != nil {
		return "", err
	}
	return string(jsonBytes), nil
}

func ProtoJSONEqual(t assert.TestingT, expected, actual proto.Message, msgAndArgs ...interface{}) bool {
	jsonExpected, err := ProtoJSON(expected)
	assert.NoError(t, err, msgAndArgs)
	jsonActual, err := ProtoJSON(actual)
	assert.NoError(t, err, msgAndArgs)
	return assert.JSONEq(t, jsonActual, jsonExpected, msgAndArgs)
}

func TestContainersCompactGroupEncode(t *testing.T) {
	intVal, err := container.InterfaceToAny(123)
	assert.NoError(t, err)
	cont := container.NewContainerFull(TestSeries, container.Tags{"test": "testtag"}, container.Values{"testfield": intVal}, TestSTsMs)
	exp := `
	{
	  "payload": {
		"@type": "metridat.Kvtss",
		"kvts": [
		  {
			"keys": {
			  "test": "testtag"
			},
			"values": {
			  "testfield": {
				"@type": "type.googleapis.com/google.protobuf.Int64Value",
				"value": "123"
			  }
			},
			"ts": "1611003344000"
		  }
		]
	  },
      "topic": "test"
	}
	`
	mqCont, err := NewMQContainerFromCont(cont)
	assert.NoError(t, err)

	data, err := proto.Marshal(mqCont)
	assert.NoError(t, err)

	nmqCont := mqcontainer.MQContainer{}
	err = proto.Unmarshal(data, &nmqCont)
	assert.NoError(t, err)
	jsonRes, err := ProtoJSON(&nmqCont)
	assert.NoError(t, err)
	assert.JSONEq(t, jsonRes, exp)
}

func TestEncode(t *testing.T) {
	intVal, err := container.InterfaceToAny(123)
	assert.NoError(t, err)

	pkt := container.NewContainer(TestSeries)
	sequenceNumber := uint64(123)
	pkt.Tags["host"] = "host"
	err = pkt.Values.Set("testfield", intVal)
	assert.NoError(t, err)
	c := pkt.Compact()
	payload := container.ContainersCompactGroup{Containers: container.ContainersCompact{c}, Series: pkt.Series}
	cont, err := NewMQContainer(payload)
	assert.NoError(t, err)
	cont.Seq = sequenceNumber

	b, err := proto.Marshal(cont)
	assert.NoError(t, err)
	tempCont := mqcontainer.MQContainer{}
	err = proto.Unmarshal(b, &tempCont)
	assert.NoError(t, err)
	ProtoJSONEqual(t, cont, &tempCont)
}

func ContainersCompactGroupJSONEqual(t assert.TestingT, expected, actual *container.ContainersCompactGroup, msgAndArgs ...interface{}) bool {
	expectedProto, err := expected.ToMqcontainer()
	assert.NoError(t, err)
	actualProto, err := actual.ToMqcontainer()
	assert.NoError(t, err)
	return ProtoJSONEqual(t, expectedProto, actualProto, msgAndArgs)
}

func TestCopyTagsAndTs2(t *testing.T) {
	series := TestSeries
	tags := container.Tags{"test": "testtag"}
	tags["re"] = "tag"
	cont := container.NewContainer(series)
	cont.TS = TestSTsMs
	cont.Tags = tags
	intVal, err := container.InterfaceToAny(123)
	assert.NoError(t, err)
	err = cont.Values.Set("testfield", intVal)
	assert.NoError(t, err)
	c := cont.Compact()
	_, err = NewMQContainer(container.ContainersCompactGroup{Containers: container.ContainersCompact{c}, Series: cont.Series})
	assert.NoError(t, err)
}
