package shooting

import (
	"os"
	"sort"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/passport/infra/daemons/shooting_gallery/shooter/pkg/clitypes"
)

type testCmdCreatorImpl struct {
	cmds []string
}

type testCmd struct {
	runOutput   []byte
	runError    error
	pid         int
	signalError error

	stop chan bool
}

func (t *testCmdCreatorImpl) Create(command string) Cmd {
	if t.cmds == nil {
		t.cmds = make([]string, 0)
	}
	t.cmds = append(t.cmds, command)

	return &testCmd{
		stop: make(chan bool),
	}
}

func (c *testCmd) Run() ([]byte, error) {
	<-c.stop
	return c.runOutput, c.runError
}

func (c *testCmd) GetPid() int {
	return c.pid
}

func (c *testCmd) Signal(sig os.Signal) error {
	close(c.stop)
	return c.signalError
}

func TestCommon(t *testing.T) {
	type testCase struct {
		instances       uint32
		connectionClose bool
		cmds            []string
	}

	vars := map[string]testCase{
		"run one instance": {
			instances:       1,
			connectionClose: true,
			cmds: []string{
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s1.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s --http-set-header "Connection: close"`,
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s2.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s --http-set-header "Connection: close"`,
			},
		},
		"run three instance": {
			instances: 3,
			cmds: []string{
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s1.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s`,
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s1.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s`,
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s1.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s`,
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s2.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s`,
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s2.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s`,
				`/usr/bin/lol --input-file-loop --input-file /var/kek/kekeke/host-s2.gz|100500% --output-http-workers=42 --output-http https://my.host.ru --exit-after 3666s`,
			},
		},
	}

	for k, tcase := range vars {
		t.Run(k, func(t *testing.T) {
			cr := &testCmdCreatorImpl{}
			cfg := Config{
				GorPath: "/usr/bin/lol",
				Target:  "my.host.ru",
			}
			params := Params{
				AmmoID:          "kekeke",
				Schema:          "https",
				Rate:            100500,
				Instances:       tcase.instances,
				Duration:        3666,
				Workers:         42,
				ConnectionClose: tcase.connectionClose,
			}
			info := clitypes.PackInfo{
				Size: 100500,
				Hosts: map[string]clitypes.HostPackInfo{
					"host-s1": {},
					"host-s2": {},
				},
			}

			s, err := NewShooting(cfg, params, "/var/kek", info, cr)
			require.NoError(t, err)
			require.Equal(t, s.packInfo, info)
			require.Len(t, s.gors, 2*int(tcase.instances))
			require.False(t, s.isStopped())
			sort.Strings(cr.cmds)
			require.Len(t, cr.cmds, 2*int(tcase.instances))
			require.Equal(t, tcase.cmds, cr.cmds)

			s.Stop()
			require.True(t, s.isStopped())
		})
	}
}
