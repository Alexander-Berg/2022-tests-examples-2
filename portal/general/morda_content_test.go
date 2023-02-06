package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewMordaContent(t *testing.T) {
	type args struct {
		dto *mordadata.MordaContent
	}

	tests := []struct {
		name string
		args args
		want *MordaContent
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
				dto: &mordadata.MordaContent{
					Value: []byte("big"),
				},
			},
			want: &MordaContent{
				Value: "big",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewMordaContent(tt.args.dto))
		})
	}
}

func TestMordaContent_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *MordaContent
		want  *mordadata.MordaContent
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "success",
			model: &MordaContent{
				Value: "big",
			},
			want: &mordadata.MordaContent{
				Value: []byte("big"),
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

func TestMordaContent_IsTouch(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "touch",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsTouch())
		})
	}
}

func TestMordaContent_IsBig(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "big",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "touch",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsBig())
		})
	}
}

func TestMordaContent_IsMob(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "mob",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}
			assert.Equal(t, tt.want, m.IsMob())
		})
	}
}

func TestMordaContent_IsPDA(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "pda",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsPDA())
		})
	}
}

func TestMordaContent_IsTel(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "tel",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsTel())
		})
	}
}

func TestMordaContent_IsTV(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "tv",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsTV())
		})
	}
}

func TestMordaContent_IsYabrotab(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "yabrotab",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsYabrotab())
		})
	}
}

func TestMordaContent_IsCom(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "com",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsCom())
		})
	}
}

func TestMordaContent_IsSpok(t *testing.T) {
	type fields struct {
		Value string
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "success",
			fields: fields{
				Value: "spok",
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				Value: "big",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			m := &MordaContent{
				Value: tt.fields.Value,
			}

			assert.Equal(t, tt.want, m.IsSpok())
		})
	}
}
