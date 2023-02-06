package adapters

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"google.golang.org/protobuf/types/known/timestamppb"

	"a.yandex-team.ru/noc/tardis/pkg/segset"
	"a.yandex-team.ru/noc/tardis/tardispb"
)

func TestPortRange_1(t *testing.T) {
	set := segset.SegmentSet{80, 81, 100, 201, 443, 444}
	source := []*tardispb.PortRange{
		{First: 80, Last: 80},
		{First: 443, Last: 443},
		{First: 100, Last: 200},
	}
	result := []*tardispb.PortRange{
		{First: 80, Last: 80},
		{First: 100, Last: 200},
		{First: 443, Last: 443},
	}
	assert.Equal(t, set, PortSetToSegSet(source))
	assert.Equal(t, result, SegSetToPortSet(set))
}

func TestPortRange_2(t *testing.T) {
	set := segset.SegmentSet{10, 41}
	source := []*tardispb.PortRange{
		{First: 10, Last: 30},
		{First: 20, Last: 40},
	}
	result := []*tardispb.PortRange{
		{First: 10, Last: 40},
	}
	assert.Equal(t, set, PortSetToSegSet(source))
	assert.Equal(t, result, SegSetToPortSet(set))
}

func TestPortRange_3(t *testing.T) {
	set := segset.SegmentSet{10, 41}
	source := []*tardispb.PortRange{
		{First: 10, Last: 40},
		{First: 20, Last: 30},
	}
	result := []*tardispb.PortRange{
		{First: 10, Last: 40},
	}
	assert.Equal(t, set, PortSetToSegSet(source))
	assert.Equal(t, result, SegSetToPortSet(set))
}

func TestPortRange_4(t *testing.T) {
	set := segset.All()
	var source []*tardispb.PortRange
	assert.Equal(t, set, PortSetToSegSet(source))
	assert.Equal(t, source, SegSetToPortSet(set))
}

var ts1 = time.Date(2021, 1, 1, 0, 0, 0, 0, time.UTC)
var ts2 = time.Date(2021, 1, 2, 0, 0, 0, 0, time.UTC)
var ts3 = time.Date(2021, 1, 3, 0, 0, 0, 0, time.UTC)

func TestTimeSlice_1(t *testing.T) {
	set := segset.SegmentSet{uint64(ts1.Unix()), uint64(ts2.Unix())}
	source := []*tardispb.TimeSlice{
		{From: timestamppb.New(ts1), To: timestamppb.New(ts2)},
	}
	assert.Equal(t, set, TimeSetToSegSet(source))
	assert.Equal(t, source, SegSetToTimeSet(set))
}

func TestTimeSlice_2(t *testing.T) {
	set := segset.All()
	var source []*tardispb.TimeSlice
	assert.Equal(t, set, TimeSetToSegSet(source))
	assert.Equal(t, source, SegSetToTimeSet(set))
}
