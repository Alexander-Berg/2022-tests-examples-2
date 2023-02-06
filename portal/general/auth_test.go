package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewAuth(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.Auth
		want *Auth
	}{
		{
			name: "nil dto",
			dto:  nil,
			want: nil,
		},
		{
			name: "empty sids",
			dto: &mordadata.Auth{
				UID:    []byte("test"),
				Sids:   map[string][]byte{},
				Logged: false,
			},
			want: &Auth{
				UID:              "test",
				Sids:             map[string]string{},
				IsChildAccount:   false,
				PlusSubscription: PlusSubscription{},
				Logged:           false,
				SocialUser:       "",
			},
		},
		{
			name: "empty UID",
			dto: &mordadata.Auth{
				UID: []byte{},
				Sids: map[string][]byte{
					"1": []byte("1"),
					"2": []byte("2"),
				},
				Logged: false,
			},
			want: &Auth{
				UID: "",
				Sids: map[string]string{
					"1": "1",
					"2": "2",
				},
				IsChildAccount:   false,
				PlusSubscription: PlusSubscription{},
				Logged:           false,
			},
		},
		{
			name: "common value",
			dto: &mordadata.Auth{
				UID: []byte("test"),
				Sids: map[string][]byte{
					"1": []byte("1"),
					"2": []byte("2"),
				},
				Logged: true,
			},
			want: &Auth{
				UID: "test",
				Sids: map[string]string{
					"1": "1",
					"2": "2",
				},
				IsChildAccount:   false,
				PlusSubscription: PlusSubscription{},
				Logged:           true,
			},
		},
		{
			name: "child account",
			dto: &mordadata.Auth{
				IsChildAccount: true,
			},
			want: &Auth{
				UID:              "",
				Sids:             map[string]string{},
				IsChildAccount:   true,
				PlusSubscription: PlusSubscription{},
			},
		},
		{
			name: "plus activated",
			dto: &mordadata.Auth{
				UID:            []byte("test_123"),
				Sids:           nil,
				IsChildAccount: false,
				PlusSubscription: &mordadata.PlusSubscription{
					Status:              true,
					NextChargeTimestamp: 1666666666,
					StatusType:          "YA_PREMIUM",
					ExpireTimestamp:     1777777777,
				},
				Logged: true,
			},
			want: &Auth{
				UID:            "test_123",
				Sids:           map[string]string{},
				IsChildAccount: false,
				PlusSubscription: PlusSubscription{
					Status:              true,
					NextChargeTimestamp: 1666666666,
					StatusType:          "YA_PREMIUM",
					ExpireTimestamp:     1777777777,
				},
				Logged: true,
			},
		},
		{
			name: "has social",
			dto: &mordadata.Auth{
				UID:        []byte("test_123"),
				Logged:     true,
				SocialUser: "some_social_name",
			},
			want: &Auth{
				UID:        "test_123",
				Sids:       map[string]string{},
				Logged:     true,
				SocialUser: "some_social_name",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewAuth(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestAuth_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *Auth
		want  *mordadata.Auth
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "empty sids",
			model: &Auth{
				UID:    "test",
				Sids:   map[string]string{},
				Logged: true,
			},
			want: &mordadata.Auth{
				UID:              []byte("test"),
				Sids:             map[string][]byte{},
				IsChildAccount:   false,
				PlusSubscription: &mordadata.PlusSubscription{},
				Logged:           true,
			},
		},
		{
			name: "empty UID",
			model: &Auth{
				UID: "",
				Sids: map[string]string{
					"1": "1",
					"2": "2",
				},
				Logged: false,
			},
			want: &mordadata.Auth{
				UID: []byte{},
				Sids: map[string][]byte{
					"1": []byte("1"),
					"2": []byte("2"),
				},
				IsChildAccount:   false,
				PlusSubscription: &mordadata.PlusSubscription{},
				Logged:           false,
			},
		},
		{
			name: "common value",
			model: &Auth{
				UID: "test",
				Sids: map[string]string{
					"1": "1",
					"2": "2",
				},
				Logged: true,
			},
			want: &mordadata.Auth{
				UID: []byte("test"),
				Sids: map[string][]byte{
					"1": []byte("1"),
					"2": []byte("2"),
				},
				IsChildAccount:   false,
				PlusSubscription: &mordadata.PlusSubscription{},
				Logged:           true,
			},
		},
		{
			name: "child account",
			model: &Auth{
				IsChildAccount: true,
			},
			want: &mordadata.Auth{
				UID:              []byte{},
				Sids:             map[string][]byte{},
				IsChildAccount:   true,
				PlusSubscription: &mordadata.PlusSubscription{},
			},
		},
		{
			name: "plus activated",
			model: &Auth{
				UID:            "test_123",
				Sids:           nil,
				IsChildAccount: false,
				PlusSubscription: PlusSubscription{
					Status:              true,
					NextChargeTimestamp: 1666666666,
					StatusType:          "YA_PREMIUM",
					ExpireTimestamp:     1777777777,
				},
			},
			want: &mordadata.Auth{
				UID:            []byte("test_123"),
				Sids:           nil,
				IsChildAccount: false,
				PlusSubscription: &mordadata.PlusSubscription{
					Status:              true,
					NextChargeTimestamp: 1666666666,
					StatusType:          "YA_PREMIUM",
					ExpireTimestamp:     1777777777,
				},
			},
		},
		{
			name: "social name",
			model: &Auth{
				UID:        "test",
				Logged:     true,
				SocialUser: "some_social_name",
			},
			want: &mordadata.Auth{
				UID:              []byte("test"),
				IsChildAccount:   false,
				PlusSubscription: &mordadata.PlusSubscription{},
				Logged:           true,
				SocialUser:       "some_social_name",
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()
			assertpb.Equal(t, tt.want, got)
		})
	}
}

func TestAuth_GetMobileMail(t *testing.T) {
	tests := []struct {
		name string
		sids map[string]string
		want string
	}{
		{
			name: "empty sids",
			sids: map[string]string{},
			want: "",
		},
		{
			name: "common value",
			sids: map[string]string{
				"55": "test",
			},
			want: "test",
		},
		{
			name: "without 55 sid",
			sids: map[string]string{
				"54":         "test",
				"mobilmail":  "test",
				"mobil_mail": "test",
			},
			want: "",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			a := &Auth{
				Sids: tt.sids,
			}
			assert.Equalf(t, tt.want, a.GetMobileMail(), "GetMobileMail()")
		})
	}
}
