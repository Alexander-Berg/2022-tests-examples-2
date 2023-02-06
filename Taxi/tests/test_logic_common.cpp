#include <gtest/gtest.h>

#include <chrono>
#include <string>
#include <utility>
#include <vector>

#include <iostream>  // delete

#include <cctz/civil_time.h>
#include <cctz/time_zone.h>

#include <userver/formats/json/serialize.hpp>

#include <clients/taxi-agglomerations/responses.hpp>
#include <models/tree.hpp>             // agglomerations-cache-v2
#include <tariff_settings/models.hpp>  // taxi-tariffs

#include <logic/common.hpp>

const auto kBrGeoNodesResponse =
    formats::json::FromString(R"=(
{
    "items":
    [
        {
            "name": "br_root",
            "name_en": "Basic Hierarchy",
            "name_ru": "Базовая иерархия",
            "node_type": "root"
        },
        {
            "name": "br_russia",
            "name_en": "Russia",
            "name_ru": "Россия",
            "node_type": "country",
            "parent_name": "br_root",
            "region_id": "225",
            "tanker_key": "name.br_russia"
        },
        {
            "name": "br_tsentralnyj_fo",
            "name_en": "Central Federal District",
            "name_ru": "Центральный ФО",
            "node_type": "node",
            "parent_name": "br_russia",
            "region_id": "3",
            "tanker_key": "name.br_tsentralnyj_fo"
        },
        {
            "name": "br_moskovskaja_obl",
            "name_en": "Moscow Region",
            "name_ru": "Московская область",
            "node_type": "node",
            "parent_name": "br_tsentralnyj_fo",
            "tanker_key": "name.br_moskovskaja_obl"
        },
        {
            "name": "br_moscow",
            "name_en": "Moscow",
            "name_ru": "Москва",
            "node_type": "agglomeration",
            "parent_name": "br_moskovskaja_obl",
            "tanker_key": "name.br_moscow"
        },
        {
            "name": "br_moscow_adm",
            "name_en": "Moscow (adm)",
            "name_ru": "Москва (адм)",
            "node_type": "node",
            "parent_name": "br_moscow",
            "region_id": "213",
            "tanker_key": "name.br_moscow_adm",
            "tariff_zones": [
            "boryasvo",
            "moscow",
            "vko"
            ]
        },
        {
            "name": "br_privolzhskij_fo",
            "name_en": "Volga Federal District",
            "name_ru": "Приволжский ФО",
            "node_type": "node",
            "parent_name": "br_russia",
            "tanker_key": "name.br_privolzhskij_fo"
        },
        {
            "name": "br_samarskaja_obl",
            "name_en": "Samara Region",
            "name_ru": "Самарская область",
            "node_type": "node",
            "parent_name": "br_privolzhskij_fo",
            "tanker_key": "name.br_samarskaja_obl"
        },
        {
            "name": "br_samara",
            "name_en": "Samara",
            "name_ru": "Самара",
            "node_type": "agglomeration",
            "parent_name": "br_samarskaja_obl",
            "tanker_key": "name.br_samara"
        },
        {
            "name": "br_samara_adm",
            "name_en": "Samara (adm)",
            "name_ru": "Самара (адм)",
            "node_type": "node",
            "parent_name": "br_samara",
            "tanker_key": "name.br_samara_adm",
            "tariff_zones": [
            "samara"
            ]
        },
        {
            "name": "br_belarus",
            "name_en": "Belarus",
            "name_ru": "Белоруссия",
            "node_type": "country",
            "parent_name": "br_root",
            "tanker_key": "name.br_belarus"
        },
        {
            "name": "br_minsk",
            "name_en": "Minsk",
            "name_ru": "Минск",
            "node_type": "agglomeration",
            "parent_name": "br_belarus",
            "tanker_key": "name.br_minsk",
            "tariff_zones": [
            "minsk"
            ]
        }
    ]
}
)=")
        .As<clients::taxi_agglomerations::ListGeoNodes>();

const caches::agglomerations::Tree tree(kBrGeoNodesResponse);

taxi_tariffs::models::TariffSettingsMap CreareTariffSettingsMap() {
  taxi_tariffs::models::TariffSettingsMap map;
  const std::vector<std::pair<std::string, std::string>> data{
      {"moscow", "Europe/Moscow"},
      {"boryasvo", "Europe/Moscow"},
      {"vko", "Europe/Moscow"},
      {"samara", "Europe/Samara"},
      {"minsk", "Europe/Minsk"}};
  for (auto [home_zone, timezone] : data) {
    clients::taxi_tariffs::TariffSettingsItem item;
    item.home_zone = home_zone;
    item.timezone = timezone;
    map[home_zone] = item;
  }
  return map;
}

const taxi_tariffs::models::TariffSettingsMap map = CreareTariffSettingsMap();

struct TestGetTimeZoneData {
  std::string full_path_to_node_or_tariff_zone;
  std::string expected_timezone_name;
};

struct TestGetTimeZoneParametrized
    : ::testing::TestWithParam<TestGetTimeZoneData> {};

TEST_P(TestGetTimeZoneParametrized, Test) {
  auto [full_path_to_node_or_tariff_zone, expected_timezone_name] = GetParam();
  const auto result_timezone =
      logic::GetTimeZoneByGeonodes(full_path_to_node_or_tariff_zone, tree, map);
  cctz::time_zone expected_timezone;
  ASSERT_TRUE(cctz::load_time_zone(expected_timezone_name, &expected_timezone));
  ASSERT_EQ(result_timezone, expected_timezone);
}

const std::vector<TestGetTimeZoneData> kTestGetTimeZoneData = {
    {"br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/"
     "br_moscow_adm",
     "Europe/Moscow"},
    {"br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/"
     "br_moscow_adm/moscow",
     "Europe/Moscow"},
    {"br_root/br_russia/br_privolzhskij_fo/br_samarskaja_obl/br_samara/"
     "br_samara_adm",
     "Europe/Samara"},
    {"br_root/br_russia/br_privolzhskij_fo/br_samarskaja_obl/br_samara/"
     "br_samara_adm/samara",
     "Europe/Samara"},
    {"br_root/br_belarus/br_minsk", "Europe/Minsk"},
    {"br_root/br_belarus/br_minsk/minsk", "Europe/Minsk"}};

INSTANTIATE_TEST_SUITE_P(TestGetTimeZoneParametrized,
                         TestGetTimeZoneParametrized,
                         ::testing::ValuesIn(kTestGetTimeZoneData));
