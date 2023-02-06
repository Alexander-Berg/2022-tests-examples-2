package searchapp

import (
	"github.com/stretchr/testify/mock"

	newinternal "a.yandex-team.ru/portal/avocado/avocado/pkg/new-internal"
	"a.yandex-team.ru/portal/avocado/libs/utils/base/models"
	"a.yandex-team.ru/portal/morda-go/tests/mocks"
)

func GeoTestConstructor(cityID int) newinternal.Geo {
	return newinternal.Geo{ID: cityID}
}

func mockGeo(apphostContext *mocks.ApphostContext, additionalHeaders map[string]string, sessionID string) {
	headers := map[string][]string{
		"Accept":                       {"*/*"},
		"Content-Length":               {"3337"},
		"Content-Type":                 {"application/x-www-form-urlencoded"},
		"Host":                         {"avocado-dev.yandex.net"},
		"User-Agent":                   {"curl/7.64.1"},
		"X-Real-Remote-Ip":             {"::1"},
		"X-Yandex-Http-Adapter-Req-Id": {"1614180646037454-1529124040349804116100126-avocado-dev-4"},
		"X-Yandex-Internal-Request":    {"1"},
		"X-Yandex-Req-Id":              {"1614180646037454-1529124040349804116100126-avocado-dev-4"},
	}

	for k, v := range additionalHeaders {
		headers[k] = append(headers[k], v)
	}

	apphostContext.
		On("GetJSONs", "geohelper_request_context", mock.Anything).
		Run(func(args mock.Arguments) {
			if len(args) != 2 {
				return
			}

			ctx := newinternal.GeohelperRequestContext{
				Geo: GeoTestConstructor(213),
				Cookies: models.YaCookies{
					YandexGID: 0,
					Yp: models.YCookie{
						Subcookies: make(map[string]models.YSubcookie),
						RawString:  "",
					},
					Ys: models.YCookie{
						Subcookies: make(map[string]models.YSubcookie),
						RawString:  "",
					},
					YandexUID:  "",
					SessionID:  sessionID,
					SessionID2: "",
				},
				Headers:  headers,
				IP:       "::1",
				URL:      "/api/v1/sa_heavy?did=&experiments=with_gif%2Ctutor_touch%2Cstream_player_1788%2Cmarket_category_interval_2%2Cmarket_product_randomize_reasons%2Csplash_promo_touch%2Cclient_logger%2Ctouch_smooth_scroll_metric%2Cmusic%2Capp_android_webcard_assist%2Cstream_picture%2Cyandex_staff%2Cextracted_points_route%2Cugc%2Cstream_special_events%2Cstream_send_strm_probe%2Cinserts_stream_mixed%2Cplayed_games%2Creport_visibility_check_inline%2Cwith_plus_50%2CCSPv2%2Ctranslator_api%2Cpg_unknown%2Cyastatic_check_ru_touch%2Cassist_divcard%2Cfront_apphost%2Cstream_personal%2Clogin_touch_new%2Cmarket_api%2Csport_div_card%2Cteaser_app_bk%2Cstream_disable_personal%2Cyandex_internal_test%2Cgh_rtx_exp_searchapp%2Cyalocal_custom_url%2Cextracted_points_edadeal%2Cstream_skippable_fragments%2Ctourist_blocks%2Cweather_sb_app&flags=no_yskin%2Credesign_div_pp&geoid=213&lang=ru&lat=55.753215&lon=37.622504&mordazone=ru&reqid=1614159060.18074.119740.363001&uuid=",
				PostBody: []byte("{\"general_div2\":{\"id\":\"general_div2\",\"ttv\":1200,\"type\":\"div2\",\"ttl\":300,\"is_mordanavigate\":0},\"games_div2\":{\"ttv\":1209600,\"id\":\"games_div2\",\"is_mordanavigate\":1,\"ttl\":300,\"type\":\"div2\"},\"homeparams\":{\"sport_div2_title\":\"\",\"version\":\"20120200\",\"general_div2_title\":\"\",\"games_div2_title\":\"\",\"menu\":{\"autoru_div2\":{\"menu_list\":[{\"text\":\"Настройки ленты\",\"action\":\"opensettings://?screen=feed\"},{\"text\":\"Скрыть карточку\",\"action\":\"hidecard://?topic_card_ids=autoru_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83\"}]},\"sport_div2\":{\"menu_list\":[{\"text\":\"Настройки ленты\",\"action\":\"opensettings://?screen=feed\"},{\"action\":\"hidecard://?topic_card_ids=sport_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83\",\"text\":\"Скрыть карточку\"}]},\"topnews_div2\":{\"menu_list\":[{\"text\":\"Настройки ленты\",\"action\":\"opensettings://?screen=feed\"},{\"action\":\"hidecard://?topic_card_ids=topnews_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83\",\"text\":\"Скрыть карточку\"}]},\"games_div2\":{\"menu_list\":[{\"text\":\"Настройки ленты\",\"action\":\"opensettings://?screen=feed\"},{\"text\":\"Скрыть карточку\",\"action\":\"hidecard://?topic_card_ids=games_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83\"}]},\"general_div2\":{\"menu_list\":[{\"action\":\"opensettings://?screen=feed\",\"text\":\"Настройки ленты\"},{\"action\":\"hidecard://?topic_card_ids=general_div2_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83\",\"text\":\"Скрыть карточку\"}]}},\"geo_country\":225,\"country\":\"RU\",\"platform\":\"android\",\"topnews_div2_title\":\"\",\"os_version\":\"9.0\",\"layout\":[{\"type\":\"search\",\"heavy\":0,\"id\":\"search\"},{\"heavy\":0,\"type\":\"div2\",\"id\":\"nowcast\"},{\"id\":\"weather.02726221751610474d77a3309b38157111920e05\",\"heavy\":0,\"type\":\"div2\"},{\"id\":\"topnews\",\"heavy\":0,\"type\":\"topnews\"},{\"type\":\"div2\",\"heavy\":0,\"id\":\"covid_gallery\"},{\"id\":\"stocks\",\"type\":\"stocks\",\"heavy\":0},{\"id\":\"native_ad_1\",\"type\":\"native_ad\",\"heavy\":0},{\"type\":\"div2\",\"heavy\":1,\"id\":\"general_div2\"},{\"id\":\"native_ad_2\",\"type\":\"native_ad\",\"heavy\":0},{\"id\":\"weather\",\"type\":\"weather\",\"heavy\":0},{\"type\":\"tv\",\"heavy\":0,\"id\":\"tv\"},{\"type\":\"div2\",\"heavy\":1,\"id\":\"topnews_div2\"},{\"heavy\":1,\"type\":\"div2\",\"id\":\"games_div2\"},{\"id\":\"autoru_div2\",\"heavy\":1,\"type\":\"div2\"},{\"type\":\"div2\",\"heavy\":1,\"id\":\"sport_div2\"},{\"id\":\"transportmap\",\"type\":\"transportmap\",\"heavy\":0},{\"id\":\"privacy_api\",\"heavy\":0,\"type\":\"div\"}],\"scale_factor\":1,\"autoru_div2_title\":\"\",\"topic\":{\"games_div2\":\"games_div2_card\",\"general_div2\":\"general_div2_card\",\"autoru_div2\":\"autoru_div2_card\",\"sport_div2\":\"sport_div2_card\",\"topnews_div2\":\"topnews_div2_card\"}},\"topnews_div2\":{\"ttl\":300,\"type\":\"div2\",\"is_mordanavigate\":1,\"id\":\"topnews_div2\",\"ttv\":1209600},\"sport_div2\":{\"is_mordanavigate\":1,\"ttl\":300,\"type\":\"div2\",\"ttv\":1200,\"id\":\"sport_div2\"},\"autoru_div2\":{\"ttv\":1200,\"id\":\"autoru_div2\",\"is_mordanavigate\":1,\"ttl\":300,\"type\":\"div2\"}}"),
			}

			pSlice, ok := args[1].(*[]newinternal.GeohelperRequestContext)
			if !ok {
				return
			}

			*pSlice = []newinternal.GeohelperRequestContext{ctx}
		}).
		Return(nil).
		Once()
}
