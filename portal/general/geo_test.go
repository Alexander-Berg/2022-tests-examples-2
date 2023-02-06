package models

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/library/go/test/assertpb"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

func TestLocation_isNil(t *testing.T) {
	type args struct {
		location *Location
	}

	tests := []struct {
		name string
		args args
		want bool
	}{
		{
			name: "is nil",
			args: args{
				location: nil,
			},
			want: true,
		},
		{
			name: "is empty",
			args: args{
				location: &Location{
					Latitude:  0,
					Longitude: 0,
					Accuracy:  0,
				},
			},
			want: true,
		},
		{
			name: "not empty lat",
			args: args{
				location: &Location{
					Latitude:  1,
					Longitude: 0,
					Accuracy:  0,
				},
			},
			want: false,
		},
		{
			name: "not empty lon",
			args: args{
				location: &Location{
					Latitude:  0,
					Longitude: 1,
					Accuracy:  0,
				},
			},
			want: false,
		},
		{
			name: "not nil accuracy",
			args: args{
				location: &Location{
					Latitude:  0,
					Longitude: 0,
					Accuracy:  1,
				},
			},
			want: false,
		},
		{
			name: "not empty all",
			args: args{
				location: &Location{
					Latitude:  1,
					Longitude: 2,
					Accuracy:  3,
				},
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, tt.args.location.isNil())
		})
	}
}

func TestLocation_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *Location
		want  *mordadata.Location
	}{
		{
			name:  "nil location",
			model: nil,
			want:  nil,
		},
		{
			name: "success",
			model: &Location{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  3,
			},
			want: &mordadata.Location{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  3,
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

func TestNewLocation(t *testing.T) {
	type args struct {
		dto *mordadata.Location
	}

	tests := []struct {
		name string
		args args
		want *Location
	}{
		{
			name: "nil location",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "success",
			args: args{
				dto: &mordadata.Location{
					Latitude:  1,
					Longitude: 2,
					Accuracy:  3,
				},
			},
			want: &Location{
				Latitude:  1,
				Longitude: 2,
				Accuracy:  3,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewLocation(tt.args.dto))
		})
	}
}

func TestGeo_GeoParentsDTO(t *testing.T) {
	type args struct {
		parents []uint32
	}

	tests := []struct {
		name string
		args args
		want *mordadata.Geo_Parents
	}{
		{
			name: "nil parents",
			args: args{
				parents: nil,
			},
			want: nil,
		},
		{
			name: "empty parents",
			args: args{
				parents: make([]uint32, 0),
			},
			want: nil,
		},
		{
			name: "success",
			args: args{
				parents: []uint32{1, 2, 3},
			},
			want: &mordadata.Geo_Parents{
				Values: []uint32{1, 2, 3},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			g := &Geo{}
			assertpb.Equal(t, tt.want, g.GeoParentsDTO(tt.args.parents))
		})
	}
}

func TestGeo_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *Geo
		want  *mordadata.Geo
	}{
		{
			name:  "nil model",
			model: nil,
			want:  nil,
		},
		{
			name: "success",
			model: &Geo{
				ByLAAS:   true,
				Auto:     true,
				CityID:   123,
				RegionID: 456,
				Location: &Location{
					Latitude:  1,
					Longitude: 2,
					Accuracy:  3,
				},
				Parents:           []uint32{1, 2, 3},
				SuspectedCityID:   312,
				SuspectedRegionID: 654,
				SuspectedLocation: &Location{
					Latitude:  4,
					Longitude: 5,
					Accuracy:  6,
				},
				SuspectedParents: []uint32{4, 5, 6},
				TimeZone: &TimeZone{
					Offset: 5 * time.Hour,
					Name:   "Europe/Moscow",
					Dst:    "test",
				},
				SuspectedTimeZone: &TimeZone{
					Offset: 6 * time.Hour,
					Name:   "Europe/Moscow",
					Dst:    "test",
				},
			},
			want: &mordadata.Geo{
				ByLaas:   true,
				Auto:     true,
				CityId:   123,
				RegionId: 456,
				Location: &mordadata.Location{
					Latitude:  1,
					Longitude: 2,
					Accuracy:  3,
				},
				Parents: &mordadata.Geo_Parents{
					Values: []uint32{1, 2, 3},
				},
				SuspectedCityId:   312,
				SuspectedRegionId: 654,
				SuspectedLocation: &mordadata.Location{
					Latitude:  4,
					Longitude: 5,
					Accuracy:  6,
				},
				SuspectedParents: &mordadata.Geo_Parents{
					Values: []uint32{4, 5, 6},
				},
				TimeZone: &mordadata.Geo_TimeZone{
					Offset: int64(5 * time.Hour),
					Name:   []byte("Europe/Moscow"),
					Dst:    []byte("test"),
				},
				SuspectedTimeZone: &mordadata.Geo_TimeZone{
					Offset: int64(6 * time.Hour),
					Name:   []byte("Europe/Moscow"),
					Dst:    []byte("test"),
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

func TestNewGeo(t *testing.T) {
	type args struct {
		dto *mordadata.Geo
	}

	tests := []struct {
		name string
		args args
		want *Geo
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
				dto: &mordadata.Geo{
					ByLaas:   true,
					Auto:     true,
					CityId:   123,
					RegionId: 456,
					Location: &mordadata.Location{
						Latitude:  1,
						Longitude: 2,
						Accuracy:  3,
					},
					Parents: &mordadata.Geo_Parents{
						Values: []uint32{1, 2, 3},
					},
					SuspectedCityId:   312,
					SuspectedRegionId: 654,
					SuspectedLocation: &mordadata.Location{
						Latitude:  4,
						Longitude: 5,
						Accuracy:  6,
					},
					SuspectedParents: &mordadata.Geo_Parents{
						Values: []uint32{4, 5, 6},
					},
					TimeZone: &mordadata.Geo_TimeZone{
						Offset: int64(5 * time.Hour),
						Name:   []byte("Europe/Moscow"),
						Dst:    []byte("test"),
					},
					SuspectedTimeZone: &mordadata.Geo_TimeZone{
						Offset: int64(6 * time.Hour),
						Name:   []byte("Europe/Moscow"),
						Dst:    []byte("test"),
					},
				},
			},
			want: &Geo{
				ByLAAS:   true,
				Auto:     true,
				CityID:   123,
				RegionID: 456,
				Location: &Location{
					Latitude:  1,
					Longitude: 2,
					Accuracy:  3,
				},
				Parents:           []uint32{1, 2, 3},
				SuspectedCityID:   312,
				SuspectedRegionID: 654,
				SuspectedLocation: &Location{
					Latitude:  4,
					Longitude: 5,
					Accuracy:  6,
				},
				SuspectedParents: []uint32{4, 5, 6},
				TimeZone: &TimeZone{
					Offset: 5 * time.Hour,
					Name:   "Europe/Moscow",
					Dst:    "test",
				},
				SuspectedTimeZone: &TimeZone{
					Offset: 6 * time.Hour,
					Name:   "Europe/Moscow",
					Dst:    "test",
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewGeo(tt.args.dto))
		})
	}
}

func TestNewTimeZone(t *testing.T) {
	type args struct {
		dto *mordadata.Geo_TimeZone
	}

	tests := []struct {
		name string
		args args
		want *TimeZone
	}{
		{
			name: "nil timezone",
			args: args{
				dto: nil,
			},
			want: nil,
		},
		{
			name: "success",
			args: args{
				dto: &mordadata.Geo_TimeZone{
					Offset: int64(5 * time.Hour),
					Name:   []byte("Europe/Moscow"),
					Dst:    []byte("test"),
				},
			},
			want: &TimeZone{
				Offset: 5 * time.Hour,
				Name:   "Europe/Moscow",
				Dst:    "test",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, NewTimeZone(tt.args.dto))
		})
	}
}

func TestGeo_GetLocalTimeOffset(t *testing.T) {
	type fields struct {
		geo *Geo
	}

	tests := []struct {
		name   string
		fields fields
		want   time.Duration
	}{
		{
			name: "nil geo",
			fields: fields{
				geo: nil,
			},
			want: 3 * time.Hour,
		},
		{
			name: "nil timezone",
			fields: fields{
				geo: &Geo{
					TimeZone: nil,
				},
			},
			want: 3 * time.Hour,
		},
		{
			name: "success",
			fields: fields{
				geo: &Geo{
					TimeZone: &TimeZone{
						Offset: 4 * time.Hour,
					},
				},
			},
			want: 4 * time.Hour,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.fields.geo.GetLocalTimeOffset()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestGeo_GetLocalTimeZoneName(t *testing.T) {
	type fields struct {
		geo *Geo
	}

	tests := []struct {
		name   string
		fields fields
		want   string
	}{
		{
			name: "nil geo",
			fields: fields{
				geo: nil,
			},
			want: "Europe/Moscow",
		},
		{
			name: "nil timezone",
			fields: fields{
				geo: &Geo{
					TimeZone: nil,
				},
			},
			want: "Europe/Moscow",
		},
		{
			name: "success",
			fields: fields{
				geo: &Geo{
					TimeZone: &TimeZone{
						Name: "Australia/Sydney",
					},
				},
			},
			want: "Australia/Sydney",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.fields.geo.GetLocalTimeZoneName()
			assert.Equal(t, tt.want, got)
		})
	}
}
