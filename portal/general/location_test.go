package lbs

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
	"a.yandex-team.ru/portal/avocado/libs/utils/pointer"
)

func TestLocation_Coordinates(t *testing.T) {
	type fields struct {
		Found     bool
		Latitude  float64
		Longitude float64
		Radius    float64
	}

	tests := []struct {
		name   string
		fields fields
		want   coordinates.Coordinates
	}{
		{
			name: "success",
			fields: fields{
				Found:     true,
				Latitude:  1.0,
				Longitude: 2.0,
				Radius:    3.6,
			},
			want: coordinates.Coordinates{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  pointer.NewFloat64(3.6),
				Recency:   pointer.NewInt(defaultRecency),
			},
		},
		{
			name: "not found",
			fields: fields{
				Found:     false,
				Latitude:  1.0,
				Longitude: 2.0,
				Radius:    3.6,
			},
			want: coordinates.Coordinates{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			l := Location{
				Found:     tt.fields.Found,
				Latitude:  tt.fields.Latitude,
				Longitude: tt.fields.Longitude,
				Radius:    tt.fields.Radius,
			}

			assert.Equal(t, tt.want, l.Coordinates())
		})
	}
}
