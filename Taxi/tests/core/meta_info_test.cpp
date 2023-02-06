#include <gtest/gtest.h>

#include <helpers/experiments3.hpp>
#include <modules/zoneinfo-core/core/meta_info/meta_info.hpp>
#include <testing/taxi_config.hpp>

#include "../test_utils/mock_experiments.hpp"

namespace zoneinfo::core {

namespace {
models::Country MockCountry(std::string code3) {
  models::Country result;
  result.id = code3;
  result.code2 = "ru";
  result.region_id = 123;
  result.currency_code = "rubli";
  return result;
}

taxi_tariffs::models::TariffSettings MockTariffSettings() {
  taxi_tariffs::models::TariffSettings result;
  result.country = "rus_ts";
  result.timezone = "Europe/Moscow";
  return result;
}

Experiments3 MockExperiments3Local() {
  formats::json::ValueBuilder superapp_help_builder;
  superapp_help_builder["help_center_url"] = "superapp_help_url";
  superapp_help_builder["help_center_email"] = "superapp_help_mail";

  auto superapp_help_value = superapp_help_builder.ExtractValue();
  return MockExperiments3({{"superapp_help", superapp_help_value}});
}

}  // namespace

TEST(TestMetaInfo, Simple) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  const auto& country = MockCountry("rus");
  const auto& experiments3 = MockExperiments3Local();
  const auto& tariff_settings = MockTariffSettings();

  MetaInfoInput input{"android", "yataxi", ""};
  MetaInfoDeps deps{country, tariff_settings, taxi_config, experiments3};
  const auto& result = BuildMetaInfo(input, deps);

  ASSERT_EQ(result.region_id, 123);
  ASSERT_EQ(result.country_code, "ru");
  ASSERT_EQ(result.currency_code, "rubli");
  ASSERT_EQ(result.timezone_offset, "+0300");
  ASSERT_EQ(result.route_show_jams, false);

  ASSERT_EQ(result.copyright->GetKey().key, "about_copyright_yandex_llc");
  ASSERT_EQ(result.copyright->GetType(), TranslationType::kOptional);

  ASSERT_EQ(result.legal_entity->GetKey().key, "legal_entities.rus");
  ASSERT_EQ(result.legal_entity->GetType(), TranslationType::kOptional);

  ASSERT_EQ(result.help_info.url, "superapp_help_url");
  ASSERT_EQ(result.help_info.email, "superapp_help_mail");
  ASSERT_EQ(result.support_phone, "+7-499-705-88-88");
}

TEST(TestMetaInfo, Copyright) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  const auto& country = MockCountry("usa");
  const auto& experiments3 = MockExperiments3Local();
  const auto& tariff_settings = MockTariffSettings();

  MetaInfoInput input{"android", "yataxi", ""};
  MetaInfoDeps deps{country, tariff_settings, taxi_config, experiments3};
  const auto& result = BuildMetaInfo(input, deps);

  ASSERT_EQ(result.copyright->GetKey().key, "about_copyright_yandex");
  ASSERT_EQ(result.copyright->GetType(), TranslationType::kOptional);
}

TEST(TestMetaInfo, Uber) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& taxi_config = config.Get<taxi_config::TaxiConfig>();
  const auto& country = MockCountry("usa");
  const auto& experiments3 = MockExperiments3Local();
  const auto& tariff_settings = MockTariffSettings();

  MetaInfoInput input{"uber_android", "yauber", ""};
  MetaInfoDeps deps{country, tariff_settings, taxi_config, experiments3};
  const auto& result = BuildMetaInfo(input, deps);

  ASSERT_EQ(result.support_phone, "+1111111111");
}

}  // namespace zoneinfo::core
