package models

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewMadmContent(t *testing.T) {
	type args struct {
		dto *mordadata.MadmContent
	}

	tests := []struct {
		name string
		args args
		want *MadmContent
	}{
		{
			name: "nil dto",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "nil dto values",
			args: args{
				dto: &mordadata.MadmContent{
					Values: nil,
				},
			},
			want: &MadmContent{
				Values: nil,
			},
		},
		{
			name: "empty dto values",
			args: args{
				dto: &mordadata.MadmContent{
					Values: make([][]byte, 0),
				},
			},
			want: &MadmContent{
				Values: nil,
			},
		},
		{
			name: "success",
			args: args{
				dto: &mordadata.MadmContent{
					Values: [][]byte{
						[]byte("touch"),
						[]byte("big"),
					},
				},
			},
			want: &MadmContent{
				Values: []string{
					"touch",
					"big",
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewMadmContent(tt.args.dto))
		})
	}
}

func TestMadmContent_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *MadmContent
		want  *mordadata.MadmContent
	}{
		{
			name:  "nil madm content",
			model: nil,
			want:  nil,
		},
		{
			name: "nil madm content values",
			model: &MadmContent{
				Values: nil,
			},
			want: &mordadata.MadmContent{
				Values: nil,
			},
		},
		{
			name: "empty madm content values",
			model: &MadmContent{
				Values: make([]string, 0),
			},
			want: &mordadata.MadmContent{
				Values: nil,
			},
		},
		{
			name: "success",
			model: &MadmContent{
				Values: []string{
					"touch",
					"big",
				},
			},
			want: &mordadata.MadmContent{
				Values: [][]byte{
					[]byte("touch"),
					[]byte("big"),
				},
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
