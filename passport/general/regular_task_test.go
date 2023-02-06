package task

import (
	"fmt"
	"testing"
	"time"

	"github.com/stretchr/testify/require"
)

type TestRunner struct {
	I int
}

func (tr *TestRunner) Run() error {
	fmt.Println("i: ", tr.I)
	tr.I += 1
	return nil
}

func TestNewRegularTask(t *testing.T) {
	tr := &TestRunner{}
	rt := NewRegularTask(tr, time.Millisecond, "some task")
	rt.Start()
	<-time.After(time.Millisecond * 500)
	rt.Stop()
	i := tr.I
	require.Greater(t, i, 0)
	<-time.After(time.Millisecond * 500)
	require.Equal(t, i, tr.I)
}
