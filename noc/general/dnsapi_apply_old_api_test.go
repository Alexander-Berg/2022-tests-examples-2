package zoneupdate

import (
	"reflect"
	"sort"
	"testing"
)

func Test_convertOperationsToPrimitives(t *testing.T) {
	type args struct {
		opsAndQuery map[Operation][]string
	}
	oaq := make(map[Operation][]string)
	oaq[Add] = []string{"sphere360.yandex.\t3600\tIN\tA\t1.1.1.1"}
	oaq[Remove] = []string{"sphere360.yandex.\t3600\tIN\tAAAA\t2a02:6b8::49d"}
	tests := []struct {
		name  string
		args  args
		want  []primitive
		want1 ErrorJSON
	}{
		{
			name: "check convert operations to primitives",
			// opsAndQuery:  map[add:[sphere360.yandex.	3600	IN	A	1.1.1.1] remove:[sphere360.yandex.	3600	IN	AAAA	2a02:6b8::49d]]
			args: args{opsAndQuery: oaq},
			// [{create sphere360.yandex. A 1.1.1.1 3600} {delete sphere360.yandex. AAAA 2a02:6b8::49d 3600}]
			want: []primitive{{
				Operation: "create",
				Name:      "sphere360.yandex.",
				Type:      "A",
				Data:      "1.1.1.1",
				TTL:       3600,
			}, {
				Operation: "delete",
				Name:      "sphere360.yandex.",
				Type:      "AAAA",
				Data:      "2a02:6b8::49d",
				TTL:       3600,
			}},
			want1: ErrorJSON{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, got1 := convertOperationsToPrimitives(tt.args.opsAndQuery)
			sort.Slice(got, func(i, j int) bool {
				return got[i].Operation < got[j].Operation
			})
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("convertOperationsToPrimitives() got = %v, want %v", got, tt.want)
			}
			if !reflect.DeepEqual(got1, tt.want1) {
				t.Errorf("convertOperationsToPrimitives() got1 = %v, want %v", got1, tt.want1)
			}
		})
	}
}
