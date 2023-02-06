package prepared

import (
	"github.com/golang/protobuf/proto"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

var (
	TestDTOBigBVer1 = &morda_data.BigB{
		TargetingInfo: &morda_data.TargetingInfo{
			CryptaID2: proto.Uint64(6304896188630272087),
			PromoGroups: [][]byte{
				[]byte("557:2000428359"),
				[]byte("557:2000718804"),
				[]byte("557:2001383267"),
			},
			RecentlyServices: map[string]*morda_data.TargetingInfo_Services{
				"visits_common": {
					Services: map[string]*morda_data.TargetingInfo_Services_Service{
						"news": {
							Name:       []byte("news"),
							UpdateTime: 1647007493,
							Weight:     3.651119471,
						},
					},
				},
				"watch_common": {
					Services: map[string]*morda_data.TargetingInfo_Services_Service{
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
			Age: []*morda_data.TargetingInfo_NumericSegment{
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
			Gender: []*morda_data.TargetingInfo_NumericSegment{
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
			MarketCart: &morda_data.TargetingInfo_MarketCart{
				TotalCost: 9999,
				Count:     4,
			},
			StatefulSearch: map[string]*morda_data.TargetingInfo_StatefulSearch{
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

	TestModelBigBVer1 = models.BigB{
		TargetingInfo: models.TargetingInfo{
			CryptaID2: common.NewOptional[uint64](6304896188630272087),
			PromoGroups: common.NewStringSet(
				"557:2000428359",
				"557:2000718804",
				"557:2001383267",
			),
			RecentlyServices: map[string]models.Services{
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
			Age: []models.NumericSegment{
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
			Gender: []models.NumericSegment{
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
			MarketCart: common.NewOptional(models.MarketCart{
				TotalCost: 9999,
				Count:     4,
			}),
			StatefulSearch: map[string]models.StatefulSearch{
				"pregnancy": {
					Name:    "pregnancy",
					Refused: common.NewOptional(false),
					ThemeID: 2174754698598328073,
				},
				"travel": {
					Name:    "travel",
					Refused: common.NewOptional(false),
					ThemeID: 16287450586626029612,
				},
			},
			ClIDType:    common.NewOptional[uint32](42),
			TopInternal: common.NewOptional[uint32](43),
			Social:      common.NewOptional[uint32](44),
		},
	}

	TestDTOBigBVer2 = &morda_data.BigB{
		TargetingInfo: &morda_data.TargetingInfo{
			CryptaID2: proto.Uint64(9654849783905194246),
			PromoGroups: [][]byte{
				[]byte("175:4"),
				[]byte("216:10"),
				[]byte("557:2022214539"),
				[]byte("557:2022637715"),
				[]byte("601:12"),
				[]byte("601:166"),
			},
			RecentlyServices: map[string]*morda_data.TargetingInfo_Services{
				"visits_desktop": {
					Services: map[string]*morda_data.TargetingInfo_Services_Service{
						"disk": {
							Name:       []byte("disk"),
							UpdateTime: 1645799367,
							Weight:     1.179334044,
						},
						"images": {
							Name:       []byte("images"),
							UpdateTime: 1647281434,
							Weight:     1.202211738,
						},
					},
				},
				"visits_main_page_common": {
					Services: map[string]*morda_data.TargetingInfo_Services_Service{
						"music": {
							Name:       []byte("music"),
							UpdateTime: 1650562656,
							Weight:     3.051138163,
						},
					},
				},
			},
			Age: []*morda_data.TargetingInfo_NumericSegment{
				{
					Id:     175,
					Value:  3,
					Weight: 142887,
				},
				{
					Id:     175,
					Value:  0,
					Weight: 98,
				},
			},
			Gender: []*morda_data.TargetingInfo_NumericSegment{
				{
					Id:     174,
					Value:  0,
					Weight: 363256,
				},
				{
					Id:     174,
					Value:  1,
					Weight: 2647,
				},
			},
			MarketCart: &morda_data.TargetingInfo_MarketCart{
				TotalCost: 1_000_000,
				Count:     1,
			},
			StatefulSearch: map[string]*morda_data.TargetingInfo_StatefulSearch{
				"lego": {
					Name:    []byte("lego"),
					Refused: &[]bool{true}[0],
					ThemeId: 15287450586626029612,
				},
			},
			ClIDType:    proto.Uint32(111),
			TopInternal: proto.Uint32(112),
			Social:      proto.Uint32(113),
		},
	}

	TestModelBigBVer2 = models.BigB{
		TargetingInfo: models.TargetingInfo{
			CryptaID2: common.NewOptional[uint64](9654849783905194246),
			PromoGroups: common.NewStringSet(
				"175:4",
				"216:10",
				"557:2022214539",
				"557:2022637715",
				"601:12",
				"601:166",
			),
			RecentlyServices: map[string]models.Services{
				"visits_desktop": {
					"disk": {
						Name:       "disk",
						UpdateTime: 1645799367,
						Weight:     1.179334044,
					},
					"images": {
						Name:       "images",
						UpdateTime: 1647281434,
						Weight:     1.202211738,
					},
				},
				"visits_main_page_common": {
					"music": {
						Name:       "music",
						UpdateTime: 1650562656,
						Weight:     3.051138163,
					},
				},
			},
			Age: []models.NumericSegment{
				{
					ID:     175,
					Value:  3,
					Weight: 142887,
				},
				{
					ID:     175,
					Value:  0,
					Weight: 98,
				},
			},
			Gender: []models.NumericSegment{
				{
					ID:     174,
					Value:  0,
					Weight: 363256,
				},
				{
					ID:     174,
					Value:  1,
					Weight: 2647,
				},
			},
			MarketCart: common.NewOptional(models.MarketCart{
				TotalCost: 1_000_000,
				Count:     1,
			}),
			StatefulSearch: map[string]models.StatefulSearch{
				"lego": {
					Name:    "lego",
					Refused: common.NewOptional(true),
					ThemeID: 15287450586626029612,
				},
			},
			ClIDType:    common.NewOptional[uint32](111),
			TopInternal: common.NewOptional[uint32](112),
			Social:      common.NewOptional[uint32](113),
		},
	}
)
