package prepared

import (
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/avocado/proto/morda_data"
)

var (
	TestDTOYaCookiesVer1 = &morda_data.YaCookies{
		YandexGid: 123,
		Yp: &morda_data.YCookie{
			RawString: []byte("100.fruit.apple#300.city.moscow"),
			Subcookies: map[string]*morda_data.YSubcookie{
				"fruit": {
					Name:   []byte("fruit"),
					Value:  []byte("apple"),
					Expire: 100,
				},
				"city": {
					Name:   []byte("city"),
					Value:  []byte("moscow"),
					Expire: 300,
				},
			},
		},
		Ys: &morda_data.YCookie{
			RawString: []byte("show_morda.yes#some_flag.1"),
			Subcookies: map[string]*morda_data.YSubcookie{
				"show_morda": {
					Name:  []byte("show_morda"),
					Value: []byte("yes"),
				},
				"some_flag": {
					Name:  []byte("some_flag"),
					Value: []byte("1"),
				},
			},
		},
		YandexUid:  []byte("1234567890123456"),
		SessionId:  []byte("SomeRandomString1"),
		SessionId2: []byte("SomeRandomString2"),
	}

	TestDTOYaCookiesVer2 = &morda_data.YaCookies{
		YandexGid: 321,
		Yp: &morda_data.YCookie{
			RawString: []byte("200.fruit.peach#400.city.sochi#600.car.volvo"),
			Subcookies: map[string]*morda_data.YSubcookie{
				"fruit": {
					Name:   []byte("fruit"),
					Value:  []byte("peach"),
					Expire: 200,
				},
				"city": {
					Name:   []byte("city"),
					Value:  []byte("sochi"),
					Expire: 400,
				},
				"car": {
					Name:   []byte("car"),
					Value:  []byte("volvo"),
					Expire: 600,
				},
			},
		},
		Ys: &morda_data.YCookie{
			RawString: []byte("show_morda.yes#another_flag.0"),
			Subcookies: map[string]*morda_data.YSubcookie{
				"show_morda": {
					Name:  []byte("show_morda"),
					Value: []byte("yes"),
				},
				"another_flag": {
					Name:  []byte("some_flag"),
					Value: []byte("0"),
				},
			},
		},
		YandexUid:  []byte("6543210987654321"),
		SessionId:  []byte("AnotherRandomString1"),
		SessionId2: []byte("AnotherRandomString2"),
	}

	TestModelYaCookiesVer1 = models.YaCookies{
		YandexGID: 123,
		Yp: models.YCookie{
			RawString: "100.fruit.apple#300.city.moscow",
			Subcookies: map[string]models.YSubcookie{
				"fruit": {
					Name:   "fruit",
					Value:  "apple",
					Expire: 100,
				},
				"city": {
					Name:   "city",
					Value:  "moscow",
					Expire: 300,
				},
			},
		},
		Ys: models.YCookie{
			RawString: "show_morda.yes#some_flag.1",
			Subcookies: map[string]models.YSubcookie{
				"show_morda": {
					Name:  "show_morda",
					Value: "yes",
				},
				"some_flag": {
					Name:  "some_flag",
					Value: "1",
				},
			},
		},
		YandexUID:  "1234567890123456",
		SessionID:  "SomeRandomString1",
		SessionID2: "SomeRandomString2",
	}

	TestModelYaCookiesVer2 = models.YaCookies{
		YandexGID: 321,
		Yp: models.YCookie{
			RawString: "200.fruit.peach#400.city.sochi#600.car.volvo",
			Subcookies: map[string]models.YSubcookie{
				"fruit": {
					Name:   "fruit",
					Value:  "peach",
					Expire: 200,
				},
				"city": {
					Name:   "city",
					Value:  "sochi",
					Expire: 400,
				},
				"car": {
					Name:   "car",
					Value:  "volvo",
					Expire: 600,
				},
			},
		},
		Ys: models.YCookie{
			RawString: "show_morda.yes#another_flag.0",
			Subcookies: map[string]models.YSubcookie{
				"show_morda": {
					Name:  "show_morda",
					Value: "yes",
				},
				"another_flag": {
					Name:  "some_flag",
					Value: "0",
				},
			},
		},
		YandexUID:  "6543210987654321",
		SessionID:  "AnotherRandomString1",
		SessionID2: "AnotherRandomString2",
	}
)
