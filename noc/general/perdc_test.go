package dc

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log/nop"
	"a.yandex-team.ru/noc/go/dc"
)

func TestWindow(t *testing.T) {
	perDC := NewPerDC(&Config{
		WindowDuration: 3 * time.Minute,
		GapDuration:    2 * time.Minute,
		DCsQueue:       [][]dc.DC{{dc.IVA, dc.AMS}, {dc.SAS}},
	}, &nop.Logger{})

	now := time.Date(1970, time.January, 1, 0, 0, 0, 1234, time.UTC)
	trNow := time.Date(1970, time.January, 1, 0, 0, 0, 0, time.UTC)
	ivaAndAMS := []dc.DC{dc.IVA, dc.AMS}
	sas := []dc.DC{dc.SAS}

	assert.Equal(t, Window{
		DC:       ivaAndAMS,
		Start:    trNow,
		Duration: 3 * time.Minute,
	}, perDC.window(now))
	assert.Equal(t, Window{
		DC:       ivaAndAMS,
		Start:    trNow,
		Duration: 3 * time.Minute,
	}, perDC.window(now.Add(2*time.Minute)))
	assert.Equal(t, Window{
		DC:       nil,
		Start:    trNow,
		Duration: 3 * time.Minute,
	}, perDC.window(now.Add(4*time.Minute)))
	assert.Equal(t, Window{
		DC:       sas,
		Start:    trNow.Add(5 * time.Minute),
		Duration: 3 * time.Minute,
	}, perDC.window(now.Add(6*time.Minute)))
	assert.Equal(t, Window{
		DC:       nil,
		Start:    trNow.Add(5 * time.Minute),
		Duration: 3 * time.Minute,
	}, perDC.window(now.Add(9*time.Minute)))
	assert.Equal(t, Window{
		DC:       ivaAndAMS,
		Start:    trNow.Add(10 * time.Minute),
		Duration: 3 * time.Minute,
	}, perDC.window(now.Add(11*time.Minute)))
}

func TestWindows(t *testing.T) {
	perDC := NewPerDC(&Config{
		WindowDuration: 3 * time.Minute,
		GapDuration:    2 * time.Minute,
		DCsQueue:       [][]dc.DC{{dc.IVA, dc.AMS}, {dc.SAS}, {dc.VLA, dc.VLX}},
	}, &nop.Logger{})

	now := time.Date(1970, time.January, 1, 0, 0, 0, 0, time.UTC)
	ivaAndAMS := []dc.DC{dc.IVA, dc.AMS}
	sas := []dc.DC{dc.SAS}
	vlaAndVLX := []dc.DC{dc.VLA, dc.VLX}

	windows := perDC.Windows(now, 20*time.Minute)
	assert.Equal(t, []Window{
		{
			DC:       ivaAndAMS,
			Start:    now,
			Duration: 3 * time.Minute,
		},
		{
			DC:       sas,
			Start:    now.Add(5 * time.Minute),
			Duration: 3 * time.Minute,
		},
		{
			DC:       vlaAndVLX,
			Start:    now.Add(10 * time.Minute),
			Duration: 3 * time.Minute,
		},
		{
			DC:       ivaAndAMS,
			Start:    now.Add(15 * time.Minute),
			Duration: 3 * time.Minute,
		},
	}, windows)
}

func TestWindowsFromGap(t *testing.T) {
	perDC := NewPerDC(&Config{
		WindowDuration: 3 * time.Minute,
		GapDuration:    2 * time.Minute,
		DCsQueue:       [][]dc.DC{{dc.IVA, dc.AMS, dc.VLX}, {dc.SAS}, {dc.VLA}},
	}, &nop.Logger{})

	now := time.Date(1970, time.January, 1, 0, 0, 0, 0, time.UTC)
	ivaAndAMSAndVLX := []dc.DC{dc.IVA, dc.AMS, dc.VLX}
	sas := []dc.DC{dc.SAS}
	vla := []dc.DC{dc.VLA}

	windows := perDC.Windows(now.Add(3*time.Minute+1*time.Second), 20*time.Minute)
	assert.Equal(t, []Window{
		{
			DC:       ivaAndAMSAndVLX,
			Start:    now,
			Duration: 3 * time.Minute,
		},
		{
			DC:       sas,
			Start:    now.Add(5 * time.Minute),
			Duration: 3 * time.Minute,
		},
		{
			DC:       vla,
			Start:    now.Add(10 * time.Minute),
			Duration: 3 * time.Minute,
		},
		{
			DC:       ivaAndAMSAndVLX,
			Start:    now.Add(15 * time.Minute),
			Duration: 3 * time.Minute,
		},
		{
			DC:       sas,
			Start:    now.Add(20 * time.Minute),
			Duration: 3 * time.Minute,
		},
	}, windows)
}
