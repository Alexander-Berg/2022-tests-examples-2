package topnews

import (
	"testing"

	"github.com/stretchr/testify/require"

	protoanswers "a.yandex-team.ru/apphost/lib/proto_answers"
	"a.yandex-team.ru/portal/avocado/libs/utils/log3"
)

type fields struct {
	IsFavorite         bool
	DisclaimerDisallow int
	FormKey            string
	ExtraStories       string
	OfficialComment    []officialComment
	Summary            []summary
}

func TestParseTopnewsRuntimeResponse(t *testing.T) {
	tests := []struct {
		name     string
		content  string
		expected fields
		isError  bool
		//isEmpty  bool
	}{
		{
			name:     `No JSON at all`,
			content:  ``,
			expected: fields{},
			isError:  true,
			// isEmpty:  false,
		},
		{
			name:     `Minimal wrong JSON`,
			content:  `{}`,
			expected: fields{},
			isError:  true,
			// isEmpty:  true,
		},
		{
			name:     "No content",
			content:  `{""}`,
			expected: fields{},
			isError:  true,
			// isEmpty:  false,
		},
		{
			name: "Fake news false",
			content: `[{
                "alias":"index",
                "name":"news",
                "url":"news_url",
                "stories":[
                    {
                        "title":"story_1"
                    }
                ],
                "disclaimer_disallow":1
            }]`,
			expected: fields{
				IsFavorite:         false,
				DisclaimerDisallow: 1,
				FormKey:            "",
			},
			isError: false,
			// isEmpty: false,
		},
		{
			name: "Fake news true",
			content: `[{
                "alias":"index",
                "name":"news",
                "url":"news_url",
                "form_key":"fakekey",
                "stories":[
                    {
                        "is_favorite":true,
                        "title":"story_1"
                    }
                ],
                "disclaimer_disallow":1
            }]`,
			expected: fields{
				IsFavorite:         true,
				DisclaimerDisallow: 1,
				FormKey:            "fakekey",
			},
			isError: false,
			// isEmpty: false,
		},
		{
			name: "Real content",
			content: `[
                {
                    "alias":"index",
                    "favorite_smi_count":4,
                    "form_key":"ucc22386aaf4f66a0c55c962fc77b5141",
                    "iter_time":1626295031,
                    "name":"Сейчас в СМИ",
                    "reqid":"1626295483689696-468983427807603505500354-news-sink-app-host-yp-2-NEWS-NEWS_API_TOPS_EXPORT",
                    "state_version":"news-prod-indexers-2-2.man.yp-c.yandex.net:1626295031000000:1626295228958434:0:d292.1f292.1",
                    "stories":[
                        {
                            "agency":{
                                "id":1002,
                                "logo":"//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                                "name":"РИА Новости"
                            },
                            "is_favorite":true,
                            "title":"Глава ВОЗ Гебрейесус заявил о начале третьей волны пандемии коронавируса в мире",
                            "url":"https://news.stable.priemka.yandex.ru/news/story/Glava_VOZ_Gebrejesus_zayavil_onachale_tretej_volny_pandemii_koronavirusa_vmire--c50d6899846ddf1cb6ce336ff72fe2ac?lang=ru&from=main_portal&fan=1&stid=wHeYZMdn4Cu5glTpQYP4&t=1626295031&persistent_id=153213747"
                        }
                    ],
                    "url":"https://yandex.ru/news",
                    "disclaimer_disallow":0
                }
            ]`,
			expected: fields{
				IsFavorite:         true,
				DisclaimerDisallow: 0,
				FormKey:            "ucc22386aaf4f66a0c55c962fc77b5141",
				ExtraStories:       "",
			},
			isError: false,
			// isEmpty: false,
		},
		{
			name: "Extra stories",
			content: `[{
                "alias":"index",
                "name":"news",
                "url":"news_url",
                "stories":[
                    {
                        "title":"story_1",
						"extra_stories":[{
							"url":"esurl",
							"title":"estitle",
							"agency":{
								"id":125,
								"name":"ag1",
								"logo":"logo1"
							}
						}]
                    }
                ],
                "disclaimer_disallow":1
            }]`,
			expected: fields{
				IsFavorite:         false,
				DisclaimerDisallow: 1,
				FormKey:            "",
				ExtraStories:       "estitle",
			},
			isError: false,
			// isEmpty: false,
		},
		{
			name: "Real V3",
			content: `{
    "data": [
        {
            "alias": "index",
            "name": "\u0421\u0435\u0439\u0447\u0430\u0441 \u0432 \u0421\u041c\u0418",
            "stories": [
                {
                    "agency": {
                        "id": 1014,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1014-1627575534690-square",
                        "name": "REGNUM"
                    },
                    "is_favorite":true,
                    "title": "\u0420\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0438\u0435 \u0432\u043e\u043b\u0435\u0439\u0431\u043e\u043b\u0438\u0441\u0442\u044b \u043f\u043e\u0431\u0435\u0434\u0438\u043b\u0438 \u0411\u0440\u0430\u0437\u0438\u043b\u0438\u044e \u0438 \u0432\u044b\u0448\u043b\u0438 \u0432\u00a0\u0444\u0438\u043d\u0430\u043b \u041e\u043b\u0438\u043c\u043f\u0438\u0430\u0434\u044b",
                    "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Rossijskie_volejbolisty_pobedili_Braziliyu_i_vyshli_vfinal_Olimpiady--3899fcf3143898fff4c7659f4a586761?lang=ru&from=main_portal&fan=1&stid=HS7kkMeNNNDkZ9EXqgbm&t=1628145859&persistent_id=154968745"
                },
                {
                    "agency": {
                        "id": 1040,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1040-1478692902361-square",
                        "name": "\u0413\u0430\u0437\u0435\u0442\u0430.Ru"
                    },
                    "title": "\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0441\u0442\u0440\u0430\u043d \u0417\u0430\u043f\u0430\u0434\u0430 \u043f\u0440\u0438\u0437\u0432\u0430\u043b\u0438 \u0420\u0424 \u043e\u0442\u043e\u0437\u0432\u0430\u0442\u044c \u043f\u0440\u0438\u0437\u043d\u0430\u043d\u0438\u0435 \u042e\u0436\u043d\u043e\u0439 \u041e\u0441\u0435\u0442\u0438\u0438 \u0438 \u0410\u0431\u0445\u0430\u0437\u0438\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Neskolko_stran_Zapada_prizvali_RF_otozvat_priznanie_YUzhnoj_Osetii_i_Abkhazii--cabcc41b6b0d5c4dcf4c366f50affe5a?lang=ru&from=main_portal&fan=1&stid=BZICKIm8Dne1ab0PQPKn&t=1628145859&persistent_id=154944124"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "has_hosted_videos": 1,
                    "title": "\u0413\u043b\u0430\u0432\u0430 \u0412\u041e\u0417 \u043f\u0440\u0438\u0437\u0432\u0430\u043b \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u043c\u043e\u0440\u0430\u0442\u043e\u0440\u0438\u0439 \u043d\u0430\u00a0\u0431\u0443\u0441\u0442\u0435\u0440\u043d\u044b\u0435 \u0434\u043e\u0437\u044b \u0432\u0430\u043a\u0446\u0438\u043d \u0434\u043e\u00a0\u043a\u043e\u043d\u0446\u0430 \u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044f",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Glava_VOZ_prizval_ustanovit_moratorij_nabusternye_dozy_vakcin_dokonca_sentyabrya--1787c3ef68a15fedf2e7db9f0b88d8bb?lang=ru&from=main_portal&fan=1&stid=1PXsqiHQOG7gXE4lOIZS&t=1628145859&persistent_id=154926563"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "has_hosted_videos": 1,
                    "title": "\u0412\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d \u043c\u0443\u0436\u0447\u0438\u043d\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u0432\u044b\u0431\u0440\u043e\u0441\u0438\u043b \u0438\u0437\u00a0\u043e\u043a\u043d\u0430 \u0434\u043e\u043c\u0430 \u0441\u0432\u043e\u0435\u0433\u043e \u0441\u044b\u043d\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/VMoskve_zaderzhan_muzhchina_kotoryj_vybrosil_izokna_doma_svoego_syna--70d3ea69827304bc7a8dcb5208a99c14?lang=ru&from=main_portal&fan=1&stid=ag9NiX1-h-ImdQqGYu1S&t=1628145859&persistent_id=154945748"
                },
                {
                    "agency": {
                        "id": 1014,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1014-1627575534690-square",
                        "name": "REGNUM"
                    },
                    "title": "\u0416\u0438\u0442\u0435\u043b\u044f\u043c \u0420\u043e\u0441\u0441\u0438\u0438 \u0440\u0430\u0437\u044a\u044f\u0441\u043d\u0438\u043b\u0438 \u0438\u0445 \u043f\u0440\u0430\u0432\u0430 \u043f\u0440\u0438\u00a0\u0432\u043d\u0435\u0437\u0430\u043f\u043d\u044b\u0445 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430\u0445 \u0432\u00a0\u043a\u0432\u0430\u0440\u0442\u0438\u0440\u0430\u0445",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/ZHitelyam_Rossii_razyasnili_ikh_prava_privnezapnykh_proverkakh_vkvartirakh--6a40c9cd5c4ed5620528810331b92eb1?lang=ru&from=main_portal&fan=1&stid=eJLViPG71mVGBDytuIVd&t=1628145859&persistent_id=154955919"
                }
            ],
            "url": "https://yandex.ru/news"
        },
        {
            "alias": "Moscow",
            "id": 213,
            "name": "\u041c\u043e\u0441\u043a\u0432\u0430",
            "stories": [
                {
                    "agency": {
                        "id": 254113803,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254113803-1530722250485-square",
                        "name": "\u041e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u0440\u0442\u0430\u043b \u041c\u044d\u0440\u0430 \u0438 \u041f\u0440\u0430\u0432\u0438\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u0430 \u041c\u043e\u0441\u043a\u0432\u044b"
                    },
                    "title": "\u041e\u0442\u043a\u0440\u044b\u0442\u0438\u0435 \u0442\u0440\u0435\u0445 \u0441\u0442\u0430\u043d\u0446\u0438\u0439 \u0411\u041a\u041b \u0443\u043b\u0443\u0447\u0448\u0438\u0442 \u0442\u0440\u0430\u043d\u0441\u043f\u043e\u0440\u0442\u043d\u0443\u044e \u0441\u0438\u0442\u0443\u0430\u0446\u0438\u044e \u043d\u0430\u00a0\u044e\u0433\u0435 \u041c\u043e\u0441\u043a\u0432\u044b",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Otkrytie_trekh_stancij_BKL_uluchshit_transportnuyu_situaciyu_nayuge_Moskvy--4986cef6658e83f917f630f1688f8c2a?lang=ru&from=reg_portal&fan=1&stid=UVup5dT_B1sAPnsIN6kn&t=1628145859&persistent_id=154964745"
                },
                {
                    "agency": {
                        "id": 1227,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1227-1540315405629-square",
                        "name": "\u041a\u043e\u043c\u0441\u043e\u043c\u043e\u043b\u044c\u0441\u043a\u0430\u044f \u043f\u0440\u0430\u0432\u0434\u0430"
                    },
                    "title": "\u0412\u0438\u043b\u044c\u0444\u0430\u043d\u0434 \u0440\u0430\u0441\u0441\u043a\u0430\u0437\u0430\u043b, \u0447\u0442\u043e \u0441\u0438\u043d\u043e\u043f\u0442\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043e\u0441\u0435\u043d\u044c \u043d\u0430\u0441\u0442\u0443\u043f\u0438\u0442 \u0432\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0432\u00a0\u0442\u0440\u0435\u0442\u044c\u0435\u0439 \u0434\u0435\u043a\u0430\u0434\u0435 \u0430\u0432\u0433\u0443\u0441\u0442\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Vilfand_rasskazal_chto_sinopticheskaya_osen_nastupit_vMoskve_vtretej_dekade_avgusta--69bad3c563971ea1ef2412219a214633?lang=ru&from=reg_portal&fan=1&stid=aluUwj5bhb0OMgZVGmfE&t=1628145859&persistent_id=154967116"
                },
                {
                    "agency": {
                        "id": 1002,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                        "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                    },
                    "title": "\u041d\u0430\u00a0\u044e\u0433\u043e-\u0432\u043e\u0441\u0442\u043e\u043a\u0435 \u041c\u043e\u0441\u043a\u0432\u044b \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043b\u0438 \u043c\u0443\u0436\u0447\u0438\u043d\u0443, \u0432\u044b\u0431\u0440\u043e\u0441\u0438\u0432\u0448\u0435\u0433\u043e \u0441\u044b\u043d\u0430 \u0438\u0437\u00a0\u043e\u043a\u043d\u0430 \u043a\u0432\u0430\u0440\u0442\u0438\u0440\u044b",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Nayugo-vostoke_Moskvy_zaderzhali_muzhchinu_vybrosivshego_syna_izokna_kvartiry--eb0b48cee190e955c14b13e66bb7b695?lang=ru&from=reg_portal&fan=1&stid=ag9NiX1-h-ImdQqGYu1S&t=1628145859&persistent_id=154945748"
                },
                {
                    "agency": {
                        "id": 1047,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1047-1478692902215-square",
                        "name": "Lenta.ru"
                    },
                    "title": "\u041c\u043e\u0441\u043a\u0432\u0438\u0447\u0435\u0439 \u043f\u0440\u0435\u0434\u0443\u043f\u0440\u0435\u0434\u0438\u043b\u0438 \u043e\u00a0\u043b\u0438\u0432\u043d\u0435 \u0441\u00a0\u0433\u0440\u043e\u0437\u0430\u043c\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Moskvichej_predupredili_olivne_sgrozami--1d300622127d48b1f57152a4fb236ace?lang=ru&from=reg_portal&fan=1&stid=bhYd9_H9rR_1wGrwr4L6&t=1628145859&persistent_id=154969123"
                },
                {
                    "agency": {
                        "id": 1027,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/117671/1027-1530099491421-square",
                        "name": "\u0420\u0411\u041a"
                    },
                    "title": "\u0420\u043e\u0441\u0442 \u0440\u043e\u0436\u0434\u0430\u0435\u043c\u043e\u0441\u0442\u0438 \u0432\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0434\u043e\u0441\u0442\u0438\u0433 \u0440\u0435\u043a\u043e\u0440\u0434\u043d\u044b\u0445 148% \u043d\u0430\u00a0\u0444\u043e\u043d\u0435 \u043f\u0430\u043d\u0434\u0435\u043c\u0438\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Rost_rozhdaemosti_vMoskve_dostig_rekordnykh_148_nafone_pandemii--0e2b0f1c9ce70dbc83ba25f757d79654?lang=ru&from=reg_portal&fan=1&stid=hKkWkHsF&t=1628145859&persistent_id=154973278"
                }
            ],
            "url": "https://yandex.ru/news/region/Moscow"
        },
        {
            "alias": "politics",
            "name": "\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430",
            "stories": [
                {
                    "agency": {
                        "id": 1027,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/117671/1027-1530099491421-square",
                        "name": "\u0420\u0411\u041a"
                    },
                    "title": "\u0421\u0435\u043c\u044c \u0441\u0442\u0440\u0430\u043d \u043f\u0440\u0438\u0437\u0432\u0430\u043b\u0438 \u0420\u043e\u0441\u0441\u0438\u044e \u043e\u0442\u043e\u0437\u0432\u0430\u0442\u044c \u043f\u0440\u0438\u0437\u043d\u0430\u043d\u0438\u0435 \u042e\u0436\u043d\u043e\u0439 \u041e\u0441\u0435\u0442\u0438\u0438 \u0438 \u0410\u0431\u0445\u0430\u0437\u0438\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Sem_stran_prizvali_Rossiyu_otozvat_priznanie_YUzhnoj_Osetii_i_Abkhazii--7986e6c6244bb07c863a3c8745f75b8f?lang=ru&from=rub_portal&wan=1&stid=BZICKIm8Dne1ab0PQPKn&t=1628145859&persistent_id=154944124"
                },
                {
                    "agency": {
                        "id": 254083361,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/254083361-1516267195536-square",
                        "name": "RT \u043d\u0430 \u0440\u0443\u0441\u0441\u043a\u043e\u043c"
                    },
                    "title": "\u0412\u00a0\u041e\u0411\u0421\u0415 \u0437\u0430\u044f\u0432\u0438\u043b\u0438, \u0447\u0442\u043e \u043d\u0435 \u0441\u043c\u043e\u0433\u0443\u0442 \u043d\u0430\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u043d\u0430\u0431\u043b\u044e\u0434\u0430\u0442\u0435\u043b\u0435\u0439 \u043d\u0430\u00a0\u0432\u044b\u0431\u043e\u0440\u044b \u0432\u00a0\u0413\u043e\u0441\u0434\u0443\u043c\u0443",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/VOBSE_zayavili_chto_ne_smogut_napravit_nablyudatelej_navybory_vGosdumu--b028bc42ec066b8d3e37f76bd1f592eb?lang=ru&from=rub_portal&wan=1&stid=ndf30c9G1svxf_elyt9-&t=1628145859&persistent_id=154905242"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u0420\u0411\u041a: \u0427\u0443\u0431\u0430\u0439\u0441 \u043f\u0440\u043e\u0433\u043d\u043e\u0437\u0438\u0440\u0443\u0435\u0442 \u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u043d\u043e\u0432\u043e\u0439 \u043c\u0438\u0440\u043e\u0432\u043e\u0439 \u044d\u043b\u0438\u0442\u044b \u043f\u0440\u0438\u00a0\u0433\u043b\u043e\u0431\u0430\u043b\u044c\u043d\u043e\u043c \u044d\u043d\u0435\u0440\u0433\u043e\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u0435",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/RBK_CHubajs_prognoziruet_formirovanie_novoj_mirovoj_ehlity_priglobalnom_ehnergoperekhode--8e8f24b69c92a37a042aa9fe1bc42c1f?lang=ru&from=rub_portal&wan=1&stid=dJbNCWBHrcVVzs39EuuZ&t=1628145859&persistent_id=154910978"
                },
                {
                    "agency": {
                        "id": 1002,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                        "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                    },
                    "title": "\u0423\u043a\u0440\u0430\u0438\u043d\u0430 \u0438\u0437-\u0437\u0430\u00a0COVID-19 \u0443\u0436\u0435\u0441\u0442\u043e\u0447\u0438\u043b\u0430 \u043f\u0440\u0430\u0432\u0438\u043b\u0430 \u0432\u044a\u0435\u0437\u0434\u0430 \u0438\u0437\u00a0\u0420\u043e\u0441\u0441\u0438\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Ukraina_iz-zaCOVID-19_uzhestochila_pravila_vezda_izRossii--28054dafab11d0e57cd9fed1b03eb3c5?lang=ru&from=rub_portal&wan=1&stid=UqmBpn-b-0_nKGMF3rYF&t=1628145859&persistent_id=154729546"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u0421\u041a \u0420\u043e\u0441\u0441\u0438\u0438 \u0432\u043e\u0437\u0431\u0443\u0434\u0438\u043b \u0434\u0435\u043b\u043e \u0432\u00a0\u043e\u0442\u043d\u043e\u0448\u0435\u043d\u0438\u0438 \u043a\u043e\u043c\u0430\u043d\u0434\u0438\u0440\u0430 \u0431\u0440\u0438\u0433\u0430\u0434\u044b \u0412\u043e\u043e\u0440\u0443\u0436\u0435\u043d\u043d\u044b\u0445 \u0441\u0438\u043b \u0423\u043a\u0440\u0430\u0438\u043d\u044b",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/SK_Rossii_vozbudil_delo_votnoshenii_komandira_brigady_Vooruzhennykh_sil_Ukrainy--aac6cdc43b12101bb4258d860a5a3d20?lang=ru&from=rub_portal&wan=1&stid=71pMrnFo08px&t=1628145859&persistent_id=154973217"
                }
            ],
            "url": "https://yandex.ru/news/rubric/politics"
        },
        {
            "alias": "society",
            "name": "\u041e\u0431\u0449\u0435\u0441\u0442\u0432\u043e",
            "stories": [
                {
                    "agency": {
                        "id": 1002,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                        "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                    },
                    "title": "\u0411\u0435\u043b\u044b\u0439 \u0434\u043e\u043c \u0432\u044b\u0441\u0442\u0443\u043f\u0438\u043b \u043f\u0440\u043e\u0442\u0438\u0432 \u0438\u0434\u0435\u0438 \u0412\u041e\u0417 \u0432\u0432\u0435\u0441\u0442\u0438 \u043c\u043e\u0440\u0430\u0442\u043e\u0440\u0438\u0439 \u043d\u0430\u00a0\u0440\u0435\u0432\u0430\u043a\u0446\u0438\u043d\u0430\u0446\u0438\u044e \u043e\u0442\u00a0COVID-19",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Belyj_dom_vystupil_protiv_idei_VOZ_vvesti_moratorij_narevakcinaciyu_otCOVID-19--d013efd20c18cd16ce8f804bcec62e74?lang=ru&from=rub_portal&wan=1&stid=1PXsqiHQOG7gXE4lOIZS&t=1628145859&persistent_id=154926563"
                },
                {
                    "agency": {
                        "id": 1014,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1014-1627575534690-square",
                        "name": "REGNUM"
                    },
                    "title": "\u0416\u0438\u0442\u0435\u043b\u044f\u043c \u0420\u043e\u0441\u0441\u0438\u0438 \u0440\u0430\u0437\u044a\u044f\u0441\u043d\u0438\u043b\u0438 \u0438\u0445 \u043f\u0440\u0430\u0432\u0430 \u043f\u0440\u0438\u00a0\u0432\u043d\u0435\u0437\u0430\u043f\u043d\u044b\u0445 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430\u0445 \u0432\u00a0\u043a\u0432\u0430\u0440\u0442\u0438\u0440\u0430\u0445",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/ZHitelyam_Rossii_razyasnili_ikh_prava_privnezapnykh_proverkakh_vkvartirakh--6a40c9cd5c4ed5620528810331b92eb1?lang=ru&from=rub_portal&wan=1&stid=eJLViPG71mVGBDytuIVd&t=1628145859&persistent_id=154955919"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u00ab\u041e\u0442\u043a\u0440\u044b\u0442\u044b\u0435 \u043c\u0435\u0434\u0438\u0430\u00bb \u043e\u0431\u044a\u044f\u0432\u0438\u043b\u0438 \u043e\u00a0\u043f\u0440\u0435\u043a\u0440\u0430\u0449\u0435\u043d\u0438\u0438 \u0440\u0430\u0431\u043e\u0442\u044b \u043f\u043e\u0441\u043b\u0435 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0438 \u0441\u0430\u0439\u0442\u0430 \u0420\u043e\u0441\u043a\u043e\u043c\u043d\u0430\u0434\u0437\u043e\u0440\u043e\u043c",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Otkrytye_media_obyavili_oprekrashhenii_raboty_posle_blokirovki_sajta_Roskomnadzorom--43e8c35cb5050d2dcc706f2fa866bdd0?lang=ru&from=rub_portal&wan=1&stid=206Lxo_Azwyg3apBihnZ&t=1628145859&persistent_id=154945462"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u00ab\u0418\u0437\u0432\u0435\u0441\u0442\u0438\u044f\u00bb: \u0432\u00a0\u0420\u0424 \u043d\u0430\u00a0\u0441\u0432\u043e\u0431\u043e\u0434\u0443 \u0432\u00a0\u0442\u0435\u0447\u0435\u043d\u0438\u0435 \u0434\u0432\u0443\u0445 \u043b\u0435\u0442 \u043c\u043e\u0433\u0443\u0442 \u0432\u044b\u0439\u0442\u0438 11 \u043e\u0441\u0443\u0436\u0434\u0435\u043d\u043d\u044b\u0445 \u043d\u0430\u00a0\u0441\u043c\u0435\u0440\u0442\u043d\u0443\u044e \u043a\u0430\u0437\u043d\u044c",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Izvestiya_vRF_nasvobodu_vtechenie_dvukh_let_mogut_vyjti_11_osuzhdennykh_nasmertnuyu_kazn--733b7701d91f7d8b6a0355cceb8da76e?lang=ru&from=rub_portal&wan=1&stid=cF59BoWCwyeHgqF3Bda3&t=1628145859&persistent_id=154958277"
                },
                {
                    "agency": {
                        "id": 1116,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1116-1478692904205-square",
                        "name": "\u0420\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0430\u044f \u0433\u0430\u0437\u0435\u0442\u0430"
                    },
                    "title": "\u0418\u043c\u043c\u0443\u043d\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u044d\u0444\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c \u0432\u0430\u043a\u0446\u0438\u043d\u044b \u00ab\u042d\u043f\u0438\u0412\u0430\u043a\u041a\u043e\u0440\u043e\u043d\u0430\u00bb \u0441\u043e\u0441\u0442\u0430\u0432\u0438\u043b\u0430 79%",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Immunologicheskaya_ehffektivnost_vakciny_EHpiVakKorona_sostavila_79--ed8e012334c090fc81b46c0e349f07df?lang=ru&from=rub_portal&wan=1&stid=8O_MUC1fPe3YVsjBcEhK&t=1628145859&persistent_id=154951330"
                }
            ],
            "url": "https://yandex.ru/news/rubric/society"
        },
        {
            "alias": "business",
            "name": "\u042d\u043a\u043e\u043d\u043e\u043c\u0438\u043a\u0430",
            "stories": [
                {
                    "agency": {
                        "id": 1048,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                        "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                    },
                    "title": "\u0420\u0411\u041a: \u0432\u043b\u0430\u0441\u0442\u0438 \u043d\u0430\u0447\u0430\u043b\u0438 \u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0443 \u043a\u00a0\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u0443 \u043d\u0430\u00a0\u0430\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u044b\u0435 \u044d\u043d\u0435\u0440\u0433\u043e\u043d\u043e\u0441\u0438\u0442\u0435\u043b\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/RBK_vlasti_nachali_podgotovku_kperekhodu_naalternativnye_ehnergonositeli--2817f89e9257cb849a9144368eeed743?lang=ru&from=rub_portal&wan=1&stid=9t41f3chKgObdd3PHD0c&t=1628145859&persistent_id=154887064"
                },
                {
                    "agency": {
                        "id": 254083361,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/254083361-1516267195536-square",
                        "name": "RT \u043d\u0430 \u0440\u0443\u0441\u0441\u043a\u043e\u043c"
                    },
                    "title": "\u0412\u00a0\u041c\u0438\u043d\u043f\u0440\u043e\u043c\u0442\u043e\u0440\u0433\u0435 \u043e\u0442\u043c\u0435\u0442\u0438\u043b\u0438 \u0441\u043d\u0438\u0436\u0435\u043d\u0438\u0435 \u0446\u0435\u043d \u043d\u0430\u00a0\u043e\u0432\u043e\u0449\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/VMinpromtorge_otmetili_snizhenie_cen_naovoshhi--39d82c343ed6601174fddee0a0ad784a?lang=ru&from=rub_portal&wan=1&stid=vl0zKrfaSe1zNy2xlS-7&t=1628145859&persistent_id=154949187"
                },
                {
                    "agency": {
                        "id": 8352,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/41096/8352-1506595261741-square",
                        "name": "BFM.ru"
                    },
                    "title": "Bloomberg: \u0420\u043e\u0441\u0441\u0438\u044f \u0437\u0430\u043d\u0438\u043c\u0430\u0435\u0442 \u0432\u0442\u043e\u0440\u043e\u0435 \u043c\u0435\u0441\u0442\u043e \u0441\u0440\u0435\u0434\u0438\u00a0\u0438\u043d\u043e\u0441\u0442\u0440\u0430\u043d\u043d\u044b\u0445 \u043f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a\u043e\u0432 \u043d\u0435\u0444\u0442\u0438 \u0432\u00a0\u0421\u0428\u0410",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Bloomberg_Rossiya_zanimaet_vtoroe_mesto_srediinostrannykh_postavshhikov_nefti_vSSHA--637606b322bdf039b033088ca56a7a79?lang=ru&from=rub_portal&wan=1&stid=18Sso0QpzEpR4lKwK9xA&t=1628145859&persistent_id=154947801"
                },
                {
                    "agency": {
                        "id": 1048,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                        "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                    },
                    "title": "\u041c\u0438\u043d\u044d\u043a\u043e\u043d\u043e\u043c\u0438\u043a\u0438 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0438\u043b\u043e \u0443\u0432\u0435\u043b\u0438\u0447\u0438\u0442\u044c \u0433\u043e\u0441\u0440\u0430\u0441\u0445\u043e\u0434\u044b \u043d\u0430\u00a01,8 \u0442\u0440\u043b\u043d \u0440\u0443\u0431. \u043d\u0430\u00a0\u0442\u0440\u0438 \u0433\u043e\u0434\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Minehkonomiki_predlozhilo_uvelichit_gosraskhody_na18_trln_rub._natri_goda--8732cb654be6da615b9d2af6989459f1?lang=ru&from=rub_portal&wan=1&stid=cs6O4jx5jYMwNS4fcPZw&t=1628145859&persistent_id=154958272"
                },
                {
                    "agency": {
                        "id": 1048,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                        "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                    },
                    "title": "\u00ab\u042f\u043d\u0434\u0435\u043a\u0441\u00bb \u0437\u0430\u043a\u0440\u044b\u043b \u043a\u0440\u0443\u043f\u043d\u0435\u0439\u0448\u0443\u044e \u0441\u0434\u0435\u043b\u043a\u0443 \u0433\u043e\u0434\u0430 \u043d\u0430\u00a0\u0440\u044b\u043d\u043a\u0435 \u043e\u0444\u0438\u0441\u043e\u0432",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/YAndeks_zakryl_krupnejshuyu_sdelku_goda_narynke_ofisov--48872905acd53ef81f2cb0123e2184bf?lang=ru&from=rub_portal&wan=1&stid=X_wYKcQKF8E2GBan&t=1628145859&persistent_id=154968873"
                }
            ],
            "url": "https://yandex.ru/news/rubric/business"
        },
        {
            "alias": "world",
            "name": "\u0412 \u043c\u0438\u0440\u0435",
            "stories": [
                {
                    "agency": {
                        "id": 1063,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1063-1478692902330-square",
                        "name": "\u0420\u043e\u0441\u0431\u0430\u043b\u0442"
                    },
                    "title": "Bloomberg: \u041f\u0440\u043e\u0442\u0438\u0432 \u0448\u0442\u0430\u043c\u043c\u0430 \u00ab\u0434\u0435\u043b\u044c\u0442\u0430\u00bb \u043c\u043e\u0433\u0443\u0442 \u043f\u043e\u0442\u0440\u0435\u0431\u043e\u0432\u0430\u0442\u044c\u0441\u044f \u043d\u043e\u0432\u044b\u0435 \u0432\u0430\u043a\u0446\u0438\u043d\u044b",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Bloomberg_Protiv_shtamma_delta_mogut_potrebovatsya_novye_vakciny--3cf4fda26de9ac7a7d08aa339982a3f7?lang=ru&from=rub_portal&wan=1&stid=7PPuqXiouUro2nLsoSpz&t=1628145859&persistent_id=154952716"
                },
                {
                    "agency": {
                        "id": 254156038,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/41096/254156038-1557303731847-square",
                        "name": "News.ru"
                    },
                    "title": "\u042f\u043f\u043e\u043d\u0438\u0438 \u043f\u043e\u0441\u043e\u0432\u0435\u0442\u043e\u0432\u0430\u043b\u0438 \u0438\u0437\u0443\u0447\u0438\u0442\u044c \u0440\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0438\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043f\u043e\u00a0\u041a\u0443\u0440\u0438\u043b\u0430\u043c",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/YAponii_posovetovali_izuchit_rossijskie_predlozheniya_poKurilam--d38d37c4ac00292682c10e05da44b4ec?lang=ru&from=rub_portal&wan=1&stid=b_uPMVOuVkbiOyPD&t=1628145859&persistent_id=154905395"
                },
                {
                    "agency": {
                        "id": 1040,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1040-1478692902361-square",
                        "name": "\u0413\u0430\u0437\u0435\u0442\u0430.Ru"
                    },
                    "title": "\u0412\u00a0\u041a\u0438\u0442\u0430\u0435 \u0441\u043e\u0437\u0434\u0430\u043b\u0438 \u043b\u0430\u043c\u043f\u0443 \u0434\u043b\u044f\u00a0\u0434\u0435\u0437\u0438\u043d\u0444\u0435\u043a\u0446\u0438\u0438 \u043e\u0442\u00a0COVID-19 \u0441\u00a0\u044d\u0444\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c\u044e 99,99%",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/VKitae_sozdali_lampu_dlyadezinfekcii_otCOVID-19_sehffektivnostyu_9999--112b0e453ac6903a7c8f18861acb4ade?lang=ru&from=rub_portal&wan=1&stid=svEqUj2f1ljqwBsNw-rv&t=1628145859&persistent_id=154960914"
                },
                {
                    "agency": {
                        "id": 1002,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                        "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                    },
                    "title": "\u041c\u044d\u0440 \u0422\u043e\u043a\u0430\u0442: \u0442\u0435\u043f\u043b\u043e\u0432\u0430\u044f \u044d\u043b\u0435\u043a\u0442\u0440\u043e\u0441\u0442\u0430\u043d\u0446\u0438\u044f \u043d\u0430\u00a0\u044e\u0433\u043e-\u0437\u0430\u043f\u0430\u0434\u0435 \u0422\u0443\u0440\u0446\u0438\u0438 \u0437\u0430\u0433\u043e\u0440\u0435\u043b\u0430\u0441\u044c \u0438\u0437-\u0437\u0430\u00a0\u043b\u0435\u0441\u043d\u043e\u0433\u043e \u043f\u043e\u0436\u0430\u0440\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Mehr_Tokat_teplovaya_ehlektrostanciya_nayugo-zapade_Turcii_zagorelas_iz-zalesnogo_pozhara--5e8a3696964eaf6f2823d90d8d08f95f?lang=ru&from=rub_portal&wan=1&stid=nsbBLLL6oaXnmWt3ZT_3&t=1628145859&persistent_id=154944165"
                },
                {
                    "agency": {
                        "id": 1047,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1047-1478692902215-square",
                        "name": "Lenta.ru"
                    },
                    "title": "\u0420\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0438\u0439 \u0430\u0442\u043e\u043c\u043d\u044b\u0439 \u043a\u0440\u0435\u0439\u0441\u0435\u0440 \u043f\u043e\u0442\u0435\u0440\u044f\u043b \u0445\u043e\u0434 \u0443\u00a0\u0431\u0435\u0440\u0435\u0433\u043e\u0432 \u0414\u0430\u043d\u0438\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Rossijskij_atomnyj_krejser_poteryal_khod_uberegov_Danii--a04788abec354e466fb8f6f8daba4faf?lang=ru&from=rub_portal&wan=1&stid=wE8k9cQjO80u&t=1628145859&persistent_id=154920290"
                }
            ],
            "url": "https://yandex.ru/news/rubric/world"
        },
        {
            "alias": "sport",
            "name": "\u0421\u043f\u043e\u0440\u0442",
            "stories": [
                {
                    "agency": {
                        "id": 2220,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/2220-1478692942720-square",
                        "name": "\u0427\u0435\u043c\u043f\u0438\u043e\u043d\u0430\u0442"
                    },
                    "title": "\u041c\u0443\u0436\u0441\u043a\u0430\u044f \u0441\u0431\u043e\u0440\u043d\u0430\u044f \u0420\u043e\u0441\u0441\u0438\u0438 \u043f\u043e\u00a0\u0432\u043e\u043b\u0435\u0439\u0431\u043e\u043b\u0443 \u0432\u044b\u0448\u043b\u0430 \u0432\u00a0\u0444\u0438\u043d\u0430\u043b \u041e\u043b\u0438\u043c\u043f\u0438\u0430\u0434\u044b-2020, \u043f\u043e\u0431\u0435\u0434\u0438\u0432 \u0411\u0440\u0430\u0437\u0438\u043b\u0438\u044e",
                    "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Muzhskaya_sbornaya_Rossii_povolejbolu_vyshla_vfinal_Olimpiady-2020_pobediv_Braziliyu--a54090b9b7695ac2cfe9e9f013e119eb?lang=ru&from=rub_portal&wan=1&stid=HS7kkMeNNNDkZ9EXqgbm&t=1628145859&persistent_id=154968745"
                },
                {
                    "agency": {
                        "id": 1002,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                        "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                    },
                    "title": "\u00ab\u0421\u043f\u0430\u0440\u0442\u0430\u043a\u00bb \u0434\u043e\u043c\u0430 \u043f\u0440\u043e\u0438\u0433\u0440\u0430\u043b \u00ab\u0411\u0435\u043d\u0444\u0438\u043a\u0435\u00bb \u0432\u00a0\u043f\u0435\u0440\u0432\u043e\u043c \u043c\u0430\u0442\u0447\u0435 \u043a\u0432\u0430\u043b\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438 \u041b\u0438\u0433\u0438 \u0447\u0435\u043c\u043f\u0438\u043e\u043d\u043e\u0432",
                    "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Spartak_doma_proigral_Benfike_vpervom_matche_kvalifikacii_Ligi_chempionov--2ebc13c4742a2b31134737e252b5681b?lang=ru&from=rub_portal&wan=1&stid=Vs3I2Qo6Bs8t7bSqYFgR&t=1628145859&persistent_id=154944234"
                },
                {
                    "agency": {
                        "id": 2220,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/2220-1478692942720-square",
                        "name": "\u0427\u0435\u043c\u043f\u0438\u043e\u043d\u0430\u0442"
                    },
                    "title": "\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u0420\u043e\u043c\u0430\u0448\u0438\u043d\u0430 \u0441\u0442\u0430\u043b\u0430 \u043f\u0435\u0440\u0432\u043e\u0439 \u0432\u00a0\u0438\u0441\u0442\u043e\u0440\u0438\u0438 6-\u043a\u0440\u0430\u0442\u043d\u043e\u0439 \u0447\u0435\u043c\u043f\u0438\u043e\u043d\u043a\u043e\u0439 \u041e\u0418 \u043f\u043e\u00a0\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u043e\u043c\u0443 \u043f\u043b\u0430\u0432\u0430\u043d\u0438\u044e",
                    "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Svetlana_Romashina_stala_pervoj_vistorii_6-kratnoj_chempionkoj_OI_posinkhronnomu_plavaniyu--32d2c2e02d07c0210854417e1f575eba?lang=ru&from=rub_portal&wan=1&stid=8TfNbdt9GKBWU8MXuNOZ&t=1628145859&persistent_id=154910469"
                },
                {
                    "agency": {
                        "id": 3678,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/61287/3678-1482247329455-square",
                        "name": "\u0421\u043f\u043e\u0440\u0442 \u0434\u0435\u043d\u044c \u0437\u0430 \u0434\u043d\u0435\u043c"
                    },
                    "title": "\u0412\u00a0\u0411\u0440\u0430\u0437\u0438\u043b\u0438\u0438 \u0441\u043e\u043e\u0431\u0449\u0438\u043b\u0438, \u0441\u043a\u043e\u043b\u044c\u043a\u043e \u00ab\u0417\u0435\u043d\u0438\u0442\u00bb \u0437\u0430\u043f\u043b\u0430\u0442\u0438\u0442 \u0437\u0430\u00a0\u043f\u0435\u0440\u0435\u0445\u043e\u0434 \u041a\u043b\u0430\u0443\u0434\u0438\u043d\u044c\u043e",
                    "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/VBrazilii_soobshhili_skolko_Zenit_zaplatit_zaperekhod_Klaudino--f93b17278240836f408327d6c26fbce0?lang=ru&from=rub_portal&wan=1&stid=-1BbNb9lU0bJphaePz7C&t=1628145859&persistent_id=154922273"
                },
                {
                    "agency": {
                        "id": 254147205,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/117671/254147205-1478693952904-square",
                        "name": "\u041c\u0430\u0442\u0447 \u0422\u0412"
                    },
                    "title": "\u0414\u0435\u0441\u044f\u0442\u0438\u0431\u043e\u0440\u0435\u0446 \u0428\u043a\u0443\u0440\u0435\u043d\u0435\u0432 \u043d\u0430\u00a0\u041e\u0418 \u0432\u00a0\u0422\u043e\u043a\u0438\u043e \u043f\u043e\u043a\u0430\u0437\u0430\u043b \u043b\u0443\u0447\u0448\u0438\u0439 \u043b\u0438\u0447\u043d\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u0441\u0435\u0437\u043e\u043d\u0430 \u0432\u00a0\u043c\u0435\u0442\u0430\u043d\u0438\u0438 \u0434\u0438\u0441\u043a\u0430",
                    "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Desyatiborec_SHkurenev_naOI_vTokio_pokazal_luchshij_lichnyj_rezultat_sezona_vmetanii_diska--2d4e0483158c27bfbd36e5da9ab8c19a?lang=ru&from=rub_portal&wan=1&stid=ylslGMfyelxdzfiQuNDj&t=1628145859&persistent_id=154871375"
                }
            ],
            "url": "https://yandex.ru/news/rubric/sport"
        },
        {
            "alias": "incident",
            "name": "\u041f\u0440\u043e\u0438\u0441\u0448\u0435\u0441\u0442\u0432\u0438\u044f",
            "stories": [
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u0412\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d \u043c\u0443\u0436\u0447\u0438\u043d\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u0432\u044b\u0431\u0440\u043e\u0441\u0438\u043b \u0438\u0437\u00a0\u043e\u043a\u043d\u0430 \u0434\u043e\u043c\u0430 \u0441\u0432\u043e\u0435\u0433\u043e \u0441\u044b\u043d\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/VMoskve_zaderzhan_muzhchina_kotoryj_vybrosil_izokna_doma_svoego_syna--70d3ea69827304bc7a8dcb5208a99c14?lang=ru&from=rub_portal&wan=1&stid=ag9NiX1-h-ImdQqGYu1S&t=1628145859&persistent_id=154945748"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u0421\u041a \u0432\u044b\u044f\u0432\u0438\u043b \u043d\u043e\u0432\u044b\u0435 \u044d\u043f\u0438\u0437\u043e\u0434\u044b \u043f\u043e\u00a0\u0434\u0435\u043b\u0443 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d\u043d\u043e\u0433\u043e \u0432\u00a0\u041f\u043e\u0434\u043c\u043e\u0441\u043a\u043e\u0432\u044c\u0435 \u0437\u0430\u00a0\u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0443 \u043a\u00a0\u0442\u0435\u0440\u0430\u043a\u0442\u0443",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/SK_vyyavil_novye_ehpizody_podelu_zaderzhannogo_vPodmoskove_zapodgotovku_kteraktu--d1b22d5e2739a585dc5c92fc6a7bbccd?lang=ru&from=rub_portal&wan=1&stid=7036yfHtKkbWIkmHqH_P&t=1628145859&persistent_id=154970756"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u0421\u0430\u043c\u043e\u043b\u0435\u0442 \u0430\u0432\u0438\u0430\u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438 \u00ab\u0420\u043e\u0441\u0441\u0438\u044f\u00bb \u0432\u0435\u0440\u043d\u0443\u043b\u0441\u044f \u0432\u00a0\u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442 \u0427\u0435\u043b\u044f\u0431\u0438\u043d\u0441\u043a\u0430 \u043f\u043e\u00a0\u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u043c \u043f\u0440\u0438\u0447\u0438\u043d\u0430\u043c",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Samolet_aviakompanii_Rossiya_vernulsya_vaehroport_CHelyabinska_potekhnicheskim_prichinam--15a361a659b00055415d3cc733fa02c8?lang=ru&from=rub_portal&wan=1&stid=NbKgVya6OBJPVBDmbkZd&t=1628145859&persistent_id=154969933"
                },
                {
                    "agency": {
                        "id": 1002,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                        "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                    },
                    "title": "\u0420\u043e\u0441\u0442\u0435\u0445 \u043e\u043f\u0440\u043e\u0432\u0435\u0440\u0433 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043e\u00a0\u043f\u043e\u0432\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u0438 \u0434\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f \u0411\u0435-200 \u043f\u0440\u0438\u00a0\u0442\u0443\u0448\u0435\u043d\u0438\u0438 \u043f\u043e\u0436\u0430\u0440\u043e\u0432 \u0432\u00a0\u0413\u0440\u0435\u0446\u0438\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Rostekh_oproverg_soobshheniya_opovrezhdenii_dvigatelya_Be-200_pritushenii_pozharov_vGrecii--c8dd4588551bd88dac0bc6eeb0136ee2?lang=ru&from=rub_portal&wan=1&stid=mUv_XFfPDotOfwL25E-q&t=1628145859&persistent_id=154933849"
                },
                {
                    "agency": {
                        "id": 1551,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                        "name": "\u0422\u0410\u0421\u0421"
                    },
                    "title": "\u0417\u0430\u043a\u043b\u044e\u0447\u0435\u043d\u043d\u043e\u0433\u043e \u043d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a\u043e\u0439 \u043a\u043e\u043b\u043e\u043d\u0438\u0438 \u043e\u0441\u0443\u0434\u0438\u043b\u0438 \u043d\u0430\u00a0\u0442\u0440\u0438 \u0433\u043e\u0434\u0430 \u0437\u0430\u00a0\u043f\u0440\u043e\u043f\u0430\u0433\u0430\u043d\u0434\u0443 \u0442\u0435\u0440\u0440\u043e\u0440\u0438\u0437\u043c\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Zaklyuchennogo_novosibirskoj_kolonii_osudili_natri_goda_zapropagandu_terrorizma--51989b79c65de78d18ed39aa55f8ad43?lang=ru&from=rub_portal&wan=1&stid=FF0WwgpVXt6uuUeMHoAh&t=1628145859&persistent_id=154964387"
                }
            ],
            "url": "https://yandex.ru/news/rubric/incident"
        },
        {
            "alias": "culture",
            "name": "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u0430",
            "stories": [
                {
                    "agency": {
                        "id": 254154182,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254154182-1550152741834-square",
                        "name": "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u043e\u043c\u0430\u043d\u0438\u044f"
                    },
                    "title": "\u0412\u044b\u0448\u0435\u043b \u0442\u0440\u0435\u0439\u043b\u0435\u0440 \u0444\u0438\u043b\u044c\u043c\u0430 \u00ab\u0417\u043e\u043b\u0443\u0448\u043a\u0430\u00bb \u0441\u00a0\u041a\u0430\u043c\u0438\u043b\u043e\u0439 \u041a\u0430\u0431\u0435\u0439\u043e",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Vyshel_trejler_filma_Zolushka_sKamiloj_Kabejo--0023b46f6177d0d99ddb31900111464f?lang=ru&from=rub_portal&wan=1&stid=nGkL78SMB0lZGTRwNUxH&t=1628145859&persistent_id=154858258"
                },
                {
                    "agency": {
                        "id": 254154182,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254154182-1550152741834-square",
                        "name": "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u043e\u043c\u0430\u043d\u0438\u044f"
                    },
                    "title": "\u0412\u044b\u0448\u0435\u043b \u0442\u0440\u0435\u0439\u043b\u0435\u0440 \u044d\u0440\u043e\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0442\u0440\u0438\u043b\u043b\u0435\u0440\u0430 \u00ab\u0421\u043e\u0432\u0440\u0438 \u043c\u043d\u0435 \u043f\u0440\u0430\u0432\u0434\u0443\u00bb \u0441\u00a0\u041f\u0440\u0438\u043b\u0443\u0447\u043d\u044b\u043c",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Vyshel_trejler_ehroticheskogo_trillera_Sovri_mne_pravdu_sPriluchnym--f9e599663d338e5e26ef3c043785470a?lang=ru&from=rub_portal&wan=1&stid=SwyZ4ZbsNUCQYOBg5cEG&t=1628145859&persistent_id=154906432"
                },
                {
                    "agency": {
                        "id": 1048,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                        "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                    },
                    "title": "\u0412\u044b\u0445\u043e\u0434 \u0441\u0435\u0440\u0438\u0430\u043b\u0430 \u00ab\u0412\u043b\u0430\u0441\u0442\u0435\u043b\u0438\u043d \u043a\u043e\u043b\u0435\u0446\u00bb \u0437\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d \u043d\u0430\u00a0\u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044c 2022 \u0433\u043e\u0434\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Vykhod_seriala_Vlastelin_kolec_zaplanirovan_nasentyabr_2022_goda--0fa97c6fd9c3b12b0d6e4649efbabf29?lang=ru&from=rub_portal&wan=1&stid=gy-2fLc1SMff4WxIUNEg&t=1628145859&persistent_id=154717596"
                },
                {
                    "agency": {
                        "id": 254165984,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/254165984-1602694686.929395-square",
                        "name": "FBM.ru"
                    },
                    "title": "\u0411\u0440\u0438\u0442\u0430\u043d\u0446\u044b \u0441\u0447\u0438\u0442\u0430\u044e\u0442, \u0447\u0442\u043e \u0441\u0438\u043a\u0432\u0435\u043b \u00ab\u041e\u0442\u0440\u044f\u0434\u0430 \u0441\u0430\u043c\u043e\u0443\u0431\u0438\u0439\u0446\u00bb \u0438\u043c\u0435\u0435\u0442 \u043d\u0435\u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0439 \u0440\u0435\u0439\u0442\u0438\u043d\u0433",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Britancy_schitayut_chto_sikvel_Otryada_samoubijc_imeet_nesootvetstvuyushhij_rejting--e9bf7e0bc0141adaf21a89e21ec2529a?lang=ru&from=rub_portal&wan=1&stid=2af3d7AmcylhBA8z4SrK&t=1628145859&persistent_id=154950008"
                },
                {
                    "agency": {
                        "id": 254091134,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/254091134-1580903043896-square",
                        "name": "\u0413\u0430\u0437\u0435\u0442\u0430 \u041a\u0443\u043b\u044c\u0442\u0443\u0440\u0430"
                    },
                    "title": "\u0411\u0440\u0430\u0442\u044c\u044f \u041a\u043e\u044d\u043d \u043f\u0435\u0440\u0435\u0441\u0442\u0430\u043d\u0443\u0442 \u0432\u043c\u0435\u0441\u0442\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c \u043d\u0430\u0434\u00a0\u0444\u0438\u043b\u044c\u043c\u0430\u043c\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Bratya_Koehn_perestanut_vmeste_rabotat_nadfilmami--13cf0ac88e8843a70043ee747c96517c?lang=ru&from=rub_portal&wan=1&stid=2j-RO0n6lgtjseSkxQfq&t=1628145859&persistent_id=154899109"
                }
            ],
            "url": "https://yandex.ru/news/rubric/culture"
        },
        {
            "alias": "computers",
            "name": "\u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438",
            "stories": [
                {
                    "agency": {
                        "id": 254152790,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/33291/254152790-1612443048.96772-square",
                        "name": "CyberSport.ru"
                    },
                    "title": "\u041f\u0440\u043e\u0434\u0430\u0436\u0438 Mass Effect Legendary Edition \u043f\u0440\u0435\u0432\u0437\u043e\u0448\u043b\u0438 \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u044f EA",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Prodazhi_Mass_Effect_Legendary_Edition_prevzoshli_ozhidaniya_EA--97c705fd6603464d4a72ecd22a3b5f62?lang=ru&from=rub_portal&wan=1&stid=QExTAtkuNUE8&t=1628145859&persistent_id=154953220"
                },
                {
                    "agency": {
                        "id": 254165984,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/254165984-1602694686.929395-square",
                        "name": "FBM.ru"
                    },
                    "title": "Windows 10 \u0441\u00a0\u0430\u0432\u0433\u0443\u0441\u0442\u0430 \u0431\u0443\u0434\u0435\u0442 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043d\u0435\u0436\u0435\u043b\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0435 \u041f\u041e",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Windows_10_savgusta_budet_avtomaticheski_blokirovat_nezhelatelnoe_PO--9cf836cf777defa70f5a48b31b62d431?lang=ru&from=rub_portal&wan=1&stid=pVQzVH2xyBFOH8aBeeUA&t=1628145859&persistent_id=154805955"
                },
                {
                    "agency": {
                        "id": 1556,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/62808/1556-1518502037969-square",
                        "name": "iXBT.com"
                    },
                    "title": "Xiaomi \u043f\u043e\u043a\u0430\u0437\u0430\u043b\u0430 6 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u043e\u0432 \u0434\u0438\u0437\u0430\u0439\u043d\u0430 \u0441\u043c\u0430\u0440\u0442\u0444\u043e\u043d\u0430 Xiaomi Mi Mix 4",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Xiaomi_pokazala_6_variantov_dizajna_smartfona_Xiaomi_Mi_Mix_4--e4251795d16d90289a677611f484f4be?lang=ru&from=rub_portal&wan=1&stid=dMzqS7AcSx1f&t=1628145859&persistent_id=154972777"
                },
                {
                    "agency": {
                        "id": 1569,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1569-1544162285015-square",
                        "name": "\u041f\u0440\u043e\u0444\u0438\u043b\u044c"
                    },
                    "title": "\u041a\u0438\u0431\u0435\u0440\u0430\u0442\u0435\u043b\u044c\u0435 \u0434\u043b\u044f\u00a0\u0441\u0430\u043c\u043e\u0441\u0442\u043e\u044f\u0442\u0435\u043b\u044c\u043d\u043e\u0433\u043e \u0438 \u0443\u0434\u0430\u043b\u0435\u043d\u043d\u043e\u0433\u043e \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u0430 \u043e\u0434\u0435\u0436\u0434\u044b \u043f\u043e\u044f\u0432\u0438\u0442\u0441\u044f \u0432\u00a0\u0420\u043e\u0441\u0441\u0438\u0438",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Kiberatele_dlyasamostoyatelnogo_i_udalennogo_proizvodstva_odezhdy_poyavitsya_vRossii--82315f042af92f5e313ca702853a9720?lang=ru&from=rub_portal&wan=1&stid=xw4IVk-MskaQ&t=1628145859&persistent_id=154959583"
                },
                {
                    "agency": {
                        "id": 1670,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/1670-1551172901405-square",
                        "name": "Ferra"
                    },
                    "title": "Sony \u0434\u043e\u0431\u0430\u0432\u0438\u0442 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0443 \u0432\u0438\u0440\u0442\u0443\u0430\u043b\u044c\u043d\u043e\u0439 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 \u0432\u043e \u0432\u0441\u0435 \u00ab\u0431\u043e\u043b\u044c\u0448\u0438\u0435\u00bb \u0438\u0433\u0440\u044b \u0434\u043b\u044f\u00a0PlayStation 5",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Sony_dobavit_podderzhku_virtualnoj_realnosti_vo_vse_bolshie_igry_dlyaPlayStation_5--8205c13561456d1ace5bd850f196bdd4?lang=ru&from=rub_portal&wan=1&stid=sSopPteIze4tsZZtPlEd&t=1628145859&persistent_id=154626977"
                }
            ],
            "url": "https://yandex.ru/news/rubric/computers"
        },
        {
            "alias": "science",
            "name": "\u041d\u0430\u0443\u043a\u0430",
            "stories": [
                {
                    "agency": {
                        "id": 254120975,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254120975-1550183881383-square",
                        "name": "SMINEWS \u0432 \u041f\u043e\u0434\u043e\u043b\u044c\u0441\u043a\u0435"
                    },
                    "title": "NG: \u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 \u043a\u0438\u0441\u043b\u043e\u0440\u043e\u0434\u0430 \u0432\u00a0\u0430\u0442\u043c\u043e\u0441\u0444\u0435\u0440\u0435 \u0417\u0435\u043c\u043b\u0438 \u0441\u0432\u044f\u0437\u0430\u043b\u0438 \u0441\u00a0\u0437\u0430\u043c\u0435\u0434\u043b\u0435\u043d\u0438\u0435\u043c \u0432\u0440\u0430\u0449\u0435\u043d\u0438\u044f",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/NG_Obrazovanie_kisloroda_vatmosfere_Zemli_svyazali_szamedleniem_vrashheniya--20c86eb5757fc4017de6c06c37777c16?lang=ru&from=rub_portal&wan=1&stid=J1shfwAwcnpbCW4s5FEl&t=1628145859&persistent_id=154714656"
                },
                {
                    "agency": {
                        "id": 254133475,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/254133475-1478693911264-square",
                        "name": "\u041c\u0435\u0434\u0438\u0430\u041f\u043e\u0442\u043e\u043a"
                    },
                    "title": "\u0413\u043e\u0440\u043e\u0434 \u0438\u043d\u043a\u043e\u0432 \u041c\u0430\u0447\u0443-\u041f\u0438\u043a\u0447\u0443 \u043e\u043a\u0430\u0437\u0430\u043b\u0441\u044f \u0434\u0440\u0435\u0432\u043d\u0435\u0435, \u0447\u0435\u043c \u0441\u0447\u0438\u0442\u0430\u043b\u043e\u0441\u044c \u0440\u0430\u043d\u0435\u0435",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Gorod_inkov_Machu-Pikchu_okazalsya_drevnee_chem_schitalos_ranee--a87faab6ea6daa542671b525fb6c3fab?lang=ru&from=rub_portal&wan=1&stid=QPUd6boOUjDqU3VMv72x&t=1628145859&persistent_id=154868664"
                },
                {
                    "agency": {
                        "id": 254114979,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/254114979-1478693761853-square",
                        "name": "\u0424\u0410\u041d"
                    },
                    "title": "\u041d\u0435\u0430\u043d\u0434\u0435\u0440\u0442\u0430\u043b\u044c\u0446\u044b \u043e\u0441\u0442\u0430\u0432\u0438\u043b\u0438 \u0440\u0438\u0441\u0443\u043d\u043a\u0438 \u043d\u0430\u00a0\u0441\u0442\u0430\u043b\u0430\u0433\u043c\u0438\u0442\u0430\u0445 \u0432\u00a0\u0418\u0441\u043f\u0430\u043d\u0438\u0438 60 \u0442\u044b\u0441\u044f\u0447 \u043b\u0435\u0442 \u043d\u0430\u0437\u0430\u0434",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Neandertalcy_ostavili_risunki_nastalagmitakh_vIspanii_60_tysyach_let_nazad--3c091f1065b86845e0f777db4eb487e3?lang=ru&from=rub_portal&wan=1&stid=sQf-IV3o-C4Ko5pMUEyR&t=1628145859&persistent_id=154719914"
                },
                {
                    "agency": {
                        "id": 254165984,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/254165984-1602694686.929395-square",
                        "name": "FBM.ru"
                    },
                    "title": "\u0423\u0447\u0435\u043d\u044b\u0435 \u041a\u0430\u043d\u0430\u0434\u044b \u0432\u044b\u044f\u0432\u0438\u043b\u0438 \u043f\u0440\u0438\u0447\u0438\u043d\u0443 \u043e\u043f\u0430\u0441\u043d\u044b\u0445 \u043e\u0441\u043b\u043e\u0436\u043d\u0435\u043d\u0438\u0439 \u043f\u0440\u0438\u00a0\u043a\u043e\u0440\u043e\u043d\u0430\u0432\u0438\u0440\u0443\u0441\u0435 COVID-19",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Uchenye_Kanady_vyyavili_prichinu_opasnykh_oslozhnenij_prikoronaviruse_COVID-19--c2d729bba24f2f05e69155682a00a5c7?lang=ru&from=rub_portal&wan=1&stid=gYmEV9MvdV0HRooP&t=1628145859&persistent_id=154963185"
                },
                {
                    "agency": {
                        "id": 254162796,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254162796-1570028445907-square",
                        "name": "\u0422\u0410\u0421\u0421 \u041d\u0430\u0443\u043a\u0430 "
                    },
                    "title": "\u0412\u00a0\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a\u0435 \u0441\u043e\u0437\u0434\u0430\u043b\u0438 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u044e \u0434\u043b\u044f\u00a0\u043d\u0435\u0444\u0442\u044f\u043d\u0438\u043a\u043e\u0432, \u0441\u043d\u0438\u0436\u0430\u044e\u0449\u0443\u044e \u0432\u044b\u0431\u0440\u043e\u0441\u044b \u0441\u0435\u0440\u043e\u0432\u043e\u0434\u043e\u0440\u043e\u0434\u0430 \u0432\u00a0100 \u0440\u0430\u0437",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/VNovosibirske_sozdali_tekhnologiyu_dlyaneftyanikov_snizhayushhuyu_vybrosy_serovodoroda_v100_raz--70251cacb630e97b47b2ae9e7ef93dbf?lang=ru&from=rub_portal&wan=1&stid=IydGK2tC&t=1628145859&persistent_id=154966973"
                }
            ],
            "url": "https://yandex.ru/news/rubric/science"
        },
        {
            "alias": "auto",
            "name": "\u0410\u0432\u0442\u043e",
            "stories": [
                {
                    "agency": {
                        "id": 1048,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                        "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                    },
                    "title": "\u0421\u0440\u0435\u0434\u043d\u0435\u0432\u0437\u0432\u0435\u0448\u0435\u043d\u043d\u0430\u044f \u0446\u0435\u043d\u0430 \u043d\u043e\u0432\u043e\u0433\u043e \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044f \u0432\u00a0\u043f\u0435\u0440\u0432\u043e\u043c \u043f\u043e\u043b\u0443\u0433\u043e\u0434\u0438\u0438 \u0432\u044b\u0440\u043e\u0441\u043b\u0430 \u043d\u0430\u00a012,5%",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Srednevzveshennaya_cena_novogo_avtomobilya_vpervom_polugodii_vyrosla_na125--1ee06f09f8b5af6cfe0a64e707b654b7?lang=ru&from=rub_portal&wan=1&stid=2uI559qNa_CTDLwwWfs7&t=1628145859&persistent_id=154882986"
                },
                {
                    "agency": {
                        "id": 6816,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/6816-1478693057271-square",
                        "name": "\u0410\u0432\u0442\u043e\u0441\u0442\u0430\u0442"
                    },
                    "title": "\u0412\u00a0\u0427\u0435\u0445\u0438\u0438 \u043d\u0430\u0447\u0430\u043b\u0441\u044f \u0432\u044b\u043f\u0443\u0441\u043a \u044d\u043b\u0435\u043a\u0442\u0440\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0423\u0410\u0417 \u00ab\u0425\u0430\u043d\u0442\u0435\u0440\u00bb",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/VCHekhii_nachalsya_vypusk_ehlektricheskogo_UAZ_KHanter--0853d9510dfb38be54dc3b0815255fc2?lang=ru&from=rub_portal&wan=1&stid=AOewEKcrNyDy7o1c-Ow7&t=1628145859&persistent_id=154728455"
                },
                {
                    "agency": {
                        "id": 254101760,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/62808/254101760-1478693655341-square",
                        "name": "32CARS.ru"
                    },
                    "title": "\u0410\u0432\u0442\u043e\u0431\u0440\u0435\u043d\u0434 Toyota \u043f\u0440\u0435\u0434\u0441\u0442\u0430\u0432\u0438\u043b\u0430 \u044e\u0431\u0438\u043b\u0435\u0439\u043d\u0443\u044e \u0432\u0435\u0440\u0441\u0438\u044e Land Cruiser 70",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Avtobrend_Toyota_predstavila_yubilejnuyu_versiyu_Land_Cruiser_70--eb34740f942185cb9b7db40818395d99?lang=ru&from=rub_portal&wan=1&stid=Go2X8w0_XyxF9bJcBiSZ&t=1628145859&persistent_id=154907549"
                },
                {
                    "agency": {
                        "id": 254167762,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/786982/254167762-1616559957.67102-square",
                        "name": "\u0413\u0434\u0435 \u0438 \u0447\u0442\u043e"
                    },
                    "title": "\u00ab\u041b\u0410\u0414\u0410 \u0426\u0435\u043d\u0442\u0440 \u0427\u0435\u0440\u0435\u043f\u043e\u0432\u0435\u0446\u00bb \u0440\u0430\u0441\u043a\u0440\u044b\u043b \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u043e\u0433\u043e \u0432\u043d\u0435\u0434\u043e\u0440\u043e\u0436\u043d\u0438\u043a\u0430 Lada Niva Bronto",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/LADA_Centr_CHerepovec_raskryl_stoimost_obnovlennogo_vnedorozhnika_Lada_Niva_Bronto--a5c9fd233e05ac4b45044891e802f77c?lang=ru&from=rub_portal&wan=1&stid=8T39oFh7fDtWbyplvphP&t=1628145859&persistent_id=154909594"
                },
                {
                    "agency": {
                        "id": 254054748,
                        "logo": "//avatars.mds.yandex.net/get-ynews-logo/56838/254054748-1478693377904-square",
                        "name": "\u0410\u0432\u0442\u043e\u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u0434\u043d\u044f"
                    },
                    "title": "\u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e \u0440\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u043e\u0433\u043e \u044d\u043b\u0435\u043a\u0442\u0440\u043e\u043a\u0430\u0440\u0430 Zetta \u043d\u0430\u0447\u043d\u0435\u0442\u0441\u044f \u0434\u043e\u00a0\u043a\u043e\u043d\u0446\u0430 2021 \u0433\u043e\u0434\u0430",
                    "url": "https://news.stable.priemka.yandex.ru/news/story/Proizvodstvo_rossijskogo_ehlektrokara_Zetta_nachnetsya_dokonca_2021_goda--5065b2fbf0c6dfa6137da257487fa9f4?lang=ru&from=rub_portal&wan=1&stid=eZLbwyEGGofP03ZnVhT9&t=1628145859&persistent_id=154675444"
                }
            ],
            "url": "https://yandex.ru/news/rubric/auto"
        }
    ],
    "iter_time": 1628145859,
    "reqid": "1628146427307528-760379911749557946200362-news-sink-app-host-yp-1-NEWS-NEWS_API_TOPS_EXPORT",
    "state_version": "news-prod-indexers-2-3.vla.yp-c.yandex.net:1628145859000000:1628146090225561:0:d294.4f294.4",
    "type": "newsd_response",
    "disclaimer_disallow":1,
	"favorite_smi_count":4,
	"form_key":"u3d4a228bd04263c75163991a6ab30272"
}
`,
			expected: fields{
				IsFavorite:         true,
				DisclaimerDisallow: 1,
				FormKey:            "u3d4a228bd04263c75163991a6ab30272",
				ExtraStories:       "",
			},
			isError: false,
			// isEmpty: false,
		},
		{
			name: "Real V3 no favorite",
			content: `{
                "data": [
                    {
                        "alias": "index",
                        "name": "\u0421\u0435\u0439\u0447\u0430\u0441 \u0432 \u0421\u041c\u0418",
                        "stories": [
                            {
                                "agency": {
                                    "id": 1014,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1014-1627575534690-square",
                                    "name": "REGNUM"
                                },
                                "is_favorite":false,
                                "title": "\u0420\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0438\u0435 \u0432\u043e\u043b\u0435\u0439\u0431\u043e\u043b\u0438\u0441\u0442\u044b \u043f\u043e\u0431\u0435\u0434\u0438\u043b\u0438 \u0411\u0440\u0430\u0437\u0438\u043b\u0438\u044e \u0438 \u0432\u044b\u0448\u043b\u0438 \u0432\u00a0\u0444\u0438\u043d\u0430\u043b \u041e\u043b\u0438\u043c\u043f\u0438\u0430\u0434\u044b",
                                "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Rossijskie_volejbolisty_pobedili_Braziliyu_i_vyshli_vfinal_Olimpiady--3899fcf3143898fff4c7659f4a586761?lang=ru&from=main_portal&fan=1&stid=HS7kkMeNNNDkZ9EXqgbm&t=1628145859&persistent_id=154968745"
                            },
                            {
                                "agency": {
                                    "id": 1040,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1040-1478692902361-square",
                                    "name": "\u0413\u0430\u0437\u0435\u0442\u0430.Ru"
                                },
                                "title": "\u041d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0441\u0442\u0440\u0430\u043d \u0417\u0430\u043f\u0430\u0434\u0430 \u043f\u0440\u0438\u0437\u0432\u0430\u043b\u0438 \u0420\u0424 \u043e\u0442\u043e\u0437\u0432\u0430\u0442\u044c \u043f\u0440\u0438\u0437\u043d\u0430\u043d\u0438\u0435 \u042e\u0436\u043d\u043e\u0439 \u041e\u0441\u0435\u0442\u0438\u0438 \u0438 \u0410\u0431\u0445\u0430\u0437\u0438\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Neskolko_stran_Zapada_prizvali_RF_otozvat_priznanie_YUzhnoj_Osetii_i_Abkhazii--cabcc41b6b0d5c4dcf4c366f50affe5a?lang=ru&from=main_portal&fan=1&stid=BZICKIm8Dne1ab0PQPKn&t=1628145859&persistent_id=154944124"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "has_hosted_videos": 1,
                                "title": "\u0413\u043b\u0430\u0432\u0430 \u0412\u041e\u0417 \u043f\u0440\u0438\u0437\u0432\u0430\u043b \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c \u043c\u043e\u0440\u0430\u0442\u043e\u0440\u0438\u0439 \u043d\u0430\u00a0\u0431\u0443\u0441\u0442\u0435\u0440\u043d\u044b\u0435 \u0434\u043e\u0437\u044b \u0432\u0430\u043a\u0446\u0438\u043d \u0434\u043e\u00a0\u043a\u043e\u043d\u0446\u0430 \u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044f",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Glava_VOZ_prizval_ustanovit_moratorij_nabusternye_dozy_vakcin_dokonca_sentyabrya--1787c3ef68a15fedf2e7db9f0b88d8bb?lang=ru&from=main_portal&fan=1&stid=1PXsqiHQOG7gXE4lOIZS&t=1628145859&persistent_id=154926563"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "has_hosted_videos": 1,
                                "title": "\u0412\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d \u043c\u0443\u0436\u0447\u0438\u043d\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u0432\u044b\u0431\u0440\u043e\u0441\u0438\u043b \u0438\u0437\u00a0\u043e\u043a\u043d\u0430 \u0434\u043e\u043c\u0430 \u0441\u0432\u043e\u0435\u0433\u043e \u0441\u044b\u043d\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/VMoskve_zaderzhan_muzhchina_kotoryj_vybrosil_izokna_doma_svoego_syna--70d3ea69827304bc7a8dcb5208a99c14?lang=ru&from=main_portal&fan=1&stid=ag9NiX1-h-ImdQqGYu1S&t=1628145859&persistent_id=154945748"
                            },
                            {
                                "agency": {
                                    "id": 1014,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1014-1627575534690-square",
                                    "name": "REGNUM"
                                },
                                "title": "\u0416\u0438\u0442\u0435\u043b\u044f\u043c \u0420\u043e\u0441\u0441\u0438\u0438 \u0440\u0430\u0437\u044a\u044f\u0441\u043d\u0438\u043b\u0438 \u0438\u0445 \u043f\u0440\u0430\u0432\u0430 \u043f\u0440\u0438\u00a0\u0432\u043d\u0435\u0437\u0430\u043f\u043d\u044b\u0445 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430\u0445 \u0432\u00a0\u043a\u0432\u0430\u0440\u0442\u0438\u0440\u0430\u0445",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/ZHitelyam_Rossii_razyasnili_ikh_prava_privnezapnykh_proverkakh_vkvartirakh--6a40c9cd5c4ed5620528810331b92eb1?lang=ru&from=main_portal&fan=1&stid=eJLViPG71mVGBDytuIVd&t=1628145859&persistent_id=154955919"
                            }
                        ],
                        "url": "https://yandex.ru/news"
                    },
                    {
                        "alias": "Moscow",
                        "id": 213,
                        "name": "\u041c\u043e\u0441\u043a\u0432\u0430",
                        "stories": [
                            {
                                "agency": {
                                    "id": 254113803,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254113803-1530722250485-square",
                                    "name": "\u041e\u0444\u0438\u0446\u0438\u0430\u043b\u044c\u043d\u044b\u0439 \u043f\u043e\u0440\u0442\u0430\u043b \u041c\u044d\u0440\u0430 \u0438 \u041f\u0440\u0430\u0432\u0438\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u0430 \u041c\u043e\u0441\u043a\u0432\u044b"
                                },
                                "title": "\u041e\u0442\u043a\u0440\u044b\u0442\u0438\u0435 \u0442\u0440\u0435\u0445 \u0441\u0442\u0430\u043d\u0446\u0438\u0439 \u0411\u041a\u041b \u0443\u043b\u0443\u0447\u0448\u0438\u0442 \u0442\u0440\u0430\u043d\u0441\u043f\u043e\u0440\u0442\u043d\u0443\u044e \u0441\u0438\u0442\u0443\u0430\u0446\u0438\u044e \u043d\u0430\u00a0\u044e\u0433\u0435 \u041c\u043e\u0441\u043a\u0432\u044b",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Otkrytie_trekh_stancij_BKL_uluchshit_transportnuyu_situaciyu_nayuge_Moskvy--4986cef6658e83f917f630f1688f8c2a?lang=ru&from=reg_portal&fan=1&stid=UVup5dT_B1sAPnsIN6kn&t=1628145859&persistent_id=154964745"
                            },
                            {
                                "agency": {
                                    "id": 1227,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1227-1540315405629-square",
                                    "name": "\u041a\u043e\u043c\u0441\u043e\u043c\u043e\u043b\u044c\u0441\u043a\u0430\u044f \u043f\u0440\u0430\u0432\u0434\u0430"
                                },
                                "title": "\u0412\u0438\u043b\u044c\u0444\u0430\u043d\u0434 \u0440\u0430\u0441\u0441\u043a\u0430\u0437\u0430\u043b, \u0447\u0442\u043e \u0441\u0438\u043d\u043e\u043f\u0442\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043e\u0441\u0435\u043d\u044c \u043d\u0430\u0441\u0442\u0443\u043f\u0438\u0442 \u0432\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0432\u00a0\u0442\u0440\u0435\u0442\u044c\u0435\u0439 \u0434\u0435\u043a\u0430\u0434\u0435 \u0430\u0432\u0433\u0443\u0441\u0442\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Vilfand_rasskazal_chto_sinopticheskaya_osen_nastupit_vMoskve_vtretej_dekade_avgusta--69bad3c563971ea1ef2412219a214633?lang=ru&from=reg_portal&fan=1&stid=aluUwj5bhb0OMgZVGmfE&t=1628145859&persistent_id=154967116"
                            },
                            {
                                "agency": {
                                    "id": 1002,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                                    "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                                },
                                "title": "\u041d\u0430\u00a0\u044e\u0433\u043e-\u0432\u043e\u0441\u0442\u043e\u043a\u0435 \u041c\u043e\u0441\u043a\u0432\u044b \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043b\u0438 \u043c\u0443\u0436\u0447\u0438\u043d\u0443, \u0432\u044b\u0431\u0440\u043e\u0441\u0438\u0432\u0448\u0435\u0433\u043e \u0441\u044b\u043d\u0430 \u0438\u0437\u00a0\u043e\u043a\u043d\u0430 \u043a\u0432\u0430\u0440\u0442\u0438\u0440\u044b",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Nayugo-vostoke_Moskvy_zaderzhali_muzhchinu_vybrosivshego_syna_izokna_kvartiry--eb0b48cee190e955c14b13e66bb7b695?lang=ru&from=reg_portal&fan=1&stid=ag9NiX1-h-ImdQqGYu1S&t=1628145859&persistent_id=154945748"
                            },
                            {
                                "agency": {
                                    "id": 1047,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1047-1478692902215-square",
                                    "name": "Lenta.ru"
                                },
                                "title": "\u041c\u043e\u0441\u043a\u0432\u0438\u0447\u0435\u0439 \u043f\u0440\u0435\u0434\u0443\u043f\u0440\u0435\u0434\u0438\u043b\u0438 \u043e\u00a0\u043b\u0438\u0432\u043d\u0435 \u0441\u00a0\u0433\u0440\u043e\u0437\u0430\u043c\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Moskvichej_predupredili_olivne_sgrozami--1d300622127d48b1f57152a4fb236ace?lang=ru&from=reg_portal&fan=1&stid=bhYd9_H9rR_1wGrwr4L6&t=1628145859&persistent_id=154969123"
                            },
                            {
                                "agency": {
                                    "id": 1027,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/117671/1027-1530099491421-square",
                                    "name": "\u0420\u0411\u041a"
                                },
                                "title": "\u0420\u043e\u0441\u0442 \u0440\u043e\u0436\u0434\u0430\u0435\u043c\u043e\u0441\u0442\u0438 \u0432\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0434\u043e\u0441\u0442\u0438\u0433 \u0440\u0435\u043a\u043e\u0440\u0434\u043d\u044b\u0445 148% \u043d\u0430\u00a0\u0444\u043e\u043d\u0435 \u043f\u0430\u043d\u0434\u0435\u043c\u0438\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Rost_rozhdaemosti_vMoskve_dostig_rekordnykh_148_nafone_pandemii--0e2b0f1c9ce70dbc83ba25f757d79654?lang=ru&from=reg_portal&fan=1&stid=hKkWkHsF&t=1628145859&persistent_id=154973278"
                            }
                        ],
                        "url": "https://yandex.ru/news/region/Moscow"
                    },
                    {
                        "alias": "politics",
                        "name": "\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430",
                        "stories": [
                            {
                                "agency": {
                                    "id": 1027,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/117671/1027-1530099491421-square",
                                    "name": "\u0420\u0411\u041a"
                                },
                                "title": "\u0421\u0435\u043c\u044c \u0441\u0442\u0440\u0430\u043d \u043f\u0440\u0438\u0437\u0432\u0430\u043b\u0438 \u0420\u043e\u0441\u0441\u0438\u044e \u043e\u0442\u043e\u0437\u0432\u0430\u0442\u044c \u043f\u0440\u0438\u0437\u043d\u0430\u043d\u0438\u0435 \u042e\u0436\u043d\u043e\u0439 \u041e\u0441\u0435\u0442\u0438\u0438 \u0438 \u0410\u0431\u0445\u0430\u0437\u0438\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Sem_stran_prizvali_Rossiyu_otozvat_priznanie_YUzhnoj_Osetii_i_Abkhazii--7986e6c6244bb07c863a3c8745f75b8f?lang=ru&from=rub_portal&wan=1&stid=BZICKIm8Dne1ab0PQPKn&t=1628145859&persistent_id=154944124"
                            },
                            {
                                "agency": {
                                    "id": 254083361,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/254083361-1516267195536-square",
                                    "name": "RT \u043d\u0430 \u0440\u0443\u0441\u0441\u043a\u043e\u043c"
                                },
                                "title": "\u0412\u00a0\u041e\u0411\u0421\u0415 \u0437\u0430\u044f\u0432\u0438\u043b\u0438, \u0447\u0442\u043e \u043d\u0435 \u0441\u043c\u043e\u0433\u0443\u0442 \u043d\u0430\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u043d\u0430\u0431\u043b\u044e\u0434\u0430\u0442\u0435\u043b\u0435\u0439 \u043d\u0430\u00a0\u0432\u044b\u0431\u043e\u0440\u044b \u0432\u00a0\u0413\u043e\u0441\u0434\u0443\u043c\u0443",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/VOBSE_zayavili_chto_ne_smogut_napravit_nablyudatelej_navybory_vGosdumu--b028bc42ec066b8d3e37f76bd1f592eb?lang=ru&from=rub_portal&wan=1&stid=ndf30c9G1svxf_elyt9-&t=1628145859&persistent_id=154905242"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u0420\u0411\u041a: \u0427\u0443\u0431\u0430\u0439\u0441 \u043f\u0440\u043e\u0433\u043d\u043e\u0437\u0438\u0440\u0443\u0435\u0442 \u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u043d\u043e\u0432\u043e\u0439 \u043c\u0438\u0440\u043e\u0432\u043e\u0439 \u044d\u043b\u0438\u0442\u044b \u043f\u0440\u0438\u00a0\u0433\u043b\u043e\u0431\u0430\u043b\u044c\u043d\u043e\u043c \u044d\u043d\u0435\u0440\u0433\u043e\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u0435",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/RBK_CHubajs_prognoziruet_formirovanie_novoj_mirovoj_ehlity_priglobalnom_ehnergoperekhode--8e8f24b69c92a37a042aa9fe1bc42c1f?lang=ru&from=rub_portal&wan=1&stid=dJbNCWBHrcVVzs39EuuZ&t=1628145859&persistent_id=154910978"
                            },
                            {
                                "agency": {
                                    "id": 1002,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                                    "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                                },
                                "title": "\u0423\u043a\u0440\u0430\u0438\u043d\u0430 \u0438\u0437-\u0437\u0430\u00a0COVID-19 \u0443\u0436\u0435\u0441\u0442\u043e\u0447\u0438\u043b\u0430 \u043f\u0440\u0430\u0432\u0438\u043b\u0430 \u0432\u044a\u0435\u0437\u0434\u0430 \u0438\u0437\u00a0\u0420\u043e\u0441\u0441\u0438\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Ukraina_iz-zaCOVID-19_uzhestochila_pravila_vezda_izRossii--28054dafab11d0e57cd9fed1b03eb3c5?lang=ru&from=rub_portal&wan=1&stid=UqmBpn-b-0_nKGMF3rYF&t=1628145859&persistent_id=154729546"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u0421\u041a \u0420\u043e\u0441\u0441\u0438\u0438 \u0432\u043e\u0437\u0431\u0443\u0434\u0438\u043b \u0434\u0435\u043b\u043e \u0432\u00a0\u043e\u0442\u043d\u043e\u0448\u0435\u043d\u0438\u0438 \u043a\u043e\u043c\u0430\u043d\u0434\u0438\u0440\u0430 \u0431\u0440\u0438\u0433\u0430\u0434\u044b \u0412\u043e\u043e\u0440\u0443\u0436\u0435\u043d\u043d\u044b\u0445 \u0441\u0438\u043b \u0423\u043a\u0440\u0430\u0438\u043d\u044b",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/SK_Rossii_vozbudil_delo_votnoshenii_komandira_brigady_Vooruzhennykh_sil_Ukrainy--aac6cdc43b12101bb4258d860a5a3d20?lang=ru&from=rub_portal&wan=1&stid=71pMrnFo08px&t=1628145859&persistent_id=154973217"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/politics"
                    },
                    {
                        "alias": "society",
                        "name": "\u041e\u0431\u0449\u0435\u0441\u0442\u0432\u043e",
                        "stories": [
                            {
                                "agency": {
                                    "id": 1002,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                                    "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                                },
                                "title": "\u0411\u0435\u043b\u044b\u0439 \u0434\u043e\u043c \u0432\u044b\u0441\u0442\u0443\u043f\u0438\u043b \u043f\u0440\u043e\u0442\u0438\u0432 \u0438\u0434\u0435\u0438 \u0412\u041e\u0417 \u0432\u0432\u0435\u0441\u0442\u0438 \u043c\u043e\u0440\u0430\u0442\u043e\u0440\u0438\u0439 \u043d\u0430\u00a0\u0440\u0435\u0432\u0430\u043a\u0446\u0438\u043d\u0430\u0446\u0438\u044e \u043e\u0442\u00a0COVID-19",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Belyj_dom_vystupil_protiv_idei_VOZ_vvesti_moratorij_narevakcinaciyu_otCOVID-19--d013efd20c18cd16ce8f804bcec62e74?lang=ru&from=rub_portal&wan=1&stid=1PXsqiHQOG7gXE4lOIZS&t=1628145859&persistent_id=154926563"
                            },
                            {
                                "agency": {
                                    "id": 1014,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1014-1627575534690-square",
                                    "name": "REGNUM"
                                },
                                "title": "\u0416\u0438\u0442\u0435\u043b\u044f\u043c \u0420\u043e\u0441\u0441\u0438\u0438 \u0440\u0430\u0437\u044a\u044f\u0441\u043d\u0438\u043b\u0438 \u0438\u0445 \u043f\u0440\u0430\u0432\u0430 \u043f\u0440\u0438\u00a0\u0432\u043d\u0435\u0437\u0430\u043f\u043d\u044b\u0445 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430\u0445 \u0432\u00a0\u043a\u0432\u0430\u0440\u0442\u0438\u0440\u0430\u0445",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/ZHitelyam_Rossii_razyasnili_ikh_prava_privnezapnykh_proverkakh_vkvartirakh--6a40c9cd5c4ed5620528810331b92eb1?lang=ru&from=rub_portal&wan=1&stid=eJLViPG71mVGBDytuIVd&t=1628145859&persistent_id=154955919"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u00ab\u041e\u0442\u043a\u0440\u044b\u0442\u044b\u0435 \u043c\u0435\u0434\u0438\u0430\u00bb \u043e\u0431\u044a\u044f\u0432\u0438\u043b\u0438 \u043e\u00a0\u043f\u0440\u0435\u043a\u0440\u0430\u0449\u0435\u043d\u0438\u0438 \u0440\u0430\u0431\u043e\u0442\u044b \u043f\u043e\u0441\u043b\u0435 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0438 \u0441\u0430\u0439\u0442\u0430 \u0420\u043e\u0441\u043a\u043e\u043c\u043d\u0430\u0434\u0437\u043e\u0440\u043e\u043c",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Otkrytye_media_obyavili_oprekrashhenii_raboty_posle_blokirovki_sajta_Roskomnadzorom--43e8c35cb5050d2dcc706f2fa866bdd0?lang=ru&from=rub_portal&wan=1&stid=206Lxo_Azwyg3apBihnZ&t=1628145859&persistent_id=154945462"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u00ab\u0418\u0437\u0432\u0435\u0441\u0442\u0438\u044f\u00bb: \u0432\u00a0\u0420\u0424 \u043d\u0430\u00a0\u0441\u0432\u043e\u0431\u043e\u0434\u0443 \u0432\u00a0\u0442\u0435\u0447\u0435\u043d\u0438\u0435 \u0434\u0432\u0443\u0445 \u043b\u0435\u0442 \u043c\u043e\u0433\u0443\u0442 \u0432\u044b\u0439\u0442\u0438 11 \u043e\u0441\u0443\u0436\u0434\u0435\u043d\u043d\u044b\u0445 \u043d\u0430\u00a0\u0441\u043c\u0435\u0440\u0442\u043d\u0443\u044e \u043a\u0430\u0437\u043d\u044c",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Izvestiya_vRF_nasvobodu_vtechenie_dvukh_let_mogut_vyjti_11_osuzhdennykh_nasmertnuyu_kazn--733b7701d91f7d8b6a0355cceb8da76e?lang=ru&from=rub_portal&wan=1&stid=cF59BoWCwyeHgqF3Bda3&t=1628145859&persistent_id=154958277"
                            },
                            {
                                "agency": {
                                    "id": 1116,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1116-1478692904205-square",
                                    "name": "\u0420\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0430\u044f \u0433\u0430\u0437\u0435\u0442\u0430"
                                },
                                "title": "\u0418\u043c\u043c\u0443\u043d\u043e\u043b\u043e\u0433\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u044d\u0444\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c \u0432\u0430\u043a\u0446\u0438\u043d\u044b \u00ab\u042d\u043f\u0438\u0412\u0430\u043a\u041a\u043e\u0440\u043e\u043d\u0430\u00bb \u0441\u043e\u0441\u0442\u0430\u0432\u0438\u043b\u0430 79%",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Immunologicheskaya_ehffektivnost_vakciny_EHpiVakKorona_sostavila_79--ed8e012334c090fc81b46c0e349f07df?lang=ru&from=rub_portal&wan=1&stid=8O_MUC1fPe3YVsjBcEhK&t=1628145859&persistent_id=154951330"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/society"
                    },
                    {
                        "alias": "business",
                        "name": "\u042d\u043a\u043e\u043d\u043e\u043c\u0438\u043a\u0430",
                        "stories": [
                            {
                                "agency": {
                                    "id": 1048,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                                    "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                                },
                                "title": "\u0420\u0411\u041a: \u0432\u043b\u0430\u0441\u0442\u0438 \u043d\u0430\u0447\u0430\u043b\u0438 \u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0443 \u043a\u00a0\u043f\u0435\u0440\u0435\u0445\u043e\u0434\u0443 \u043d\u0430\u00a0\u0430\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u044b\u0435 \u044d\u043d\u0435\u0440\u0433\u043e\u043d\u043e\u0441\u0438\u0442\u0435\u043b\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/RBK_vlasti_nachali_podgotovku_kperekhodu_naalternativnye_ehnergonositeli--2817f89e9257cb849a9144368eeed743?lang=ru&from=rub_portal&wan=1&stid=9t41f3chKgObdd3PHD0c&t=1628145859&persistent_id=154887064"
                            },
                            {
                                "agency": {
                                    "id": 254083361,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/254083361-1516267195536-square",
                                    "name": "RT \u043d\u0430 \u0440\u0443\u0441\u0441\u043a\u043e\u043c"
                                },
                                "title": "\u0412\u00a0\u041c\u0438\u043d\u043f\u0440\u043e\u043c\u0442\u043e\u0440\u0433\u0435 \u043e\u0442\u043c\u0435\u0442\u0438\u043b\u0438 \u0441\u043d\u0438\u0436\u0435\u043d\u0438\u0435 \u0446\u0435\u043d \u043d\u0430\u00a0\u043e\u0432\u043e\u0449\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/VMinpromtorge_otmetili_snizhenie_cen_naovoshhi--39d82c343ed6601174fddee0a0ad784a?lang=ru&from=rub_portal&wan=1&stid=vl0zKrfaSe1zNy2xlS-7&t=1628145859&persistent_id=154949187"
                            },
                            {
                                "agency": {
                                    "id": 8352,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/41096/8352-1506595261741-square",
                                    "name": "BFM.ru"
                                },
                                "title": "Bloomberg: \u0420\u043e\u0441\u0441\u0438\u044f \u0437\u0430\u043d\u0438\u043c\u0430\u0435\u0442 \u0432\u0442\u043e\u0440\u043e\u0435 \u043c\u0435\u0441\u0442\u043e \u0441\u0440\u0435\u0434\u0438\u00a0\u0438\u043d\u043e\u0441\u0442\u0440\u0430\u043d\u043d\u044b\u0445 \u043f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a\u043e\u0432 \u043d\u0435\u0444\u0442\u0438 \u0432\u00a0\u0421\u0428\u0410",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Bloomberg_Rossiya_zanimaet_vtoroe_mesto_srediinostrannykh_postavshhikov_nefti_vSSHA--637606b322bdf039b033088ca56a7a79?lang=ru&from=rub_portal&wan=1&stid=18Sso0QpzEpR4lKwK9xA&t=1628145859&persistent_id=154947801"
                            },
                            {
                                "agency": {
                                    "id": 1048,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                                    "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                                },
                                "title": "\u041c\u0438\u043d\u044d\u043a\u043e\u043d\u043e\u043c\u0438\u043a\u0438 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0438\u043b\u043e \u0443\u0432\u0435\u043b\u0438\u0447\u0438\u0442\u044c \u0433\u043e\u0441\u0440\u0430\u0441\u0445\u043e\u0434\u044b \u043d\u0430\u00a01,8 \u0442\u0440\u043b\u043d \u0440\u0443\u0431. \u043d\u0430\u00a0\u0442\u0440\u0438 \u0433\u043e\u0434\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Minehkonomiki_predlozhilo_uvelichit_gosraskhody_na18_trln_rub._natri_goda--8732cb654be6da615b9d2af6989459f1?lang=ru&from=rub_portal&wan=1&stid=cs6O4jx5jYMwNS4fcPZw&t=1628145859&persistent_id=154958272"
                            },
                            {
                                "agency": {
                                    "id": 1048,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                                    "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                                },
                                "title": "\u00ab\u042f\u043d\u0434\u0435\u043a\u0441\u00bb \u0437\u0430\u043a\u0440\u044b\u043b \u043a\u0440\u0443\u043f\u043d\u0435\u0439\u0448\u0443\u044e \u0441\u0434\u0435\u043b\u043a\u0443 \u0433\u043e\u0434\u0430 \u043d\u0430\u00a0\u0440\u044b\u043d\u043a\u0435 \u043e\u0444\u0438\u0441\u043e\u0432",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/YAndeks_zakryl_krupnejshuyu_sdelku_goda_narynke_ofisov--48872905acd53ef81f2cb0123e2184bf?lang=ru&from=rub_portal&wan=1&stid=X_wYKcQKF8E2GBan&t=1628145859&persistent_id=154968873"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/business"
                    },
                    {
                        "alias": "world",
                        "name": "\u0412 \u043c\u0438\u0440\u0435",
                        "stories": [
                            {
                                "agency": {
                                    "id": 1063,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1063-1478692902330-square",
                                    "name": "\u0420\u043e\u0441\u0431\u0430\u043b\u0442"
                                },
                                "title": "Bloomberg: \u041f\u0440\u043e\u0442\u0438\u0432 \u0448\u0442\u0430\u043c\u043c\u0430 \u00ab\u0434\u0435\u043b\u044c\u0442\u0430\u00bb \u043c\u043e\u0433\u0443\u0442 \u043f\u043e\u0442\u0440\u0435\u0431\u043e\u0432\u0430\u0442\u044c\u0441\u044f \u043d\u043e\u0432\u044b\u0435 \u0432\u0430\u043a\u0446\u0438\u043d\u044b",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Bloomberg_Protiv_shtamma_delta_mogut_potrebovatsya_novye_vakciny--3cf4fda26de9ac7a7d08aa339982a3f7?lang=ru&from=rub_portal&wan=1&stid=7PPuqXiouUro2nLsoSpz&t=1628145859&persistent_id=154952716"
                            },
                            {
                                "agency": {
                                    "id": 254156038,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/41096/254156038-1557303731847-square",
                                    "name": "News.ru"
                                },
                                "title": "\u042f\u043f\u043e\u043d\u0438\u0438 \u043f\u043e\u0441\u043e\u0432\u0435\u0442\u043e\u0432\u0430\u043b\u0438 \u0438\u0437\u0443\u0447\u0438\u0442\u044c \u0440\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0438\u0435 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043f\u043e\u00a0\u041a\u0443\u0440\u0438\u043b\u0430\u043c",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/YAponii_posovetovali_izuchit_rossijskie_predlozheniya_poKurilam--d38d37c4ac00292682c10e05da44b4ec?lang=ru&from=rub_portal&wan=1&stid=b_uPMVOuVkbiOyPD&t=1628145859&persistent_id=154905395"
                            },
                            {
                                "agency": {
                                    "id": 1040,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1040-1478692902361-square",
                                    "name": "\u0413\u0430\u0437\u0435\u0442\u0430.Ru"
                                },
                                "title": "\u0412\u00a0\u041a\u0438\u0442\u0430\u0435 \u0441\u043e\u0437\u0434\u0430\u043b\u0438 \u043b\u0430\u043c\u043f\u0443 \u0434\u043b\u044f\u00a0\u0434\u0435\u0437\u0438\u043d\u0444\u0435\u043a\u0446\u0438\u0438 \u043e\u0442\u00a0COVID-19 \u0441\u00a0\u044d\u0444\u0444\u0435\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c\u044e 99,99%",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/VKitae_sozdali_lampu_dlyadezinfekcii_otCOVID-19_sehffektivnostyu_9999--112b0e453ac6903a7c8f18861acb4ade?lang=ru&from=rub_portal&wan=1&stid=svEqUj2f1ljqwBsNw-rv&t=1628145859&persistent_id=154960914"
                            },
                            {
                                "agency": {
                                    "id": 1002,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                                    "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                                },
                                "title": "\u041c\u044d\u0440 \u0422\u043e\u043a\u0430\u0442: \u0442\u0435\u043f\u043b\u043e\u0432\u0430\u044f \u044d\u043b\u0435\u043a\u0442\u0440\u043e\u0441\u0442\u0430\u043d\u0446\u0438\u044f \u043d\u0430\u00a0\u044e\u0433\u043e-\u0437\u0430\u043f\u0430\u0434\u0435 \u0422\u0443\u0440\u0446\u0438\u0438 \u0437\u0430\u0433\u043e\u0440\u0435\u043b\u0430\u0441\u044c \u0438\u0437-\u0437\u0430\u00a0\u043b\u0435\u0441\u043d\u043e\u0433\u043e \u043f\u043e\u0436\u0430\u0440\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Mehr_Tokat_teplovaya_ehlektrostanciya_nayugo-zapade_Turcii_zagorelas_iz-zalesnogo_pozhara--5e8a3696964eaf6f2823d90d8d08f95f?lang=ru&from=rub_portal&wan=1&stid=nsbBLLL6oaXnmWt3ZT_3&t=1628145859&persistent_id=154944165"
                            },
                            {
                                "agency": {
                                    "id": 1047,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1047-1478692902215-square",
                                    "name": "Lenta.ru"
                                },
                                "title": "\u0420\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u0438\u0439 \u0430\u0442\u043e\u043c\u043d\u044b\u0439 \u043a\u0440\u0435\u0439\u0441\u0435\u0440 \u043f\u043e\u0442\u0435\u0440\u044f\u043b \u0445\u043e\u0434 \u0443\u00a0\u0431\u0435\u0440\u0435\u0433\u043e\u0432 \u0414\u0430\u043d\u0438\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Rossijskij_atomnyj_krejser_poteryal_khod_uberegov_Danii--a04788abec354e466fb8f6f8daba4faf?lang=ru&from=rub_portal&wan=1&stid=wE8k9cQjO80u&t=1628145859&persistent_id=154920290"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/world"
                    },
                    {
                        "alias": "sport",
                        "name": "\u0421\u043f\u043e\u0440\u0442",
                        "stories": [
                            {
                                "agency": {
                                    "id": 2220,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/2220-1478692942720-square",
                                    "name": "\u0427\u0435\u043c\u043f\u0438\u043e\u043d\u0430\u0442"
                                },
                                "title": "\u041c\u0443\u0436\u0441\u043a\u0430\u044f \u0441\u0431\u043e\u0440\u043d\u0430\u044f \u0420\u043e\u0441\u0441\u0438\u0438 \u043f\u043e\u00a0\u0432\u043e\u043b\u0435\u0439\u0431\u043e\u043b\u0443 \u0432\u044b\u0448\u043b\u0430 \u0432\u00a0\u0444\u0438\u043d\u0430\u043b \u041e\u043b\u0438\u043c\u043f\u0438\u0430\u0434\u044b-2020, \u043f\u043e\u0431\u0435\u0434\u0438\u0432 \u0411\u0440\u0430\u0437\u0438\u043b\u0438\u044e",
                                "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Muzhskaya_sbornaya_Rossii_povolejbolu_vyshla_vfinal_Olimpiady-2020_pobediv_Braziliyu--a54090b9b7695ac2cfe9e9f013e119eb?lang=ru&from=rub_portal&wan=1&stid=HS7kkMeNNNDkZ9EXqgbm&t=1628145859&persistent_id=154968745"
                            },
                            {
                                "agency": {
                                    "id": 1002,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                                    "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                                },
                                "title": "\u00ab\u0421\u043f\u0430\u0440\u0442\u0430\u043a\u00bb \u0434\u043e\u043c\u0430 \u043f\u0440\u043e\u0438\u0433\u0440\u0430\u043b \u00ab\u0411\u0435\u043d\u0444\u0438\u043a\u0435\u00bb \u0432\u00a0\u043f\u0435\u0440\u0432\u043e\u043c \u043c\u0430\u0442\u0447\u0435 \u043a\u0432\u0430\u043b\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438 \u041b\u0438\u0433\u0438 \u0447\u0435\u043c\u043f\u0438\u043e\u043d\u043e\u0432",
                                "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Spartak_doma_proigral_Benfike_vpervom_matche_kvalifikacii_Ligi_chempionov--2ebc13c4742a2b31134737e252b5681b?lang=ru&from=rub_portal&wan=1&stid=Vs3I2Qo6Bs8t7bSqYFgR&t=1628145859&persistent_id=154944234"
                            },
                            {
                                "agency": {
                                    "id": 2220,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/2220-1478692942720-square",
                                    "name": "\u0427\u0435\u043c\u043f\u0438\u043e\u043d\u0430\u0442"
                                },
                                "title": "\u0421\u0432\u0435\u0442\u043b\u0430\u043d\u0430 \u0420\u043e\u043c\u0430\u0448\u0438\u043d\u0430 \u0441\u0442\u0430\u043b\u0430 \u043f\u0435\u0440\u0432\u043e\u0439 \u0432\u00a0\u0438\u0441\u0442\u043e\u0440\u0438\u0438 6-\u043a\u0440\u0430\u0442\u043d\u043e\u0439 \u0447\u0435\u043c\u043f\u0438\u043e\u043d\u043a\u043e\u0439 \u041e\u0418 \u043f\u043e\u00a0\u0441\u0438\u043d\u0445\u0440\u043e\u043d\u043d\u043e\u043c\u0443 \u043f\u043b\u0430\u0432\u0430\u043d\u0438\u044e",
                                "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Svetlana_Romashina_stala_pervoj_vistorii_6-kratnoj_chempionkoj_OI_posinkhronnomu_plavaniyu--32d2c2e02d07c0210854417e1f575eba?lang=ru&from=rub_portal&wan=1&stid=8TfNbdt9GKBWU8MXuNOZ&t=1628145859&persistent_id=154910469"
                            },
                            {
                                "agency": {
                                    "id": 3678,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/61287/3678-1482247329455-square",
                                    "name": "\u0421\u043f\u043e\u0440\u0442 \u0434\u0435\u043d\u044c \u0437\u0430 \u0434\u043d\u0435\u043c"
                                },
                                "title": "\u0412\u00a0\u0411\u0440\u0430\u0437\u0438\u043b\u0438\u0438 \u0441\u043e\u043e\u0431\u0449\u0438\u043b\u0438, \u0441\u043a\u043e\u043b\u044c\u043a\u043e \u00ab\u0417\u0435\u043d\u0438\u0442\u00bb \u0437\u0430\u043f\u043b\u0430\u0442\u0438\u0442 \u0437\u0430\u00a0\u043f\u0435\u0440\u0435\u0445\u043e\u0434 \u041a\u043b\u0430\u0443\u0434\u0438\u043d\u044c\u043e",
                                "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/VBrazilii_soobshhili_skolko_Zenit_zaplatit_zaperekhod_Klaudino--f93b17278240836f408327d6c26fbce0?lang=ru&from=rub_portal&wan=1&stid=-1BbNb9lU0bJphaePz7C&t=1628145859&persistent_id=154922273"
                            },
                            {
                                "agency": {
                                    "id": 254147205,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/117671/254147205-1478693952904-square",
                                    "name": "\u041c\u0430\u0442\u0447 \u0422\u0412"
                                },
                                "title": "\u0414\u0435\u0441\u044f\u0442\u0438\u0431\u043e\u0440\u0435\u0446 \u0428\u043a\u0443\u0440\u0435\u043d\u0435\u0432 \u043d\u0430\u00a0\u041e\u0418 \u0432\u00a0\u0422\u043e\u043a\u0438\u043e \u043f\u043e\u043a\u0430\u0437\u0430\u043b \u043b\u0443\u0447\u0448\u0438\u0439 \u043b\u0438\u0447\u043d\u044b\u0439 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u0441\u0435\u0437\u043e\u043d\u0430 \u0432\u00a0\u043c\u0435\u0442\u0430\u043d\u0438\u0438 \u0434\u0438\u0441\u043a\u0430",
                                "url": "https://yandexsport.stable.priemka.yandex.ru/sport/story/Desyatiborec_SHkurenev_naOI_vTokio_pokazal_luchshij_lichnyj_rezultat_sezona_vmetanii_diska--2d4e0483158c27bfbd36e5da9ab8c19a?lang=ru&from=rub_portal&wan=1&stid=ylslGMfyelxdzfiQuNDj&t=1628145859&persistent_id=154871375"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/sport"
                    },
                    {
                        "alias": "incident",
                        "name": "\u041f\u0440\u043e\u0438\u0441\u0448\u0435\u0441\u0442\u0432\u0438\u044f",
                        "stories": [
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u0412\u00a0\u041c\u043e\u0441\u043a\u0432\u0435 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d \u043c\u0443\u0436\u0447\u0438\u043d\u0430, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u0432\u044b\u0431\u0440\u043e\u0441\u0438\u043b \u0438\u0437\u00a0\u043e\u043a\u043d\u0430 \u0434\u043e\u043c\u0430 \u0441\u0432\u043e\u0435\u0433\u043e \u0441\u044b\u043d\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/VMoskve_zaderzhan_muzhchina_kotoryj_vybrosil_izokna_doma_svoego_syna--70d3ea69827304bc7a8dcb5208a99c14?lang=ru&from=rub_portal&wan=1&stid=ag9NiX1-h-ImdQqGYu1S&t=1628145859&persistent_id=154945748"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u0421\u041a \u0432\u044b\u044f\u0432\u0438\u043b \u043d\u043e\u0432\u044b\u0435 \u044d\u043f\u0438\u0437\u043e\u0434\u044b \u043f\u043e\u00a0\u0434\u0435\u043b\u0443 \u0437\u0430\u0434\u0435\u0440\u0436\u0430\u043d\u043d\u043e\u0433\u043e \u0432\u00a0\u041f\u043e\u0434\u043c\u043e\u0441\u043a\u043e\u0432\u044c\u0435 \u0437\u0430\u00a0\u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u043a\u0443 \u043a\u00a0\u0442\u0435\u0440\u0430\u043a\u0442\u0443",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/SK_vyyavil_novye_ehpizody_podelu_zaderzhannogo_vPodmoskove_zapodgotovku_kteraktu--d1b22d5e2739a585dc5c92fc6a7bbccd?lang=ru&from=rub_portal&wan=1&stid=7036yfHtKkbWIkmHqH_P&t=1628145859&persistent_id=154970756"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u0421\u0430\u043c\u043e\u043b\u0435\u0442 \u0430\u0432\u0438\u0430\u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438 \u00ab\u0420\u043e\u0441\u0441\u0438\u044f\u00bb \u0432\u0435\u0440\u043d\u0443\u043b\u0441\u044f \u0432\u00a0\u0430\u044d\u0440\u043e\u043f\u043e\u0440\u0442 \u0427\u0435\u043b\u044f\u0431\u0438\u043d\u0441\u043a\u0430 \u043f\u043e\u00a0\u0442\u0435\u0445\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u043c \u043f\u0440\u0438\u0447\u0438\u043d\u0430\u043c",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Samolet_aviakompanii_Rossiya_vernulsya_vaehroport_CHelyabinska_potekhnicheskim_prichinam--15a361a659b00055415d3cc733fa02c8?lang=ru&from=rub_portal&wan=1&stid=NbKgVya6OBJPVBDmbkZd&t=1628145859&persistent_id=154969933"
                            },
                            {
                                "agency": {
                                    "id": 1002,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/1002-1544074003449-square",
                                    "name": "\u0420\u0418\u0410 \u041d\u043e\u0432\u043e\u0441\u0442\u0438"
                                },
                                "title": "\u0420\u043e\u0441\u0442\u0435\u0445 \u043e\u043f\u0440\u043e\u0432\u0435\u0440\u0433 \u0441\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u044f \u043e\u00a0\u043f\u043e\u0432\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u0438 \u0434\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044f \u0411\u0435-200 \u043f\u0440\u0438\u00a0\u0442\u0443\u0448\u0435\u043d\u0438\u0438 \u043f\u043e\u0436\u0430\u0440\u043e\u0432 \u0432\u00a0\u0413\u0440\u0435\u0446\u0438\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Rostekh_oproverg_soobshheniya_opovrezhdenii_dvigatelya_Be-200_pritushenii_pozharov_vGrecii--c8dd4588551bd88dac0bc6eeb0136ee2?lang=ru&from=rub_portal&wan=1&stid=mUv_XFfPDotOfwL25E-q&t=1628145859&persistent_id=154933849"
                            },
                            {
                                "agency": {
                                    "id": 1551,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square",
                                    "name": "\u0422\u0410\u0421\u0421"
                                },
                                "title": "\u0417\u0430\u043a\u043b\u044e\u0447\u0435\u043d\u043d\u043e\u0433\u043e \u043d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a\u043e\u0439 \u043a\u043e\u043b\u043e\u043d\u0438\u0438 \u043e\u0441\u0443\u0434\u0438\u043b\u0438 \u043d\u0430\u00a0\u0442\u0440\u0438 \u0433\u043e\u0434\u0430 \u0437\u0430\u00a0\u043f\u0440\u043e\u043f\u0430\u0433\u0430\u043d\u0434\u0443 \u0442\u0435\u0440\u0440\u043e\u0440\u0438\u0437\u043c\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Zaklyuchennogo_novosibirskoj_kolonii_osudili_natri_goda_zapropagandu_terrorizma--51989b79c65de78d18ed39aa55f8ad43?lang=ru&from=rub_portal&wan=1&stid=FF0WwgpVXt6uuUeMHoAh&t=1628145859&persistent_id=154964387"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/incident"
                    },
                    {
                        "alias": "culture",
                        "name": "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u0430",
                        "stories": [
                            {
                                "agency": {
                                    "id": 254154182,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254154182-1550152741834-square",
                                    "name": "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u043e\u043c\u0430\u043d\u0438\u044f"
                                },
                                "title": "\u0412\u044b\u0448\u0435\u043b \u0442\u0440\u0435\u0439\u043b\u0435\u0440 \u0444\u0438\u043b\u044c\u043c\u0430 \u00ab\u0417\u043e\u043b\u0443\u0448\u043a\u0430\u00bb \u0441\u00a0\u041a\u0430\u043c\u0438\u043b\u043e\u0439 \u041a\u0430\u0431\u0435\u0439\u043e",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Vyshel_trejler_filma_Zolushka_sKamiloj_Kabejo--0023b46f6177d0d99ddb31900111464f?lang=ru&from=rub_portal&wan=1&stid=nGkL78SMB0lZGTRwNUxH&t=1628145859&persistent_id=154858258"
                            },
                            {
                                "agency": {
                                    "id": 254154182,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254154182-1550152741834-square",
                                    "name": "\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u043e\u043c\u0430\u043d\u0438\u044f"
                                },
                                "title": "\u0412\u044b\u0448\u0435\u043b \u0442\u0440\u0435\u0439\u043b\u0435\u0440 \u044d\u0440\u043e\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0442\u0440\u0438\u043b\u043b\u0435\u0440\u0430 \u00ab\u0421\u043e\u0432\u0440\u0438 \u043c\u043d\u0435 \u043f\u0440\u0430\u0432\u0434\u0443\u00bb \u0441\u00a0\u041f\u0440\u0438\u043b\u0443\u0447\u043d\u044b\u043c",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Vyshel_trejler_ehroticheskogo_trillera_Sovri_mne_pravdu_sPriluchnym--f9e599663d338e5e26ef3c043785470a?lang=ru&from=rub_portal&wan=1&stid=SwyZ4ZbsNUCQYOBg5cEG&t=1628145859&persistent_id=154906432"
                            },
                            {
                                "agency": {
                                    "id": 1048,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                                    "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                                },
                                "title": "\u0412\u044b\u0445\u043e\u0434 \u0441\u0435\u0440\u0438\u0430\u043b\u0430 \u00ab\u0412\u043b\u0430\u0441\u0442\u0435\u043b\u0438\u043d \u043a\u043e\u043b\u0435\u0446\u00bb \u0437\u0430\u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u0430\u043d \u043d\u0430\u00a0\u0441\u0435\u043d\u0442\u044f\u0431\u0440\u044c 2022 \u0433\u043e\u0434\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Vykhod_seriala_Vlastelin_kolec_zaplanirovan_nasentyabr_2022_goda--0fa97c6fd9c3b12b0d6e4649efbabf29?lang=ru&from=rub_portal&wan=1&stid=gy-2fLc1SMff4WxIUNEg&t=1628145859&persistent_id=154717596"
                            },
                            {
                                "agency": {
                                    "id": 254165984,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/254165984-1602694686.929395-square",
                                    "name": "FBM.ru"
                                },
                                "title": "\u0411\u0440\u0438\u0442\u0430\u043d\u0446\u044b \u0441\u0447\u0438\u0442\u0430\u044e\u0442, \u0447\u0442\u043e \u0441\u0438\u043a\u0432\u0435\u043b \u00ab\u041e\u0442\u0440\u044f\u0434\u0430 \u0441\u0430\u043c\u043e\u0443\u0431\u0438\u0439\u0446\u00bb \u0438\u043c\u0435\u0435\u0442 \u043d\u0435\u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0439 \u0440\u0435\u0439\u0442\u0438\u043d\u0433",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Britancy_schitayut_chto_sikvel_Otryada_samoubijc_imeet_nesootvetstvuyushhij_rejting--e9bf7e0bc0141adaf21a89e21ec2529a?lang=ru&from=rub_portal&wan=1&stid=2af3d7AmcylhBA8z4SrK&t=1628145859&persistent_id=154950008"
                            },
                            {
                                "agency": {
                                    "id": 254091134,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/254091134-1580903043896-square",
                                    "name": "\u0413\u0430\u0437\u0435\u0442\u0430 \u041a\u0443\u043b\u044c\u0442\u0443\u0440\u0430"
                                },
                                "title": "\u0411\u0440\u0430\u0442\u044c\u044f \u041a\u043e\u044d\u043d \u043f\u0435\u0440\u0435\u0441\u0442\u0430\u043d\u0443\u0442 \u0432\u043c\u0435\u0441\u0442\u0435 \u0440\u0430\u0431\u043e\u0442\u0430\u0442\u044c \u043d\u0430\u0434\u00a0\u0444\u0438\u043b\u044c\u043c\u0430\u043c\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Bratya_Koehn_perestanut_vmeste_rabotat_nadfilmami--13cf0ac88e8843a70043ee747c96517c?lang=ru&from=rub_portal&wan=1&stid=2j-RO0n6lgtjseSkxQfq&t=1628145859&persistent_id=154899109"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/culture"
                    },
                    {
                        "alias": "computers",
                        "name": "\u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438",
                        "stories": [
                            {
                                "agency": {
                                    "id": 254152790,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/33291/254152790-1612443048.96772-square",
                                    "name": "CyberSport.ru"
                                },
                                "title": "\u041f\u0440\u043e\u0434\u0430\u0436\u0438 Mass Effect Legendary Edition \u043f\u0440\u0435\u0432\u0437\u043e\u0448\u043b\u0438 \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u044f EA",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Prodazhi_Mass_Effect_Legendary_Edition_prevzoshli_ozhidaniya_EA--97c705fd6603464d4a72ecd22a3b5f62?lang=ru&from=rub_portal&wan=1&stid=QExTAtkuNUE8&t=1628145859&persistent_id=154953220"
                            },
                            {
                                "agency": {
                                    "id": 254165984,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/254165984-1602694686.929395-square",
                                    "name": "FBM.ru"
                                },
                                "title": "Windows 10 \u0441\u00a0\u0430\u0432\u0433\u0443\u0441\u0442\u0430 \u0431\u0443\u0434\u0435\u0442 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043d\u0435\u0436\u0435\u043b\u0430\u0442\u0435\u043b\u044c\u043d\u043e\u0435 \u041f\u041e",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Windows_10_savgusta_budet_avtomaticheski_blokirovat_nezhelatelnoe_PO--9cf836cf777defa70f5a48b31b62d431?lang=ru&from=rub_portal&wan=1&stid=pVQzVH2xyBFOH8aBeeUA&t=1628145859&persistent_id=154805955"
                            },
                            {
                                "agency": {
                                    "id": 1556,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/62808/1556-1518502037969-square",
                                    "name": "iXBT.com"
                                },
                                "title": "Xiaomi \u043f\u043e\u043a\u0430\u0437\u0430\u043b\u0430 6 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u043e\u0432 \u0434\u0438\u0437\u0430\u0439\u043d\u0430 \u0441\u043c\u0430\u0440\u0442\u0444\u043e\u043d\u0430 Xiaomi Mi Mix 4",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Xiaomi_pokazala_6_variantov_dizajna_smartfona_Xiaomi_Mi_Mix_4--e4251795d16d90289a677611f484f4be?lang=ru&from=rub_portal&wan=1&stid=dMzqS7AcSx1f&t=1628145859&persistent_id=154972777"
                            },
                            {
                                "agency": {
                                    "id": 1569,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/1569-1544162285015-square",
                                    "name": "\u041f\u0440\u043e\u0444\u0438\u043b\u044c"
                                },
                                "title": "\u041a\u0438\u0431\u0435\u0440\u0430\u0442\u0435\u043b\u044c\u0435 \u0434\u043b\u044f\u00a0\u0441\u0430\u043c\u043e\u0441\u0442\u043e\u044f\u0442\u0435\u043b\u044c\u043d\u043e\u0433\u043e \u0438 \u0443\u0434\u0430\u043b\u0435\u043d\u043d\u043e\u0433\u043e \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u0430 \u043e\u0434\u0435\u0436\u0434\u044b \u043f\u043e\u044f\u0432\u0438\u0442\u0441\u044f \u0432\u00a0\u0420\u043e\u0441\u0441\u0438\u0438",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Kiberatele_dlyasamostoyatelnogo_i_udalennogo_proizvodstva_odezhdy_poyavitsya_vRossii--82315f042af92f5e313ca702853a9720?lang=ru&from=rub_portal&wan=1&stid=xw4IVk-MskaQ&t=1628145859&persistent_id=154959583"
                            },
                            {
                                "agency": {
                                    "id": 1670,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/1670-1551172901405-square",
                                    "name": "Ferra"
                                },
                                "title": "Sony \u0434\u043e\u0431\u0430\u0432\u0438\u0442 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0443 \u0432\u0438\u0440\u0442\u0443\u0430\u043b\u044c\u043d\u043e\u0439 \u0440\u0435\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u0438 \u0432\u043e \u0432\u0441\u0435 \u00ab\u0431\u043e\u043b\u044c\u0448\u0438\u0435\u00bb \u0438\u0433\u0440\u044b \u0434\u043b\u044f\u00a0PlayStation 5",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Sony_dobavit_podderzhku_virtualnoj_realnosti_vo_vse_bolshie_igry_dlyaPlayStation_5--8205c13561456d1ace5bd850f196bdd4?lang=ru&from=rub_portal&wan=1&stid=sSopPteIze4tsZZtPlEd&t=1628145859&persistent_id=154626977"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/computers"
                    },
                    {
                        "alias": "science",
                        "name": "\u041d\u0430\u0443\u043a\u0430",
                        "stories": [
                            {
                                "agency": {
                                    "id": 254120975,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254120975-1550183881383-square",
                                    "name": "SMINEWS \u0432 \u041f\u043e\u0434\u043e\u043b\u044c\u0441\u043a\u0435"
                                },
                                "title": "NG: \u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 \u043a\u0438\u0441\u043b\u043e\u0440\u043e\u0434\u0430 \u0432\u00a0\u0430\u0442\u043c\u043e\u0441\u0444\u0435\u0440\u0435 \u0417\u0435\u043c\u043b\u0438 \u0441\u0432\u044f\u0437\u0430\u043b\u0438 \u0441\u00a0\u0437\u0430\u043c\u0435\u0434\u043b\u0435\u043d\u0438\u0435\u043c \u0432\u0440\u0430\u0449\u0435\u043d\u0438\u044f",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/NG_Obrazovanie_kisloroda_vatmosfere_Zemli_svyazali_szamedleniem_vrashheniya--20c86eb5757fc4017de6c06c37777c16?lang=ru&from=rub_portal&wan=1&stid=J1shfwAwcnpbCW4s5FEl&t=1628145859&persistent_id=154714656"
                            },
                            {
                                "agency": {
                                    "id": 254133475,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/254133475-1478693911264-square",
                                    "name": "\u041c\u0435\u0434\u0438\u0430\u041f\u043e\u0442\u043e\u043a"
                                },
                                "title": "\u0413\u043e\u0440\u043e\u0434 \u0438\u043d\u043a\u043e\u0432 \u041c\u0430\u0447\u0443-\u041f\u0438\u043a\u0447\u0443 \u043e\u043a\u0430\u0437\u0430\u043b\u0441\u044f \u0434\u0440\u0435\u0432\u043d\u0435\u0435, \u0447\u0435\u043c \u0441\u0447\u0438\u0442\u0430\u043b\u043e\u0441\u044c \u0440\u0430\u043d\u0435\u0435",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Gorod_inkov_Machu-Pikchu_okazalsya_drevnee_chem_schitalos_ranee--a87faab6ea6daa542671b525fb6c3fab?lang=ru&from=rub_portal&wan=1&stid=QPUd6boOUjDqU3VMv72x&t=1628145859&persistent_id=154868664"
                            },
                            {
                                "agency": {
                                    "id": 254114979,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/135513/254114979-1478693761853-square",
                                    "name": "\u0424\u0410\u041d"
                                },
                                "title": "\u041d\u0435\u0430\u043d\u0434\u0435\u0440\u0442\u0430\u043b\u044c\u0446\u044b \u043e\u0441\u0442\u0430\u0432\u0438\u043b\u0438 \u0440\u0438\u0441\u0443\u043d\u043a\u0438 \u043d\u0430\u00a0\u0441\u0442\u0430\u043b\u0430\u0433\u043c\u0438\u0442\u0430\u0445 \u0432\u00a0\u0418\u0441\u043f\u0430\u043d\u0438\u0438 60 \u0442\u044b\u0441\u044f\u0447 \u043b\u0435\u0442 \u043d\u0430\u0437\u0430\u0434",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Neandertalcy_ostavili_risunki_nastalagmitakh_vIspanii_60_tysyach_let_nazad--3c091f1065b86845e0f777db4eb487e3?lang=ru&from=rub_portal&wan=1&stid=sQf-IV3o-C4Ko5pMUEyR&t=1628145859&persistent_id=154719914"
                            },
                            {
                                "agency": {
                                    "id": 254165984,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/966506/254165984-1602694686.929395-square",
                                    "name": "FBM.ru"
                                },
                                "title": "\u0423\u0447\u0435\u043d\u044b\u0435 \u041a\u0430\u043d\u0430\u0434\u044b \u0432\u044b\u044f\u0432\u0438\u043b\u0438 \u043f\u0440\u0438\u0447\u0438\u043d\u0443 \u043e\u043f\u0430\u0441\u043d\u044b\u0445 \u043e\u0441\u043b\u043e\u0436\u043d\u0435\u043d\u0438\u0439 \u043f\u0440\u0438\u00a0\u043a\u043e\u0440\u043e\u043d\u0430\u0432\u0438\u0440\u0443\u0441\u0435 COVID-19",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Uchenye_Kanady_vyyavili_prichinu_opasnykh_oslozhnenij_prikoronaviruse_COVID-19--c2d729bba24f2f05e69155682a00a5c7?lang=ru&from=rub_portal&wan=1&stid=gYmEV9MvdV0HRooP&t=1628145859&persistent_id=154963185"
                            },
                            {
                                "agency": {
                                    "id": 254162796,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/50744/254162796-1570028445907-square",
                                    "name": "\u0422\u0410\u0421\u0421 \u041d\u0430\u0443\u043a\u0430 "
                                },
                                "title": "\u0412\u00a0\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a\u0435 \u0441\u043e\u0437\u0434\u0430\u043b\u0438 \u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u044e \u0434\u043b\u044f\u00a0\u043d\u0435\u0444\u0442\u044f\u043d\u0438\u043a\u043e\u0432, \u0441\u043d\u0438\u0436\u0430\u044e\u0449\u0443\u044e \u0432\u044b\u0431\u0440\u043e\u0441\u044b \u0441\u0435\u0440\u043e\u0432\u043e\u0434\u043e\u0440\u043e\u0434\u0430 \u0432\u00a0100 \u0440\u0430\u0437",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/VNovosibirske_sozdali_tekhnologiyu_dlyaneftyanikov_snizhayushhuyu_vybrosy_serovodoroda_v100_raz--70251cacb630e97b47b2ae9e7ef93dbf?lang=ru&from=rub_portal&wan=1&stid=IydGK2tC&t=1628145859&persistent_id=154966973"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/science"
                    },
                    {
                        "alias": "auto",
                        "name": "\u0410\u0432\u0442\u043e",
                        "stories": [
                            {
                                "agency": {
                                    "id": 1048,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692902313-square",
                                    "name": "\u041a\u043e\u043c\u043c\u0435\u0440\u0441\u0430\u043d\u0442\u044a"
                                },
                                "title": "\u0421\u0440\u0435\u0434\u043d\u0435\u0432\u0437\u0432\u0435\u0448\u0435\u043d\u043d\u0430\u044f \u0446\u0435\u043d\u0430 \u043d\u043e\u0432\u043e\u0433\u043e \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044f \u0432\u00a0\u043f\u0435\u0440\u0432\u043e\u043c \u043f\u043e\u043b\u0443\u0433\u043e\u0434\u0438\u0438 \u0432\u044b\u0440\u043e\u0441\u043b\u0430 \u043d\u0430\u00a012,5%",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Srednevzveshennaya_cena_novogo_avtomobilya_vpervom_polugodii_vyrosla_na125--1ee06f09f8b5af6cfe0a64e707b654b7?lang=ru&from=rub_portal&wan=1&stid=2uI559qNa_CTDLwwWfs7&t=1628145859&persistent_id=154882986"
                            },
                            {
                                "agency": {
                                    "id": 6816,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/28627/6816-1478693057271-square",
                                    "name": "\u0410\u0432\u0442\u043e\u0441\u0442\u0430\u0442"
                                },
                                "title": "\u0412\u00a0\u0427\u0435\u0445\u0438\u0438 \u043d\u0430\u0447\u0430\u043b\u0441\u044f \u0432\u044b\u043f\u0443\u0441\u043a \u044d\u043b\u0435\u043a\u0442\u0440\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0423\u0410\u0417 \u00ab\u0425\u0430\u043d\u0442\u0435\u0440\u00bb",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/VCHekhii_nachalsya_vypusk_ehlektricheskogo_UAZ_KHanter--0853d9510dfb38be54dc3b0815255fc2?lang=ru&from=rub_portal&wan=1&stid=AOewEKcrNyDy7o1c-Ow7&t=1628145859&persistent_id=154728455"
                            },
                            {
                                "agency": {
                                    "id": 254101760,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/62808/254101760-1478693655341-square",
                                    "name": "32CARS.ru"
                                },
                                "title": "\u0410\u0432\u0442\u043e\u0431\u0440\u0435\u043d\u0434 Toyota \u043f\u0440\u0435\u0434\u0441\u0442\u0430\u0432\u0438\u043b\u0430 \u044e\u0431\u0438\u043b\u0435\u0439\u043d\u0443\u044e \u0432\u0435\u0440\u0441\u0438\u044e Land Cruiser 70",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Avtobrend_Toyota_predstavila_yubilejnuyu_versiyu_Land_Cruiser_70--eb34740f942185cb9b7db40818395d99?lang=ru&from=rub_portal&wan=1&stid=Go2X8w0_XyxF9bJcBiSZ&t=1628145859&persistent_id=154907549"
                            },
                            {
                                "agency": {
                                    "id": 254167762,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/786982/254167762-1616559957.67102-square",
                                    "name": "\u0413\u0434\u0435 \u0438 \u0447\u0442\u043e"
                                },
                                "title": "\u00ab\u041b\u0410\u0414\u0410 \u0426\u0435\u043d\u0442\u0440 \u0427\u0435\u0440\u0435\u043f\u043e\u0432\u0435\u0446\u00bb \u0440\u0430\u0441\u043a\u0440\u044b\u043b \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043d\u043e\u0433\u043e \u0432\u043d\u0435\u0434\u043e\u0440\u043e\u0436\u043d\u0438\u043a\u0430 Lada Niva Bronto",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/LADA_Centr_CHerepovec_raskryl_stoimost_obnovlennogo_vnedorozhnika_Lada_Niva_Bronto--a5c9fd233e05ac4b45044891e802f77c?lang=ru&from=rub_portal&wan=1&stid=8T39oFh7fDtWbyplvphP&t=1628145859&persistent_id=154909594"
                            },
                            {
                                "agency": {
                                    "id": 254054748,
                                    "logo": "//avatars.mds.yandex.net/get-ynews-logo/56838/254054748-1478693377904-square",
                                    "name": "\u0410\u0432\u0442\u043e\u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u0434\u043d\u044f"
                                },
                                "title": "\u041f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e \u0440\u043e\u0441\u0441\u0438\u0439\u0441\u043a\u043e\u0433\u043e \u044d\u043b\u0435\u043a\u0442\u0440\u043e\u043a\u0430\u0440\u0430 Zetta \u043d\u0430\u0447\u043d\u0435\u0442\u0441\u044f \u0434\u043e\u00a0\u043a\u043e\u043d\u0446\u0430 2021 \u0433\u043e\u0434\u0430",
                                "url": "https://news.stable.priemka.yandex.ru/news/story/Proizvodstvo_rossijskogo_ehlektrokara_Zetta_nachnetsya_dokonca_2021_goda--5065b2fbf0c6dfa6137da257487fa9f4?lang=ru&from=rub_portal&wan=1&stid=eZLbwyEGGofP03ZnVhT9&t=1628145859&persistent_id=154675444"
                            }
                        ],
                        "url": "https://yandex.ru/news/rubric/auto"
                    }
                ],
                "iter_time": 1628145859,
                "reqid": "1628146427307528-760379911749557946200362-news-sink-app-host-yp-1-NEWS-NEWS_API_TOPS_EXPORT",
                "state_version": "news-prod-indexers-2-3.vla.yp-c.yandex.net:1628145859000000:1628146090225561:0:d294.4f294.4",
                "type": "newsd_response",
                "disclaimer_disallow":1,
                "favorite_smi_count":4,
                "form_key":"u3d4a228bd04263c75163991a6ab30272"
            }`,
			expected: fields{
				IsFavorite:         false,
				DisclaimerDisallow: 1,
				FormKey:            "u3d4a228bd04263c75163991a6ab30272",
				ExtraStories:       "",
			},
			isError: false,
			// isEmpty: false,
		},
		{
			name: "Real V3 Empty Data",
			content: `{
                "data": [],
                "iter_time": 1628145859,
                "reqid": "1628146427307528-760379911749557946200362-news-sink-app-host-yp-1-NEWS-NEWS_API_TOPS_EXPORT",
                "state_version": "news-prod-indexers-2-3.vla.yp-c.yandex.net:1628145859000000:1628146090225561:0:d294.4f294.4",
                "type": "newsd_response",
                "disclaimer_disallow":1,
                "favorite_smi_count":4,
                "form_key":"u3d4a228bd04263c75163991a6ab30272"
            }`,
			expected: fields{
				IsFavorite:         true,
				DisclaimerDisallow: 1,
				FormKey:            "u3d4a228bd04263c75163991a6ab30272",
				ExtraStories:       "",
			},
			isError: true,
			// isEmpty: true,
		},
		{
			name: "Test case with valid official comments and summary",
			content: `{
			  "data": [
				{
				  "name": "Сейчас в СМИ",
				  "url": "https://yandex.ru/news",
				  "stories": [
					{
					  "summary": {
						"timestamp": 1627301302,
						"points": [
						  {
							"agency_id": 1551,
							"url": "https://tass.ru/obschestvo/11988349",
							"text": "Доступ к сайту Алексея Навального, который отбывает наказание в колонии по делу \"Ив Роше\", ограничен, следует из сервиса Роскомнадзора для проверки ограничения доступа к сайтам и страницам сайтов."
						  },
						  {
							"agency_id": 1040,
							"url": "https://www.gazeta.ru/tech/news/2021/07/26/n_16297172.shtml",
							"text": "Блокировку подтверждают соратники Навального в соцсетях."
						  }
						],
						"cluster_id": 154096452
					  },
					  "url": "https://news.stable.priemka.yandex.ru/news/story/Roskomnadzor_zablokiroval_sajt_Navalnogo--ad4603406d7d857cae83a23eaed8c8bd?lang=ru&from=main_portal&fan=1&stid=KviguGlO19PXki8WCZXT&t=1627301032&persistent_id=154096452",
					  "title": "Роскомнадзор заблокировал сайт Навального",
					  "official_comments": [
						{
						  "timestamp": 1616770252016157,
						  "user_id": "2906",
						  "message": {
							"show_in_tail": true,
							"text": "В 18.15 был дан отбой оперативным службам, информация не подтвердилась. В зданиях не обнаружено взрывных устройств и взрывчатых веществ. Угрозы населению нет.",
							"agency_name": "Комсомольская правда - Пермь",
							"company_logo": "",
							"company_url": "https://www.perm.kp.ru/online/news/4236122/#",
							"unique_id": "https://www.perm.kp.ru/online/news/4236122/ AgencyId{2906}",
							"company_title": "Министерство территориальной безопасности Пермского края",
							"url": "https://www.perm.kp.ru/online/news/4236122/#"
						  },
						  "moderation_pending": true
						}
					  ],
					  "agency": {
						"name": "Интерфакс",
						"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1114-1478692903988-square",
						"id": 1114
					  }
					}
				  ],
				  "alias": "index"
				}
			  ],
			  "state_version": "news-testing-indexers-4.man.yp-c.yandex.net:1627301032000000:1627301233636452:0:d293.1f293.1",
			  "reqid": "1627301312936004-54576225075919072000354-priemka-stable-news-app-host-4-NEWS-NEWS_API_TOPS_EXPORT",
			  "agencies_info": {
				"1040": {
				  "is_rkn": true,
				  "site_url": "https://www.gazeta.ru",
				  "logo_square": "135513/1040-1478692902361-square",
				  "actual_name": "Газета.Ru",
				  "host": "gazeta.ru",
				  "id": "1040"
				},
				"1114": {
				  "is_rkn": true,
				  "site_url": "https://www.interfax.ru",
				  "logo_square": "26056/1114-1478692903988-square",
				  "actual_name": "Интерфакс",
				  "host": "interfax.ru",
				  "id": "1114"
				},
				"1551": {
				  "is_rkn": true,
				  "site_url": "http://tass.ru",
				  "logo_square": "50744/1551-1563808847385-square",
				  "actual_name": "ТАСС",
				  "host": "tass.ru",
				  "id": "1551"
				}
			  },
			  "type": "newsd_response",
			  "iter_time": 1627301032
			}`,
			expected: fields{
				IsFavorite: false,
				OfficialComment: []officialComment{
					{
						Message: message{
							AgencyName:   "Комсомольская правда - Пермь",
							CompanyTitle: "Министерство территориальной безопасности Пермского края",
							CompanyURL:   "https://www.perm.kp.ru/online/news/4236122/#",
							Text:         "В 18.15 был дан отбой оперативным службам, информация не подтвердилась. В зданиях не обнаружено взрывных устройств и взрывчатых веществ. Угрозы населению нет.",
							URL:          "https://www.perm.kp.ru/online/news/4236122/#",
						},
					},
				},
				Summary: []summary{
					{
						AgencyName: "ТАСС",
						AgencyURL:  "http://tass.ru",
						AgencyLogo: "https://avatars.mds.yandex.net/get-ynews-logo/50744/1551-1563808847385-square/logo-square",
						URL:        "https://tass.ru/obschestvo/11988349",
						Text:       "Доступ к сайту Алексея Навального, который отбывает наказание в колонии по делу \"Ив Роше\", ограничен, следует из сервиса Роскомнадзора для проверки ограничения доступа к сайтам и страницам сайтов.",
					},
					{
						AgencyName: "Газета.Ru",
						AgencyURL:  "https://www.gazeta.ru",
						AgencyLogo: "https://avatars.mds.yandex.net/get-ynews-logo/135513/1040-1478692902361-square/logo-square",
						URL:        "https://www.gazeta.ru/tech/news/2021/07/26/n_16297172.shtml",
						Text:       "Блокировку подтверждают соратники Навального в соцсетях.",
					},
				},
			},
			isError: false,
			// isEmpty: true,
		},
		{
			name: "Test case with invalid summary agency ID",
			content: `{
			  "data": [
				{
				  "name": "Сейчас в СМИ",
				  "url": "https://yandex.ru/news",
				  "stories": [
					{
					  "summary": {
						"timestamp": 1627301302,
						"points": [
						  {
							"agency_id": 0,
							"url": "https://tass.ru/obschestvo/11988349",
							"text": "Доступ к сайту Алексея Навального, который отбывает наказание в колонии по делу \"Ив Роше\", ограничен, следует из сервиса Роскомнадзора для проверки ограничения доступа к сайтам и страницам сайтов."
						  }
						],
						"cluster_id": 154096452
					  },
					  "url": "https://news.stable.priemka.yandex.ru/news/story/Roskomnadzor_zablokiroval_sajt_Navalnogo--ad4603406d7d857cae83a23eaed8c8bd?lang=ru&from=main_portal&fan=1&stid=KviguGlO19PXki8WCZXT&t=1627301032&persistent_id=154096452",
					  "title": "Роскомнадзор заблокировал сайт Навального",
					  "agency": {
						"name": "Интерфакс",
						"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1114-1478692903988-square",
						"id": 1114
					  }
					}
				  ],
				  "alias": "index"
				}
			  ],
			  "state_version": "news-testing-indexers-4.man.yp-c.yandex.net:1627301032000000:1627301233636452:0:d293.1f293.1",
			  "reqid": "1627301312936004-54576225075919072000354-priemka-stable-news-app-host-4-NEWS-NEWS_API_TOPS_EXPORT",
			  "agencies_info": {
				"1040": {
				  "is_rkn": true,
				  "site_url": "https://www.gazeta.ru",
				  "logo_square": "135513/1040-1478692902361-square",
				  "actual_name": "Газета.Ru",
				  "host": "gazeta.ru",
				  "id": "1040"
				}
			  },
			  "type": "newsd_response",
			  "iter_time": 1627301032
			}`,
			expected: fields{
				IsFavorite: false,
			},
			isError: false,
			// isEmpty: true,
		},
	}

	logger := log3.NewLoggerStub()
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			inputData := &protoanswers.THttpResponse{
				StatusCode: 200,
				Content:    []byte(tt.content),
			}

			if got, err := parseTopnewsRuntimeResponse(inputData, logger); err != nil {
				if tt.isError {
					// ловим ожидаемые ошибки
					require.Error(t, err)
				} else {
					// падаем на ошибках которых быть не должно
					require.NoError(t, err)
				}
			} else {
				// кейсы без ошибок
				// этот тест для задачи про прокидывание is_favorite
				if len(got) > 0 {
					require.Equal(t, tt.expected.IsFavorite, got[0].Stories[0].IsFavorite)
					require.Equal(t, tt.expected.DisclaimerDisallow, got[0].DisclaimerDisallow)
					require.Equal(t, tt.expected.FormKey, got[0].FormKey)
					if len(tt.expected.ExtraStories) > 0 {
						require.Equal(t, tt.expected.ExtraStories, got[0].Stories[0].ExtraStories[0].Title)
					}
					if len(tt.expected.OfficialComment) > 0 {
						require.Equal(t, tt.expected.OfficialComment, got[0].Stories[0].OfficialComments)
					}
					if len(tt.expected.Summary) > 0 {
						require.Equal(t, len(tt.expected.Summary), len(got[0].Stories[0].Summary))
						require.Equal(t, tt.expected.Summary, got[0].Stories[0].Summary)
					}
				}
			}
		})
	}
}

func TestProcessPersonalTabResponse(t *testing.T) {
	tests := []struct {
		name     string
		content  string
		expected fields
		isError  bool
	}{
		{
			name:     `No JSON at all`,
			content:  ``,
			expected: fields{},
			isError:  true,
		},
		{
			name:     `Minimal wrong JSON`,
			content:  `{}`,
			expected: fields{},
			isError:  true,
		},
		{
			name:     "No content",
			content:  `{""}`,
			expected: fields{},
			isError:  true,
		},
		{
			name: "Too less stories",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "Everything ok",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{
				IsFavorite: true,
			},
			isError: false,
			// isEmpty: false,
		},
		{
			name: "No tab alias",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "No tab url",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "First story no title",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "First story no url",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "First story no logo",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "First story no logo",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "First story no source_name",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
		{
			name: "First story no source_id",
			content: `{
				"rubric": {
					"title": "Интересное",
					"alias": "personal_feed",
					"url": "/personal_feed.html"
				},
				"items": [{
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ"
						}]
					}
				}, {
					"obj": {
						"is_favorite": true,
						"title": "Индекс Мосбиржи опустился ниже 3500 пунктов впервые с декабря 2021 года",
						"url": "https://news.stable.priemka.yandex.ru/news/story/",
						"annot_docs": [{
							"logo": "//avatars.mds.yandex.net/get-ynews-logo/26056/1048-1478692900145-regular",
							"source_name": "Коммерсантъ",
							"source_id": 1048
						}]
					}
				}]
			}`,
			expected: fields{},
			isError:  true,
			// isEmpty: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			inputData := &protoanswers.THttpResponse{
				StatusCode: 200,
				Content:    []byte(tt.content),
			}
			h := processHandler{}
			if got, err := h.processPersonalTabResponse(inputData); err != nil {
				if tt.isError {
					// ловим ожидаемые ошибки
					require.Error(t, err)
				} else {
					// падаем на ошибках которых быть не должно
					require.NoError(t, err)
				}
			} else {
				// кейсы без ошибок
				// этот тест для задачи про прокидывание is_favorite
				if tt.expected.IsFavorite {
					require.Equal(t, tt.expected.IsFavorite, got.Stories[0].IsFavorite)
				}
			}
		})
	}
}

func TestRemoveTabsWithoutAlias(t *testing.T) {
	tests := []struct {
		name         string
		tabs         response
		expectedTabs response
	}{
		{
			name: "All tabs have alias",
			tabs: []tab{
				{
					Alias: "alias1",
				},
				{
					Alias: "alias2",
				},
			},
			expectedTabs: []tab{
				{
					Alias: "alias1",
				},
				{
					Alias: "alias2",
				},
			},
		},
		{
			name: "One tab without alias",
			tabs: []tab{
				{
					Expanded: 1,
				},
			},
			expectedTabs: []tab{},
		},
		{
			name: "Some tabs without alias",
			tabs: []tab{
				{
					Expanded: 1,
				},
				{
					Alias:    "alias1",
					Expanded: 1,
				},
				{
					Expanded: 1,
				},
				{
					Alias:    "alias2",
					Expanded: 1,
				},
				{
					Expanded: 1,
				},
			},
			expectedTabs: []tab{
				{
					Alias:    "alias1",
					Expanded: 1,
				},
				{
					Alias:    "alias2",
					Expanded: 1,
				},
			},
		},
		{
			name:         "Empty list of tabs",
			tabs:         []tab{},
			expectedTabs: []tab{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			logger := log3.NewLoggerStub()
			tabs := removeTabsWithoutAlias(tt.tabs, logger)
			require.Equal(t, tt.expectedTabs, tabs)
		})
	}
}
