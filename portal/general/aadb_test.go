package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewAADB(t *testing.T) {
	type args struct {
		dto *mordadata.AntiAdblock
	}
	tests := []struct {
		name string
		args args
		want *AADB
	}{
		{
			name: "DTO is nil",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "IsAddBlock is false",
			args: args{
				dto: &mordadata.AntiAdblock{
					IsAddBlock: false,
				},
			},
			want: &AADB{
				IsAddBlock: false,
			},
		},
		{
			name: "IsAddBlock is true",
			args: args{
				dto: &mordadata.AntiAdblock{
					IsAddBlock: true,
				},
			},
			want: &AADB{
				IsAddBlock: true,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewAADB(tt.args.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestAADB_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *AADB
		want  *mordadata.AntiAdblock
	}{
		{
			name:  "Model is nil",
			model: nil,
			want:  nil,
		},
		{
			name: "IsAddBlock is false",
			model: &AADB{
				IsAddBlock: false,
			},
			want: &mordadata.AntiAdblock{
				IsAddBlock: false,
			},
		},
		{
			name: "IsAddBlock is true",
			model: &AADB{
				IsAddBlock: true,
			},
			want: &mordadata.AntiAdblock{
				IsAddBlock: true,
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
