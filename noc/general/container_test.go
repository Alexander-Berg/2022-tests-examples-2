package container

import (
	"testing"

	"github.com/stretchr/testify/assert"
	zzap "go.uber.org/zap"
	"go.uber.org/zap/zaptest/observer"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/proto"

	"a.yandex-team.ru/library/go/core/log/zap"
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

func TestCopyTagsAndTs(t *testing.T) {
	series := TestSeries
	tags := Tags{"test": "testtag"}
	cont := NewContainer(series)
	cont.TS = TestSTsMs
	cont.Tags = tags

	intVal, err := InterfaceToAny(123)
	assert.NoError(t, err)

	err = cont.Values.Set("testfield", intVal)
	assert.NoError(t, err)
	contCopy := cont.CopyWithoutValues()
	assert.Equal(t, int64(1611003344000), contCopy.TS)
	assert.Equal(t, tags, contCopy.Tags)
}

func TestCompact(t *testing.T) {
	cont := NewContainerFull(TestSeries, Tags{"test": "testtag"}, Values{"testfield": UIntToAny(123)}, 1613302662000)
	ls := Containers{}
	ls = append(ls, cont)
	cont = NewContainerFull(TestSeries, Tags{"test": "testtag"}, Values{"testfield2": UIntToAny(123)}, 1613302662001)
	ls = append(ls, cont)
	cont = NewContainerFull(TestSeries, Tags{"test": "testtag"}, Values{"testfield3": UIntToAny(123)}, 1613302662002)
	ls = append(ls, cont)

	contComp := ls.Compact()
	assert.Len(t, contComp, 1)
	assert.Len(t, contComp[0].Containers, 3)
}

func TestCompactGroup(t *testing.T) {
	ts := int64(1613302662000)
	tags := Tags{"test": "testtag"}
	val1 := Values{"testfield": UIntToAny(123)}
	val2 := Values{"testfield2": UIntToAny(32221)}
	val3 := Values{"testfield3": UIntToAny(9)}
	valAll := Values{"testfield": UIntToAny(123), "testfield2": UIntToAny(32221), "testfield3": UIntToAny(9)}

	cont := NewContainerFull(TestSeries, tags, val1, ts)
	ls := Containers{}
	ls = append(ls, cont)
	cont = NewContainerFull(TestSeries, tags, val2, ts)
	ls = append(ls, cont)
	cont = NewContainerFull(TestSeries, tags, val3, ts)
	ls = append(ls, cont)

	allcont := Containers{NewContainerFull(TestSeries, tags, valAll, ts)}
	contComp := ls.Merge()
	assert.Equal(t, allcont, contComp)
	//assert.Len(t, contComp[0].Containers, 3)
}

//
func TestCheck(t *testing.T) {
	badTag := NewContainerFull(TestSeries, Tags{}, Values{"testfield": IntToAny(321)}, 1613302662000)
	norm1 := NewContainerFull(TestSeries, Tags{"test": "norm1"}, Values{"testfield": IntToAny(321)}, 1613302662000)
	badTS := NewContainerFull(TestSeries, Tags{"test": "badTS"}, Values{"testfield": IntToAny(321)}, 123)
	norm2 := NewContainerFull(TestSeries, Tags{"test1": "norm2"}, Values{"testfield": IntToAny(321)}, 1613302662000)
	badVal := NewContainerFull(TestSeries, Tags{"test": "badVal"}, Values{}, 1613302662000)

	testInput := Containers{badTag, norm1, badTS, norm2, badVal}
	exp := Containers{norm2, norm1}

	zlcore, logged := observer.New(zzap.ErrorLevel)
	logger := zap.NewWithCore(zlcore)
	testInput.CheckAndClean(logger)
	assert.Equal(t, testInput, exp)
	assert.Equal(t, 3, logged.Len())
}

func TestCheckNilNilValue(t *testing.T) {
	type testStructure struct {
		PacketCount *uint64
	}
	items := testStructure{}
	testVal := Values{}
	err := testVal.UpdateValue("test", items.PacketCount)
	assert.Error(t, err)
}
