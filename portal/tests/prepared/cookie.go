package prepared

import (
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

var (
	TestCookieVer1 = &morda_data.Cookie{
		Parsed: map[string]*morda_data.Cookie_Value{
			"test": {
				Values: [][]byte{
					[]byte("oo"),
				},
			},
		},
	}

	TestCookieVer2 = &morda_data.Cookie{
		Parsed: map[string]*morda_data.Cookie_Value{
			"yandexuid": {
				Values: [][]byte{
					[]byte("1234567890123456789"),
				},
			},
			"ip": {
				Values: [][]byte{
					[]byte("8.8.8.8"),
					[]byte("ffff:ffff:ffff:ffff"),
				},
			},
			"mda": {
				Values: [][]byte{
					[]byte("0"),
				},
			},
			"yandex_gid": {
				Values: [][]byte{
					[]byte("213"),
				},
			},
		},
	}
)
