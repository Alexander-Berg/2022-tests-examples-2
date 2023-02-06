package coordinates

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCoordinates_Empty(t *testing.T) {
	type fields struct {
		Lat float64
		Lon float64
	}

	tests := []struct {
		name   string
		fields fields
		want   bool
	}{
		{
			name: "empty",
			fields: fields{
				Lat: 0,
				Lon: 0,
			},
			want: true,
		},
		{
			name: "not empty",
			fields: fields{
				Lat: 1,
				Lon: 1,
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := Coordinates{
				Latitude:  tt.fields.Lat,
				Longitude: tt.fields.Lon,
			}
			assert.Equal(t, tt.want, c.Empty())
		})
	}
}
