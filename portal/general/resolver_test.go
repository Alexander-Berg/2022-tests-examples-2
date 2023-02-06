package resolver

import (
	"testing"
	"time"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"

	gb "a.yandex-team.ru/library/go/yandex/geobase"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/errors/v3"
	"a.yandex-team.ru/portal/avocado/libs/utils/geo/coordinates"
)

func Test_resolver_makeGeoParents(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		regionID int
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    []uint32
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "geobase error",
			args: args{
				regionID: 213,
			},
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(213)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "success",
			args: args{
				regionID: 213,
			},
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(213)).Return([]gb.ID{1, 2, 3}, nil)
					return geoBase
				},
			},
			want:    []uint32{1, 2, 3},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			got, err := r.MakeGeoParents(tt.args.regionID)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_resolver_getFallbackGeo(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	tests := []struct {
		name    string
		fields  fields
		want    *models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get region by id failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gb.ID(fallbackRegionID)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "make geo parents failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gb.ID(fallbackRegionID)).Return(&gb.Region{
						ID: fallbackRegionID,
					}, nil)
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(fallbackRegionID)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "make geo time offset failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gb.ID(fallbackRegionID)).Return(&gb.Region{
						ID: fallbackRegionID,
					}, nil)
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(fallbackRegionID)).Return([]gb.ID{1, 2, 3}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(fallbackRegionID)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(fallbackRegionID)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gb.ID(fallbackRegionID)).Return(&gb.Region{
						ID:        fallbackRegionID,
						CityID:    fallbackRegionID,
						Latitude:  1,
						Longitude: 2,
					}, nil)
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(fallbackRegionID)).Return([]gb.ID{1, 2, 3}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(fallbackRegionID)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
					}, nil)
					return geoBase
				},
			},
			want: &models.Geo{
				CityID:   fallbackRegionID,
				RegionID: fallbackRegionID,
				Location: &models.Location{
					Latitude:  1,
					Longitude: 2,
				},
				Parents: []uint32{1, 2, 3},
				TimeZone: &models.TimeZone{
					Offset: 3 * time.Hour,
				},
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			got, err := r.getFallbackGeo()
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_resolver_makeGeo(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		region *gb.Region
		coords coordinates.Coordinates
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *models.Geo
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "make geo parents failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(213)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "make geo time offset",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(213)).Return([]gb.ID{1, 2, 3}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetParentsIDsDef(gb.ID(213)).Return([]gb.ID{1, 2, 3}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID:     213,
					CityID: 213,
				},
				coords: coordinates.Coordinates{
					Latitude:  1,
					Longitude: 2,
				},
			},
			want: &models.Geo{
				RegionID: 213,
				CityID:   213,
				Location: &models.Location{
					Latitude:  1,
					Longitude: 2,
				},
				Parents: []uint32{1, 2, 3},
				TimeZone: &models.TimeZone{
					Offset: 3 * time.Hour,
				},
			},
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			got, err := r.makeGeo(tt.args.region, tt.args.coords)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_resolver_IsGoodRegion(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		regionID int
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "empty region id",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					return nil
				},
			},
			args: args{
				regionID: 0,
			},
			want: false,
		},
		{
			name: "yandex region id",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					return nil
				},
			},
			args: args{
				regionID: 9001,
			},
			want: false,
		},
		{
			name: "unknown region",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gomock.Any()).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				regionID: 999999999,
			},
			want: false,
		},
		{
			name: "invalid region type",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gomock.Any()).Return(&gb.Region{
						ID:   100,
						Type: gb.RegionTypeRemoved,
					}, nil)
					return geoBase
				},
			},
			args: args{
				regionID: 100,
			},
			want: false,
		},
		{
			name: "success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gomock.Any()).Return(&gb.Region{
						ID:   100,
						Type: gb.RegionTypeCity,
					}, nil)
					return geoBase
				},
			},
			args: args{
				regionID: 100,
			},
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			assert.Equal(t, tt.want, r.IsGoodRegion(tt.args.regionID))
		})
	}
}

func Test_resolver_GetCapitalRegionID(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		regionID int
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   int
	}{
		{
			name: "empty region id",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					return nil
				},
			},
			args: args{
				regionID: 0,
			},
			want: 0,
		},
		{
			name: "unknown region",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gomock.Any()).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				regionID: 999999999,
			},
			want: 0,
		},
		{
			name: "empty region id",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					return nil
				},
			},
			args: args{
				regionID: 0,
			},
			want: 0,
		},
		{
			name: "success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gomock.Any()).Return(&gb.Region{
						ID:        100,
						CapitalID: 200,
					}, nil)
					return geoBase
				},
			},
			args: args{
				regionID: 100,
			},
			want: 200,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			assert.Equal(t, tt.want, r.GetCapitalRegionID(tt.args.regionID))
		})
	}
}

func Test_resolver_HasRegion(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		regionID int
	}

	tests := []struct {
		name   string
		fields fields
		args   args
		want   bool
	}{
		{
			name: "empty region id",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					return nil
				},
			},
			args: args{
				regionID: 0,
			},
			want: false,
		},
		{
			name: "success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gomock.Any()).Return(&gb.Region{
						ID: 100,
					}, nil)
					return geoBase
				},
			},
			args: args{
				regionID: 100,
			},
			want: true,
		},
		{
			name: "failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetRegionByID(gomock.Any()).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				regionID: 100,
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			assert.Equal(t, tt.want, r.HasRegion(tt.args.regionID))
		})
	}
}

func Test_resolver_getTimezone(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		region *gb.Region
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *gb.Timezone
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get timezone by id success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want: &gb.Timezone{
				Offset: 3 * time.Hour,
			},
			wantErr: assert.NoError,
		},
		{
			name: "get timezone by capital id success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(111)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID:        213,
					CapitalID: 111,
				},
			},
			want: &gb.Timezone{
				Offset: 3 * time.Hour,
			},
			wantErr: assert.NoError,
		},
		{
			name: "get timezone by first parent success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return([]gb.ID{111}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(111)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want: &gb.Timezone{
				Offset: 3 * time.Hour,
			},
			wantErr: assert.NoError,
		},
		{
			name: "empty timezone by first parent",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return(nil, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want:    nil,
			wantErr: assert.NoError,
		},
		{
			name: "get timezone by first parent failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "get timezone by second parent success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return([]gb.ID{111}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(111)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(111)).Return([]gb.ID{222}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(222)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want: &gb.Timezone{
				Offset: 3 * time.Hour,
			},
			wantErr: assert.NoError,
		},
		{
			name: "empty timezone by second parent",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return([]gb.ID{111}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(111)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(111)).Return(nil, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want:    nil,
			wantErr: assert.NoError,
		},
		{
			name: "get timezone by second parent failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return([]gb.ID{111}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(111)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(111)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "empty timezone",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return([]gb.ID{111}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(111)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(111)).Return([]gb.ID{222}, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(222)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want:    nil,
			wantErr: assert.NoError,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			got, err := r.getTimezone(tt.args.region)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}

func Test_resolver_makeGeoTimeZone(t *testing.T) {
	type fields struct {
		createGeoBase func(t *testing.T) *MockgeoBase
	}

	type args struct {
		region *gb.Region
	}

	tests := []struct {
		name    string
		fields  fields
		args    args
		want    *models.TimeZone
		wantErr assert.ErrorAssertionFunc
	}{
		{
			name: "get timezone success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
						Name:   "Europe/Moscow",
						Dst:    "test",
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want: &models.TimeZone{
				Offset: 3 * time.Hour,
				Name:   "Europe/Moscow",
				Dst:    "test",
			},
			wantErr: assert.NoError,
		},
		{
			name: "get timezone failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(213)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(213)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 213,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
		{
			name: "multi zone region id",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(111)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(111)).Return(nil, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(10393)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
						Name:   "Europe/Moscow",
						Dst:    "test",
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 111,
				},
			},
			want: &models.TimeZone{
				Offset: 3 * time.Hour,
				Name:   "Europe/Moscow",
				Dst:    "test",
			},
			wantErr: assert.NoError,
		},
		{
			name: "fallback region id success",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(555)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(555)).Return(nil, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(fallbackRegionID)).Return(&gb.Timezone{
						Offset: 3 * time.Hour,
						Name:   "Europe/Moscow",
						Dst:    "test",
					}, nil)
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 555,
				},
			},
			want: &models.TimeZone{
				Offset: 3 * time.Hour,
				Name:   "Europe/Moscow",
				Dst:    "test",
			},
			wantErr: assert.NoError,
		},
		{
			name: "fallback region id failed",
			fields: fields{
				createGeoBase: func(t *testing.T) *MockgeoBase {
					geoBase := NewMockgeoBase(gomock.NewController(t))
					geoBase.EXPECT().GetTimezoneByID(gb.ID(555)).Return(nil, errors.Error("error"))
					geoBase.EXPECT().GetOnlyParentsIDsDef(gb.ID(555)).Return(nil, nil)
					geoBase.EXPECT().GetTimezoneByID(gb.ID(fallbackRegionID)).Return(nil, errors.Error("error"))
					return geoBase
				},
			},
			args: args{
				region: &gb.Region{
					ID: 555,
				},
			},
			want:    nil,
			wantErr: assert.Error,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			r := &resolver{
				geoBase: tt.fields.createGeoBase(t),
			}

			got, err := r.makeGeoTimeZone(tt.args.region)
			assert.Equal(t, tt.want, got)
			tt.wantErr(t, err)
		})
	}
}
