package compare

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_geoComparator_diffCompareGeoParents(t *testing.T) {
	type args struct {
		expected []uint32
		got      []uint32
	}
	tests := []struct {
		name        string
		args        args
		wantExtra   []uint32
		wantMissing []uint32
	}{
		{
			name:        "both nil",
			wantExtra:   make([]uint32, 0),
			wantMissing: make([]uint32, 0),
		},
		{
			name: "both empty",
			args: args{
				expected: make([]uint32, 0),
				got:      make([]uint32, 0),
			},
			wantExtra:   make([]uint32, 0),
			wantMissing: make([]uint32, 0),
		},
		{
			name: "only extra",
			args: args{
				expected: []uint32{1, 2},
				got:      []uint32{1, 2, 3, 4},
			},
			wantExtra:   []uint32{3, 4},
			wantMissing: make([]uint32, 0),
		},
		{
			name: "only missing",
			args: args{
				expected: []uint32{1, 2},
				got:      nil,
			},
			wantExtra:   make([]uint32, 0),
			wantMissing: []uint32{1, 2},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &geoComparator{}

			gotExtra, gotMissing := c.diffCompareGeoParents(tt.args.expected, tt.args.got)
			assert.Equal(t, tt.wantExtra, gotExtra)
			assert.Equal(t, tt.wantMissing, gotMissing)
		})
	}
}

func Test_geoComparator_formatCompareGeoParentsError(t *testing.T) {
	type args struct {
		extra   []uint32
		missing []uint32
	}

	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name:    "nil args",
			wantErr: false,
		},
		{
			name: "no diff",
			args: args{
				extra:   make([]uint32, 0),
				missing: make([]uint32, 0),
			},
			wantErr: false,
		},
		{
			name: "extra and missing",
			args: args{
				extra:   []uint32{1, 2},
				missing: []uint32{3},
			},
			want:    "not equal; ([ExtraGeoParents], [MissingGeoParents], [ExpectedGeoParents], [GotGeoParents])",
			wantErr: true,
		},
		{
			name: "missing",
			args: args{
				missing: []uint32{3},
			},
			want:    "not equal; ([MissingGeoParents], [ExpectedGeoParents], [GotGeoParents])",
			wantErr: true,
		},
		{
			name: "extra",
			args: args{
				extra: []uint32{1, 2},
			},
			want:    "not equal; ([ExtraGeoParents], [ExpectedGeoParents], [GotGeoParents])",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			co := &geoComparator{}
			err := co.formatCompareGeoParentsError([]uint32{}, []uint32{}, tt.args.extra, tt.args.missing)

			if !tt.wantErr {
				require.NoError(t, err)
			} else {
				require.Error(t, err)
				errTemplated, ok := err.(errorTemplated)
				require.True(t, ok)
				template, _ := errTemplated.GetTemplated()
				require.Equal(t, tt.want, template)
			}
		})
	}
}

func Test_geoComparator_compareGeoRegionID(t *testing.T) {
	type args struct {
		expected uint32
		got      uint32
	}

	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "equal",
			args: args{
				expected: 123,
				got:      123,
			},
			wantErr: false,
		},
		{
			name: "not equal",
			args: args{
				expected: 123,
				got:      321,
			},
			want:    "not equal; ([ExpectedRegionID], [GotRegionID])",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &geoComparator{}

			err := c.compareGeoRegionID(tt.args.expected, tt.args.got)
			if tt.wantErr {
				require.Error(t, err)
				errTemplated, ok := err.(errorTemplated)
				require.True(t, ok)
				template, _ := errTemplated.GetTemplated()
				require.Equal(t, tt.want, template)
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func Test_geoComparator_compareGeo(t *testing.T) {
	createMockGeoGetter := func(ctrl *gomock.Controller, regionID uint32, geoParents []uint32, withError bool) *MockgeoGetter {
		getter := NewMockgeoGetter(ctrl)
		if withError {
			getter.EXPECT().GetGeo().Return(models.Geo{
				RegionID: regionID,
				Parents:  geoParents,
			})
		} else {
			getter.EXPECT().GetGeo().Return(models.Geo{
				RegionID: regionID,
				Parents:  geoParents,
			})
		}

		return getter
	}

	type args struct {
		expectedRegionID   uint32
		expectedGeoParents []uint32
		gotRegionID        uint32
		gotGeoParents      []uint32
	}

	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "no diff",
			args: args{
				expectedRegionID:   123,
				expectedGeoParents: []uint32{123, 321},
				gotRegionID:        123,
				gotGeoParents:      []uint32{123, 321},
			},
			wantErr: false,
		},
		{
			name: "region ids not equal",
			args: args{
				expectedRegionID:   123,
				expectedGeoParents: []uint32{123, 321},
				gotRegionID:        321,
				gotGeoParents:      []uint32{123, 321},
			},
			want:    "compare region ids: not equal; ([ExpectedRegionID], [GotRegionID])",
			wantErr: true,
		},
		{
			name: "geo parents not equal",
			args: args{
				expectedRegionID:   123,
				expectedGeoParents: []uint32{123, 321},
				gotRegionID:        123,
				gotGeoParents:      []uint32{456, 654},
			},
			want:    "compare geo parents: not equal; ([ExtraGeoParents], [MissingGeoParents], [ExpectedGeoParents], [GotGeoParents])",
			wantErr: true,
		},
		{
			name: "region ids and geo parents not equal",
			args: args{
				expectedRegionID:   123,
				expectedGeoParents: []uint32{123, 321},
				gotRegionID:        456,
				gotGeoParents:      []uint32{456, 654},
			},
			want:    "collapsed errors:\n\tcompare region ids: not equal; ([ExpectedRegionID], [GotRegionID])\n\tcompare geo parents: not equal; ([ExtraGeoParents], [MissingGeoParents], [ExpectedGeoParents], [GotGeoParents])",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			c := &geoComparator{}

			ctrl := gomock.NewController(t)
			expected := createMockGeoGetter(ctrl, tt.args.expectedRegionID, tt.args.expectedGeoParents, false)
			got := createMockGeoGetter(ctrl, tt.args.gotRegionID, tt.args.gotGeoParents, true)

			err := c.compareGeo(expected, got)
			if tt.wantErr {
				require.Error(t, err)
				errTemplated, ok := err.(errorTemplated)
				require.True(t, ok)
				template, _ := errTemplated.GetTemplated()
				require.Equal(t, tt.want, template)
			} else {
				require.NoError(t, err)
			}
		})
	}
}
