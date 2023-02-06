package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewCSP(t *testing.T) {
	type args struct {
		dto *mordadata.CSP
	}

	tests := []struct {
		name string
		args args
		want *CSP
	}{
		{
			name: "nil dto",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "success",
			args: args{
				dto: &mordadata.CSP{
					Nonce: "test",
				},
			},
			want: &CSP{
				Nonce: "test",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewCSP(tt.args.dto))
		})
	}
}

func TestCSP_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *CSP
		want  *mordadata.CSP
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "success",
			model: &CSP{
				Nonce: "test",
			},
			want: &mordadata.CSP{
				Nonce: "test",
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
