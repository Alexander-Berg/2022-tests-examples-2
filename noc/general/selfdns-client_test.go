package main

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"

	"a.yandex-team.ru/noc/traffic/dns/selfdns-api-client/internal/config"
	"a.yandex-team.ru/noc/traffic/dns/selfdns-api-client/internal/plugins"
)

func TestMakeHTTPPostRequestError(t *testing.T) {
	testTable := []struct {
		name             string
		server           *httptest.Server
		expectedResponse *APIErrors
		expectedErr      error
	}{
		{
			name: "error-server-response",
			server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusUnauthorized)
				_, _ = w.Write([]byte(`{
								"success": false,
								"errors": [
									{
										"code": 401,
										"message": "authorization failed, err:'authorization failed, err:'authorization error, err:', status:'INVALID', error:'expired_token''''",
										"error": "Unauthorized"
									}
								]
							}`))
			})),
			expectedResponse: &APIErrors{[]APIError{{Error: "Unauthorized", Code: 401}}},
			expectedErr:      nil,
		},
	}
	dnsData := plugins.DNSData{Records: []plugins.Host{{Hostname: "testhostname", IP: "127.0.0.1", TTL: 123}}}
	data, _ := json.Marshal(dnsData)
	clientConfig := config.ClientConfig{
		OAuthToken:     "",
		PluginsDir:     "",
		PluginsEnabled: nil,
		LogFilePath:    "",
		TimeOut:        0,
		TTL:            0,
		Service:        "",
		MaxUptime:      0,
		Force:          false,
	}
	var bodyValue APIErrors
	for _, tc := range testTable {
		t.Run(tc.name, func(t *testing.T) {
			defer tc.server.Close()
			resp, err := makeHTTPPostRequest(tc.server.URL, data, clientConfig)
			if err != nil {
				return
			}
			defer resp.Body.Close()
			respInByte, _ := ioutil.ReadAll(resp.Body)
			err = json.Unmarshal(respInByte, &bodyValue)
			if !reflect.DeepEqual(&bodyValue, tc.expectedResponse) {
				t.Errorf("expected (%v), got (%v)", tc.expectedResponse, resp)
			}
			if !errors.Is(err, tc.expectedErr) {
				t.Errorf("expected (%v), got (%v)", tc.expectedErr, err)
			}
		})
	}
}

type testEmptyBody struct {
}

func TestMakeHTTPPostRequestHappyPathNoChange(t *testing.T) {
	testTable := []struct {
		name             string
		server           *httptest.Server
		expectedResponse *testEmptyBody
		expectedErr      error
	}{
		{
			name: "happy-path-no-change-server-response",
			server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				_, _ = w.Write([]byte(`{}`))
			})),
			expectedResponse: &testEmptyBody{},
			expectedErr:      nil,
		},
	}
	dnsData := plugins.DNSData{Records: []plugins.Host{{Hostname: "testhostname", IP: "127.0.0.1", TTL: 123}}}
	data, _ := json.Marshal(dnsData)
	clientConfig := config.ClientConfig{
		OAuthToken:     "",
		PluginsDir:     "",
		PluginsEnabled: nil,
		LogFilePath:    "",
		TimeOut:        0,
		TTL:            0,
		Service:        "",
		MaxUptime:      0,
		Force:          false,
	}
	var bodyValue testEmptyBody
	for _, tc := range testTable {
		t.Run(tc.name, func(t *testing.T) {
			defer tc.server.Close()
			resp, err := makeHTTPPostRequest(tc.server.URL, data, clientConfig)
			if err != nil {
				return
			}
			defer resp.Body.Close()
			respInByte, _ := ioutil.ReadAll(resp.Body)
			err = json.Unmarshal(respInByte, &bodyValue)
			if !reflect.DeepEqual(&bodyValue, tc.expectedResponse) {
				t.Errorf("expected (%v), got (%v)", tc.expectedResponse, resp)
			}
			if !errors.Is(err, tc.expectedErr) {
				t.Errorf("expected (%v), got (%v)", tc.expectedErr, err)
			}
		})
	}
}

func TestMakeHTTPPostRequestHappyPathWithChange(t *testing.T) {
	testTable := []struct {
		name             string
		server           *httptest.Server
		expectedResponse *Response
		expectedErr      error
	}{
		{
			name: "happy-path-with-change-server-response",
			server: httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.WriteHeader(http.StatusOK)
				_, _ = w.Write([]byte(`{
        "operations": {
                "operations": {
                        "UPDATE-DELETE": [
                                {
                                        "owner": "5.d.2.b.a.a.e.f.f.f.1.1.e.b.c.9.0.0.3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa",
                                        "rdstring": "snapshot-sas1.svc.cloud-testing.yandex.net.",
                                        "realm": "realm-iaas",
                                        "record-type": "PTR",
                                        "status": "OK",
                                        "status-reason": "Processed",
                                        "type": "UPDATE-DELETE",
                                        "zone": "3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa"
                                }
                        ],
                        "UPDATE-ADD": [
                                {
                                        "owner": "5.d.2.b.a.a.e.f.f.f.1.1.e.b.c.9.0.0.3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa.",
                                        "rdstring": "snapshot-sas1.svc.cloud-testing.yandex.net.",
                                        "realm": "realm-iaas",
                                        "record-type": "PTR",
                                        "status": "OK",
                                        "status-reason": "Processed",
                                        "type": "UPDATE-ADD",
                                        "zone": "3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa"
                                }
                        ]
                }
        }
    }
`))
			})),
			expectedResponse: &Response{Zone: map[string]Action{"operations": {UpdDel: []ActionInfo{
				{Owner: "5.d.2.b.a.a.e.f.f.f.1.1.e.b.c.9.0.0.3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa",
					Rdstring:     "snapshot-sas1.svc.cloud-testing.yandex.net.",
					Realm:        "realm-iaas",
					RecordType:   "PTR",
					Status:       "OK",
					StatusReason: "Processed",
					ActionType:   "UPDATE-DELETE",
					Zone:         "3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa"}}, Upd: []ActionInfo{
				{Owner: "5.d.2.b.a.a.e.f.f.f.1.1.e.b.c.9.0.0.3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa.",
					Rdstring:     "snapshot-sas1.svc.cloud-testing.yandex.net.",
					Realm:        "realm-iaas",
					RecordType:   "PTR",
					Status:       "OK",
					StatusReason: "Processed",
					ActionType:   "UPDATE-ADD",
					Zone:         "3.1.0.0.f.b.8.b.6.0.2.0.a.2.ip6.arpa"}}},
			},
			},
			expectedErr: nil,
		},
	}
	dnsData := plugins.DNSData{Records: []plugins.Host{{Hostname: "testhostname", IP: "127.0.0.1", TTL: 123}}}
	data, _ := json.Marshal(dnsData)
	clientConfig := config.ClientConfig{
		OAuthToken:     "",
		PluginsDir:     "",
		PluginsEnabled: nil,
		LogFilePath:    "",
		TimeOut:        0,
		TTL:            0,
		Service:        "",
		MaxUptime:      0,
		Force:          false,
	}
	var bodyValue Response
	for _, tc := range testTable {
		t.Run(tc.name, func(t *testing.T) {
			defer tc.server.Close()
			resp, err := makeHTTPPostRequest(tc.server.URL, data, clientConfig)
			if err != nil {
				return
			}
			defer resp.Body.Close()
			respInByte, _ := ioutil.ReadAll(resp.Body)
			err = json.Unmarshal(respInByte, &bodyValue)
			if !reflect.DeepEqual(&bodyValue, tc.expectedResponse) {
				t.Errorf("expected (%v), got (%v)", tc.expectedResponse, resp)
			}
			if !errors.Is(err, tc.expectedErr) {
				t.Errorf("expected (%v), got (%v)", tc.expectedErr, err)
			}
		})
	}
}

func TestSecondsToUptime(t *testing.T) {
	type args struct {
		seconds uint64
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "convert-seconds-to-uptime",
			args: args{seconds: 1800},
			want: "0 days, 00:30:00",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := SecondsToUptime(tt.args.seconds); got != tt.want {
				t.Errorf("SecondsToUptime() = %v, want %v", got, tt.want)
			}
		})
	}
}
