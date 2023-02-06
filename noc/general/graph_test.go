package graph

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/library/go/core/log/zap"
	"a.yandex-team.ru/noc/nalivkin/internal/actions"
	"a.yandex-team.ru/noc/nalivkin/internal/vars"
)

var testLogger = zap.Must(zap.ConsoleConfig(log.DebugLevel))

type storage struct {
	abortedBy string
	mu        sync.Mutex
}

func (m *storage) CreateGraphs(context.Context, ...*Graph) error {
	return nil
}
func (m *storage) UpdateGraphStatus(context.Context, int, Status) error {
	return nil
}
func (m *storage) UpdateState(context.Context, *State) error {
	return nil
}
func (m *storage) CreateMultiState(context.Context, *MultiState, *State, string) error {
	return nil
}
func (m *storage) WriteEvent(context.Context, *State, Event) error {
	return nil
}
func (m *storage) WriteLog(_ context.Context, _ int, _ int, nodeID int, nodeLabel string, level log.Level, message string) error {
	logger := log.With(testLogger, log.String("node", nodeLabel))
	return log.WriteAt(logger.Structured(), level, message)
}
func (m *storage) AbortedBy(context.Context, int) (string, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.abortedBy, nil
}
func (m *storage) setAborted(v string) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.abortedBy = v
}

type setTwoVarsAction struct{}

func (m *setTwoVarsAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	return []vars.Var{vars.NewInt(42), vars.NewString("hello")}, nil
}
func (m *setTwoVarsAction) ValidateArgs(args vars.VarMap) error {
	return nil
}
func (m *setTwoVarsAction) Copy() actions.Action {
	return m
}

type squareAction struct{}

func (m *squareAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	if err := m.ValidateArgs(aCtx.Args); err != nil {
		return nil, err
	}
	val := aCtx.Args["myarg"].(vars.Int).Value()
	return []vars.Var{vars.NewInt(val * val)}, nil
}
func (m *squareAction) ValidateArgs(args vars.VarMap) error {
	if len(args) != 1 {
		return fmt.Errorf("invalid num args")
	}
	v, ok := args["myarg"]
	if !ok {
		return fmt.Errorf("missing myarg")
	}
	if v.Type() != vars.IntType {
		return fmt.Errorf("invalid arg type")
	}
	return nil
}
func (m *squareAction) Copy() actions.Action {
	return m
}

type worldAction struct{}

func (m *worldAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	if err := m.ValidateArgs(aCtx.Args); err != nil {
		return nil, err
	}
	val := aCtx.Args["myarg"].(vars.String).Value()
	return []vars.Var{vars.NewString(val + " world")}, nil
}
func (m *worldAction) ValidateArgs(args vars.VarMap) error {
	if len(args) > 2 {
		return fmt.Errorf("invalid num args")
	}
	v, ok := args["myarg"]
	if !ok {
		return fmt.Errorf("missing myarg")
	}
	if v.Type() != vars.StringType {
		return fmt.Errorf("invalid arg type")
	}
	return nil
}
func (m *worldAction) Copy() actions.Action {
	return m
}

type errAction struct {
	num    int
	action actions.Action

	origNum int
	runned  bool
}

func (m *errAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	if !m.runned {
		m.origNum = m.num
		m.runned = true
	}
	if m.num <= 0 {
		return m.action.Run(ctx, aCtx)
	}
	m.num--
	return nil, fmt.Errorf("can not run me")
}
func (m *errAction) ValidateArgs(args vars.VarMap) error {
	return m.action.ValidateArgs(args)
}
func (m *errAction) Copy() actions.Action {
	num := m.num
	if m.runned {
		num = m.origNum
	}
	return &errAction{num: num, action: m.action.Copy()}
}

type errOnce struct {
	action actions.Action
	once   *sync.Once
}

func (m *errOnce) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	var err error
	m.once.Do(func() {
		err = fmt.Errorf("can not run me")
	})
	if err != nil {
		return nil, err
	}

	return m.action.Run(ctx, aCtx)
}
func (m *errOnce) ValidateArgs(args vars.VarMap) error {
	return m.action.ValidateArgs(args)
}
func (m *errOnce) Copy() actions.Action {
	return &errOnce{action: m.action.Copy(), once: m.once}
}

type sleepAction struct{}

func (m *sleepAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	select {
	case <-ctx.Done():
	case <-time.After(24 * time.Hour):
	}
	return nil, nil
}
func (m *sleepAction) ValidateArgs(args vars.VarMap) error {
	return nil
}
func (m *sleepAction) Copy() actions.Action {
	return m
}

type counterAction struct {
	num int
}

func (m *counterAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	m.num++
	return []vars.Var{vars.NewInt(m.num)}, nil
}
func (m *counterAction) ValidateArgs(args vars.VarMap) error {
	return nil
}
func (m *counterAction) Copy() actions.Action {
	return &counterAction{}
}

type setListAction struct{}

func (m *setListAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	return []vars.Var{vars.NewStringList([]string{"my", "little", "pony"})}, nil
}
func (m *setListAction) ValidateArgs(args vars.VarMap) error {
	return nil
}
func (m *setListAction) Copy() actions.Action {
	return m
}

func TestRunWithVars(t *testing.T) {
	nodes := map[string]*node{
		"start": {
			label:  "start",
			action: actions.NewStart(),
			next:   []string{"finish"},
			args: map[string]vars.ReferenceVar{
				"object_id":         vars.NewRef("input.object_id"),
				"location_tag":      vars.NewRef("input.location_tag"),
				"input_object_name": vars.NewRef("input.input_object_name"),
			},
			outputNames: []string{"obj_id", "loc_tag", "input_obj_name"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"start"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	graph := Graph{
		state:   NewState(nodes, "start", &storage{}, &Clients{}, testLogger),
		storage: &storage{},
		logger:  testLogger,
	}
	assert.NoError(t, WithVariables(vars.VarMap{
		"input.location_tag":      vars.NewString("VLA"),
		"input.input_object_name": vars.NewString("vla1-1s1"),
	})(&graph))
	err := graph.Run(context.Background())
	assert.EqualError(t, err, "failed to dereference arg object_id: variable {{ input.object_id }} is not set")

	graph = Graph{
		state:   NewState(nodes, "start", &storage{}, &Clients{}, testLogger),
		storage: &storage{},
		logger:  testLogger,
	}
	assert.NoError(t, WithVariables(vars.VarMap{
		"input.object_id":         vars.NewInt(123),
		"input.location_tag":      vars.NewString("VLA"),
		"input.input_object_name": vars.NewString("vla1-1s1"),
	})(&graph))
	err = graph.Run(context.Background())
	assert.NoError(t, err)
	assert.Equal(
		t,
		vars.VarMap{
			"input.object_id":         vars.NewInt(123),
			"obj_id":                  vars.NewInt(123),
			"input.location_tag":      vars.NewString("VLA"),
			"loc_tag":                 vars.NewString("VLA"),
			"input.input_object_name": vars.NewString("vla1-1s1"),
			"input_obj_name":          vars.NewString("vla1-1s1"),
		},
		graph.state.variables,
	)
}

func TestAbort(t *testing.T) {
	nodes := map[string]*node{
		"start": {
			label:     "start",
			action:    &sleepAction{},
			next:      []string{"finish"},
			onFail:    "start",
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"start"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	storage := &storage{}
	state := NewState(nodes, "start", storage, &Clients{}, testLogger)

	wait := make(chan error)
	go func() {
		wait <- state.Run(context.Background())
	}()

	storage.setAborted("test")
	err := <-wait

	assert.EqualError(t, err, "aborted by user test")
	assert.Equal(t, StatusFailed, state.status)
}

type passListAction struct{}

func (m *passListAction) Run(ctx context.Context, aCtx *actions.ActionCtx) ([]vars.Var, error) {
	val := aCtx.Args["mylist"].(vars.StringList)
	return []vars.Var{val}, nil
}
func (m *passListAction) ValidateArgs(args vars.VarMap) error {
	return nil
}
func (m *passListAction) Copy() actions.Action {
	return m
}

func TestDereferenceList(t *testing.T) {
	nodes := map[string]*node{
		"start": {
			label:  "start",
			action: &passListAction{},
			args: map[string]vars.ReferenceVar{
				"mylist": vars.NewReferenceVar(vars.NewStringList([]string{"hi", "{{ bb }}"})),
			},
			outputNames: []string{"result"},
			next:        []string{"finish"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"start"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	graph := Graph{
		state:   NewState(nodes, "start", &storage{}, &Clients{}, testLogger),
		storage: &storage{},
		logger:  testLogger,
	}
	graph.state.variables = vars.VarMap{
		"bb": vars.NewString("there"),
	}
	err := graph.Run(context.Background())
	assert.NoError(t, err)
	assert.Equal(
		t,
		vars.VarMap{
			"bb":     vars.NewString("there"),
			"result": vars.NewStringList([]string{"hi", "there"}),
		},
		graph.state.variables,
	)
}
