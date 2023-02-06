package req

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
)

func Test_newYabs(t *testing.T) {
	type testCase struct {
		name  string
		flags yabsData
		want  models.Yabs
	}
	tests := []testCase{
		{
			name: "nil flags",
			flags: yabsData{
				BkFlags: nil,
			},
			want: models.Yabs{},
		},
		{
			name: "no flags",
			flags: yabsData{
				BkFlags: make(map[string]yabsBkFlag),
			},
			want: models.Yabs{},
		},
		{
			name: "regular case",
			flags: yabsData{
				BkFlags: map[string]yabsBkFlag{
					"flag": {
						CloseURL: "close_url",
						ClickURL: "click_url",
						LinkNext: "link_next",
					},
				},
			},
			want: models.Yabs{
				BKFlags: map[string]models.BKFlag{
					"flag": {
						CloseURL: "close_url",
						ClickURL: "click_url",
						LinkNext: "link_next",
					},
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := newYabs(tt.flags)
			assert.Equal(t, tt.want, got)
		})
	}
}
