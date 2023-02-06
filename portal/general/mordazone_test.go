package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewMordaZone(t *testing.T) {
	type testCase struct {
		name string
		dto  *mordadata.MordaZone
		want *MordaZone
	}
	tests := []testCase{
		{
			name: "nil DTO",
			dto:  nil,
			want: nil,
		},
		{
			name: "empty",
			dto:  &mordadata.MordaZone{},
			want: &MordaZone{},
		},
		{
			name: "common value",
			dto: &mordadata.MordaZone{
				Value: []byte("com.tr"),
			},
			want: &MordaZone{
				Value: "com.tr",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewMordaZone(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestMordaZone_DTO(t *testing.T) {
	type testCase struct {
		name  string
		model *MordaZone
		want  *mordadata.MordaZone
	}

	tests := []testCase{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty fields",
			model: &MordaZone{},
			want: &mordadata.MordaZone{
				Value: []byte(""),
			},
		},
		{
			name: "common value",
			model: &MordaZone{
				Value: "com.tr",
			},
			want: &mordadata.MordaZone{
				Value: []byte("com.tr"),
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
