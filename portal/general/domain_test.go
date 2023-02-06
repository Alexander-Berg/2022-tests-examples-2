package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewDomain(t *testing.T) {
	type testCase struct {
		name string
		dto  *mordadata.Domain
		want *Domain
	}
	tests := []testCase{
		{
			name: "nil DTO",
			dto:  nil,
			want: nil,
		},
		{
			name: "empty",
			dto:  &mordadata.Domain{},
			want: &Domain{},
		},
		{
			name: "common value",
			dto: &mordadata.Domain{
				Zone:      []byte("com.tr"),
				Domain:    []byte("yandex.com.tr"),
				Subdomain: []byte("v194d0.wdevx"),
				Prefix:    []byte("v194d0"),
				Wdevx:     []byte("wdevx"),
			},
			want: &Domain{
				Zone:      "com.tr",
				Domain:    "yandex.com.tr",
				Subdomain: "v194d0.wdevx",
				Prefix:    "v194d0",
				WDevX:     "wdevx",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewDomain(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestDomain_DTO(t *testing.T) {
	type testCase struct {
		name  string
		model *Domain
		want  *mordadata.Domain
	}

	tests := []testCase{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty fields",
			model: &Domain{},
			want: &mordadata.Domain{
				Zone:      []byte(""),
				Domain:    []byte(""),
				Subdomain: []byte(""),
				Prefix:    []byte(""),
				Wdevx:     []byte(""),
			},
		},
		{
			name: "common value",
			model: &Domain{
				Zone:      "com.tr",
				Domain:    "yandex.com.tr",
				Subdomain: "v194d0.wdevx",
				Prefix:    "v194d0",
				WDevX:     "wdevx",
			},
			want: &mordadata.Domain{
				Zone:      []byte("com.tr"),
				Domain:    []byte("yandex.com.tr"),
				Subdomain: []byte("v194d0.wdevx"),
				Prefix:    []byte("v194d0"),
				Wdevx:     []byte("wdevx"),
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
