#include <models/tariff_time_zone.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

using namespace std::string_literals;

constexpr auto kMoscowTariffZone = "moscow";
constexpr auto kMoscowGeonode = "br_moscow";

constexpr auto kAlmatyTariffZone = "almaty";
constexpr auto kAlmatyGeonode = "br_almaty";

constexpr auto kRootGeonode = "br_root";

constexpr auto kRubCurrency = "RUB";
constexpr auto kKzCurrency = "KZT";

const auto kBrGeoNodesResponse =
    formats::json::FromString(R"=(
{
    "items": [
        {
            "name": "br_kazakhstan",
            "name_en": "Kazakhstan",
            "name_ru": "Казахстан",
            "node_type": "country",
            "parent_name": "br_root"
        },
        {
            "name": "br_almaty",
            "name_en": "Almaty",
            "name_ru": "Алматы",
            "node_type": "agglomeration",
            "parent_name": "br_kazakhstan",
            "tariff_zones": ["almaty"]
        },
        {
            "name": "br_moscow",
            "name_en": "Moscow",
            "name_ru": "Москва",
            "node_type": "agglomeration",
            "parent_name": "br_moskovskaja_obl"
        },
        {
            "name": "br_moscow_adm",
            "name_en": "Moscow (adm)",
            "name_ru": "Москва (адм)",
            "node_type": "node",
            "parent_name": "br_moscow",
            "tariff_zones": [
                "boryasvo",
                "moscow",
                "vko"
            ]
        },
        {
            "name": "br_moscow_middle_region",
            "name_en": "Moscow (Middle Region)",
            "name_ru": "Москва (среднее)",
            "node_type": "node",
            "parent_name": "br_moscow"
        },
        {
            "name": "br_moskovskaja_obl",
            "name_en": "Moscow Region",
            "name_ru": "Московская область",
            "node_type": "node",
            "parent_name": "br_tsentralnyj_fo"
        },
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
            "parent_name": "br_root"
        },
        {
            "name": "br_tsentralnyj_fo",
            "name_en": "Central Federal District",
            "name_ru": "Центральный ФО",
            "node_type": "node",
            "parent_name": "br_russia"
        }
    ]
}
)=")
        .As<clients::taxi_agglomerations::ListGeoNodes>();

const auto kTree = caches::agglomerations::Tree(kBrGeoNodesResponse);

const tarifftz::TariffTimeZoneMap kAllZones = {
    {kMoscowTariffZone, {"Europe/Moscow", kRubCurrency}},
    {kAlmatyTariffZone, {"Asia/Almaty", kKzCurrency}}};

TEST(GetCurrency, ForTariffZone) {
  EXPECT_EQ(tarifftz::GetCurrency({kMoscowTariffZone}, kAllZones, kTree),
            kRubCurrency);
  EXPECT_EQ(tarifftz::GetCurrency({kAlmatyTariffZone}, kAllZones, kTree),
            kKzCurrency);
}

TEST(GetCurrency, ForTwoDifferentTariffZone) {
  EXPECT_THROW(tarifftz::GetCurrency({kMoscowTariffZone, kAlmatyTariffZone},
                                     kAllZones, kTree),
               std::runtime_error);
}

TEST(GetCurrency, ForInvalidTariffZone) {
  EXPECT_THROW(tarifftz::GetCurrency({"invalid"}, kAllZones, kTree),
               std::runtime_error);
}

TEST(GetCurrency, ForGeoNode) {
  EXPECT_EQ(tarifftz::GetCurrency({kMoscowGeonode}, kAllZones, kTree),
            kRubCurrency);
  EXPECT_EQ(tarifftz::GetCurrency({kAlmatyGeonode}, kAllZones, kTree),
            kKzCurrency);
}

TEST(GetCurrency, ForInvalidGeoNode) {
  EXPECT_THROW(tarifftz::GetCurrency({"br_invalid"}, kAllZones, kTree),
               std::runtime_error);
  EXPECT_THROW(tarifftz::GetCurrency({kRootGeonode}, kAllZones, kTree),
               std::runtime_error);
}

TEST(GetCurrency, ForTwoDifferentGeoNode) {
  EXPECT_THROW(
      tarifftz::GetCurrency({kMoscowGeonode, kAlmatyGeonode}, kAllZones, kTree),
      std::runtime_error);
}

TEST(GetCurrency, ForDifferentGeoNodeAndTariffZone) {
  EXPECT_THROW(tarifftz::GetCurrency({kMoscowGeonode, kAlmatyTariffZone},
                                     kAllZones, kTree),
               std::runtime_error);
}
