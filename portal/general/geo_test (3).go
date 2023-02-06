package req

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_newGeoParents(t *testing.T) {
	type args struct {
		parents []jsonNumber
	}

	tests := []struct {
		name    string
		args    args
		wantNil bool
	}{
		{
			name:    "nil parents",
			wantNil: true,
		},
		{
			name: "empty parents",
			args: args{
				parents: []jsonNumber{},
			},
			wantNil: true,
		},
		{
			name: "not nil parents",
			args: args{
				parents: []jsonNumber{
					"213",
					"123",
				},
			},
			wantNil: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newGeoParents(tt.args.parents)
			if tt.wantNil {
				assert.Nil(t, got)
			} else {
				assert.NotNil(t, got)
			}
		})
	}
}

func Test_newGeo(t *testing.T) {
	type args struct {
		geo geo
	}

	tests := []struct {
		name string
		args args
		want models.Geo
	}{
		{
			name: "get region id failed",
			args: args{
				geo: geo{
					GeoByDomainIP: "abc",
				},
			},
			want: models.Geo{},
		},
		{
			name: "empty geo",
			args: args{
				geo: geo{},
			},
			want: models.Geo{},
		},
		{
			name: "success",
			args: args{
				geo: geo{
					GeoByDomainIP: "213",
					GeoAndParents: []jsonNumber{
						"123",
					},
				},
			},
			want: models.Geo{
				RegionID: 213,
				Parents:  []uint32{123},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			assert.Equal(t, tt.want, newGeo(tt.args.geo))
		})
	}
}
