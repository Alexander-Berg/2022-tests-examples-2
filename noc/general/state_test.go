package graph

import (
	"context"
	"sync"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/noc/nalivkin/internal/actions"
	"a.yandex-team.ru/noc/nalivkin/internal/vars"
)

func TestSequentional(t *testing.T) {
	nodes := map[string]*node{
		"set vars": {
			label:       "set vars",
			action:      &setTwoVarsAction{},
			outputNames: []string{"some_int", "some_string"},
			next:        []string{"square var"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"square var": {
			label:       "square var",
			action:      &squareAction{},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("some_int")},
			outputNames: []string{"squared_int"},
			next:        []string{"append world"},
			parents:     []string{"set vars"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world": {
			label:       "append world",
			action:      &worldAction{},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("some_string")},
			outputNames: []string{"modified_string"},
			next:        []string{"square const"},
			parents:     []string{"square var"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"square const": {
			label:       "square const",
			action:      &squareAction{},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewReferenceVar(vars.NewInt(7))},
			outputNames: []string{"squared_int_const"},
			next:        []string{"finish"},
			parents:     []string{"append world"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"square const"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}
	state := NewState(nodes, "set vars", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, StatusSuccess, state.status)
	assert.Equal(
		t,
		vars.VarMap{
			"modified_string":   vars.NewString("hello world"),
			"some_int":          vars.NewInt(42),
			"some_string":       vars.NewString("hello"),
			"squared_int":       vars.NewInt(42 * 42),
			"squared_int_const": vars.NewInt(7 * 7),
		},
		state.variables,
	)
}

func TestParallel(t *testing.T) {
	nodes := map[string]*node{
		"set vars": {
			label:       "set vars",
			action:      &setTwoVarsAction{},
			outputNames: []string{"some_int", "some_string"},
			next:        []string{"square var", "append world", "square const"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"square var": {
			label:       "square var",
			action:      &squareAction{},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("some_int")},
			outputNames: []string{"squared_int"},
			next:        []string{"finish"},
			parents:     []string{"set vars"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world": {
			label:       "append world",
			action:      &worldAction{},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("some_string")},
			outputNames: []string{"modified_string"},
			next:        []string{"finish"},
			parents:     []string{"set vars"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"square const": {
			label:       "square const",
			action:      &squareAction{},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewReferenceVar(vars.NewInt(7))},
			outputNames: []string{"squared_int_const"},
			next:        []string{"finish"},
			parents:     []string{"set vars"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"square var", "append world", "square const"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}
	state := NewState(nodes, "set vars", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, StatusSuccess, state.status)
	assert.Equal(
		t,
		vars.VarMap{
			"modified_string":   vars.NewString("hello world"),
			"some_int":          vars.NewInt(42),
			"some_string":       vars.NewString("hello"),
			"squared_int":       vars.NewInt(42 * 42),
			"squared_int_const": vars.NewInt(7 * 7),
		},
		state.variables,
	)
}

func TestMaxVisits(t *testing.T) {
	nodes := map[string]*node{
		"start": {
			label:     "start",
			action:    actions.NewDummy(),
			next:      []string{"error", "sleep"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
		"error": {
			label:     "error",
			action:    &errAction{num: 10, action: actions.NewDummy()},
			next:      []string{"finish"},
			parents:   []string{"start"},
			onFail:    "error",
			maxVisits: 3,
			timeout:   time.Duration(1 * time.Hour),
		},
		"sleep": { // will be cancelled on error
			label:     "sleep",
			action:    &sleepAction{},
			next:      []string{"finish"},
			parents:   []string{"start"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"error", "sleep"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	state := NewState(nodes, "start", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.EqualError(t, err, "max visits (3) reached for node [error]")
	assert.Equal(t, StatusFailed, state.status)
}

func TestRewriteVarsOnFail(t *testing.T) {
	nodes := map[string]*node{
		"start": {
			label:     "start",
			action:    actions.NewDummy(),
			next:      []string{"counter"},
			maxVisits: 10,
			timeout:   time.Duration(1 * time.Hour),
		},
		"counter": {
			label:       "counter",
			action:      &counterAction{},
			outputNames: []string{"counter_val"},
			next:        []string{"error"},
			parents:     []string{"start"},
			maxVisits:   10,
			timeout:     time.Duration(1 * time.Hour),
		},
		"error": {
			label:     "error",
			action:    &errAction{num: 3, action: actions.NewDummy()},
			next:      []string{"finish"},
			parents:   []string{"counter"},
			onFail:    "start",
			maxVisits: 10,
			timeout:   time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"error"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	state := NewState(nodes, "start", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, StatusSuccess, state.status)
	assert.Equal(
		t,
		// there were 3 errors, so [counter] node was executed 4 times
		vars.VarMap{"counter_val": vars.NewInt(4)},
		state.variables,
	)
}

func TestTimeout(t *testing.T) {
	nodes := map[string]*node{
		"start": {
			label:     "start",
			action:    &sleepAction{},
			next:      []string{"finish"},
			onFail:    "start",
			maxVisits: 1,
			timeout:   time.Duration(500 * time.Millisecond),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"start"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	state := NewState(nodes, "start", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.EqualError(t, err, "max visits (1) reached for node [start]")
	assert.Equal(t, StatusFailed, state.status)
}

func TestMultiple(t *testing.T) {
	nodes := map[string]*node{
		"set list": {
			label:       "set list",
			action:      &setListAction{},
			next:        []string{"set vars"},
			outputNames: []string{"my_list"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"set vars": {
			label:       "set vars",
			action:      &setTwoVarsAction{},
			outputNames: []string{"some_int", "some_string"},
			next:        []string{"append world"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world": {
			label:       "append world",
			action:      &worldAction{},
			next:        []string{"append world 2"},
			parents:     []string{"set list"},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("my_list")},
			outputNames: []string{"modified_strings"},
			multiple:    "my_list",
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world 2": {
			label:   "append world 2",
			action:  &worldAction{},
			next:    []string{"finish"},
			parents: []string{"append world"},
			args: map[string]vars.ReferenceVar{
				"myarg": vars.NewRef("modified_strings"),
				"myint": vars.NewRef("some_int"),
			},
			outputNames: []string{"modified_strings2"},
			multiple:    "modified_strings",
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"append world 2"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	state := NewState(nodes, "set list", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, StatusSuccess, state.status)

	expectedVarNames := map[string]struct{}{
		"my_list":           {},
		"some_int":          {},
		"some_string":       {},
		"modified_strings":  {},
		"modified_strings2": {},
	}
	assert.Equal(t, len(expectedVarNames), len(state.variables))
	for name := range state.variables {
		_, ok := expectedVarNames[name]
		assert.Equal(t, true, ok)
	}

	assert.Equal(t, vars.NewStringList([]string{"my", "little", "pony"}), state.variables["my_list"])

	s, err := state.variables["modified_strings"].ToSlice()
	assert.NoError(t, err)
	assert.ElementsMatch(
		t,
		[]vars.Var{vars.NewString("my world"), vars.NewString("little world"), vars.NewString("pony world")},
		s,
	)

	s, err = state.variables["modified_strings2"].ToSlice()
	assert.NoError(t, err)
	assert.ElementsMatch(
		t,
		[]vars.Var{vars.NewString("my world world"), vars.NewString("little world world"), vars.NewString("pony world world")},
		s,
	)

	assert.Equal(t, 1, state.visitCounter["append world"])
	assert.Equal(t, 0, state.visitCounter["append world 2"]) // runned in inner state
}

func TestMultipleOnFailInner(t *testing.T) {
	nodes := map[string]*node{
		"set list": {
			label:       "set list",
			action:      &setListAction{},
			next:        []string{"append world"},
			outputNames: []string{"my_list"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world": {
			label:       "append world",
			action:      &worldAction{},
			next:        []string{"append world 2"},
			parents:     []string{"set list"},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("my_list")},
			outputNames: []string{"modified_strings"},
			multiple:    "my_list",
			maxVisits:   2,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world 2": { // fails one time
			label:       "append world 2",
			action:      &errAction{num: 1, action: &worldAction{}},
			next:        []string{"finish"},
			parents:     []string{"append world"},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("modified_strings")},
			outputNames: []string{"modified_strings2"},
			multiple:    "modified_strings",
			maxVisits:   2,
			onFail:      "append world",
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"append world 2"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	state := NewState(nodes, "set list", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, StatusSuccess, state.status)

	s, err := state.variables["modified_strings"].ToSlice()
	assert.NoError(t, err)
	assert.ElementsMatch(
		t,
		[]vars.Var{vars.NewString("my world"), vars.NewString("little world"), vars.NewString("pony world")},
		s,
	)

	s, err = state.variables["modified_strings2"].ToSlice()
	assert.NoError(t, err)
	assert.ElementsMatch(
		t,
		[]vars.Var{vars.NewString("my world world"), vars.NewString("little world world"), vars.NewString("pony world world")},
		s,
	)

	assert.Equal(t, 1, state.visitCounter["append world"])
	assert.Equal(t, 0, state.visitCounter["append world 2"]) // runned in inner state

	assert.Equal(t, 2, state.multiStates["append world"].state.visitCounter["append world#0"])
	assert.Equal(t, 2, state.multiStates["append world"].state.visitCounter["append world#1"])
	assert.Equal(t, 2, state.multiStates["append world"].state.visitCounter["append world#2"])
}

func TestMultipleOnFailInnerErrorIsVisible(t *testing.T) {
	nodes := map[string]*node{
		"set list": {
			label:       "set list",
			action:      &setListAction{},
			next:        []string{"append world"},
			outputNames: []string{"my_list"},
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world": {
			label:       "append world",
			action:      &errAction{num: 1, action: &worldAction{}},
			next:        []string{"append world 2"},
			parents:     []string{"set list"},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("my_list")},
			outputNames: []string{"modified_strings"},
			multiple:    "my_list",
			maxVisits:   1,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world 2": { // fails one time
			label:       "append world 2",
			action:      &errAction{num: 1, action: &worldAction{}},
			next:        []string{"finish"},
			parents:     []string{"append world"},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("modified_strings")},
			outputNames: []string{"modified_strings2"},
			multiple:    "modified_strings",
			maxVisits:   1,
			onFail:      "append world",
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"append world 2"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	state := NewState(nodes, "set list", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.EqualError(t, err, "can not run me")
	assert.Equal(t, StatusFailed, state.status)
}

func TestMultipleOnFailOuter(t *testing.T) {
	nodes := map[string]*node{
		"set list": {
			label:       "set list",
			action:      &setListAction{},
			next:        []string{"append world"},
			outputNames: []string{"my_list"},
			maxVisits:   2,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world": {
			label:       "append world",
			action:      &worldAction{},
			next:        []string{"append world 2"},
			parents:     []string{"set list"},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("my_list")},
			outputNames: []string{"modified_strings"},
			multiple:    "my_list",
			maxVisits:   2,
			timeout:     time.Duration(1 * time.Hour),
		},
		"append world 2": { // fails one time
			label:       "append world 2",
			action:      &errOnce{action: &worldAction{}, once: &sync.Once{}},
			next:        []string{"finish"},
			parents:     []string{"append world"},
			args:        map[string]vars.ReferenceVar{"myarg": vars.NewRef("modified_strings")},
			outputNames: []string{"modified_strings2"},
			multiple:    "modified_strings",
			maxVisits:   1,
			onFail:      "set list",
			timeout:     time.Duration(1 * time.Hour),
		},
		"finish": {
			label:     "finish",
			action:    actions.NewDummy(),
			parents:   []string{"append world 2"},
			maxVisits: 1,
			timeout:   time.Duration(1 * time.Hour),
		},
	}

	state := NewState(nodes, "set list", &storage{}, &Clients{}, testLogger)
	err := state.Run(context.Background())

	assert.NoError(t, err)
	assert.Equal(t, StatusSuccess, state.status)

	s, err := state.variables["modified_strings"].ToSlice()
	assert.NoError(t, err)
	assert.ElementsMatch(
		t,
		[]vars.Var{vars.NewString("my world"), vars.NewString("little world"), vars.NewString("pony world")},
		s,
	)

	s, err = state.variables["modified_strings2"].ToSlice()
	assert.NoError(t, err)
	assert.ElementsMatch(
		t,
		[]vars.Var{vars.NewString("my world world"), vars.NewString("little world world"), vars.NewString("pony world world")},
		s,
	)

	assert.Equal(t, 2, state.visitCounter["append world"])
	assert.Equal(t, 0, state.visitCounter["append world 2"]) // runned in inner state

	assert.Equal(t, 1, state.multiStates["append world"].state.visitCounter["append world#0"])
	assert.Equal(t, 1, state.multiStates["append world"].state.visitCounter["append world#1"])
	assert.Equal(t, 1, state.multiStates["append world"].state.visitCounter["append world#2"])
}
