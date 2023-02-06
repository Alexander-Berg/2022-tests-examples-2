package zoneupdate

import (
	"reflect"
	"testing"
)

func TestApplyQuery(t *testing.T) {
	type args struct {
		opsAndQuery map[Operation][]string
		auth        Auther
		apiURL      string
		dryRun      bool
		debug       bool
	}

	oaqAdd := map[Operation][]string{}
	oaqAdd[Add] = []string{"invest.yandex.ru.\t600\tIN\tA\t213.180.193.129"}
	oaqNotImpl := map[Operation][]string{}
	oaqNotImpl[NotImp] = []string{""}
	tests := []struct {
		name string
		args args
		want ErrorJSON
	}{
		{
			name: "Test apply add query",
			args: args{
				opsAndQuery: oaqAdd,
				auth:        MockInitAuth("MockToken", "MockHeader"),
				apiURL:      "localhost",
				dryRun:      false,
				debug:       false,
			},
			want: ErrorJSON{Code: 0},
		},
		{
			name: "Test apply error query",
			args: args{
				opsAndQuery: oaqNotImpl,
				auth:        MockInitAuth("MockToken", "MockHeader"),
				apiURL:      "localhost",
				dryRun:      false,
				debug:       false,
			},
			want: ErrorJSON{Code: -1, Msg: "some error with checkedQuery: "},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := ApplyQuery(tt.args.opsAndQuery, tt.args.auth, tt.args.apiURL, tt.args.dryRun, tt.args.debug); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ApplyQuery() = %v, want %v", got, tt.want)
			}
		})
	}
}
