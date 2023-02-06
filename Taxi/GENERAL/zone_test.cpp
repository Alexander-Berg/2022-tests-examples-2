#include "zone.hpp"
#include <defs/all_definitions.hpp>
#include <discounts-match/rules_match_base.hpp>
#include <models/names.hpp>
#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

namespace {

void Sort(rules_match::MatchComplexConditions::ValueType& result) {
  auto& base_values =
      std::get<rules_match::generated::BaseConditionsVector>(result.values);
  auto& result_values =
      std::get<std::vector<handlers::libraries::discounts_match::Zone>>(
          base_values);
  std::sort(result_values.begin(), result_values.end(),
            [](auto& lhs, auto rhs) { return lhs.name < rhs.name; });
}

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
                "moscow"
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
        },
        {
            "name": "br_tel_aviv",
            "name_en": "Tel Aviv",
            "name_ru": "Тель Авив",
            "node_type": "node",
            "parent_name": "br_root",
            "tariff_zones": ["tel_aviv"]
        }
    ]
}
)=")
        .As<clients::taxi_agglomerations::ListGeoNodes>();

caches::agglomerations::Tree kTree(kBrGeoNodesResponse);
}  // namespace

TEST(MakeMatchZoneCondition, EmptyTree) {
  std::vector<handlers::libraries::discounts_match::Zone> values;
  values.push_back({"moscow",
                    handlers::libraries::discounts_match::ZoneType::kTariffZone,
                    true});
  values.push_back({"moscow",
                    handlers::libraries::discounts_match::ZoneType::kTariffZone,
                    false});
  auto expected = rules_match::MatchConditions::ValueType{
      models::names::conditions::kZone, std::move(values)};
  utils::MakeMatchZoneCondition("moscow", caches::agglomerations::Tree{});
  EXPECT_EQ(
      utils::MakeMatchZoneCondition("moscow", caches::agglomerations::Tree{}),
      expected);
}

TEST(MakeFindZoneCondition, ByPrioritizedTariffZones) {
  std::vector<handlers::libraries::discounts_match::Zone> values;
  values.push_back({"moscow",
                    handlers::libraries::discounts_match::ZoneType::kTariffZone,
                    true});
  auto expected = rules_match::MatchComplexConditions::ValueType{
      models::names::conditions::kZone, values};
  EXPECT_EQ(
      utils::MakeFindZoneCondition(
          values, handlers::FindDiscountsRequestZonefiltertype::kExact, kTree),
      expected);
}

TEST(MakeFindZoneCondition, ByNotPrioritizedTariffZones) {
  std::vector<handlers::libraries::discounts_match::Zone> values;
  values.push_back({"moscow",
                    handlers::libraries::discounts_match::ZoneType::kTariffZone,
                    false});
  auto expected = rules_match::MatchComplexConditions::ValueType{
      models::names::conditions::kZone, values};
  EXPECT_EQ(
      utils::MakeFindZoneCondition(
          values, handlers::FindDiscountsRequestZonefiltertype::kExact, kTree),
      expected);
}

TEST(MakeFindZoneCondition, WithDescendants) {
  std::vector<handlers::libraries::discounts_match::Zone> values;
  values.push_back({"br_moscow_adm",
                    handlers::libraries::discounts_match::ZoneType::kGeonode,
                    false});
  auto expected = rules_match::MatchComplexConditions::ValueType{
      models::names::conditions::kZone,
      std::vector<handlers::libraries::discounts_match::Zone>{
          {"boryasvo",
           handlers::libraries::discounts_match::ZoneType::kTariffZone, false},
          {"br_moscow_adm",
           handlers::libraries::discounts_match::ZoneType::kGeonode, false},
          {"moscow",
           handlers::libraries::discounts_match::ZoneType::kTariffZone, false},
      }};
  auto result = utils::MakeFindZoneCondition(
      values, handlers::FindDiscountsRequestZonefiltertype::kWithDescendants,
      kTree);
  Sort(expected);
  Sort(result);
  EXPECT_EQ(result, expected);
}

TEST(MakeFindZoneCondition, WithAncestors) {
  std::vector<handlers::libraries::discounts_match::Zone> values;
  values.push_back({"br_russia",
                    handlers::libraries::discounts_match::ZoneType::kGeonode,
                    false});
  auto expected = rules_match::MatchComplexConditions::ValueType{
      models::names::conditions::kZone,
      std::vector<handlers::libraries::discounts_match::Zone>{
          {"br_root", handlers::libraries::discounts_match::ZoneType::kGeonode,
           false},
          {"br_russia",
           handlers::libraries::discounts_match::ZoneType::kGeonode, false}}};
  auto result = utils::MakeFindZoneCondition(
      values, handlers::FindDiscountsRequestZonefiltertype::kWithAncestors,
      kTree);
  Sort(expected);
  Sort(result);
  EXPECT_EQ(result, expected);
}
