package tools

import (
	"context"
	"os"
	"sync"
	"syscall"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// TestSig tests WaitSignal
// For more examples https://a.yandex-team.ru/arc_vcs/contrib/go/_std/src/os/signal/signal_test.go?rev=r9419268#L132
func TestSig(t *testing.T) {
	ctx := context.Background()
	var wg sync.WaitGroup
	wg.Add(1)
	last := ""
	go func() {
		wg.Done()
		_ = WaitSignal(ctx, []os.Signal{syscall.SIGUSR2}, func(signal os.Signal) error {
			last = signal.String()
			return nil
		})
	}()
	wg.Wait()
	time.Sleep(1 * time.Second)
	err := syscall.Kill(syscall.Getpid(), syscall.SIGUSR2)
	assert.NoError(t, err)
	time.Sleep(1 * time.Second)
	assert.Equal(t, syscall.SIGUSR2.String(), last)
}
