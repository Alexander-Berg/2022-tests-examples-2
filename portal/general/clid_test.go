package models

import (
	"testing"

	"github.com/stretchr/testify/require"
	"google.golang.org/protobuf/proto"

	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestNewClid(t *testing.T) {
	type args struct {
		dto *mordadata.Clid
	}
	tests := []struct {
		name string
		args args
		want *Clid
	}{
		{
			name: "DTO is nil",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "Client in dto is nil",
			args: args{
				dto: &mordadata.Clid{
					Client: nil,
				},
			},
			want: &Clid{
				Client: "",
			},
		},
		{
			name: "Client in dto is empty",
			args: args{
				dto: &mordadata.Clid{
					Client: []byte{},
				},
			},
			want: &Clid{
				Client: "",
			},
		},
		{
			name: "Client in dto is not empty",
			args: args{
				dto: &mordadata.Clid{
					Client: []byte(`test`),
				},
			},
			want: &Clid{
				Client: "test",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewClid(tt.args.dto)

			require.Equal(t, tt.want, got)
		})
	}
}

func TestClid_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *Clid
		want  *mordadata.Clid
	}{
		{
			name:  "Model is nil",
			model: nil,
			want:  nil,
		},
		{
			name: "Client in model is empty",
			model: &Clid{
				Client: "",
			},
			want: &mordadata.Clid{
				Client: []byte{},
			},
		},
		{
			name: "Client in model is not empty",
			model: &Clid{
				Client: "test",
			},
			want: &mordadata.Clid{
				Client: []byte("test"),
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()

			require.True(t, proto.Equal(tt.want, got))
		})
	}
}

func TestClid_NeedShowAppWin10(t *testing.T) {
	tests := []struct {
		name  string
		model *Clid
		want  bool
	}{
		{
			name:  "Model is nil",
			model: nil,
			want:  false,
		},
		{
			name: "Empty client",
			model: &Clid{
				Client: "",
			},
			want: false,
		},
		{
			name: "Desktop client",
			model: &Clid{
				Client: DesktopDefaultClid,
			},
			want: false,
		},
		{
			name: "Microsoft client #1",
			model: &Clid{
				Client: MicrosoftMordaZenClid,
			},
			want: true,
		},
		{
			name: "Microsoft client #2",
			model: &Clid{
				Client: MicrosoftMordaZenClid2,
			},
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.NeedShowAppWin10()

			require.Equal(t, tt.want, got)
		})
	}
}

func TestClid_IsDesktop(t *testing.T) {
	tests := []struct {
		name  string
		model *Clid
		want  bool
	}{
		{
			name: "Desktop",
			model: &Clid{
				Client: DesktopDefaultClid,
			},
			want: true,
		},
		{
			name: "Microsoft #1",
			model: &Clid{
				Client: MicrosoftMordaZenClid,
			},
			want: true,
		},
		{
			name: "Microsoft #2",
			model: &Clid{
				Client: MicrosoftMordaZenClid2,
			},
			want: true,
		},
		{
			name: "Rand",
			model: &Clid{
				Client: "89435",
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.IsDesktop()

			require.Equal(t, tt.want, got)
		})
	}
}
