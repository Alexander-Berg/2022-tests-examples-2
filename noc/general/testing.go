package actions

import (
	"context"
	"strings"
	"time"

	"a.yandex-team.ru/library/go/core/log"
	"a.yandex-team.ru/noc/nalivkin/internal/vars"
)

func NewSetString() *SetString {
	return &SetString{}
}

type SetString struct{}

func (m *SetString) Run(ctx context.Context, aCtx *ActionCtx) ([]vars.Var, error) {
	if err := m.ValidateArgs(aCtx.Args); err != nil {
		return nil, err
	}
	time.Sleep(time.Duration(aCtx.Args["sleep_secs"].(vars.Int).Value() * int(time.Second)))
	if err := aCtx.logger.Write(ctx, log.DebugLevel, "running SetString!"); err != nil {
		return nil, err
	}
	return []vars.Var{aCtx.Args["string"]}, nil
}

func (m *SetString) ValidateArgs(args vars.VarMap) error {
	return ArgsSchema{
		"string":     vars.StringType,
		"sleep_secs": vars.IntType,
	}.Validate(args)
}

func (m *SetString) Copy() Action {
	return NewSetString()
}

func NewSplitString() *SplitString {
	return &SplitString{}
}

type SplitString struct{}

func (m *SplitString) Run(ctx context.Context, aCtx *ActionCtx) ([]vars.Var, error) {
	if err := m.ValidateArgs(aCtx.Args); err != nil {
		return nil, err
	}
	time.Sleep(time.Duration(aCtx.Args["sleep_secs"].(vars.Int).Value() * int(time.Second)))
	s := aCtx.Args["string"].(vars.String).Value()
	v := vars.NewStringList(strings.Split(s, " "))
	return []vars.Var{v}, nil
}

func (m *SplitString) ValidateArgs(args vars.VarMap) error {
	return ArgsSchema{
		"string":     vars.StringType,
		"sleep_secs": vars.IntType,
	}.Validate(args)
}

func (m *SplitString) Copy() Action {
	return NewSplitString()
}

func NewConcat() *Concat {
	return &Concat{}
}

type Concat struct{}

func (m *Concat) Run(ctx context.Context, aCtx *ActionCtx) ([]vars.Var, error) {
	if err := m.ValidateArgs(aCtx.Args); err != nil {
		return nil, err
	}
	time.Sleep(time.Duration(aCtx.Args["sleep_secs"].(vars.Int).Value() * int(time.Second)))
	s1 := aCtx.Args["string1"].(vars.String).Value()
	s2 := aCtx.Args["string2"].(vars.String).Value()
	return []vars.Var{vars.NewString(s1 + s2)}, nil
}

func (m *Concat) ValidateArgs(args vars.VarMap) error {
	return ArgsSchema{
		"string1":    vars.StringType,
		"string2":    vars.StringType,
		"sleep_secs": vars.IntType,
	}.Validate(args)
}

func (m *Concat) Copy() Action {
	return NewConcat()
}

type SetInt struct{}

func NewSetInt() *SetInt {
	return &SetInt{}
}

func (m *SetInt) Run(ctx context.Context, aCtx *ActionCtx) ([]vars.Var, error) {
	if err := m.ValidateArgs(aCtx.Args); err != nil {
		return nil, err
	}
	time.Sleep(time.Duration(aCtx.Args["sleep_secs"].(vars.Int).Value() * int(time.Second)))
	value, _ := vars.IntVal(aCtx.Args["int"])
	return []vars.Var{vars.NewInt(value)}, nil
}

func (m *SetInt) ValidateArgs(args vars.VarMap) error {
	return ArgsSchema{
		"int":        vars.IntType,
		"sleep_secs": vars.IntType,
	}.Validate(args)
}

func (m *SetInt) Copy() Action {
	return NewSetInt()
}
