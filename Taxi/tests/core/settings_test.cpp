#include <gtest/gtest.h>

#include <helpers/experiments3.hpp>
#include <modules/zoneinfo-core/core/settings/settings.hpp>

#include <set>

#include <testing/taxi_config.hpp>

namespace zoneinfo::core {

namespace {

ZoneSettingInput MockInput(std::string zone_name,
                           std::string application = "iphone") {
  return ZoneSettingInput{zone_name, application};
}

models::Country MockCountry() {
  models::Country result;
  result.min_hold_amount = "10";
  return result;
}

taxi_tariffs::models::TariffSettings MockTariffSettings() {
  taxi_tariffs::models::TariffSettings result;
  result.client_exact_order_round_minutes = 20;
  result.client_exact_order_times = std::vector<int>{1, 2, 3};
  result.is_beta = false;
  result.max_route_points_count = 3;
  result.skip_main_screen = false;
  result.req_destination = true;
  result.skip_req_destination = true;
  result.payment_options = {"card", "personal_wallet", "googlepay",
                            "coop_account"};
  return result;
}

}  // namespace

TEST(TestSettings, Simple) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  const auto& experiments3 = Experiments3{{}};
  const auto& tariff_settings = MockTariffSettings();
  const auto& country = MockCountry();

  ZoneSettingInput input = MockInput("moscow");
  ZoneSettingsDeps deps{country, tariff_settings, taxi_config, experiments3};
  const auto& result = BuildZoneSettings(input, deps);

  ASSERT_EQ(result.exact_order_round_minutes, 20);
  ASSERT_EQ(result.is_beta, false);
  ASSERT_EQ(result.max_route_points_count, 3);
  ASSERT_EQ(result.skip_main_screen, std::nullopt);
  ASSERT_EQ(result.min_hold_amount, "10");

  std::vector<int> order_times{1, 2, 3};
  ASSERT_EQ(result.exact_order_times, order_times);

  // "personal_wallet" and "coop_account" filtered out by notmatched ecp
  std::set<std::string> expected_options{"creditcard", "googlepay"};
  ASSERT_EQ(result.payment_options, expected_options);

  const auto& destination = result.destination;
  ASSERT_EQ(destination.is_destination_required, true);
  ASSERT_EQ(destination.dont_require_if_bad_map, true);
  ASSERT_EQ(destination.min_timedelta, std::nullopt);

  const auto& tariff_urls = result.tariff_urls;
  ASSERT_EQ(tariff_urls->tariff_url,
            "https://m.taxi.yandex.ru/zone-tariff/?id=moscow");
  ASSERT_EQ(tariff_urls->tariff_url_key, "MTAXI");
  ASSERT_EQ(tariff_urls->tariff_url_path, "/zone-tariff/?id=moscow");
}

TEST(TestSettings, Uber) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  const auto& experiments3 = Experiments3{{}};
  const auto& tariff_settings = MockTariffSettings();
  const auto& country = MockCountry();

  ZoneSettingInput input = MockInput("moscow", "uber_iphone");
  ZoneSettingsDeps deps{country, tariff_settings, taxi_config, experiments3};
  const auto& result = BuildZoneSettings(input, deps);

  const auto& tariff_urls = result.tariff_urls;
  ASSERT_EQ(tariff_urls->tariff_url,
            "https://support-uber.com/webview/tariff/moscow");
  ASSERT_EQ(tariff_urls->tariff_url_key, "MYAUBER");
  ASSERT_EQ(tariff_urls->tariff_url_path, "/webview/tariff/moscow");
}

TEST(TestSettings, Destination) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  const auto& experiments3 = Experiments3{{}};
  const auto& country = MockCountry();

  auto tariff_settings = MockTariffSettings();
  tariff_settings.req_destination = false;
  tariff_settings.req_destination_rules = {1500};

  ZoneSettingInput input = MockInput("moscow", "uber_iphone");
  ZoneSettingsDeps deps{country, tariff_settings, taxi_config, experiments3};
  const auto& result = BuildZoneSettings(input, deps);

  const auto& destination = result.destination;
  ASSERT_EQ(destination.is_destination_required, false);
  ASSERT_EQ(destination.min_timedelta, 1500);
}

}  // namespace zoneinfo::core
