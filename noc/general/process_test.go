package zoneupdate

import (
	"fmt"
	"reflect"
	"testing"
)

func TestCheckRawAndReturnValidDNSQuery(t *testing.T) {
	type args struct {
		q       []string
		reverse bool
	}
	tests := []struct {
		name  string
		args  args
		want  []string
		want1 error
	}{
		{
			"raw A query",
			args{q: []string{"invest.yandex.ru. 600 A 213.180.193.129"}, reverse: true},
			[]string{"invest.yandex.ru.\t600\tIN\tA\t213.180.193.129"},
			nil,
		},
		{
			"raw delete A query",
			args{q: []string{"invest.yandex.ru. 600 A 213.180.193.129"}, reverse: true},
			[]string{"invest.yandex.ru.\t600\tIN\tA\t213.180.193.129"},
			nil,
		},
		{
			"raw AAAA query",
			args{q: []string{"adfox.ru. 300 IN AAAA 2a02:6b8::366"}, reverse: true},
			[]string{"adfox.ru.\t300\tIN\tAAAA\t2a02:6b8::366"},
			nil,
		},
		{
			"raw PTR query without reverse",
			args{q: []string{"2a02:6b8::2:242 900 IN PTR ya.ru."}, reverse: true},
			[]string{"2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa.\t900\tIN\tPTR\tya.ru."},
			nil,
		},
		{
			"raw PTR query without reverse for old api",
			args{q: []string{"2a02:6b8::2:242 900 IN PTR ya.ru."}, reverse: false},
			[]string{"2a02:6b8::2:242\t900\tIN\tPTR\tya.ru."},
			nil,
		},
		{
			"raw reverse PTR ipv6 query without reverse",
			args{q: []string{"2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa. 900 IN PTR ya.ru."}, reverse: false},
			[]string{"2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa.\t900\tIN\tPTR\tya.ru."},
			nil,
		},
		{
			"raw reverse PTR ipv6 query with reverse",
			args{q: []string{"2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa. 900 IN PTR ya.ru."}, reverse: true},
			[]string{"2a02:6b8::2:242\t900\tIN\tPTR\tya.ru."},
			nil,
		},
		{
			"raw reverse PTR ipv4 query without reverse",
			args{q: []string{"1.2.3.4.in-addr.arpa. 900 IN PTR ya.ru."}, reverse: false},
			[]string{"1.2.3.4.in-addr.arpa.\t900\tIN\tPTR\tya.ru."},
			nil,
		},
		{
			"raw reverse PTR ipv4 query with reverse",
			args{q: []string{"1.2.3.4.in-addr.arpa. 900 IN PTR ya.ru."}, reverse: true},
			[]string{"4.3.2.1\t900\tIN\tPTR\tya.ru."},
			nil,
		},
		{
			"bad A raw query",
			args{q: []string{"213.180.193.129 600 A invest.yandex.ru."}, reverse: true},
			[]string{},
			fmt.Errorf("bad A A"),
		},
		{
			"raw heavy TXT query",
			args{q: []string{"mail._domainkey.adv-events.yandex.ru.   3600    IN      TXT     \"v=DKIM1; k=rsa; t=s; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCHXMn6iPHN9w47A1PZs2yRdd4vtozf0M6QbUxjPOYRBYVH1pERf9HETOJQevTx3SUCPJyOwT+gcZUrpjUlokgM/FI1lhTOyY92h6fMRxECVk0eHYS0Hl66XfvGKebQIIUHtfMqKsh7LAjfpWT1E1kOx/lQpV9qk1jNXaY2JDyJKQIDAQAB\""}, reverse: true},
			[]string{"mail._domainkey.adv-events.yandex.ru.\t3600\tIN\tTXT\t\"v=DKIM1; k=rsa; t=s; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCHXMn6iPHN9w47A1PZs2yRdd4vtozf0M6QbUxjPOYRBYVH1pERf9HETOJQevTx3SUCPJyOwT+gcZUrpjUlokgM/FI1lhTOyY92h6fMRxECVk0eHYS0Hl66XfvGKebQIIUHtfMqKsh7LAjfpWT1E1kOx/lQpV9qk1jNXaY2JDyJKQIDAQAB\""},
			nil,
		},
		{
			"raw SRV query",
			args{q: []string{"_imap._tcp 7200 SRV 0 0 0 ."}, reverse: true},
			[]string{"_imap._tcp.\t7200\tIN\tSRV\t0 0 0 ."},
			nil,
		},
		{
			"raw MX query",
			args{q: []string{"adfox.ru. 300 IN MX 10 mx.yandex.ru."}, reverse: true},
			[]string{"adfox.ru.\t300\tIN\tMX\t10 mx.yandex.ru."},
			nil,
		},
		{
			"raw CAA query",
			args{q: []string{"example.com.  IN  CAA 0 iodef mailto:security@example.com"}, reverse: true},
			[]string{"example.com.\t3600\tIN\tCAA\t0 iodef \"mailto:security@example.com\""},
			nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, got1 := CheckRawAndReturnValidDNSQuery(tt.args.q, tt.args.reverse)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("CheckRawAndReturnValidDNSQuery() got = %v, want %v", got, tt.want)
			}
			if got1 != tt.want1 {
				if got1.Error() == tt.want1.Error() {
					t.Errorf("CheckRawAndReturnValidDNSQuery() got1 = %v, want %v", got1, tt.want1)
				}
			}
		})
	}
}

func TestCheckSimpleAndReturnValidDNSQuery(t *testing.T) {
	type args struct {
		expression string
		reverse    bool
	}
	tests := []struct {
		name  string
		args  args
		want  string
		want1 Operation
		want2 error
	}{
		{
			"simple A query",
			args{expression: "add-a invest.yandex.ru. 213.180.193.129", reverse: true},
			"invest.yandex.ru.\t600\tIN\tA\t213.180.193.129",
			Add,
			nil,
		},
		{
			"simple delete A query",
			args{expression: "delete-a invest.yandex.ru. 213.180.193.129", reverse: true},
			"invest.yandex.ru.\t600\tIN\tA\t213.180.193.129",
			Remove,
			nil,
		},
		{
			"simple A query with TTL",
			args{expression: "add-a invest.yandex.ru. 900 213.180.193.129", reverse: true},
			"invest.yandex.ru.\t900\tIN\tA\t213.180.193.129",
			Add,
			nil,
		},
		{
			"raw AAAA query",
			args{expression: "add-aaaa adfox.ru. 2a02:6b8::366", reverse: true},
			"adfox.ru.\t600\tIN\tAAAA\t2a02:6b8::366",
			Add,
			nil,
		},
		{
			"simple PTR query without reverse",
			args{expression: "add-ptr 2a02:6b8::2:242 ya.ru.", reverse: true},
			"2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa.\t600\tIN\tPTR\tya.ru.",
			Add,
			nil,
		},
		{
			"simple PTR query without reverse for old api",
			args{expression: "add-ptr 2a02:6b8::2:242 ya.ru.", reverse: false},
			"2a02:6b8::2:242\t600\tIN\tPTR\tya.ru.",
			Add,
			nil,
		},
		{
			"simple reverse PTR ipv6 query with reverse",
			args{expression: "add-ptr 2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa. ya.ru.", reverse: true},
			"2a02:6b8::2:242\t600\tIN\tPTR\tya.ru.",
			Add,
			nil,
		},
		{
			"simple reverse PTR ipv6 query without reverse",
			args{expression: "add-ptr 2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa. ya.ru.", reverse: false},
			"2.4.2.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.6.0.2.0.a.2.ip6.arpa.\t600\tIN\tPTR\tya.ru.",
			Add,
			nil,
		},
		{
			"bad A simple query",
			args{expression: "add-a 213.180.193.129 invest.yandex.ru.", reverse: true},
			"",
			NotImp,
			fmt.Errorf("bad A A"),
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, got1, got2 := CheckSimpleAndReturnValidDNSQuery(tt.args.expression, tt.args.reverse)
			if got != tt.want {
				t.Errorf("CheckSimpleAndReturnValidDNSQuery() got = %v, want %v", got, tt.want)
			}
			if got1 != tt.want1 {
				t.Errorf("CheckSimpleAndReturnValidDNSQuery() got1 = %v, want %v", got1, tt.want1)
			}
			if got2 != tt.want2 {
				if got2.Error() == tt.want2.Error() {
					t.Errorf("CheckSimpleAndReturnValidDNSQuery() got2 = %v, want %v", got2, tt.want2)
				}
			}
		})
	}
}
