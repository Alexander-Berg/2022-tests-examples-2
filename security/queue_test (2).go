package protoqueue

import (
	"bytes"
	"fmt"
	"strings"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/pkg/events"
	"a.yandex-team.ru/security/gideon/internal/protoseq"
)

func decodeEvent(t *testing.T, data []byte) events.Event {
	evts := decodeEvents(t, data)
	require.NotEmpty(t, evts)
	return evts[0]
}

func decodeEvents(t *testing.T, data []byte) []events.Event {
	pseq := protoseq.NewDecoder(bytes.NewReader(data))
	ok := pseq.More()
	require.True(t, ok)

	var out []events.Event
	for pseq.More() {
		var e events.Event
		require.NoError(t, pseq.Decode(&e))
		out = append(out, e)
	}
	require.NoError(t, pseq.Err())
	return out
}

func TestBytesQueue_one(t *testing.T) {
	q := NewBytesQueue(10, 40)
	for i := uint64(0); i < 10; i++ {
		t.Run(fmt.Sprintf("put_%d", i), func(t *testing.T) {
			_, err := q.WriteEvent(&events.Event{
				Ts: i,
			})
			require.NoError(t, err)
		})
	}

	t.Run("check_full", func(t *testing.T) {
		_, err := q.WriteEvent(&events.Event{})
		require.Error(t, err)
	})

	for i := uint64(0); i < 10; i++ {
		t.Run(fmt.Sprintf("deque_%d", i), func(t *testing.T) {
			buf, isLast := q.PopBuffer()
			defer q.PushBuffer(buf)

			require.True(t, i != 9 || isLast)
			require.NotNil(t, buf)
			data := buf.Bytes()
			require.Equal(t, i, decodeEvent(t, data).Ts)
		})
	}

	t.Run("check_empty", func(t *testing.T) {
		_, err := q.WriteEvent(&events.Event{})
		require.NoError(t, err)
	})
}

func TestBytesQueue_pushBack(t *testing.T) {
	q := NewBytesQueue(10, 40)
	for k := 0; k < 10; k++ {
		t.Run(fmt.Sprintf("iter_%d", k), func(t *testing.T) {
			for i := uint64(0); i < 10; i++ {
				t.Run(fmt.Sprintf("put_%d", i), func(t *testing.T) {
					_, err := q.WriteEvent(&events.Event{
						Ts: i,
					})
					require.NoError(t, err)
				})
			}

			t.Run("check_full", func(t *testing.T) {
				_, err := q.WriteEvent(&events.Event{})
				require.Error(t, err)
			})

			for i := uint64(0); i < 10; i++ {
				t.Run(fmt.Sprintf("deque_%d", i), func(t *testing.T) {
					buf, _ := q.PopBuffer()
					defer q.PushBuffer(buf)

					require.NotNil(t, buf)
					data := buf.Bytes()
					require.Equal(t, i, decodeEvent(t, data).Ts)
				})
			}
		})
	}
}

func TestBytesQueue_multiple(t *testing.T) {
	msgSize := func() int {
		msg := events.Event{
			Ts: 1,
			Proc: &events.ProcInfo{
				Uid: 1,
			},
		}
		return 4 + 32 + msg.Size()
	}()

	q := NewBytesQueue(10, msgSize*3)
	for i := uint64(0); i < 10; i++ {
		t.Run(fmt.Sprintf("put_%d", i), func(t *testing.T) {
			_, err := q.WriteEvent(&events.Event{
				Ts: i,
				Proc: &events.ProcInfo{
					Uid: 1,
				},
			})
			require.NoError(t, err)

			_, err = q.WriteEvent(&events.Event{
				Ts: i,
				Proc: &events.ProcInfo{
					Uid: 2,
				},
			})
			require.NoError(t, err)

			_, err = q.WriteEvent(&events.Event{
				Ts: i,
				Proc: &events.ProcInfo{
					Uid: 3,
				},
			})
			require.NoError(t, err)
		})
	}

	t.Run("check_full", func(t *testing.T) {
		_, err := q.WriteEvent(&events.Event{})
		require.Error(t, err)
	})

	for i := uint64(0); i < 10; i++ {
		t.Run(fmt.Sprintf("deque_%d", i), func(t *testing.T) {
			buf, isLast := q.PopBuffer()
			defer q.PushBuffer(buf)
			require.True(t, i != 9 || isLast)
			require.NotNil(t, buf)
			evts := decodeEvents(t, buf.Bytes())
			require.Len(t, evts, 3)
			for k := uint32(0); k < 3; k++ {
				require.Equal(t, i, evts[k].Ts)
				require.Equal(t, k+1, evts[k].Proc.Uid)
			}
		})
	}

	t.Run("check_empty", func(t *testing.T) {
		_, err := q.WriteEvent(&events.Event{})
		require.NoError(t, err)
	})
}

func TestBytesQueue_concurrent(t *testing.T) {
	q := NewBytesQueue(10, 120)
	for i := 0; i < 30; i++ {
		t.Run(fmt.Sprintf("put_%d", i), func(t *testing.T) {
			t.Parallel()
			_, err := q.WriteEvent(&events.Event{})
			require.NoError(t, err)
		})
	}

	t.Run("deque", func(t *testing.T) {
		c := 0
		for {
			b, _ := q.PopBuffer()
			if b != nil {
				c++
				q.PushBuffer(b)
			}

			if c == 10 {
				break
			}
		}
	})
}

func TestBytesQueue_oversize(t *testing.T) {
	q := NewBytesQueue(10, 40)
	for i := uint64(0); i < 10; i++ {
		t.Run(fmt.Sprintf("put_%d", i), func(t *testing.T) {
			_, err := q.WriteEvent(&events.Event{
				Ts: i,
				Proc: &events.ProcInfo{
					PodSetId: strings.Repeat("A", 20),
				},
			})
			require.Error(t, err)
		})
	}

	t.Run("check_empty", func(t *testing.T) {
		_, err := q.WriteEvent(&events.Event{})
		require.NoError(t, err)
	})

	for i := uint64(0); i < 10; i++ {
		t.Run(fmt.Sprintf("deque_%d", i), func(t *testing.T) {
			buf, _ := q.PopBuffer()
			if buf != nil {
				q.PushBuffer(buf)
			}
		})
	}

	t.Run("check_empty", func(t *testing.T) {
		_, err := q.WriteEvent(&events.Event{})
		require.NoError(t, err)
	})
}
