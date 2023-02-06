package madmtypes

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGeos_ParseMADM(t *testing.T) {
	var s struct{}
	tests := []struct {
		name    string
		input   string
		want    Geos
		wantErr bool
	}{
		{
			name:  "empty geos",
			input: "",
			want:  Geos{make(map[uint32]struct{}), make(map[uint32]struct{})},
		},
		{
			name:  "positive only",
			input: `1 , 2  ,3,  4,5`,
			want: Geos{
				IDs:        map[uint32]struct{}{1: s, 2: s, 3: s, 4: s, 5: s},
				ExcludeIDs: make(map[uint32]struct{}),
			},
		},
		{
			name:  "negative only",
			input: `-1, -2,-3   ,-4,-5`,
			want: Geos{
				IDs:        make(map[uint32]struct{}),
				ExcludeIDs: map[uint32]struct{}{1: s, 2: s, 3: s, 4: s, 5: s},
			},
		},
		{
			name:  "positive and negative",
			input: `1, -2,3  , -4,5,-6,`,
			want: Geos{
				IDs:        map[uint32]struct{}{1: s, 3: s, 5: s},
				ExcludeIDs: map[uint32]struct{}{2: s, 4: s, 6: s},
			},
		},
		{
			name:    "with parsing error",
			input:   `1, 2, 3, not_a_number`,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var g Geos
			err := g.ParseMADM([]byte(tt.input))

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				require.Equal(t, tt.want, g)
			}
		})
	}
}
