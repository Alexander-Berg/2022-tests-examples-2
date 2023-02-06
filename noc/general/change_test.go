package interactive

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"reflect"
	"strings"
	"testing"

	zoneUpdate "a.yandex-team.ru/noc/traffic/dns/dns-client2/pkg/zone_update"
)

func fakeExecCommand(command string, args ...string) *exec.Cmd {
	cs := []string{"-test.run=TestHelperProcess", "--", command}
	cs = append(cs, args...)
	cmd := exec.Command(os.Args[0], cs...)
	cmd.Env = []string{"GO_WANT_HELPER_PROCESS=1"}

	bForEdit, _ := ioutil.ReadFile(args[0])
	newFileForSave := strings.Split(string(bForEdit), "\n")
	newFileForSave[1] = strings.ReplaceAll(newFileForSave[1], "ns3", "ns9")
	_ = os.WriteFile(args[0], []byte(strings.Join(newFileForSave[1:], "\n")), 0600)

	return cmd
}

func TestHelperProcess(t *testing.T) {
	if os.Getenv("GO_WANT_HELPER_PROCESS") != "1" {
		return
	}

	_, err := fmt.Fprintf(os.Stdout, "trick for test exec.Command\n")
	if err != nil {
		return
	}
	os.Exit(0)
}

func Test_editZoneAndGetChanged(t *testing.T) {
	execEditCommand = fakeExecCommand
	defer func() { execEditCommand = exec.Command }()

	var zl zoneUpdate.ZoneList
	_ = json.Unmarshal(zoneUpdate.TestZoneJSON, &zl)

	mapForTest1 := map[zoneUpdate.Operation][]string{}
	mapForTest1[zoneUpdate.Remove] = []string{"sphere360.yandex.\t3600\tIN\tA\t87.250.254.54", "sphere360.yandex.\t172800\tIN\tNS\tns3.yandex.ru."}
	mapForTest1[zoneUpdate.Add] = []string{"sphere360.yandex.\t172800\tIN\tNS\tns9.yandex.ru."}

	type args struct {
		rss []zoneUpdate.RecordSets
		ask bool
	}
	tests := []struct {
		name            string
		args            args
		wantOpsAndQuery map[zoneUpdate.Operation][]string
		wantErr         bool
	}{
		{
			"Test Add operation",
			args{zl.RecordSets, false},
			mapForTest1, // gotOpsAndQuery = map[remove:[sphere360.yandex.	3600	IN	A	87.250.254.54 sphere360.yandex.	172800	IN	NS	ns3.yandex.ru.] add:[sphere360.yandex.	172800	IN	NS	ns9.yandex.ru.]]
			false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotOpsAndQuery, err := editZoneAndGetChanged(tt.args.rss, tt.args.ask)
			if (err != nil) != tt.wantErr {
				t.Errorf("editZoneAndGetChanged() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(gotOpsAndQuery, tt.wantOpsAndQuery) {
				t.Errorf("editZoneAndGetChanged() gotOpsAndQuery = %v, want %v", gotOpsAndQuery, tt.wantOpsAndQuery)
			}
		})
	}
}
