package filter_test

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/security/gideon/gideon/pkg/events"
	"a.yandex-team.ru/security/gideon/viewer/internal/filter"
)

func TestBuildWhere(t *testing.T) {
	cases := []struct {
		filter   string
		where    string
		args     []interface{}
		buildErr bool
	}{
		{
			filter: `[
{"key":"kind","operator":"==","values":["ProcExec"]},
{"key":"host","operator":"==","values":["lol","kek"]},
{"key":"pod_id","operator":"!=","values":["cheburek"]},
{"key":"pod_set_id","operator":"!=","values":["1","2","3"]}
]`,
			where: "Kind==? AND (Host==? OR Host==?) AND Proc_PodID!=? AND (Proc_PodSetID!=? OR Proc_PodSetID!=? OR Proc_PodSetID!=?)",
			args:  []interface{}{events.EventKind_EK_PROC_EXEC, "lol", "kek", "cheburek", "1", "2", "3"},
		},
		{
			where:    "Host LIKE ?",
			args:     []interface{}{"lala"},
			filter:   `[{"key":"host","operator":"~=","values":["lala"]}]`,
			buildErr: false,
		},
		{
			filter:   `[{"kind":"kind","operator":"~=","values":["ProcExec"]}]`,
			buildErr: true,
		},
		{
			filter:   `[{"key":"kek","operator":"==","values":["ProcExec"]}]`,
			buildErr: true,
		},
	}

	for _, tc := range cases {
		t.Run(tc.filter, func(t *testing.T) {
			var expressions filter.Filter
			err := json.Unmarshal([]byte(tc.filter), &expressions)
			require.NoError(t, err)

			where, args, err := filter.BuildWhere(expressions)
			if tc.buildErr {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, tc.where, where)
			require.Equal(t, tc.args, args)
		})
	}
}
