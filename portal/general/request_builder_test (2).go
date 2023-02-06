package laas

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_requestBuilder_WithIP(t *testing.T) {
	type args struct {
		ip string
	}

	tests := []struct {
		name string
		args args
		want *requestBuilder
	}{
		{
			name: "success",
			args: args{
				ip: "127.0.0.1",
			},
			want: &requestBuilder{
				ip: "127.0.0.1",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{}

			got := r.WithIP(tt.args.ip)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_WithGPAuto(t *testing.T) {
	type args struct {
		gpAuto string
	}

	tests := []struct {
		name string
		args args
		want *requestBuilder
	}{
		{
			name: "success",
			args: args{
				gpAuto: "1:2:85:0:1643672808",
			},
			want: &requestBuilder{
				gpAuto: "1:2:85:0:1643672808",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{}

			got := r.WithGPAuto(tt.args.gpAuto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_WithHeaders(t *testing.T) {
	type args struct {
		headers http.Header
	}

	tests := []struct {
		name string
		args args
		want *requestBuilder
	}{
		{
			name: "success",
			args: args{
				headers: map[string][]string{
					"test": {"123"},
				},
			},
			want: &requestBuilder{
				headers: map[string][]string{
					"test": {"123"},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{}

			got := r.WithHeaders(tt.args.headers)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_WithAppInfo(t *testing.T) {
	type args struct {
		appInfo models.AppInfo
	}

	tests := []struct {
		name string
		args args
		want *requestBuilder
	}{
		{
			name: "success",
			args: args{
				appInfo: models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "78000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				},
			},
			want: &requestBuilder{
				appInfo: models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "78000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{}

			got := r.WithAppInfo(tt.args.appInfo)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_WithWifi(t *testing.T) {
	type args struct {
		wifi string
	}

	tests := []struct {
		name string
		args args
		want *requestBuilder
	}{
		{
			name: "success",
			args: args{
				wifi: "c0:4a:00:aa:d2:56,-53",
			},
			want: &requestBuilder{
				wifi: "c0-4a-00-aa-d2-56:-53",
			},
		},
		{
			name: "skip invalid net",
			args: args{
				wifi: "c0:4a:00:aa:d2:56,-53;a0:4a:01:bb:d2:54",
			},
			want: &requestBuilder{
				wifi: "c0-4a-00-aa-d2-56:-53",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{}

			got := r.WithWifi(tt.args.wifi)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_WithCellID(t *testing.T) {
	type args struct {
		cellID string
	}
	tests := []struct {
		name string
		args args
		want *requestBuilder
	}{
		{
			name: "success",
			args: args{
				cellID: "250,02,37433,1618,0",
			},
			want: &requestBuilder{
				cellID: "250:02:37433:1618:0",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{}

			got := r.WithCellID(tt.args.cellID)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_Build(t *testing.T) {
	type fields struct {
		ip      string
		gpAuto  string
		headers http.Header
		appInfo models.AppInfo
		wifi    string
		cellID  string
	}

	tests := []struct {
		name    string
		fields  fields
		want    *Request
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "empty ip failed",
			fields: fields{
				ip: "",
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				ip:     "127.0.0.1",
				gpAuto: "1:2:85:0:1643672808",
				headers: map[string][]string{
					"X-Forwarded-For": {"192.168.0.1"},
					"X-Real-Ip":       {"127.0.0.1"},
					"X-Yandex-Req-Id": {"123"},
				},
				appInfo: models.AppInfo{
					ID:        "ru.yandex.searchplugin",
					Version:   "78000000",
					Platform:  "android",
					UUID:      "123456789",
					DID:       "987654321",
					OSVersion: "15.3",
				},
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "250:02:37433:1618:0",
			},
			want: &Request{
				Method: "GET",
				Headers: [][]string{
					{
						"Cookie",
						"ys=gpauto.1:2:85:0:1643672808",
					},
					{
						"X-Forwarded-For",
						"192.168.0.1",
					},
					{
						"X-Real-Ip",
						"127.0.0.1",
					},
					{
						"X-Req-Id",
						"123",
					},
				},
				URI:      "/region?app_id=ru.yandex.searchplugin&app_platform=android&app_version=78000000&cellnetworks=250%3A02%3A37433%3A1618%3A0&did=987654321&service=mobile_search_app&uuid=123456789&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
				RemoteIP: "127.0.0.1",
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{
				ip:      tt.fields.ip,
				gpAuto:  tt.fields.gpAuto,
				headers: tt.fields.headers,
				appInfo: tt.fields.appInfo,
				wifi:    tt.fields.wifi,
				cellID:  tt.fields.cellID,
			}

			got, err := r.Build()
			tt.wantErr(t, err)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_makeHeaders(t *testing.T) {
	type fields struct {
		ip      string
		gpAuto  string
		headers http.Header
		appInfo models.AppInfo
		wifi    string
		cellID  string
	}

	tests := []struct {
		name   string
		fields fields
		want   [][]string
	}{
		{
			name: "all headers",
			fields: fields{
				gpAuto: "1:2:85:0:1643672808",
				headers: map[string][]string{
					"X-Forwarded-For": {"192.168.0.1"},
					"X-Real-Ip":       {"127.0.0.1"},
					"X-Yandex-Req-Id": {"123"},
				},
			},
			want: [][]string{
				{
					"Cookie",
					"ys=gpauto.1:2:85:0:1643672808",
				},
				{
					"X-Forwarded-For",
					"192.168.0.1",
				},
				{
					"X-Real-Ip",
					"127.0.0.1",
				},
				{
					"X-Req-Id",
					"123",
				},
			},
		},
		{
			name: "xff only",
			fields: fields{
				headers: map[string][]string{
					"X-Forwarded-For": {"192.168.0.1"},
				},
			},
			want: [][]string{
				{
					"X-Forwarded-For",
					"192.168.0.1",
				},
			},
		},
		{
			name: "xri only",
			fields: fields{
				headers: map[string][]string{
					"X-Real-Ip": {"127.0.0.1"},
				},
			},
			want: [][]string{
				{
					"X-Real-Ip",
					"127.0.0.1",
				},
			},
		},
		{
			name: "req id only",
			fields: fields{
				headers: map[string][]string{
					"X-Yandex-Req-Id": {"123"},
				},
			},
			want: [][]string{
				{
					"X-Req-Id",
					"123",
				},
			},
		},
		{
			name: "ys cookie with gpauto only",
			fields: fields{
				gpAuto: "1:2:85:0:1643672808",
			},
			want: [][]string{
				{
					"Cookie",
					"ys=gpauto.1:2:85:0:1643672808",
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{
				ip:      tt.fields.ip,
				gpAuto:  tt.fields.gpAuto,
				headers: tt.fields.headers,
				appInfo: tt.fields.appInfo,
				wifi:    tt.fields.wifi,
				cellID:  tt.fields.cellID,
			}

			got := r.makeHeaders()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_requestBuilder_makeURIPath(t *testing.T) {
	type fields struct {
		ip      string
		gpAuto  string
		headers http.Header
		appInfo models.AppInfo
		wifi    string
		cellID  string
	}

	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{
			name: "all params",
			fields: fields{
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "250:02:37433:1618:0",
				appInfo: models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "123456",
					Platform: "android",
					UUID:     "1111",
					DID:      "2222",
				},
			},
			want: "/region?app_id=ru.search.plugin&app_platform=android&app_version=123456&cellnetworks=250%3A02%3A37433%3A1618%3A0&did=2222&service=mobile_search_app&uuid=1111&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
		},
		{
			name: "empty wifi",
			fields: fields{
				wifi:   "",
				cellID: "250:02:37433:1618:0",
				appInfo: models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "123456",
					Platform: "android",
					UUID:     "1111",
					DID:      "2222",
				},
			},
			want: "/region?app_id=ru.search.plugin&app_platform=android&app_version=123456&cellnetworks=250%3A02%3A37433%3A1618%3A0&did=2222&service=mobile_search_app&uuid=1111",
		},
		{
			name: "empty cellid",
			fields: fields{
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "",
				appInfo: models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "123456",
					Platform: "android",
					UUID:     "1111",
					DID:      "2222",
				},
			},
			want: "/region?app_id=ru.search.plugin&app_platform=android&app_version=123456&did=2222&service=mobile_search_app&uuid=1111&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
		},
		{
			name: "empty app_id",
			fields: fields{
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "250:02:37433:1618:0",
				appInfo: models.AppInfo{
					ID:       "",
					Version:  "123456",
					Platform: "android",
					UUID:     "1111",
					DID:      "2222",
				},
			},
			want: "/region?app_platform=android&app_version=123456&cellnetworks=250%3A02%3A37433%3A1618%3A0&did=2222&service=mobile_search_app&uuid=1111&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
		},
		{
			name: "empty app_platform",
			fields: fields{
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "250:02:37433:1618:0",
				appInfo: models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "123456",
					Platform: "",
					UUID:     "1111",
					DID:      "2222",
				},
			},
			want: "/region?app_id=ru.search.plugin&app_version=123456&cellnetworks=250%3A02%3A37433%3A1618%3A0&did=2222&service=mobile_search_app&uuid=1111&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
		},
		{
			name: "empty app_version",
			fields: fields{
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "250:02:37433:1618:0",
				appInfo: models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "",
					Platform: "android",
					UUID:     "1111",
					DID:      "2222",
				},
			},
			want: "/region?app_id=ru.search.plugin&app_platform=android&cellnetworks=250%3A02%3A37433%3A1618%3A0&did=2222&service=mobile_search_app&uuid=1111&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
		},
		{
			name: "empty uuid",
			fields: fields{
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "250:02:37433:1618:0",
				appInfo: models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "123456",
					Platform: "android",
					UUID:     "",
					DID:      "2222",
				},
			},
			want: "/region?app_id=ru.search.plugin&app_platform=android&app_version=123456&cellnetworks=250%3A02%3A37433%3A1618%3A0&did=2222&service=mobile_search_app&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
		},
		{
			name: "empty did",
			fields: fields{
				wifi:   "c0-4a-00-aa-d2-56:-53",
				cellID: "250:02:37433:1618:0",
				appInfo: models.AppInfo{
					ID:       "ru.search.plugin",
					Version:  "123456",
					Platform: "android",
					UUID:     "1111",
					DID:      "",
				},
			},
			want: "/region?app_id=ru.search.plugin&app_platform=android&app_version=123456&cellnetworks=250%3A02%3A37433%3A1618%3A0&service=mobile_search_app&uuid=1111&wifinetworks=c0-4a-00-aa-d2-56%3A-53",
		},
		{
			name: "all empty",
			want: "/region?service=mobile_search_app",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &requestBuilder{
				ip:      tt.fields.ip,
				gpAuto:  tt.fields.gpAuto,
				headers: tt.fields.headers,
				appInfo: tt.fields.appInfo,
				wifi:    tt.fields.wifi,
				cellID:  tt.fields.cellID,
			}

			got := r.makeURIPath()
			assert.Equal(t, tt.want, got)
		})
	}
}
