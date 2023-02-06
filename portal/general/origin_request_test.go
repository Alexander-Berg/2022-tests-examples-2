package models

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/library/go/test/assertpb"
)

func TestNewOriginRequest(t *testing.T) {
	type args struct {
		dto *protoanswers.THttpRequest
	}
	tests := []struct {
		name string
		args args
		want *OriginRequest
	}{
		{
			name: "simple request",
			args: args{
				dto: &protoanswers.THttpRequest{
					Method:  protoanswers.THttpRequest_Get,
					Scheme:  protoanswers.THttpRequest_Https,
					Path:    "/test",
					Headers: []*protoanswers.THeader{{Name: "Host", Value: "test"}, {Name: "Cookie", Value: "cookie val"}},
					Content: []byte(`something that can not affect tests`),
				},
			},
			want: &OriginRequest{
				Method: protoanswers.THttpRequest_Get,
				Scheme: protoanswers.THttpRequest_Https,
				Path:   "/test",
				Headers: map[string][]string{
					"Host":   {"test"},
					"Cookie": {"cookie val"},
				},
				Content: []byte(`something that can not affect tests`),
			},
		},
		{
			name: "nil dto",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "empty dto",
			args: args{
				dto: &protoanswers.THttpRequest{},
			},
			want: &OriginRequest{
				Headers: map[string][]string{},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewOriginRequest(tt.args.dto))
		})
	}
}

func TestOriginRequest_DTO(t *testing.T) {
	type fields struct {
		Method   protoanswers.THttpRequest_EMethod
		Scheme   protoanswers.THttpRequest_EScheme
		Path     string
		Headers  http.Header
		Content  []byte
		RemoteIP string
	}
	tests := []struct {
		name   string
		fields fields
		want   *protoanswers.THttpRequest
	}{
		{
			name: "simple request",
			fields: fields{
				Method: protoanswers.THttpRequest_Get,
				Scheme: protoanswers.THttpRequest_Https,
				Path:   "/test",
				Headers: map[string][]string{
					"Host":   {"test"},
					"Cookie": {"cookie val"},
				},
				Content: []byte(`something that can not affect tests`),
			},
			want: &protoanswers.THttpRequest{
				Method: protoanswers.THttpRequest_Get,
				Scheme: protoanswers.THttpRequest_Https,
				Path:   "/test",
				Headers: []*protoanswers.THeader{
					{Name: "Cookie", Value: "cookie val"},
					{Name: "Host", Value: "test"},
				},
				Content: []byte(`something that can not affect tests`),
			},
		},
		{
			name: "several cookie headers",
			fields: fields{
				Method: protoanswers.THttpRequest_Get,
				Scheme: protoanswers.THttpRequest_Https,
				Path:   "/test",
				Headers: map[string][]string{
					"Host":   {"test"},
					"Cookie": {"val2", "val1", "val3"},
				},
				Content: []byte(`something that can not affect tests`),
			},
			want: &protoanswers.THttpRequest{
				Method: protoanswers.THttpRequest_Get,
				Scheme: protoanswers.THttpRequest_Https,
				Path:   "/test",
				Headers: []*protoanswers.THeader{
					{Name: "Cookie", Value: "val2"},
					{Name: "Cookie", Value: "val1"},
					{Name: "Cookie", Value: "val3"},
					{Name: "Host", Value: "test"},
				},
				Content: []byte(`something that can not affect tests`),
			},
		},
		{
			name:   "empty model",
			fields: fields{},
			want: &protoanswers.THttpRequest{
				Headers: []*protoanswers.THeader{},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &OriginRequest{
				Method:   tt.fields.Method,
				Scheme:   tt.fields.Scheme,
				Path:     tt.fields.Path,
				Headers:  tt.fields.Headers,
				Content:  tt.fields.Content,
				RemoteIP: tt.fields.RemoteIP,
			}
			got := m.DTO()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestOriginRequest_GetHost(t *testing.T) {
	type fields struct {
		Headers http.Header
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{
			name: "simple request",
			fields: fields{
				Headers: map[string][]string{
					"Host": {"test"},
				},
			},
			want: "test",
		},
		{
			name:   "empty model",
			fields: fields{},
			want:   "",
		},
		{
			name: "models without host header",
			fields: fields{
				Headers: map[string][]string{
					"Cookie": {"cookie val"},
				},
			},
			want: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &OriginRequest{
				Headers: tt.fields.Headers,
			}
			got, _ := m.GetHost()
			require.Equal(t, tt.want, got)
		})
	}
}

func TestOriginRequest_GetHostWithoutPort(t *testing.T) {
	type fields struct {
		Headers http.Header
	}
	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{
			name: "simple request",
			fields: fields{
				Headers: map[string][]string{
					"Host": {"yandex.ru"},
				},
			},
			want: "yandex.ru",
		},
		{
			name: "simple request with port",
			fields: fields{
				Headers: map[string][]string{
					"Host": {"yandex.ru:443"},
				},
			},
			want: "yandex.ru",
		},
		{
			name:   "empty model",
			fields: fields{},
			want:   "",
		},
		{
			name: "models without host header",
			fields: fields{
				Headers: map[string][]string{
					"Cookie": {"cookie val"},
				},
			},
			want: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &OriginRequest{
				Headers: tt.fields.Headers,
			}
			got, _ := m.GetHostWithoutPort()
			require.Equal(t, tt.want, got)
		})
	}
}

func TestOriginRequest_GetIP(t *testing.T) {
	type fields struct {
		Headers http.Header
	}
	tests := []struct {
		name    string
		fields  fields
		want    string
		wantErr bool
	}{
		{
			name: "ip in X-Forwarded-For-Y header",
			fields: fields{
				Headers: map[string][]string{
					"X-Forwarded-For-Y": {"123.123.123.123"},
				},
			},
			want:    "123.123.123.123",
			wantErr: false,
		},
		{
			name: "ip in X-Real-Ip header",
			fields: fields{
				Headers: map[string][]string{
					"X-Real-Ip": {"123.123.123.123"},
				},
			},
			want:    "123.123.123.123",
			wantErr: false,
		},
		{
			name: "ip in X-Real-Remote-Ip header",
			fields: fields{
				Headers: map[string][]string{
					"X-Real-Remote-Ip": {"123.123.123.123"},
				},
			},
			want:    "123.123.123.123",
			wantErr: false,
		},
		{
			name:    "empty model",
			fields:  fields{},
			want:    "",
			wantErr: true,
		},
		{
			name: "models without ip headers",
			fields: fields{
				Headers: map[string][]string{
					"Cookie": {"cookie val"},
					"Host":   {"test"},
				},
			},
			want:    "",
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &OriginRequest{
				Headers: tt.fields.Headers,
			}
			got, err := m.GetIP()

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, got)
			}
		})
	}
}

func TestOriginRequest_sortHeaders(t *testing.T) {
	tests := []struct {
		name    string
		headers []*protoanswers.THeader
		want    []*protoanswers.THeader
	}{
		{
			name: "sorted",
			headers: []*protoanswers.THeader{
				{Name: "Cookie", Value: "qwe123"},
				{Name: "Host", Value: "yandex.ru"},
				{Name: "X-Yandex-Random-UID", Value: "111111111"},
			},
			want: []*protoanswers.THeader{
				{Name: "Cookie", Value: "qwe123"},
				{Name: "Host", Value: "yandex.ru"},
				{Name: "X-Yandex-Random-UID", Value: "111111111"},
			},
		},
		{
			name: "unsorted",
			headers: []*protoanswers.THeader{
				{Name: "X-Yandex-Random-UID", Value: "111111111"},
				{Name: "Cookie", Value: "qwe123"},
				{Name: "Host", Value: "yandex.ru"},
			},
			want: []*protoanswers.THeader{
				{Name: "Cookie", Value: "qwe123"},
				{Name: "Host", Value: "yandex.ru"},
				{Name: "X-Yandex-Random-UID", Value: "111111111"},
			},
		},
		{
			name: "unsorted with repeated names",
			headers: []*protoanswers.THeader{
				{Name: "Cookie", Value: "qwe123"},
				{Name: "X-Yandex-Random-UID", Value: "111111111"},
				{Name: "Host", Value: "yandex.com"},
				{Name: "Cookie", Value: "abc123"},
				{Name: "Host", Value: "yandex.ru"},
			},
			want: []*protoanswers.THeader{
				{Name: "Cookie", Value: "qwe123"},
				{Name: "Cookie", Value: "abc123"},
				{Name: "Host", Value: "yandex.com"},
				{Name: "Host", Value: "yandex.ru"},
				{Name: "X-Yandex-Random-UID", Value: "111111111"},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &OriginRequest{}
			r.sortHeaders(tt.headers)
			assert.Equal(t, tt.want, tt.headers)
		})
	}
}
