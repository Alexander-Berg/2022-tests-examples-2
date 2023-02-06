package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewLocale(t *testing.T) {
	type testCase struct {
		name string
		dto  *mordadata.Lang
		want *Locale
	}
	cases := []testCase{
		{
			name: "DTO is nil",
			dto:  nil,
			want: nil,
		},
		{
			name: "nil locale",
			dto: &mordadata.Lang{
				Locale: nil,
			},
			want: &Locale{
				Value: "",
			},
		},
		{
			name: "empty locale",
			dto: &mordadata.Lang{
				Locale: make([]byte, 0),
			},
			want: &Locale{
				Value: "",
			},
		},
		{
			name: "regular case",
			dto: &mordadata.Lang{
				Locale: []byte("ru"),
			},
			want: &Locale{
				Value: "ru",
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := NewLocale(tt.dto)
			assert.Equal(t, tt.want, actual)
		})
	}
}

func TestLocale_DTO(t *testing.T) {
	type testCase struct {
		name  string
		model *Locale
		want  *mordadata.Lang
	}
	cases := []testCase{
		{
			name:  "nil locale",
			model: nil,
			want:  nil,
		},
		{
			name: "empty string",
			model: &Locale{
				Value: "",
			},
			want: &mordadata.Lang{
				Locale: make([]byte, 0),
			},
		},
		{
			name: "regular case",
			model: &Locale{
				Value: "ru",
			},
			want: &mordadata.Lang{
				Locale: []byte("ru"),
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			actual := tt.model.DTO()
			assertpb.Equal(t, tt.want, actual)
		})
	}
}
