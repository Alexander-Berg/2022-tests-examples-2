package config

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func Test_config_New(t *testing.T) {
	type testCase struct {
		name        string
		args        []string
		want        Config
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:        "no args",
			args:        nil,
			wantErrFunc: assert.Error,
		},
		{
			name: "single arg",
			args: []string{"--port", "20400"},
			want: Config{
				ApphostPort: 20400,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "several args",
			args: []string{"--port", "20400", "--unistat", "20500", "--pprof", "8587", "--procs", "4"},
			want: Config{
				ApphostPort: 20400,
				UnistatPort: 20500,
				PprofPort:   8587,
				GoMaxProcs:  4,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name:        "incorrect args",
			args:        []string{"--port", "some_trash"},
			wantErrFunc: assert.Error,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			got, err := New(tt.args)
			tt.wantErrFunc(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_config_validate(t *testing.T) {
	type testCase struct {
		name        string
		arg         Config
		wantErrFunc assert.ErrorAssertionFunc
	}

	cases := []testCase{
		{
			name:        "default values",
			arg:         Config{},
			wantErrFunc: assert.Error,
		},
		{
			name: "negative Apphost port",
			arg: Config{
				ApphostPort: -42,
			},
			wantErrFunc: assert.Error,
		},
		{
			name: "negative unistat port",
			arg: Config{
				ApphostPort: 20400,
				UnistatPort: -42,
			},
			wantErrFunc: assert.Error,
		},
		{
			name: "negative pprof port",
			arg: Config{
				ApphostPort: 20400,
				PprofPort:   -42,
			},
			wantErrFunc: assert.Error,
		},
		{
			name: "negative pprof port",
			arg: Config{
				ApphostPort: 20400,
				PprofPort:   -42,
			},
			wantErrFunc: assert.Error,
		},
		{
			name: "negative gomaxprocs value",
			arg: Config{
				ApphostPort: 20400,
				GoMaxProcs:  -1,
			},
			wantErrFunc: assert.NoError,
		},
		{
			name: "regular case",
			arg: Config{
				ApphostPort: 20400,
				UnistatPort: 20500,
				PprofPort:   8888,
				GoMaxProcs:  4,
			},
			wantErrFunc: assert.NoError,
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.arg.validate()
			tt.wantErrFunc(t, err)
		})
	}
}
