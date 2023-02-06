package blackbox

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/require"
)

func Test_isLogged(t *testing.T) {
	tests := []struct {
		name    string
		data    string
		want    bool
		wantErr bool
	}{
		{
			name: "VALID status",
			data: "VALID",
			want: true,
		},
		{
			name: "NEED_RESET status",
			data: "NEED_RESET",
			want: true,
		},
		{
			name: "INVALID status",
			data: "INVALID",
			want: false,
		},
		{
			name: "empty status",
			data: "",
			want: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := isLogged(tt.data)
			require.Equal(t, tt.want, result)
		})
	}
}

func Test_AuthData(t *testing.T) {
	tests := []struct {
		name    string
		data    string
		want    AuthInfo
		wantErr bool
	}{
		{
			name: "No auth",
			data: "{\"status\":{\"value\":\"INVALID\",\"id\":5},\"error\":\"cookie is too old and cannot be checked\"}",
			want: AuthInfo{},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			bbResponse := BlackboxResponse{}
			_ = json.Unmarshal([]byte(tt.data), &bbResponse)
			authInfo := NewResponseParser(bbResponse).Parse()
			require.Equal(t, tt.want, authInfo)
		})
	}
}

func TestUserParser_getEmail(t *testing.T) {
	tests := []struct {
		name    string
		Address string
		want    authString
	}{
		{
			name:    "valid unicode address",
			Address: "test@yandex.ru",
			want:    "test@yandex.ru",
		},
		{
			name:    "punycode address",
			Address: "test@xn--d1acpjx3f.xn--p1ai",
			want:    "test@яндекс.рф",
		},
		{
			name:    "full cyrillic address",
			Address: "почта@xn--d1acpjx3f.xn--p1ai",
			want:    "почта@яндекс.рф",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &UserParser{
				user: User{
					AddressList: []Address{
						{Address: tt.Address, Default: true},
					},
				},
			}
			if got := p.getEmail(); got != tt.want {
				t.Errorf("getEmail() = %v, want %v", got, tt.want)
			}
		})
	}
}
