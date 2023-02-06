package madmtypes

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

func TestNewTimeOfDay(t *testing.T) {
	tod := NewTimeOfDay(1, 2, 3)
	require.Equal(t, 1, tod.Hour())
	require.Equal(t, 2, tod.Minute())
	require.Equal(t, 3, tod.Second())
}

func TestNewTimeOfDayFromTime(t *testing.T) {
	tod := NewTimeOfDayFromTime(time.Date(1993, 12, 11, 1, 2, 3, 123, time.UTC))
	require.Equal(t, 1, tod.Hour())
	require.Equal(t, 2, tod.Minute())
	require.Equal(t, 3, tod.Second())
}

func TestTimeOfDay_Before(t *testing.T) {
	require.True(t, NewTimeOfDay(0, 0, 0).Before(NewTimeOfDay(0, 0, 1)))
	require.True(t, NewTimeOfDay(0, 0, 0).Before(NewTimeOfDay(0, 1, 0)))
	require.True(t, NewTimeOfDay(0, 0, 0).Before(NewTimeOfDay(1, 0, 0)))
	require.False(t, NewTimeOfDay(0, 0, 1).Before(NewTimeOfDay(0, 0, 1)))
}

func TestTimeOfDay_After(t *testing.T) {
	require.True(t, NewTimeOfDay(0, 0, 1).After(NewTimeOfDay(0, 0, 0)))
	require.True(t, NewTimeOfDay(0, 1, 0).After(NewTimeOfDay(0, 0, 0)))
	require.True(t, NewTimeOfDay(1, 0, 0).After(NewTimeOfDay(0, 0, 0)))
	require.False(t, NewTimeOfDay(0, 0, 1).After(NewTimeOfDay(0, 0, 1)))
}

func TestTimeOfDay_ParseMADM(t *testing.T) {
	var tod TimeOfDay
	for _, tc := range testCases {
		err := tod.ParseMADM([]byte(tc.Repr))
		if tc.WantErr {
			require.Error(t, err)
			continue
		}
		require.NoError(t, err)
		require.Equal(t, tc.Hour, tod.Hour())
		require.Equal(t, tc.Min, tod.Minute())
		require.Equal(t, tc.Sec, tod.Second())
	}
}

var testCases = []struct {
	Repr    string
	Hour    int
	Min     int
	Sec     int
	WantErr bool
}{
	{
		Repr: "01:02",
		Hour: 1,
		Min:  2,
	},
	{
		Repr: "01:02:03",
		Hour: 1,
		Min:  2,
		Sec:  3,
	},
	{
		Repr:    "01",
		WantErr: true,
	},
	{
		Repr:    "1:2",
		WantErr: true,
	},
	{
		Repr:    "foo",
		WantErr: true,
	},
}
