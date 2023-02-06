package models

import (
	"testing"

	"github.com/golang/protobuf/proto"
	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	mordadata "a.yandex-team.ru/portal/avocado/proto/morda_data"
)

var (
	preparedBigBModel = BigB{
		TargetingInfo: TargetingInfo{
			CryptaID2: common.NewOptional[uint64](6304896188630272087),
			PromoGroups: common.NewStringSet(
				"557:2000428359",
				"557:2000718804",
				"557:2001383267",
			),
			RecentlyServices: map[string]Services{
				"visits_common": {
					"news": {
						Name:       "news",
						UpdateTime: 1647007493,
						Weight:     3.651119471,
					},
				},
				"watch_common": {
					"maps": {
						Name:       "maps",
						UpdateTime: 1649991865,
						Weight:     1,
					},
					"pogoda": {
						Name:       "pogoda",
						UpdateTime: 1650291618,
						Weight:     1.999997616,
					},
				},
			},
			Age: []NumericSegment{
				{
					ID:     175,
					Value:  1,
					Weight: 90069,
				},
				{
					ID:     175,
					Value:  2,
					Weight: 751134,
				},
				{
					ID:     175,
					Value:  4,
					Weight: 15809,
				},
			},
			Gender: []NumericSegment{
				{
					ID:     174,
					Value:  0,
					Weight: 958280,
				},
				{
					ID:     174,
					Value:  1,
					Weight: 41719,
				},
			},
			MarketCart: common.NewOptional(MarketCart{
				TotalCost: 9999,
				Count:     4,
			}),
			StatefulSearch: map[string]StatefulSearch{
				"pregnancy": {
					Name:    "pregnancy",
					ThemeID: 2174754698598328073,

					Refused: common.NewOptional(false),
				},
				"travel": {
					Name:    "travel",
					ThemeID: 16287450586626029612,

					Refused: common.NewOptional(false),
				},
			},
			ClIDType:    common.NewOptional[uint32](42),
			TopInternal: common.NewOptional[uint32](43),
			Social:      common.NewOptional[uint32](44),
		},
	}

	preparedBigBDTO = &mordadata.BigB{
		TargetingInfo: &mordadata.TargetingInfo{
			CryptaID2: proto.Uint64(6304896188630272087),
			PromoGroups: [][]byte{
				[]byte("557:2000428359"),
				[]byte("557:2000718804"),
				[]byte("557:2001383267"),
			},
			RecentlyServices: map[string]*mordadata.TargetingInfo_Services{
				"visits_common": {
					Services: map[string]*mordadata.TargetingInfo_Services_Service{
						"news": {
							Name:       []byte("news"),
							UpdateTime: 1647007493,
							Weight:     3.651119471,
						},
					},
				},
				"watch_common": {
					Services: map[string]*mordadata.TargetingInfo_Services_Service{
						"maps": {
							Name:       []byte("maps"),
							UpdateTime: 1649991865,
							Weight:     1,
						},
						"pogoda": {
							Name:       []byte("pogoda"),
							UpdateTime: 1650291618,
							Weight:     1.999997616,
						},
					},
				},
			},
			Age: []*mordadata.TargetingInfo_NumericSegment{
				{
					Id:     175,
					Value:  1,
					Weight: 90069,
				},
				{
					Id:     175,
					Value:  2,
					Weight: 751134,
				},
				{
					Id:     175,
					Value:  4,
					Weight: 15809,
				},
			},
			Gender: []*mordadata.TargetingInfo_NumericSegment{
				{
					Id:     174,
					Value:  0,
					Weight: 958280,
				},
				{
					Id:     174,
					Value:  1,
					Weight: 41719,
				},
			},
			MarketCart: &mordadata.TargetingInfo_MarketCart{
				TotalCost: 9999,
				Count:     4,
			},
			StatefulSearch: map[string]*mordadata.TargetingInfo_StatefulSearch{
				"pregnancy": {
					Name:    []byte("pregnancy"),
					Refused: &[]bool{false}[0],
					ThemeId: 2174754698598328073,
				},
				"travel": {
					Name:    []byte("travel"),
					Refused: &[]bool{false}[0],
					ThemeId: 16287450586626029612,
				},
			},
			ClIDType:    proto.Uint32(42),
			TopInternal: proto.Uint32(43),
			Social:      proto.Uint32(44),
		},
	}
)

func TestBigB_DTO(t *testing.T) {
	tests := []struct {
		name  string
		model *BigB
		want  *mordadata.BigB
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty",
			model: &BigB{},
			want: &mordadata.BigB{
				TargetingInfo: &mordadata.TargetingInfo{
					PromoGroups:      [][]byte{},
					RecentlyServices: map[string]*mordadata.TargetingInfo_Services{},
					Age:              []*mordadata.TargetingInfo_NumericSegment{},
					Gender:           []*mordadata.TargetingInfo_NumericSegment{},
					StatefulSearch:   map[string]*mordadata.TargetingInfo_StatefulSearch{},
				},
			},
		},
		{
			name:  "prepared",
			model: &preparedBigBModel,
			want:  preparedBigBDTO,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.DTO()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestMarketCart_dto(t *testing.T) {
	preparedMarketCart := preparedBigBModel.TargetingInfo.MarketCart.Get()
	tests := []struct {
		name  string
		model *MarketCart
		want  *mordadata.TargetingInfo_MarketCart
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name: "empty",

			model: &MarketCart{},
			want:  &mordadata.TargetingInfo_MarketCart{},
		},
		{
			name:  "prepared",
			model: &preparedMarketCart,
			want:  preparedBigBDTO.TargetingInfo.MarketCart,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.dto()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestNewBigB(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.BigB
		want *BigB
	}{
		{
			name: "nil",
			dto:  nil,
			want: nil,
		},
		{
			name: "empty",
			dto:  &mordadata.BigB{},
			want: &BigB{},
		},
		{
			name: "prepared",
			dto:  preparedBigBDTO,
			want: &preparedBigBModel,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := NewBigB(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestNumericSegment_dto(t *testing.T) {
	tests := []struct {
		name  string
		model *NumericSegment
		want  *mordadata.TargetingInfo_NumericSegment
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty",
			model: &NumericSegment{},
			want:  &mordadata.TargetingInfo_NumericSegment{},
		},
		{
			name: "filled",
			model: &NumericSegment{
				ID:     42,
				Weight: 234,
				Value:  2,
			},
			want: &mordadata.TargetingInfo_NumericSegment{
				Id:     42,
				Weight: 234,
				Value:  2,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.dto()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestTargetingInfo_dto(t *testing.T) {
	tests := []struct {
		name  string
		model *TargetingInfo
		want  *mordadata.TargetingInfo
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty",
			model: &TargetingInfo{},
			want: &mordadata.TargetingInfo{
				PromoGroups:      [][]byte{},
				RecentlyServices: map[string]*mordadata.TargetingInfo_Services{},
				Age:              []*mordadata.TargetingInfo_NumericSegment{},
				Gender:           []*mordadata.TargetingInfo_NumericSegment{},
				StatefulSearch:   map[string]*mordadata.TargetingInfo_StatefulSearch{},
			},
		},
		{
			name:  "prepared",
			model: &preparedBigBModel.TargetingInfo,
			want:  preparedBigBDTO.TargetingInfo,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.dto()
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestTargetingInfo_getNumericSegmentsDTO(t *testing.T) {
	tests := []struct {
		name string
		age  []NumericSegment
		want []*mordadata.TargetingInfo_NumericSegment
	}{
		{
			name: "nil",
			age:  nil,
			want: []*mordadata.TargetingInfo_NumericSegment{},
		},
		{
			name: "empty",
			age:  []NumericSegment{},
			want: []*mordadata.TargetingInfo_NumericSegment{},
		},
		{
			name: "filled",
			age: []NumericSegment{
				{ID: 42, Weight: 43, Value: 44},
			},
			want: []*mordadata.TargetingInfo_NumericSegment{
				{Id: 42, Weight: 43, Value: 44},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := getNumericSegmentsDTO(tt.age)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestTargetingInfo_getRecentlyServicesDTO(t *testing.T) {
	tests := []struct {
		name     string
		services map[string]Services
		want     map[string]*mordadata.TargetingInfo_Services
	}{
		{
			name:     "nil",
			services: nil,
			want:     map[string]*mordadata.TargetingInfo_Services{},
		},
		{
			name:     "empty",
			services: map[string]Services{},
			want:     map[string]*mordadata.TargetingInfo_Services{},
		},
		{
			name: "filled",
			services: map[string]Services{
				"s1": nil,
				"s2": {},
				"s3": {
					"s3_1": {},
					"s3_2": {
						Name:       "s3_2",
						UpdateTime: 42,
						Weight:     43,
					},
				},
			},
			want: map[string]*mordadata.TargetingInfo_Services{
				"s1": {
					Services: map[string]*mordadata.TargetingInfo_Services_Service{},
				},
				"s2": {
					Services: map[string]*mordadata.TargetingInfo_Services_Service{},
				},
				"s3": {
					Services: map[string]*mordadata.TargetingInfo_Services_Service{
						"s3_1": {
							Name: []byte{},
						},
						"s3_2": {
							Name:       []byte("s3_2"),
							UpdateTime: 42,
							Weight:     43,
						},
					},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := getRecentlyServicesDTO(tt.services)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_makeRecentlyServicesMap(t *testing.T) {
	tests := []struct {
		name string
		dto  map[string]*mordadata.TargetingInfo_Services
		want map[string]Services
	}{
		{
			name: "nil",
			dto:  nil,
			want: map[string]Services{},
		},
		{
			name: "empty",
			dto:  map[string]*mordadata.TargetingInfo_Services{},
			want: map[string]Services{},
		},
		{
			name: "filled",
			dto: map[string]*mordadata.TargetingInfo_Services{
				"s1": {
					Services: nil,
				},
				"s2": {
					Services: map[string]*mordadata.TargetingInfo_Services_Service{},
				},
				"s3": {
					Services: map[string]*mordadata.TargetingInfo_Services_Service{
						"s3_1": {},
						"s3_2": {
							Name:       []byte("s3_2"),
							UpdateTime: 42,
							Weight:     43,
						},
					},
				},
			},
			want: map[string]Services{
				"s1": {},
				"s2": {},
				"s3": {
					"s3_1": {},
					"s3_2": {
						Name:       "s3_2",
						UpdateTime: 42,
						Weight:     43,
					},
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := makeRecentlyServicesMap(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_newMarketCart(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.TargetingInfo_MarketCart
		want *MarketCart
	}{
		{
			name: "nil",
			dto:  nil,
			want: nil,
		},
		{
			name: "empty",
			dto:  &mordadata.TargetingInfo_MarketCart{},
			want: &MarketCart{},
		},
		{
			name: "filled",
			dto: &mordadata.TargetingInfo_MarketCart{
				TotalCost: 99,
				Count:     42,
			},
			want: &MarketCart{
				TotalCost: 99,
				Count:     42,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newMarketCart(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_newNumericSegment(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.TargetingInfo_NumericSegment
		want NumericSegment
	}{
		{
			name: "nil",
			dto:  nil,
			want: NumericSegment{},
		},
		{
			name: "empty",
			dto:  &mordadata.TargetingInfo_NumericSegment{},
			want: NumericSegment{},
		},
		{
			name: "filled",
			dto: &mordadata.TargetingInfo_NumericSegment{
				Id:     42,
				Weight: 43,
				Value:  44,
			},
			want: NumericSegment{
				ID:     42,
				Weight: 43,
				Value:  44,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newNumericSegment(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_newNumericSegmentSlice(t *testing.T) {
	tests := []struct {
		name string
		dto  []*mordadata.TargetingInfo_NumericSegment
		want []NumericSegment
	}{
		{
			name: "nil",
			dto:  nil,
			want: []NumericSegment{},
		},
		{
			name: "empty",
			dto:  []*mordadata.TargetingInfo_NumericSegment{},
			want: []NumericSegment{},
		},
		{
			name: "filled",
			dto: []*mordadata.TargetingInfo_NumericSegment{
				nil,
				{},
				{
					Id:     42,
					Weight: 43,
					Value:  44,
				},
			},
			want: []NumericSegment{
				{},
				{},
				{
					ID:     42,
					Weight: 43,
					Value:  44,
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newNumericSegmentSlice(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_newService(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.TargetingInfo_Services_Service
		want Service
	}{
		{
			name: "nil",
			dto:  nil,
			want: Service{},
		},
		{
			name: "empty",
			dto:  &mordadata.TargetingInfo_Services_Service{},
			want: Service{},
		},
		{
			name: "filled",
			dto: &mordadata.TargetingInfo_Services_Service{
				Name:       []byte("name"),
				UpdateTime: 42,
				Weight:     43,
			},
			want: Service{
				Name:       "name",
				UpdateTime: 42,
				Weight:     43,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newService(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_newServices(t *testing.T) {
	tests := []struct {
		name string
		dto  map[string]*mordadata.TargetingInfo_Services_Service
		want Services
	}{
		{
			name: "nil",
			dto:  nil,
			want: Services{},
		},
		{
			name: "empty",
			dto:  map[string]*mordadata.TargetingInfo_Services_Service{},
			want: Services{},
		},
		{
			name: "filled",
			dto: map[string]*mordadata.TargetingInfo_Services_Service{
				"s1": nil,
				"s2": {},
				"s3": {
					Name:       []byte("name"),
					UpdateTime: 42,
					Weight:     43,
				},
			},
			want: map[string]Service{
				"s1": {},
				"s2": {},
				"s3": {
					Name:       "name",
					UpdateTime: 42,
					Weight:     43,
				},
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newServices(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_newTargetingInfo(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.TargetingInfo
		want TargetingInfo
	}{
		{
			name: "nil",
			dto:  nil,
			want: TargetingInfo{},
		},
		{
			name: "empty",
			dto:  &mordadata.TargetingInfo{},
			want: TargetingInfo{
				PromoGroups:      common.NewStringSet(),
				RecentlyServices: map[string]Services{},
				Age:              []NumericSegment{},
				Gender:           []NumericSegment{},
				StatefulSearch:   map[string]StatefulSearch{},
			},
		},
		{
			name: "prepared",
			dto:  preparedBigBDTO.TargetingInfo,
			want: preparedBigBModel.TargetingInfo,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newTargetingInfo(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_newStatefulSearch(t *testing.T) {
	tests := []struct {
		name string
		dto  *mordadata.TargetingInfo_StatefulSearch
		want StatefulSearch
	}{
		{
			name: "nil",
			dto:  nil,
			want: StatefulSearch{},
		},
		{
			name: "empty",
			dto:  &mordadata.TargetingInfo_StatefulSearch{},
			want: StatefulSearch{},
		},
		{
			name: "filled",
			dto: &mordadata.TargetingInfo_StatefulSearch{
				Name:    []byte("name"),
				Refused: &[]bool{true}[0],
				ThemeId: 123,
			},
			want: StatefulSearch{
				Name:    "name",
				Refused: common.NewOptional(true),
				ThemeID: 123,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newStatefulSearch(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func TestStatefulSearch_dto(t *testing.T) {
	tests := []struct {
		name  string
		model *StatefulSearch
		want  *mordadata.TargetingInfo_StatefulSearch
	}{
		{
			name:  "nil",
			model: nil,
			want:  nil,
		},
		{
			name:  "empty",
			model: &StatefulSearch{},
			want: &mordadata.TargetingInfo_StatefulSearch{
				Name: []byte{},
			},
		},
		{
			name: "filled",
			model: &StatefulSearch{
				Name:    "name",
				Refused: common.NewOptional(true),
				ThemeID: 123,
			},
			want: &mordadata.TargetingInfo_StatefulSearch{
				Name:    []byte("name"),
				Refused: &[]bool{true}[0],
				ThemeId: 123,
			},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := tt.model.dto()
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_makeStatefulSearchMap(t *testing.T) {
	tests := []struct {
		name string
		dto  map[string]*mordadata.TargetingInfo_StatefulSearch
		want map[string]StatefulSearch
	}{
		{
			name: "nil",
			dto:  nil,
			want: map[string]StatefulSearch{},
		},
		{
			name: "empty",
			dto:  map[string]*mordadata.TargetingInfo_StatefulSearch{},
			want: map[string]StatefulSearch{},
		},
		{
			name: "prepared",
			dto:  preparedBigBDTO.TargetingInfo.StatefulSearch,
			want: preparedBigBModel.TargetingInfo.StatefulSearch,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := makeStatefulSearchMap(tt.dto)
			assert.Equal(t, tt.want, got)
		})
	}
}

func Test_getStatefulSearchDTO(t *testing.T) {
	tests := []struct {
		name           string
		statefulSearch map[string]StatefulSearch
		want           map[string]*mordadata.TargetingInfo_StatefulSearch
	}{
		{
			name:           "nil",
			statefulSearch: nil,
			want:           map[string]*mordadata.TargetingInfo_StatefulSearch{},
		},
		{
			name:           "empty",
			statefulSearch: map[string]StatefulSearch{},
			want:           map[string]*mordadata.TargetingInfo_StatefulSearch{},
		},
		{
			name:           "prepared",
			statefulSearch: preparedBigBModel.TargetingInfo.StatefulSearch,
			want:           preparedBigBDTO.TargetingInfo.StatefulSearch,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := getStatefulSearchDTO(tt.statefulSearch)
			assert.Equal(t, tt.want, got)
		})
	}
}
