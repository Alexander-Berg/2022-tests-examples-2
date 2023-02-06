#include <array>
#include <set>
#include <string>

#include <discounts-match/conditions.hpp>
#include <discounts/models/error.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>
#include <userver/utest/utest.hpp>

#include <models/conditions_validator.hpp>
#include <models/names.hpp>

namespace {
using namespace std::string_literals;

using Arrays = std::vector<std::set<std::string>>;
using Integers = std::vector<int64_t>;
using Strings = std::vector<std::string>;
using Zones = std::vector<handlers::libraries::discounts_match::Zone>;
using ZoneType = ::handlers::libraries::discounts_match::ZoneType;
using namespace caches::agglomerations;
using Geoarea = client_geoareas::models::Geoarea;
using GeoareaPtr = std::shared_ptr<const Geoarea>;

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

const auto kTariffSettingsData =
    std::make_shared<taxi_tariffs::models::TariffSettingsMap>(
        formats::json::FromString(R"=(
{
  "moscow":
    {
      "timezone":"Europe/Moscow"
    },
  "vko":
    {
      "timezone":"Europe/Moscow"
    },
  "boryasvo":
    {
      "timezone":"Europe/Moscow"
    },
  "tel_aviv":
    {
      "timezone":"Asia/Jerusalem"
    }
}
    )=")
            .As<std::unordered_map<
                std::string, clients::taxi_tariffs::TariffSettingsItem>>());

std::pair<std::string, GeoareaPtr> MakeGeoarea(
    std::string name,
    const std::vector<std::vector<::geometry::Position>>& polygon) {
  Geoarea geoarea("id", "type", name, utils::datetime::Now(), polygon, {}, {});
  return std::make_pair(name, std::make_shared<Geoarea>(std::move(geoarea)));
}

const models::GeoareasPtr GetGeoareas() {
  using namespace ::geometry::literals;
  std::unordered_map<std::string, GeoareaPtr> geoareas{
      MakeGeoarea("berlin", {{{15.0_lon, 15.0_lat},
                              {15.0_lon, 19.0_lat},
                              {19.0_lon, 19.0_lat},
                              {15.0_lon, 15.0_lat}}}),
      MakeGeoarea("moscow", {{{35.0_lon, 35.0_lat},
                              {35.0_lon, 39.0_lat},
                              {39.0_lon, 39.0_lat},
                              {35.0_lon, 35.0_lat}}}),
      MakeGeoarea("moscow_airport", {{{36.0_lon, 36.0_lat},
                                      {36.0_lon, 38.0_lat},
                                      {38.0_lon, 38.0_lat},
                                      {36.0_lon, 36.0_lat}}}),
      MakeGeoarea("paris", {{{5.0_lon, 5.0_lat},
                             {5.0_lon, 10.0_lat},
                             {10.0_lon, 10.0_lat},
                             {5.0_lon, 5.0_lat}}}),
      MakeGeoarea("paris_airport", {{{6.0_lon, 6.0_lat},
                                     {6.0_lon, 8.0_lat},
                                     {8.0_lon, 8.0_lat},
                                     {6.0_lon, 6.0_lat}}})};
  return std::make_shared<decltype(geoareas)>(std::move(geoareas));
}

template <typename ConditionValue>
handlers::libraries::discounts_match::RuleCondition MakeRuleCondition(
    const std::string& condition_name, const ConditionValue& condition_value) {
  return handlers::libraries::discounts_match::RuleCondition{
      {condition_name, condition_value}, {}};
}

rules_match::RuleConditions MakeConditionsMap(
    const rules_match::RuleConditions::ValueType& condition) {
  return rules_match::RuleConditions{
      std::array<rules_match::RuleConditions::ValueType, 1>{condition}};
}

template <typename ConditionValue>
rules_match::RuleConditions MakeConditionsWithGeoarea(
    const ConditionValue& condition_value) {
  auto condition = handlers::libraries::discounts_match::RuleCondition{
      {models::names::conditions::kGeoareaASet, condition_value}, {}};
  return rules_match::RuleConditions{
      std::array<rules_match::RuleConditions::ValueType, 1>{condition}};
}

void CheckValidateGeoareasA(
    const std::unordered_set<std::string>& tariffs_names,
    const std::set<std::string>& start_geoarea_names,
    bool empty_cache = false) {
  const auto& conditions = MakeConditionsWithGeoarea(
      std::vector<std::set<std::string>>{start_geoarea_names});
  models::ConditionsValidator::ValidateGeoareasA(
      empty_cache ? nullptr : GetGeoareas(), conditions, tariffs_names);
}

}  // namespace

TEST(ConditionsValidator, ValidateGeoareasA__borderline_cases) {
  EXPECT_NO_THROW(CheckValidateGeoareasA({}, {"moscow_airport"}));
  EXPECT_NO_THROW(CheckValidateGeoareasA({"moscow"}, {}));
  EXPECT_NO_THROW(CheckValidateGeoareasA({"moscow"}, {"moscow_airport"}, true));
}

TEST(ConditionsValidator, ValidateGeoareasA__no_trow) {
  EXPECT_NO_THROW(CheckValidateGeoareasA({"moscow"}, {}));
  EXPECT_NO_THROW(CheckValidateGeoareasA({}, {"moscow_airport"}));
  EXPECT_NO_THROW(CheckValidateGeoareasA({"moscow"}, {"moscow"}));
  EXPECT_NO_THROW(CheckValidateGeoareasA({"moscow"}, {"moscow_airport"}));
  EXPECT_NO_THROW(CheckValidateGeoareasA({"paris"}, {"paris_airport"}));
  EXPECT_NO_THROW(CheckValidateGeoareasA({"moscow", "paris"},
                                         {"moscow_airport", "paris_airport"}));
}

TEST(ConditionsValidator, ValidateGeoareasA__trow) {
  EXPECT_THROW(CheckValidateGeoareasA({"moscow"}, {"paris_airport"}),
               discounts::models::Error);
  EXPECT_THROW(CheckValidateGeoareasA({"moscow"}, {"not_valid_name"}),
               discounts::models::Error);
  EXPECT_THROW(
      CheckValidateGeoareasA({"berlin"}, {"moscow_airport", "paris_airport"}),
      discounts::models::Error);
}

TEST(ConditionsValidator, ValidateZones__Valid) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"moscow"s, ZoneType::kTariffZone, true},
                              {"br_root"s, ZoneType::kGeonode, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_NO_THROW(models::ConditionsValidator::ValidateZones(
      conditions, Tree(kBrGeoNodesResponse)));
}

TEST(ConditionsValidator, ValidateZones__EmptyConditions) {
  ASSERT_THROW(
      models::ConditionsValidator::ValidateZones({}, Tree(kBrGeoNodesResponse)),
      discounts::models::Error);
}

TEST(ConditionsValidator, ValidateZones__InValid__invalid_geo_node) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_invalid_zone"s, ZoneType::kGeonode, true}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateZones(
                   conditions, Tree(kBrGeoNodesResponse)),
               discounts::models::Error);
}

TEST(ConditionsValidator, ValidateZones__InValid__br_moscow_covered_by_russia) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_russia"s, ZoneType::kGeonode, true},
                              {"br_moscow"s, ZoneType::kGeonode, true}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateZones(
                   conditions, Tree(kBrGeoNodesResponse)),
               discounts::models::Error);
}

TEST(ConditionsValidator, ValidateZones__InValid__moscow_covered_by_russia) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_russia"s, ZoneType::kGeonode, true},
                              {"moscow"s, ZoneType::kTariffZone, true}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateZones(
                   conditions, Tree(kBrGeoNodesResponse)),
               discounts::models::Error);
}

TEST(ConditionsValidator,
     ValidateZones__InValid__moscow_covered_by_br_moscow_adm) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_moscow_adm"s, ZoneType::kGeonode, true},
                              {"moscow"s, ZoneType::kTariffZone, true}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateZones(
                   conditions, Tree(kBrGeoNodesResponse)),
               discounts::models::Error);
}

TEST(ConditionsValidator, ValidateTimezonesFromZones__Valid) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_moscow_adm"s, ZoneType::kGeonode, false},
                              {"moscow"s, ZoneType::kTariffZone, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_NO_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
      conditions, Tree(kBrGeoNodesResponse), kTariffSettingsData,
      {{}, false, {}, false}, {}));
}

TEST(
    ConditionsValidator,
    ValidateTimezonesFromZones__Valid__several_zones_with_several_timezones_utc) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_moscow"s, ZoneType::kGeonode, false},
                              {"br_tel_aviv"s, ZoneType::kGeonode, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_NO_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
      conditions, Tree(kBrGeoNodesResponse), kTariffSettingsData,
      {{}, true, {}, true}, {}));
}

TEST(
    ConditionsValidator,
    ValidateTimezonesFromZones__Valid__several_zones_with_several_timezones_utc_new) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_moscow"s, ZoneType::kGeonode, false},
                              {"br_tel_aviv"s, ZoneType::kGeonode, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_NO_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
      conditions, Tree(kBrGeoNodesResponse), kTariffSettingsData,
      {{}, false, {}, true}, "UTC"));
}

TEST(ConditionsValidator, ValidateTimezonesFromZones__EmptyConditions) {
  ASSERT_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
                   {}, Tree(kBrGeoNodesResponse), kTariffSettingsData,
                   {{}, false, {}, false}, {}),
               discounts::models::Error);
}

TEST(
    ConditionsValidator,
    ValidateTimezonesFromZones__InValid__several_zones_with_several_timezones_not_utc) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_moscow"s, ZoneType::kGeonode, false},
                              {"br_tel_aviv"s, ZoneType::kTariffZone, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
                   conditions, Tree(kBrGeoNodesResponse), kTariffSettingsData,
                   {{}, false, {}, false}, {}),
               discounts::models::Error);
}

TEST(
    ConditionsValidator,
    ValidateTimezonesFromZones__InValid__several_zones_with_several_timezones_not_utc_new) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"br_moscow"s, ZoneType::kGeonode, false},
                              {"br_tel_aviv"s, ZoneType::kTariffZone, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
                   conditions, Tree(kBrGeoNodesResponse), kTariffSettingsData,
                   {{}, true, {}, false}, "Europe/Moscow"),
               discounts::models::Error);
}

TEST(ConditionsValidator,
     ValidateTimezonesFromZones__InValid__invalid_tariff_zone) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"invalid"s, ZoneType::kTariffZone, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
                   conditions, Tree(kBrGeoNodesResponse), kTariffSettingsData,
                   {{}, false, {}, false}, {}),
               discounts::models::Error);
}

TEST(ConditionsValidator,
     ValidateTimezonesFromZones__InValid__invalid_geonode) {
  const auto& condition =
      MakeRuleCondition(models::names::conditions::kZone,
                        Zones{{"invalid"s, ZoneType::kGeonode, false}});
  const auto& conditions = MakeConditionsMap(condition);
  ASSERT_THROW(models::ConditionsValidator::ValidateTimezonesFromZones(
                   conditions, Tree(kBrGeoNodesResponse), kTariffSettingsData,
                   {{}, false, {}, false}, {}),
               discounts::models::Error);
}

TEST(ConditionsValidator, ValidatePointBIsSetGeoareaBSetRelation) {
  const auto& geoarea_b_set_condition =
      MakeRuleCondition(models::names::conditions::kGeoareaBSet, Arrays{{}});
  {
    const auto& point_b_is_set_condition = MakeRuleCondition(
        models::names::conditions::kPointBIsSet, Integers{true});
    auto conditions = MakeConditionsMap(point_b_is_set_condition);
    conditions.Add(
        rules_match::RuleConditions::ValueType{geoarea_b_set_condition});
    ASSERT_NO_THROW(
        models::ConditionsValidator::ValidatePointBIsSet(conditions));
  }
  {
    const auto& point_b_is_set_condition = MakeRuleCondition(
        models::names::conditions::kPointBIsSet, Integers{false});
    auto conditions = MakeConditionsMap(point_b_is_set_condition);
    conditions.Add(
        rules_match::RuleConditions::ValueType{geoarea_b_set_condition});
    ASSERT_THROW(models::ConditionsValidator::ValidatePointBIsSet(conditions),
                 discounts::models::Error);
  }
}

TEST(ConditionsValidator, ValidateApplicationType) {
  const std::unordered_map<std::string, std::string> application_map_discounts{
      {"application_name_1", "application_type_1"},
      {"application_name_2", "application_type_2"}};
  const dynamic_config::ValueDict<std::string> application_map_brand{
      "name",
      {{"application_name_2", "application_type_2"},
       {"application_name_3", "application_type_3"}}};
  {
    const auto& application_type_condition =
        MakeRuleCondition(models::names::conditions::kApplicationType,
                          Strings{"application_type_1"});
    const auto& conditions = MakeConditionsMap(application_type_condition);
    ASSERT_NO_THROW(models::ConditionsValidator::ValidateApplicationType(
        conditions, application_map_discounts, application_map_brand));
  }
  {
    const auto& application_type_condition =
        MakeRuleCondition(models::names::conditions::kApplicationType,
                          Strings{"application_type_2"});
    const auto& conditions = MakeConditionsMap(application_type_condition);
    ASSERT_NO_THROW(models::ConditionsValidator::ValidateApplicationType(
        conditions, application_map_discounts, application_map_brand));
  }
  {
    const auto& application_type_condition =
        MakeRuleCondition(models::names::conditions::kApplicationType,
                          Strings{"application_type_3"});
    const auto& conditions = MakeConditionsMap(application_type_condition);
    ASSERT_NO_THROW(models::ConditionsValidator::ValidateApplicationType(
        conditions, application_map_discounts, application_map_brand));
  }
  {
    const auto& application_type_condition =
        MakeRuleCondition(models::names::conditions::kApplicationType,
                          Strings{"application_type_4"});
    const auto& conditions = MakeConditionsMap(application_type_condition);
    ASSERT_THROW(
        models::ConditionsValidator::ValidateApplicationType(
            conditions, application_map_discounts, application_map_brand),
        discounts::models::Error);
  }
}

TEST(ConditionsValidator, ValidateApplicationCondition) {
  const dynamic_config::ValueDict<std::string> application_map_brand{
      "name", {{"application_name", "application_brand"}}};
  const dynamic_config::ValueDict<std::string> application_map_platform{
      "name", {{"application_name", "application_platform"}}};
  {
    const auto& application_brand_condition =
        MakeRuleCondition(models::names::conditions::kApplicationBrand,
                          Strings{"application_brand"});
    const auto& conditions = MakeConditionsMap(application_brand_condition);
    ASSERT_NO_THROW(models::ConditionsValidator::ValidateApplicationCondition(
        conditions, application_map_brand,
        models::names::conditions::kApplicationBrand));
  }
  {
    const auto& application_brand_condition =
        MakeRuleCondition(models::names::conditions::kApplicationBrand,
                          Strings{"other_application_brand"});
    const auto& conditions = MakeConditionsMap(application_brand_condition);
    ASSERT_THROW(models::ConditionsValidator::ValidateApplicationCondition(
                     conditions, application_map_brand,
                     models::names::conditions::kApplicationBrand),
                 discounts::models::Error);
  }
  {
    const auto& application_platform_condition =
        MakeRuleCondition(models::names::conditions::kApplicationPlatform,
                          Strings{"application_platform"});
    const auto& conditions = MakeConditionsMap(application_platform_condition);
    ASSERT_NO_THROW(models::ConditionsValidator::ValidateApplicationCondition(
        conditions, application_map_platform,
        models::names::conditions::kApplicationPlatform));
  }
  {
    const auto& application_platform_condition =
        MakeRuleCondition(models::names::conditions::kApplicationPlatform,
                          Strings{"other_application_platform"});
    const auto& conditions = MakeConditionsMap(application_platform_condition);
    ASSERT_THROW(models::ConditionsValidator::ValidateApplicationCondition(
                     conditions, application_map_platform,
                     models::names::conditions::kApplicationPlatform),
                 discounts::models::Error);
  }
}
