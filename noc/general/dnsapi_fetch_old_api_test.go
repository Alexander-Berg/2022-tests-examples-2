package zoneupdate

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"
)

func TestFetchZoneOldAPI(t *testing.T) {
	type args struct {
		zone   string
		auth   Auther
		apiURL string
		debug  bool
	}

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(testZoneResponseXMLBody))
	}))
	tests := []struct {
		name    string
		args    args
		want    []RecordSets
		wantErr bool
	}{
		{
			name: "fetch and parse zone from old xml api",
			args: args{
				zone:   "dns.yandex.net",
				auth:   TokenForTestInitAuth("AV....Pw", "OAuth"),
				debug:  false,
				apiURL: server.URL,
			},
			/*
				[
				{ID:dns-static01v-test.dns.yandex.net. Records:[{TTL:3600 Class:IN Type:AAAA Data:2a02:6b8:c0e:103:0:433f:fed0:c34b}]}
				{ID:ns-khab01.dns.yandex.net. Records:[{TTL:7200 Class:IN Type:A Data:5.255.194.114}]}
				{ID:ns01v-test.dns.yandex.net. Records:[{TTL:3600 Class:IN Type:A Data:5.255.194.1} {TTL:3600 Class:IN Type:AAAA Data:2a02:6b8:c0e:103:0:433f:fed0:fccc}]}
				{ID:test.ns01v-test.dns.yandex.net. Records:[{TTL:3600 Class:IN Type:CNAME Data:ns01v-test.dns.yandex.net.}]}]
			*/
			want: []RecordSets{{
				ID: "dns-static01v-test.dns.yandex.net.",
				Records: []Records{{
					TTL:   3600,
					Class: "IN",
					Type:  "AAAA",
					Data:  "2a02:6b8:c0e:103:0:433f:fed0:c34b",
				}},
			}, {
				ID: "ns-khab01.dns.yandex.net.",
				Records: []Records{{
					TTL:   7200,
					Class: "IN",
					Type:  "A",
					Data:  "5.255.194.114",
				}},
			}, {
				ID: "ns01v-test.dns.yandex.net.",
				Records: []Records{{
					TTL:   3600,
					Class: "IN",
					Type:  "A",
					Data:  "5.255.194.1",
				}, {
					TTL:   3600,
					Class: "IN",
					Type:  "AAAA",
					Data:  "2a02:6b8:c0e:103:0:433f:fed0:fccc",
				}},
			}, {
				ID: "test.ns01v-test.dns.yandex.net.",
				Records: []Records{{
					TTL:   3600,
					Class: "IN",
					Type:  "CNAME",
					Data:  "ns01v-test.dns.yandex.net.",
				}},
			}},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := FetchZoneOldAPI(tt.args.zone, tt.args.auth, tt.args.apiURL, tt.args.debug)
			//fmt.Printf("got = %+v\n error = %s\n", got, err)
			if (err != nil) != tt.wantErr {
				t.Errorf("FetchZoneOldAPI() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("FetchZoneOldAPI() got = %v, want %v", got, tt.want)
			}
		})
	}
}

type TokenForTest struct {
	Token  string
	Header string
}

func (m TokenForTest) GetToken() string {
	return m.Token
}

func (m TokenForTest) GetHeader() string {
	return m.Header
}

func (m TokenForTest) String() string {
	return fmt.Sprintf("oauth token: %s and header: %s\n", m.Token, m.GetHeader())
}

func TokenForTestInitAuth(token string, header string) TokenForTest {
	return TokenForTest{
		Token:  token,
		Header: header,
	}
}

var testZoneResponseXMLBody = `
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<!-- Generated on "dns-api02v.berry.yandex.net" at "2022-05-01 12:02:05.838448989 +0300 MSK m=+138849.405059143" -->

<response type="netinfo">
  <netinfo>
    <network-type>direct</network-type>
    <name>dns.yandex.net.</name>
    <type>dynamic</type>
    <content type="axfr">
    <record type="AAAA" ttl="3600">
    <left-side>dns-static01v-test.dns.yandex.net.</left-side>
    <right-side>2a02:6b8:c0e:103:0:433f:fed0:c34b</right-side>
    </record>
    <record type="NS" ttl="172800">
    <left-side>dns.yandex.net.</left-side>
    <right-side>ns4.yandex.ru.</right-side>
    </record>
    <record type="A" ttl="7200">
    <left-side>ns-khab01.dns.yandex.net.</left-side>
    <right-side>5.255.194.114</right-side>
    </record>
    <record type="A" ttl="3600">
    <left-side>ns01v-test.dns.yandex.net.</left-side>
    <right-side>5.255.194.1</right-side>
    </record>
    <record type="AAAA" ttl="3600">
    <left-side>ns01v-test.dns.yandex.net.</left-side>
    <right-side>2a02:6b8:c0e:103:0:433f:fed0:fccc</right-side>
    </record>
    <record type="CNAME" ttl="3600">
    <left-side>test.ns01v-test.dns.yandex.net.</left-side>
    <right-side>ns01v-test.dns.yandex.net.</right-side>
    </record>
    </content>
    <acl-match>yes</acl-match>
    <acl-match-robot>yes</acl-match-robot>
    <acl-match-group>yes</acl-match-group>
    <acl-match-group-id></acl-match-group-id>
    <acl-list>ROBOT_KEY("kcsf-js4q-mlun-zbdl");GROUP_KEYS(svc_dostavkatraffika_administration);</acl-list>
    <sub-type>realzone</sub-type>
  </netinfo>
   <display>
   <encoded-text>eJyMUk2P0zAQvfcv9OLbAIlbN3HSxAc4wA0QB45RtZrYExFaO5HtlC2/HqW0LF9SNhdrPt7MvPeyWq2bWlj259eIw7YRh3UjLPs+OFJgXNhc0Bl63DiKG2D6hCEoML0nHYGFqb1l3BZhcailiAqmqTcK6kIKWeGOVybvuKxL5DXuM266QudVsSvzXELq0P5zBqS3nfONkLaoj+RMUA24kCcuyNSF5DLCIe384OKvWnIZ54pG/YXgkKKO/RkjmXsRDqn2dM1kIsu4kFyUTFRK7lWWbfJqV4idLFgiciHYx8/v02k0C+1Fnj31P0MgDJG8grefPrwDdmeWPPFgDaybOrM3pjMoXTe1tFcGcwgHxl8vt81hbu9y/AQunucJT1bB9eGTu9rQdz2ZZWaoT4qRi328JDf7fn8Sc3Foez1bGuB54yBeRrrjUZ8EpEP7lXRUMGKM5J3abl9sXr188/f/c0UfFWCrk6CHkWDW7JoNZ/1ghhDxfMTosev6Iz6gsb3rQ/QY+8EBpH46zZtrU1LbZrwqCsNlSyVvaU+83EtdVhJpVxaQDt/cbOl/RFum6UkP3gQFWQ1smCIbOmbxUUEhhFiGj37QFAIZBcVus6+zsrYBVqsfAQAA//+PDSMY</encoded-text>
   <encoding>ZIPPED+ENCODED</encoding>
   </display>
  <zone-stats>
    <processing_time>52.055821ms</processing_time>
  </zone-stats>
</response>
`
