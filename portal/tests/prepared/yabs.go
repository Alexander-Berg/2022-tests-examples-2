package prepared

import "a.yandex-team.ru/portal/avocado/proto/morda_data"

var (
	TestYabs = morda_data.Yabs{
		BkFlags: map[string]*morda_data.Yabs_BkFlag{
			"some_flag": {
				ClickUrl: []byte("click_url"),
				CloseUrl: []byte("close_url"),
				LinkNext: []byte("link_next"),
			},
		},
	}
)
