package diskqueue_test

import (
	"bytes"
	"context"
	"io"
	"io/ioutil"
	"os"
	"strconv"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap/zaptest"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/security/csp-report/internal/logbroker/diskqueue"
	"a.yandex-team.ru/security/csp-report/internal/logbroker/message"
)

func newLogger(t *testing.T) log.Structured {
	l := zap.Logger{L: zaptest.NewLogger(t)}
	return l.Structured()
}

func sClear(path string) {
	_ = os.RemoveAll(path)
}

func sClose(closer io.Closer) {
	_ = closer.Close()
}

func messageEqual(t *testing.T, a, b *message.Message) {
	t.Helper()

	isEqual := func(a, b *message.Message) bool {
		switch {
		case a.Addr != b.Addr:
			return false
		case a.Origin != b.Origin:
			return false
		case a.RequestURI != b.RequestURI:
			return false
		case a.UserAgent != b.UserAgent:
			return false
		case !bytes.Equal(a.Content, b.Content):
			return false
		case !a.TS.Equal(b.TS):
			return false
		default:
			return true
		}
	}

	if !isEqual(a, b) {
		t.Errorf("messages not equal: %#v != %#v", a, b)
	}
}

func TestDiskQueue(t *testing.T) {
	l := newLogger(t)

	tmpDir, err := ioutil.TempDir("", "test-disk-queue")
	require.NoError(t, err)
	defer sClear(tmpDir)

	diskQ, err := diskqueue.New(tmpDir, diskqueue.WithLogger(l))
	require.NoError(t, err)
	defer sClose(diskQ)
	require.Equal(t, int64(0), diskQ.Depth())

	msg := &message.Message{
		Addr: "test",
		TS:   time.Now(),
	}
	err = diskQ.Put(context.Background(), msg)
	require.NoError(t, err)

	select {
	case msgOut := <-diskQ.ReadChan():
		messageEqual(t, msg, msgOut)
	case <-time.After(20 * time.Second):
		t.Error("no message in 20 sec")
		t.FailNow()
	}
}

func TestDiskQueueRoll(t *testing.T) {
	l := newLogger(t)

	tmpDir, err := ioutil.TempDir("", "test-disk-queue-roll")
	require.NoError(t, err)
	defer sClear(tmpDir)

	diskQ, err := diskqueue.New(
		tmpDir,
		diskqueue.WithLogger(l),
		diskqueue.WithMaxBytesPerFile(1),
	)
	require.NoError(t, err)
	defer sClose(diskQ)
	require.Equal(t, int64(0), diskQ.Depth())

	for i := 0; i < 10; i++ {
		err := diskQ.Put(context.Background(), &message.Message{
			Origin: strconv.Itoa(i),
		})
		require.NoError(t, err)
	}

	for i := 0; i < 10; i++ {
		select {
		case msg := <-diskQ.ReadChan():
			assert.Equal(t, strconv.Itoa(i), msg.Origin)
		case <-time.After(20 * time.Second):
			t.Error("no message in 20 sec")
			t.FailNow()
		}
	}
}

func TestDiskQueueTorture(t *testing.T) {
	var wg sync.WaitGroup

	l := newLogger(t)
	tmpDir, err := ioutil.TempDir("", "test-disk-queue-torture")
	require.NoError(t, err)
	defer sClear(tmpDir)
	dq, err := diskqueue.New(
		tmpDir,
		diskqueue.WithLogger(l),
		diskqueue.WithMaxBytesPerFile(10),
	)
	require.NoError(t, err)
	require.Equal(t, int64(0), dq.Depth())

	numWriters := 4
	numReaders := 4
	readExitChan := make(chan int)
	writeExitChan := make(chan int)

	msg := message.Message{
		Addr:       "test-addr",
		RequestURI: "test-request-uri",
		UserAgent:  "test-user-agent",
		Origin:     "test-origin",
		Content:    []byte("test-content"),
		TS:         time.Now(),
	}
	var depth int64
	for i := 0; i < numWriters; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				time.Sleep(100000 * time.Nanosecond)
				select {
				case <-writeExitChan:
					return
				default:
					err := dq.Put(context.Background(), &msg)
					if err == nil {
						atomic.AddInt64(&depth, 1)
					}
				}
			}
		}()
	}

	time.Sleep(1 * time.Second)

	err = dq.Close()
	require.NoError(t, err)

	l.Info("closing writeExitChan")
	close(writeExitChan)
	wg.Wait()

	l.Info("restarting diskqueue")

	dq, err = diskqueue.New(
		tmpDir,
		diskqueue.WithLogger(l),
		diskqueue.WithMaxBytesPerFile(10),
	)
	require.NoError(t, err)
	defer sClose(dq)
	require.Equal(t, depth, dq.Depth())

	var read int64
	for i := 0; i < numReaders; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				time.Sleep(100000 * time.Nanosecond)
				select {
				case m := <-dq.ReadChan():
					messageEqual(t, m, &msg)
					atomic.AddInt64(&read, 1)
				case <-readExitChan:
					return
				}
			}
		}()
	}

	l.Info("waiting for depth 0")
	for {
		if dq.Depth() == 0 {
			break
		}
		time.Sleep(50 * time.Millisecond)
	}

	l.Info("closing readExitChan")
	close(readExitChan)
	wg.Wait()

	require.Equal(t, depth, read)
}
