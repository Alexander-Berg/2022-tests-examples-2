package req

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/libs/utils/common"
	"a.yandex-team.ru/portal/morda-go/tests/prepared"
)

func Test_newBigB(t *testing.T) {
	tests := []struct {
		name string
		bigb bigB
		want models.BigB
	}{
		{
			name: "all empty fields",
			bigb: bigB{},
			want: models.BigB{
				TargetingInfo: models.TargetingInfo{
					PromoGroups:      common.NewStringSet(),
					RecentlyServices: map[string]models.Services{},
					Age:              []models.NumericSegment{},
					Gender:           []models.NumericSegment{},
					StatefulSearch:   map[string]models.StatefulSearch{},
				},
			},
		},
		{
			name: "all filled",
			bigb: bigB{
				TargetingInfo: bigBTargetingInfo{
					CryptaID2: common.NewOptional(jsonNumber("6304896188630272087")),
					PromoGroups: map[string]jsonNumber{
						"557:2000428359": "1",
						"557:2000718804": "1",
						"557:2001383267": "1",
					},
					RecentlyServices: map[string]map[string]bigBService{
						"visits_common": {
							"news": {
								Name:       "news",
								UpdateTime: "1647007493",
								Weight:     "3.651119471",
							},
						},
						"watch_common": {
							"maps": {
								Name:       "maps",
								UpdateTime: "1649991865",
								Weight:     "1",
							},
							"pogoda": {
								Name:       "pogoda",
								UpdateTime: "1650291618",
								Weight:     "1.999997616",
							},
						},
					},
					Age: []bigBNumericSegment{
						{
							ID:     "175",
							Value:  "1",
							Weight: "90069",
						},
						{
							ID:     "175",
							Value:  "2",
							Weight: "751134",
						},
						{
							ID:     "175",
							Value:  "4",
							Weight: "15809",
						},
					},
					Gender: []bigBNumericSegment{
						{
							ID:     "174",
							Value:  "0",
							Weight: "958280",
						},
						{
							ID:     "174",
							Value:  "1",
							Weight: "41719",
						},
					},
					MarketCart: common.NewOptional(bigBMarketCart{
						TotalCost: "9999",
						Count:     "4",
					}),
					StatefulSearch: map[string]bigBStatefulSearch{
						"pregnancy": {
							Name:    "pregnancy",
							Refused: common.NewOptional(jsonNumber("0")),
							ThemeID: "2174754698598328073",
						},
						"travel": {
							Name:    "travel",
							Refused: common.NewOptional(jsonNumber("0")),
							ThemeID: "16287450586626029612",
						},
					},
					ClIDType:    common.NewOptional(jsonNumber("42")),
					TopInternal: common.NewOptional(jsonNumber("43")),
					Social:      common.NewOptional(jsonNumber("44")),
				},
			},
			want: prepared.TestModelBigBVer1,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newBigB(tt.bigb)
			assert.Equal(t, tt.want, got)
		})
	}
}
