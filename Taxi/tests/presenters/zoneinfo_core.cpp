#include <gtest/gtest.h>

#include <l10n/translations.hpp>

#include <set>

#include <testing/taxi_config.hpp>
#include <views/v1/zoneinfo/core/post/presenters/presenter.hpp>

#include "../test_utils/mock_imager.hpp"
#include "../test_utils/mock_legacy_translator.hpp"
#include "../test_utils/mock_translator.hpp"

namespace zoneinfo::presenter {

namespace {

core::ZoneInfoCoreResult MockCore() {
  core::ZoneInfoCoreResult result;

  // meta_info
  result.meta_info.region_id = 777;
  result.meta_info.country_code = "ru";
  result.meta_info.currency_code = "RUB";
  result.meta_info.timezone_offset = "+0300";
  result.meta_info.route_show_jams = true;
  result.meta_info.copyright =
      MakeOptionalTranslation(MakeTankerKey("client_messages", "copyright"));
  result.meta_info.support_phone = "+7123";
  result.meta_info.legal_entity =
      MakeOptionalTranslation(MakeTankerKey("client_messages", "legal_entity"));

  // settings
  result.settings.exact_order_round_minutes = 1;
  result.settings.is_beta = true;
  result.settings.max_route_points_count = 3;
  result.settings.payment_options = std::set<std::string>{"card"};
  result.settings.min_hold_amount = "1500";
  result.settings.tariff_urls = core::ZoneTariffUrls{"url", "key", "path"};
  result.settings.destination = core::ZoneDestinationSettings{false, false, 14};

  // tariffs info
  core::CategoryInfo econom;
  econom.basic.id = "econom";
  econom.basic.class_name = "econom";
  econom.basic.service_levels = std::vector<int>{154};

  econom.basic.name =
      MakeRequiredTranslation({l10n::keysets::kTariff, "name.econom"});
  auto description_key =
      MakeTankerKey(l10n::keysets::kClientMessages,
                    "mainscreen.description_econom_izberbash");
  auto description_fallback_key = MakeTankerKey(
      l10n::keysets::kClientMessages, "mainscreen.description_econom");
  econom.basic.description =
      MakeRequiredTranslation(description_key, description_fallback_key);
  econom.basic.short_description = MakeOptionalTranslation(
      {l10n::keysets::kClientMessages, "mainscreen.short_description_econom"});

  econom.basic.icon = MakeRequiredImage({"car_icon"});
  econom.basic.image = MakeRequiredImage({"car_image"});

  econom.basic.settings.can_be_default = true;
  econom.basic.settings.comments_disabled = true;
  econom.basic.settings.is_default = true;
  econom.basic.settings.mark_as_new = false;
  econom.basic.settings.max_route_points_count = 40;
  econom.basic.settings.max_waiting_time = 3;
  econom.basic.settings.only_for_soon_orders = false;
  econom.basic.settings.toll_roads_enabled = false;
  auto restrict_by_payment_type =
      std::vector<std::string>{"card",      "corp",         "applepay",
                               "googlepay", "coop_account", "personal_wallet"};
  econom.basic.settings.restrict_by_payment_type = restrict_by_payment_type;

  core::CategoryNotification notification;
  notification.key = "key";
  notification.type = "type";
  notification.show_count = 3;
  notification.translations = {
      {"button", MakeOptionalTranslation(
                     {l10n::keysets::kClientMessages, "notification.button"})}};
  econom.notifications = {notification};

  econom.order_for_other.order_for_other_prohibited = false;

  result.categories_info.push_back(econom);

  return result;
}

}  // namespace

TEST(TestCorePresenter, Simple) {
  auto imager = MockImager();
  auto translator = MockTranslator();
  auto legacy_translator = MockLegacyTranslator();
  auto taxi_config =
      dynamic_config::GetDefaultSnapshot().Get<taxi_config::TaxiConfig>();
  ClientExperimentsContext client_experiments_context = {};

  ZoneInfoCorePresenterDeps deps{translator, legacy_translator, imager,
                                 taxi_config, client_experiments_context};
  ZoneInfoCorePresenterInput input{"ru", "android", 640};
  core::ZoneInfoCoreResult core = MockCore();
  auto resp = BuildResponse(core, input, deps);

  ASSERT_EQ(resp.copyright, "client_messages_copyright_tr_ru");
  ASSERT_EQ(resp.support_phone, "+7123");
  ASSERT_EQ(resp.country_code, "ru");
  ASSERT_EQ(resp.currency_code, "RUB");
  ASSERT_EQ(resp.exact_order_round_minutes, 1);
  ASSERT_EQ(resp.exact_order_times, std::vector<int>{});
  ASSERT_EQ(resp.is_beta, true);
  ASSERT_EQ(resp.legal_entity, "client_messages_legal_entity_tr_ru");
  ASSERT_EQ(resp.max_route_points_count, 3);
  ASSERT_EQ(resp.min_hold_amount, "1500");
  ASSERT_EQ(resp.region_id, 777);
  ASSERT_EQ(resp.req_destination, std::nullopt);
  ASSERT_EQ(resp.route_show_jams, true);
  ASSERT_EQ(resp.skip_main_screen, std::nullopt);
  ASSERT_EQ(resp.skip_req_destination, false);
  ASSERT_EQ(resp.tariffs_url, "url");
  ASSERT_EQ(resp.tz, "+0300");

  handlers::ZoneinfoCoreResponsePaymentoptions options;
  options.extra["card"] = true;
  ASSERT_EQ(resp.payment_options, options);

  handlers::UrlParts parts{"key", "path"};
  ASSERT_EQ(resp.tariffs_url_parts, parts);

  handlers::ZoneinfoCoreResponseReqdestinationrules rules{14};
  ASSERT_EQ(resp.req_destination_rules, rules);

  const auto& result_econom = resp.max_tariffs->at(0);
  ASSERT_EQ(result_econom.id, "econom");
  ASSERT_EQ(result_econom.class_, "econom");
  ASSERT_EQ(result_econom.service_levels, std::vector<int>{154});

  ASSERT_EQ(result_econom.name, "tariff_name.econom_tr_ru");
  ASSERT_EQ(result_econom.description,
            "client_messages_mainscreen.description_econom_izberbash_tr_ru");
  ASSERT_EQ(result_econom.short_description,
            "client_messages_mainscreen.short_description_econom_tr_ru");

  ASSERT_EQ(result_econom.icon->url, "car_icon_no_branding_0_for_android_640");
  ASSERT_EQ(result_econom.image->url,
            "car_image_no_branding_0_for_android_640");

  ASSERT_EQ(result_econom.can_be_default, true);
  ASSERT_EQ(result_econom.comments_disabled, true);
  ASSERT_EQ(result_econom.is_default, true);
  ASSERT_EQ(result_econom.mark_as_new, false);
  ASSERT_EQ(result_econom.max_route_points_count, 40);
  ASSERT_EQ(result_econom.max_waiting_time, 3);
  ASSERT_EQ(result_econom.only_for_soon_orders, false);
  ASSERT_EQ(result_econom.toll_roads_enabled, false);
  ASSERT_EQ(result_econom.order_for_other_prohibited, false);

  auto expected_restrict_by_payment_type =
      std::vector<std::string>{"card",      "corp",         "applepay",
                               "googlepay", "coop_account", "personal_wallet"};
  ASSERT_EQ(result_econom.restrict_by_payment_type,
            expected_restrict_by_payment_type);

  ASSERT_NE(result_econom.notifications, std::nullopt);

  const auto& result_notifications = result_econom.notifications.value();
  ASSERT_NE(result_notifications.extra.find("key"),
            result_notifications.extra.end());

  const auto& result_notification = result_notifications.extra.at("key");

  ASSERT_EQ(result_notification.type, "type");
  ASSERT_EQ(result_notification.show_count, 3);
  ASSERT_NE(result_notification.translations->extra.find("button"),
            result_notification.translations->extra.end());
  ASSERT_EQ(result_notification.translations->extra.at("button"),
            "client_messages_notification.button_tr_ru");
}

}  // namespace zoneinfo::presenter
