package blocks

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestSettings_IsZenFolded(t *testing.T) {
	tests := []struct {
		name     string
		settings *Settings
		want     bool
	}{
		{
			name:     "Empty settings",
			settings: &Settings{},
			want:     false,
		},
		{
			name: "Folded map is empty",
			settings: &Settings{
				folded: map[ID]bool{},
			},
			want: false,
		},
		{
			name: "Folded map contain information for zen but it was false",
			settings: &Settings{
				folded: map[ID]bool{
					InfinityZenID: false,
				},
			},
			want: false,
		},
		{
			name: "Folded map contain information for zen and it was true",
			settings: &Settings{
				folded: map[ID]bool{
					InfinityZenID: true,
				},
			},
			want: true,
		},
		{
			name:     "Settings is nil",
			settings: nil,
			want:     false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.settings.IsZenFolded()

			require.Equal(t, tt.want, got)
		})
	}
}
