package zoneupdate

import (
	"reflect"
	"testing"
)

func TestFetchZone(t *testing.T) {
	type args struct {
		zone   string
		auth   Auther
		apiURL string
	}
	tests := []struct {
		name    string
		args    args
		want    []RecordSets
		wantErr bool
	}{
		{
			name: "Test for fetch mock zone",
			args: args{
				zone:   "test.yandex.",
				auth:   MockInitAuth("MockToken", "OAUTH"),
				apiURL: "localhost",
			},
			want: []RecordSets{
				{
					ID: "test.yandex",
					Records: []Records{
						{
							TTL:   3600,
							Class: "IN",
							Type:  "A",
							Data:  "1.1.1.1",
						},
					},
				},
				{
					ID: "www.test.yandex",
					Records: []Records{
						{
							TTL:   10,
							Class: "IN",
							Type:  "CNAME",
							Data:  "test.yandex.",
						},
					},
				},
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			TestZoneJSON = testZoneJSON
			got, err := FetchZone(tt.args.zone, tt.args.auth, tt.args.apiURL)
			if (err != nil) != tt.wantErr {
				t.Errorf("FetchZone() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("FetchZone() got = %v, want %v", got, tt.want)
			}
		})
	}
}

var testZoneJSON = []byte(`{
  "status": 1,
  "record_sets": [
    {
      "id": "test.yandex",
      "records": [
        {
          "ttl": 3600,
          "class": "IN",
          "type": "A",
          "data": "1.1.1.1"
        }
      ]
    },
    {
      "id": "www.test.yandex",
      "records": [
        {
          "ttl": 10,
          "class": "IN",
          "type": "CNAME",
          "data": "test.yandex."
        }
      ]
    }
  ],
  "continuation_token": "dGVzdC55YW5kZXg="
}`)
