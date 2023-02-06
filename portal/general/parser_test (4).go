package bigb

import (
	"testing"

	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
	"a.yandex-team.ru/portal/avocado/morda-go/tests/mocks"
	protoyabs "a.yandex-team.ru/yabs/proto"
)

func TestProcessCryptaId(t *testing.T) {
	tests := []struct {
		name string
		resp *protoyabs.Profile
		want *models.BigB

		shouldError bool
		errMsg      string
	}{
		{
			name: "nil",
			resp: nil,
			want: &models.BigB{},

			shouldError: false,
		},
		{
			name: "empty point",
			resp: &protoyabs.Profile{},
			want: &models.BigB{},

			shouldError: true,
			errMsg:      "userProfile.UserIdentifiers=nil",
		},
		{
			name: "CryptaId=nil",
			resp: &protoyabs.Profile{
				UserIdentifiers: &protoyabs.Profile_TUserIdentifiers{
					CryptaId: nil,
				},
			},
			want: &models.BigB{},

			shouldError: true,
			errMsg:      "userProfile.UserIdentifiers.CryptaId=nil",
		},
		{
			name: "CryptaID2 defined",
			resp: &protoyabs.Profile{
				UserIdentifiers: &protoyabs.Profile_TUserIdentifiers{
					CryptaId: &[]uint64{123}[0],
				},
			},
			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					CryptaID2: common.NewOptional[uint64](123),
				},
			},

			shouldError: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			p := &parser{}
			bigb := &models.BigB{}
			err := p.processCryptaID(tt.resp, bigb)
			if tt.shouldError {
				require.EqualError(t, err, tt.errMsg)
			} else {
				require.NoError(t, err)
			}
			assert.Equal(t, bigb, tt.want)
		})
	}
}

func TestProcessProfileItems(t *testing.T) {
	tests := []struct {
		name string

		bigBMadmGetterMockInitFunc func(base *mocks.Base, m *MockbigBMadmGetter)

		resp       *protoyabs.Profile
		actualBigb *models.BigB

		want *models.BigB

		shouldError bool
		errMsg      string
	}{
		{
			name: "nil resp and model",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {},

			resp:       nil,
			actualBigb: nil,

			want: nil,

			shouldError: false,
		},
		{
			name: "nil resp",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {},

			resp:       nil,
			actualBigb: &models.BigB{},

			want: &models.BigB{},
		},
		{
			name: "empty resp",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {},

			resp:       &protoyabs.Profile{},
			actualBigb: &models.BigB{},

			want: &models.BigB{},

			shouldError: false,
		},
		{
			name: "empty point",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{557}[0],
						UpdateTime: &[]uint32{222}[0],
						UintValues: []uint64{333},
					},
				},
			},
			actualBigb: &models.BigB{},

			want: &models.BigB{},

			shouldError: false,
		},
		{
			name: "undefined PromoGroups",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{557}[0],
						UpdateTime: &[]uint32{222}[0],
						UintValues: []uint64{333},
					},
				},
			},
			actualBigb: &models.BigB{},

			want: &models.BigB{},

			shouldError: false,
		},
		{
			name: "wrong value from GetFirstBigBKeywords",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{111}[0],
						UpdateTime: &[]uint32{222}[0],
						UintValues: []uint64{333},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
				},
			},

			shouldError: false,
		},
		{
			name: "correct value from GetFirstBigBKeywords, parse UintValues",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{557}[0],
						UpdateTime: &[]uint32{222}[0],
						UintValues: []uint64{333},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"557:333": {},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "correct value from GetFirstBigBKeywords, parse PairValues",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{557}[0],
						UpdateTime: &[]uint32{333}[0],
						PairValues: []*protoyabs.Profile_Pair{
							{
								First: &[]uint64{111}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"557:111": {},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "correct value from GetFirstBigBKeywords, parse WeightedUintValues",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{557}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First: &[]uint64{111}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"557:111": {},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "correct value from GetFirstBigBKeywords, parse WeightedPairValues",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{557}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedPairValues: []*protoyabs.Profile_WeightedPair{
							{
								First: &[]uint64{111}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"557:111": {},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "process gender",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{174}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First:  &[]uint64{111}[0],
								Weight: &[]uint64{222}[0],
							},
							{
								First:  &[]uint64{333}[0],
								Weight: &[]uint64{444}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
					Gender: []models.NumericSegment{
						{
							ID:     uint64(174),
							Weight: float64(222),
							Value:  int64(111),
						},
						{
							ID:     uint64(174),
							Weight: float64(444),
							Value:  int64(333),
						},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "process age",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{175}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First:  &[]uint64{111}[0],
								Weight: &[]uint64{222}[0],
							},
							{
								First:  &[]uint64{333}[0],
								Weight: &[]uint64{444}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
					Age: []models.NumericSegment{
						{
							ID:     uint64(175),
							Weight: float64(222),
							Value:  int64(111),
						},
						{
							ID:     uint64(175),
							Weight: float64(444),
							Value:  int64(333),
						},
					},
				},
			},

			shouldError: false,
		},

		{
			name: "process gender",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{174}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First:  &[]uint64{111}[0],
								Weight: &[]uint64{222}[0],
							},
							{
								First:  &[]uint64{333}[0],
								Weight: &[]uint64{444}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
					Gender: []models.NumericSegment{
						{
							ID:     uint64(174),
							Weight: float64(222),
							Value:  int64(111),
						},
						{
							ID:     uint64(174),
							Weight: float64(444),
							Value:  int64(333),
						},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "process age and gender",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{174}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First:  &[]uint64{111}[0],
								Weight: &[]uint64{222}[0],
							},
							{
								First:  &[]uint64{333}[0],
								Weight: &[]uint64{444}[0],
							},
						},
					},
					{
						KeywordId:  &[]int32{175}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First:  &[]uint64{111}[0],
								Weight: &[]uint64{222}[0],
							},
							{
								First:  &[]uint64{333}[0],
								Weight: &[]uint64{444}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
					Age: []models.NumericSegment{
						{
							ID:     uint64(175),
							Weight: float64(222),
							Value:  int64(111),
						},
						{
							ID:     uint64(175),
							Weight: float64(444),
							Value:  int64(333),
						},
					},
					Gender: []models.NumericSegment{
						{
							ID:     uint64(174),
							Weight: float64(222),
							Value:  int64(111),
						},
						{
							ID:     uint64(174),
							Weight: float64(444),
							Value:  int64(333),
						},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "process age and gender with valid GetFirstBigBKeywords",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("174 175", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{174}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First:  &[]uint64{111}[0],
								Weight: &[]uint64{222}[0],
							},
							{
								First:  &[]uint64{333}[0],
								Weight: &[]uint64{444}[0],
							},
						},
					},
					{
						KeywordId:  &[]int32{175}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First:  &[]uint64{111}[0],
								Weight: &[]uint64{222}[0],
							},
							{
								First:  &[]uint64{333}[0],
								Weight: &[]uint64{444}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"174:111": {},
						"174:333": {},
						"175:111": {},
						"175:333": {},
					},
					Age: []models.NumericSegment{
						{
							ID:     uint64(175),
							Weight: float64(222),
							Value:  int64(111),
						},
						{
							ID:     uint64(175),
							Weight: float64(444),
							Value:  int64(333),
						},
					},
					Gender: []models.NumericSegment{
						{
							ID:     uint64(174),
							Weight: float64(222),
							Value:  int64(111),
						},
						{
							ID:     uint64(174),
							Weight: float64(444),
							Value:  int64(333),
						},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "correct value from GetFirstBigBKeywords, parse WeightedPairValues",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("554 555 556 557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{554}[0],
						UpdateTime: &[]uint32{333}[0],
						UintValues: []uint64{111},
					},
					{
						KeywordId:  &[]int32{555}[0],
						UpdateTime: &[]uint32{333}[0],
						PairValues: []*protoyabs.Profile_Pair{
							{
								First: &[]uint64{111}[0],
							},
						},
					},
					{
						KeywordId:  &[]int32{556}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedUintValues: []*protoyabs.Profile_WeightedUInt{
							{
								First: &[]uint64{111}[0],
							},
						},
					},
					{
						KeywordId:  &[]int32{557}[0],
						UpdateTime: &[]uint32{333}[0],
						WeightedPairValues: []*protoyabs.Profile_WeightedPair{
							{
								First: &[]uint64{111}[0],
							},
						},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{
						"554:111": {},
						"555:111": {},
						"556:111": {},
						"557:111": {},
					},
				},
			},

			shouldError: false,
		},
		{
			name: "process market cart",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{1038}[0],
						UpdateTime: &[]uint32{333}[0],
						UintValues: []uint64{111, 222},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
					MarketCart: common.NewOptional(models.MarketCart{
						TotalCost: float64(111),
						Count:     uint64(222),
					}),
				},
			},
		},
		{
			name: "process market cart",

			bigBMadmGetterMockInitFunc: func(base *mocks.Base, m *MockbigBMadmGetter) {
				m.EXPECT().GetFirstBigBKeywords(base).Return("557", nil).AnyTimes()
			},

			resp: &protoyabs.Profile{
				Items: []*protoyabs.Profile_ProfileItem{
					{
						KeywordId:  &[]int32{294}[0],
						UpdateTime: &[]uint32{555}[0],
						UintValues: []uint64{111},
					},
					{
						KeywordId:  &[]int32{326}[0],
						UpdateTime: &[]uint32{666}[0],
						UintValues: []uint64{222},
					},
					{
						KeywordId:  &[]int32{200}[0],
						UpdateTime: &[]uint32{777}[0],
						UintValues: []uint64{333},
					},
				},
			},
			actualBigb: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.NewStringSet(),
				},
			},

			want: &models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups: common.StringSet{},
					ClIDType:    common.NewOptional[uint32](111),
					TopInternal: common.NewOptional[uint32](222),
					Social:      common.NewOptional[uint32](333),
				},
			},

			shouldError: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			base := mocks.Base{}
			logger := log3.NewLoggerStub()
			base.On("GetLogger").Return(logger)

			ctrl := gomock.NewController(t)
			bigBMadmGetterMock := NewMockbigBMadmGetter(ctrl)
			tt.bigBMadmGetterMockInitFunc(&base, bigBMadmGetterMock)
			p := &parser{
				bigBMadmGetter: bigBMadmGetterMock,
			}

			p.processProfileItems(&base, tt.resp, tt.actualBigb)
			assert.Equal(t, tt.want, tt.actualBigb)
		})
	}
}

//// TODO: дополнить тестами позднее
//func TestProcessProfileCounters(t *testing.T) {
//
//}
//
//func TestProcessCounterItemRecentlyServices(t *testing.T) {
//
//}
//
//func TestProcessCounterItemStatefulSearch(t *testing.T) {
//
//}
