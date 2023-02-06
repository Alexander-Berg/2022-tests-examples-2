#include "queries.hpp"

#include <models/hierarchy.hpp>
#include <models/match_tree.hpp>

#include <set>

#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include <types/any_other_type.hpp>
#include <types/any_other_value_type.hpp>
#include <types/range.hpp>
#include <types/zone.hpp>

using Query = storages::postgres::Query;

const rules_match::models::Hierarchy kHierarchy =
    formats::json::FromString(R"JSON(
{
    "name": "full_discounts",
    "conditions": [
        {
            "condition_name": "intermediate_point_is_set",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": true,
            "type": "integer"
        },
        {
            "condition_name": "class",
            "default": {
                "value": "default"
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "text"
        },
        {
            "condition_name": "zone",
            "default": {
                "value": {"name": "br_root", "type": "geonode", "is_prioritized": false}
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "zone"
        },
        {
            "condition_name": "order_type",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "text"
        },
        {
            "condition_name": "tag_from_experiment",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "text"
        },
        {
            "condition_name": "tag",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "text"
        },
        {
            "condition_name": "payment_method",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "text"
        },
        {
            "condition_name": "application_type",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "text"
        },
        {
            "condition_name": "has_yaplus",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "integer"
        },
        {
            "condition_name": "tariff",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "text"
        },
        {
            "condition_name": "point_b_is_set",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": true,
            "type": "integer"
        },
        {
            "condition_name": "geoarea_a_set",
            "default": {
                "value": []
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "array"
        },
        {
            "condition_name": "geoarea_b_set",
            "default": {
                "value": []
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "array"
        },
        {
            "condition_name": "surge_range",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": true,
            "exclusions_for_other": true,
            "exclusions_for_type": false,
            "support_any": true,
            "support_other": true,
            "type": "double_range"
        },
        {
            "condition_name": "active_period",
            "default": {
                "value": {
                    "start": "2000-01-01T00:00:00+00:00",
                    "end": "2100-01-01T00:00:00+00:00",
                    "is_start_utc": false,
                    "is_end_utc": false
                }
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "time_range"
        }
    ]
}
)JSON")
        .As<handlers::libraries::discounts_match::HierarchyDescription>();

TEST(GetHierarchyName, Ok) {
  const auto kExpectedDataId = R"SQL(
SELECT
CASE

WHEN exists(
       SELECT __data_id
       FROM ride_discounts.match_rules_full_discounts
       WHERE __data_id = match_data.data_id
   )
   THEN 'full_discounts'

WHEN exists(
       SELECT __data_id
       FROM ride_discounts.match_rules_payment_method_discounts
       WHERE __data_id = match_data.data_id
   )
   THEN 'payment_method_discounts'

WHEN exists(
       SELECT __data_id
       FROM ride_discounts.match_rules_experimental_discounts
       WHERE __data_id = match_data.data_id
   )
   THEN 'experimental_discounts'

END AS hierarchy_name
FROM ride_discounts.match_data
WHERE match_data.data_id = $1
LIMIT 1;
)SQL";
  auto result = rules_match::queries::GetHierarchyName(
      "ride_discounts",
      {"full_discounts", "payment_method_discounts", "experimental_discounts"});
  ASSERT_EQ(result.Statement(), kExpectedDataId);
  ASSERT_EQ(result.GetName(), Query::Name("getting_hierarchy_name_by_data_id"));
}

TEST(GetRulesByIds, Ok) {
  const auto kExpected = R"SQL(
SELECT
  "intermediate_point_is_set"
  ,"class"
  ,"zone"
  ,"order_type"
  ,"tag_from_experiment"
  ,"tag"
  ,"payment_method"
  ,"application_type"
  ,"has_yaplus"
  ,"tariff"
  ,"point_b_is_set"
  ,"geoarea_a_set"
  ,"geoarea_b_set"
  ,"surge_range"
  ,"active_period"
  ,__data_id
  ,__revision
  ,meta_info.value AS meta_info
FROM ride_discounts.match_rules_full_discounts
INNER JOIN ride_discounts.meta_info
  ON __meta_info_id = ride_discounts.meta_info.id
INNER JOIN ride_discounts.match_data
  ON __data_id = ride_discounts.match_data.data_id
WHERE
  (
    __data_id IN (SELECT(UNNEST($1)))
    OR __revision IN (SELECT(UNNEST($2)))
    OR (match_data.data->>'name' LIKE ANY (SELECT(UNNEST($3))))
    OR (NOT meta_info.value->>'create_draft_id' IS NULL AND meta_info.value->>'create_draft_id' IN (SELECT(UNNEST($4))))
  )
  AND __revision > $5
ORDER BY __revision
LIMIT $6;
)SQL";
  auto result =
      rules_match::queries::GetRulesByIds("ride_discounts", kHierarchy);
  ASSERT_EQ(result.Statement(), kExpected);
  ASSERT_EQ(result.GetName(), Query::Name("getting_rules_by_ids"));
}

TEST(GetMatchDataByDataId, Ok) {
  const auto kExpected = R"SQL(
SELECT data, series_id, data_id
FROM schema_name.match_data
WHERE data_id = $1;
)SQL";
  const auto result = rules_match::queries::GetMatchDataByDataId("schema_name");
  ASSERT_EQ(result.Statement(), kExpected);
  ASSERT_EQ(result.GetName(), Query::Name("getting_match_data_by_data_id"));
}

struct GetSelectRulesQueryData {
  const bool match_by_rules = false;
  const bool with_filter_ids = false;
  const std::optional<rules_match::models::Hierarchy::RulesConditions>
      rules_conditions;
  const char* expected_arguments;
  const char* expected_query_statement;
};

TEST(GetIntersectingIds, OkMatchByRules) {
  static const auto kExpected = R"SQL(
WITH data_ids AS (
  SELECT data_id
  FROM ride_discounts.match_data
  WHERE series_id = $2
),
active_period_ids AS (
    SELECT entity_id
    FROM ride_discounts.active_period
    WHERE (
          (ride_discounts.active_period.is_start_utc = ($1->0->>'is_start_utc')::BOOL)
          AND (ride_discounts.active_period.is_end_utc = ($1->0->>'is_end_utc')::BOOL)
          AND (ride_discounts.active_period.entity_value && ($1->0->>'entity_value')::TSTZRANGE)
        )
          AND (LOWER(ride_discounts.active_period.entity_value) <>
               UPPER(ride_discounts.active_period.entity_value))
)
SELECT __revision AS revision
FROM ride_discounts.match_rules_full_discounts
INNER JOIN data_ids ON __data_id = data_ids.data_id
INNER JOIN active_period_ids ON active_period = active_period_ids.entity_id;
)SQL";
  const std::chrono::system_clock::time_point start;
  const auto end = start + std::chrono::seconds{1};
  const auto conditions = kHierarchy.ConvertToRulesConditions(
      rules_match::MatchConditions{std::vector<
          handlers::libraries::discounts_match::MatchCondition>{
          {"active_period",
           std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {start, true, end, true}}}}},
      rules_match::RulesMatchBase::MatchType::StrongMatch);
  auto [query, arguments] = rules_match::queries::GetIntersectingIds(
      "ride_discounts", kHierarchy.GetName(),
      *kHierarchy.GetConditionDescription("active_period"), conditions.back(),
      true);
  ASSERT_EQ(query.GetName(), Query::Name("select_intersecting_data_ids"));
  ASSERT_EQ(query.Statement(), kExpected);
  auto expected_arguments = formats::json::FromString(R"JSON([
  {
      "is_start_utc": true,
      "is_end_utc": true,
       "entity_value": "[1970-01-01 00:00:00 +00:00,1970-01-01 00:00:01 +00:00)"
  }
])JSON");
  ASSERT_EQ(arguments, expected_arguments);
}

TEST(GetIntersectingIds, OkMatchByRulesGroup) {
  static const auto kExpected = R"SQL(
WITH data_ids AS (
  SELECT data_id
  FROM ride_discounts.match_data
  WHERE series_id = $2
),
active_period_ids AS (
    SELECT entity_id
    FROM ride_discounts.active_period
    WHERE (
          (ride_discounts.active_period.is_start_utc = ($1->0->>'is_start_utc')::BOOL)
          AND (ride_discounts.active_period.is_end_utc = ($1->0->>'is_end_utc')::BOOL)
          AND (ride_discounts.active_period.entity_value && ($1->0->>'entity_value')::TSTZRANGE)
        )
          AND (LOWER(ride_discounts.active_period.entity_value) <>
               UPPER(ride_discounts.active_period.entity_value))
)
SELECT DISTINCT __data_id AS data_id
FROM ride_discounts.match_rules_full_discounts
INNER JOIN data_ids ON __data_id = data_ids.data_id
INNER JOIN active_period_ids ON active_period = active_period_ids.entity_id;
)SQL";
  const std::chrono::system_clock::time_point start;
  const auto end = start + std::chrono::seconds{1};
  const auto conditions = kHierarchy.ConvertToRulesConditions(
      rules_match::MatchConditions{std::vector<
          handlers::libraries::discounts_match::MatchCondition>{
          {"active_period",
           std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {start, true, end, true}}}}},
      rules_match::RulesMatchBase::MatchType::StrongMatch);
  auto [query, arguments] = rules_match::queries::GetIntersectingIds(
      "ride_discounts", kHierarchy.GetName(),
      *kHierarchy.GetConditionDescription("active_period"), conditions.back(),
      false);
  ASSERT_EQ(query.GetName(), Query::Name("select_intersecting_data_ids"));
  ASSERT_EQ(query.Statement(), kExpected);
  auto expected_arguments = formats::json::FromString(R"JSON([
  {
      "is_start_utc": true,
      "is_end_utc": true,
       "entity_value": "[1970-01-01 00:00:00 +00:00,1970-01-01 00:00:01 +00:00)"
  }
])JSON");
  ASSERT_EQ(arguments, expected_arguments);
}

TEST(GetIntersectingIds, NoActivePeriodFail) {
  const auto conditions = kHierarchy.ConvertToRulesConditions(
      rules_match::MatchConditions{
          std::vector<handlers::libraries::discounts_match::MatchCondition>{}},
      rules_match::RulesMatchBase::MatchType::WeakMatch);
  EXPECT_THROW((rules_match::queries::GetIntersectingIds(
                   "ride_discounts", kHierarchy.GetName(),
                   *kHierarchy.GetConditionDescription("active_period"),
                   conditions.back(), true)),
               rules_match::ValidationError);
  EXPECT_THROW((rules_match::queries::GetIntersectingIds(
                   "ride_discounts", kHierarchy.GetName(),
                   *kHierarchy.GetConditionDescription("active_period"),
                   conditions.back(), false)),
               rules_match::ValidationError);
}

class GetSelectRulesQueryP
    : public testing::Test,
      public testing::WithParamInterface<GetSelectRulesQueryData> {};

TEST_P(GetSelectRulesQueryP, Ok) {
  const auto& param = GetParam();
  const auto& [query, arguments] = rules_match::queries::GetSelectRules(
      "ride_discounts", kHierarchy, param.rules_conditions,
      param.match_by_rules, param.with_filter_ids);

  ASSERT_EQ(query.GetName(),
            Query::Name{param.match_by_rules ? "select_rules_query"
                                             : "select_rules_groups_query"});
  ASSERT_EQ(query.Statement(), param.expected_query_statement);
  ASSERT_EQ(arguments, formats::json::FromString(param.expected_arguments));
}

TEST(GetSelectRulesQuery, Error) {
  auto rules_conditions = std::make_optional<
      rules_match::models::Hierarchy::RulesConditions>(
      kHierarchy.ConvertToRulesConditions(
          rules_match::MatchComplexConditions{std::vector<
              handlers::libraries::discounts_match::MatchComplexCondition>{
              {"class",
               handlers::libraries::discounts_match::AnyOtherValueType::kAny}}},
          rules_match::RulesMatchBase::MatchType::WeakMatch));

  ASSERT_THROW(
      rules_match::queries::GetSelectRules("ride_discounts", kHierarchy,
                                           rules_conditions, false, false),
      rules_match::ValidationError);
}

namespace {

const auto kRulesConditions =
    std::make_optional<rules_match::models::Hierarchy::RulesConditions>(
        kHierarchy.ConvertToRulesConditions(
            rules_match::MatchConditions{std::vector<
                handlers::libraries::discounts_match::MatchCondition>{
                {"intermediate_point_is_set", std::vector<int64_t>{1}},
                {"class", std::vector<std::string>{"default"}},
                {"zone",
                 std::vector<handlers::libraries::discounts_match::Zone>{
                     {"br_russia",
                      handlers::libraries::discounts_match::ZoneType::kGeonode,
                      false}}},
                {"geoarea_a_set", std::vector<std::set<std::string>>{{"test"}}},
                {"surge_range",
                 std::vector<
                     handlers::libraries::discounts_match::DoubleRangeValue>{
                     {handlers::libraries::discounts_match::
                          DoubleRangeValueType::kDoubleRange,
                      "0.0", "1.0"}}}}},
            rules_match::RulesMatchBase::MatchType::StrongMatch));

const auto kNotClosedSurgeRangeConditions =
    std::make_optional<rules_match::models::Hierarchy::RulesConditions>(
        kHierarchy.ConvertToRulesConditions(
            rules_match::MatchConditions{std::vector<
                handlers::libraries::discounts_match::MatchCondition>{
                {"surge_range",
                 std::vector<
                     handlers::libraries::discounts_match::DoubleRangeValue>{
                     {handlers::libraries::discounts_match::
                          DoubleRangeValueType::kDoubleRange,
                      "0.0", std::nullopt}}}}},
            rules_match::RulesMatchBase::MatchType::StrongMatch));

const auto kEmptyRulesConditions =
    std::make_optional<rules_match::models::Hierarchy::RulesConditions>(
        kHierarchy.ConvertToRulesConditions(
            rules_match::MatchConditions{},
            rules_match::RulesMatchBase::MatchType::WeakMatch));

constexpr auto kSelectRulesQueryMatchByRules = R"SQL(WITH "filtered_rules" AS (
  SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN ride_discounts.meta_info
  ON ride_discounts.meta_info.id = ride_discounts.match_rules_full_discounts.__meta_info_id
  WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
, "intermediate_point_is_set" AS (
  SELECT *
  FROM ride_discounts.intermediate_point_is_set
  WHERE (ride_discounts.intermediate_point_is_set.entity_value = 1))
, "class" AS (
  SELECT *
  FROM ride_discounts.class
  WHERE (ride_discounts.class.entity_value = $1->>0))
, "zone" AS (
  SELECT *
  FROM ride_discounts.zone
  WHERE ((ride_discounts.zone.is_prioritized = false) AND (ride_discounts.zone.name = $1->>1)) AND (ride_discounts.zone.type = 'geonode'))
, "order_type" AS (
  SELECT *
  FROM ride_discounts.order_type
  WHERE (ride_discounts.order_type.entity_type = 'Other'))
, "tag_from_experiment" AS (
  SELECT *
  FROM ride_discounts.tag_from_experiment
  WHERE (ride_discounts.tag_from_experiment.entity_type = 'Other'))
, "tag" AS (
  SELECT *
  FROM ride_discounts.tag
  WHERE (ride_discounts.tag.entity_type = 'Other'))
, "payment_method" AS (
  SELECT *
  FROM ride_discounts.payment_method
  WHERE (ride_discounts.payment_method.entity_type = 'Other'))
, "application_type" AS (
  SELECT *
  FROM ride_discounts.application_type
  WHERE (ride_discounts.application_type.entity_type = 'Other'))
, "has_yaplus" AS (
  SELECT *
  FROM ride_discounts.has_yaplus
  WHERE (ride_discounts.has_yaplus.entity_type = 'Other'))
, "tariff" AS (
  SELECT *
  FROM ride_discounts.tariff
  WHERE (ride_discounts.tariff.entity_type = 'Other'))
, "point_b_is_set" AS (
  SELECT *
  FROM ride_discounts.point_b_is_set
  WHERE (ride_discounts.point_b_is_set.entity_type = 'Other'))
, "geoarea_a_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_a_set
  WHERE (ride_discounts.geoarea_a_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->2)))))
, "geoarea_b_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_b_set
  WHERE (ride_discounts.geoarea_b_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->3)))))
, "surge_range" AS (
  SELECT *
  FROM ride_discounts.surge_range
  WHERE (ride_discounts.surge_range.entity_value && '[0,1.000000)'))
, "active_period" AS (
  SELECT *
  FROM ride_discounts.active_period
  WHERE (
          (ride_discounts.active_period.is_start_utc = ($1->4->>'is_start_utc')::BOOL)
          AND (ride_discounts.active_period.is_end_utc = ($1->4->>'is_end_utc')::BOOL)
          AND (ride_discounts.active_period.entity_value && ($1->4->>'entity_value')::TSTZRANGE)
        ))
SELECT *
FROM "filtered_rules"
  INNER JOIN "intermediate_point_is_set" ON "intermediate_point_is_set".entity_id = "filtered_rules".intermediate_point_is_set
  INNER JOIN "class" ON "class".entity_id = "filtered_rules".class
  INNER JOIN "zone" ON "zone".entity_id = "filtered_rules".zone
  INNER JOIN "order_type" ON "order_type".entity_id = "filtered_rules".order_type
  INNER JOIN "tag_from_experiment" ON "tag_from_experiment".entity_id = "filtered_rules".tag_from_experiment
  INNER JOIN "tag" ON "tag".entity_id = "filtered_rules".tag
  INNER JOIN "payment_method" ON "payment_method".entity_id = "filtered_rules".payment_method
  INNER JOIN "application_type" ON "application_type".entity_id = "filtered_rules".application_type
  INNER JOIN "has_yaplus" ON "has_yaplus".entity_id = "filtered_rules".has_yaplus
  INNER JOIN "tariff" ON "tariff".entity_id = "filtered_rules".tariff
  INNER JOIN "point_b_is_set" ON "point_b_is_set".entity_id = "filtered_rules".point_b_is_set
  INNER JOIN "geoarea_a_set" ON "geoarea_a_set".entity_id = "filtered_rules".geoarea_a_set
  INNER JOIN "geoarea_b_set" ON "geoarea_b_set".entity_id = "filtered_rules".geoarea_b_set
  INNER JOIN "surge_range" ON "surge_range".entity_id = "filtered_rules".surge_range
  INNER JOIN "active_period" ON "active_period".entity_id = "filtered_rules".active_period
ORDER BY __revision
LIMIT $3;)SQL";

constexpr auto kSelectRulesQueryWithNotClosedSurgeRange =
    R"SQL(WITH "filtered_rules" AS (
  SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN ride_discounts.meta_info
  ON ride_discounts.meta_info.id = ride_discounts.match_rules_full_discounts.__meta_info_id
  WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
, "intermediate_point_is_set" AS (
  SELECT *
  FROM ride_discounts.intermediate_point_is_set
  WHERE (ride_discounts.intermediate_point_is_set.entity_type = 'Other'))
, "class" AS (
  SELECT *
  FROM ride_discounts.class
  WHERE (ride_discounts.class.entity_value = $1->>0))
, "zone" AS (
  SELECT *
  FROM ride_discounts.zone
  WHERE ((ride_discounts.zone.is_prioritized = false) AND (ride_discounts.zone.name = $1->>1)) AND (ride_discounts.zone.type = 'geonode'))
, "order_type" AS (
  SELECT *
  FROM ride_discounts.order_type
  WHERE (ride_discounts.order_type.entity_type = 'Other'))
, "tag_from_experiment" AS (
  SELECT *
  FROM ride_discounts.tag_from_experiment
  WHERE (ride_discounts.tag_from_experiment.entity_type = 'Other'))
, "tag" AS (
  SELECT *
  FROM ride_discounts.tag
  WHERE (ride_discounts.tag.entity_type = 'Other'))
, "payment_method" AS (
  SELECT *
  FROM ride_discounts.payment_method
  WHERE (ride_discounts.payment_method.entity_type = 'Other'))
, "application_type" AS (
  SELECT *
  FROM ride_discounts.application_type
  WHERE (ride_discounts.application_type.entity_type = 'Other'))
, "has_yaplus" AS (
  SELECT *
  FROM ride_discounts.has_yaplus
  WHERE (ride_discounts.has_yaplus.entity_type = 'Other'))
, "tariff" AS (
  SELECT *
  FROM ride_discounts.tariff
  WHERE (ride_discounts.tariff.entity_type = 'Other'))
, "point_b_is_set" AS (
  SELECT *
  FROM ride_discounts.point_b_is_set
  WHERE (ride_discounts.point_b_is_set.entity_type = 'Other'))
, "geoarea_a_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_a_set
  WHERE (ride_discounts.geoarea_a_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->2)))))
, "geoarea_b_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_b_set
  WHERE (ride_discounts.geoarea_b_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->3)))))
, "surge_range" AS (
  SELECT *
  FROM ride_discounts.surge_range
  WHERE (ride_discounts.surge_range.entity_value && '[0,)'))
, "active_period" AS (
  SELECT *
  FROM ride_discounts.active_period
  WHERE (
          (ride_discounts.active_period.is_start_utc = ($1->4->>'is_start_utc')::BOOL)
          AND (ride_discounts.active_period.is_end_utc = ($1->4->>'is_end_utc')::BOOL)
          AND (ride_discounts.active_period.entity_value && ($1->4->>'entity_value')::TSTZRANGE)
        ))
SELECT *
FROM "filtered_rules"
  INNER JOIN "intermediate_point_is_set" ON "intermediate_point_is_set".entity_id = "filtered_rules".intermediate_point_is_set
  INNER JOIN "class" ON "class".entity_id = "filtered_rules".class
  INNER JOIN "zone" ON "zone".entity_id = "filtered_rules".zone
  INNER JOIN "order_type" ON "order_type".entity_id = "filtered_rules".order_type
  INNER JOIN "tag_from_experiment" ON "tag_from_experiment".entity_id = "filtered_rules".tag_from_experiment
  INNER JOIN "tag" ON "tag".entity_id = "filtered_rules".tag
  INNER JOIN "payment_method" ON "payment_method".entity_id = "filtered_rules".payment_method
  INNER JOIN "application_type" ON "application_type".entity_id = "filtered_rules".application_type
  INNER JOIN "has_yaplus" ON "has_yaplus".entity_id = "filtered_rules".has_yaplus
  INNER JOIN "tariff" ON "tariff".entity_id = "filtered_rules".tariff
  INNER JOIN "point_b_is_set" ON "point_b_is_set".entity_id = "filtered_rules".point_b_is_set
  INNER JOIN "geoarea_a_set" ON "geoarea_a_set".entity_id = "filtered_rules".geoarea_a_set
  INNER JOIN "geoarea_b_set" ON "geoarea_b_set".entity_id = "filtered_rules".geoarea_b_set
  INNER JOIN "surge_range" ON "surge_range".entity_id = "filtered_rules".surge_range
  INNER JOIN "active_period" ON "active_period".entity_id = "filtered_rules".active_period
ORDER BY __revision
LIMIT $3;)SQL";

constexpr auto kSelectRulesQueryMatchByRulesGroups =
    R"SQL(WITH "intermediate_point_is_set" AS (
  SELECT *
  FROM ride_discounts.intermediate_point_is_set
  WHERE (ride_discounts.intermediate_point_is_set.entity_value = 1))
, "class" AS (
  SELECT *
  FROM ride_discounts.class
  WHERE (ride_discounts.class.entity_value = $1->>0))
, "zone" AS (
  SELECT *
  FROM ride_discounts.zone
  WHERE ((ride_discounts.zone.is_prioritized = false) AND (ride_discounts.zone.name = $1->>1)) AND (ride_discounts.zone.type = 'geonode'))
, "order_type" AS (
  SELECT *
  FROM ride_discounts.order_type
  WHERE (ride_discounts.order_type.entity_type = 'Other'))
, "tag_from_experiment" AS (
  SELECT *
  FROM ride_discounts.tag_from_experiment
  WHERE (ride_discounts.tag_from_experiment.entity_type = 'Other'))
, "tag" AS (
  SELECT *
  FROM ride_discounts.tag
  WHERE (ride_discounts.tag.entity_type = 'Other'))
, "payment_method" AS (
  SELECT *
  FROM ride_discounts.payment_method
  WHERE (ride_discounts.payment_method.entity_type = 'Other'))
, "application_type" AS (
  SELECT *
  FROM ride_discounts.application_type
  WHERE (ride_discounts.application_type.entity_type = 'Other'))
, "has_yaplus" AS (
  SELECT *
  FROM ride_discounts.has_yaplus
  WHERE (ride_discounts.has_yaplus.entity_type = 'Other'))
, "tariff" AS (
  SELECT *
  FROM ride_discounts.tariff
  WHERE (ride_discounts.tariff.entity_type = 'Other'))
, "point_b_is_set" AS (
  SELECT *
  FROM ride_discounts.point_b_is_set
  WHERE (ride_discounts.point_b_is_set.entity_type = 'Other'))
, "geoarea_a_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_a_set
  WHERE (ride_discounts.geoarea_a_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->2)))))
, "geoarea_b_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_b_set
  WHERE (ride_discounts.geoarea_b_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->3)))))
, "surge_range" AS (
  SELECT *
  FROM ride_discounts.surge_range
  WHERE (ride_discounts.surge_range.entity_value && '[0,1.000000)'))
, "active_period" AS (
  SELECT *
  FROM ride_discounts.active_period
  WHERE (
          (ride_discounts.active_period.is_start_utc = ($1->4->>'is_start_utc')::BOOL)
          AND (ride_discounts.active_period.is_end_utc = ($1->4->>'is_end_utc')::BOOL)
          AND (ride_discounts.active_period.entity_value && ($1->4->>'entity_value')::TSTZRANGE)
        ))
, "data_ids" AS (
  SELECT DISTINCT match_rules_full_discounts.__data_id AS data_id
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN "intermediate_point_is_set" ON "intermediate_point_is_set".entity_id = match_rules_full_discounts.intermediate_point_is_set
  INNER JOIN "class" ON "class".entity_id = match_rules_full_discounts.class
  INNER JOIN "zone" ON "zone".entity_id = match_rules_full_discounts.zone
  INNER JOIN "order_type" ON "order_type".entity_id = match_rules_full_discounts.order_type
  INNER JOIN "tag_from_experiment" ON "tag_from_experiment".entity_id = match_rules_full_discounts.tag_from_experiment
  INNER JOIN "tag" ON "tag".entity_id = match_rules_full_discounts.tag
  INNER JOIN "payment_method" ON "payment_method".entity_id = match_rules_full_discounts.payment_method
  INNER JOIN "application_type" ON "application_type".entity_id = match_rules_full_discounts.application_type
  INNER JOIN "has_yaplus" ON "has_yaplus".entity_id = match_rules_full_discounts.has_yaplus
  INNER JOIN "tariff" ON "tariff".entity_id = match_rules_full_discounts.tariff
  INNER JOIN "point_b_is_set" ON "point_b_is_set".entity_id = match_rules_full_discounts.point_b_is_set
  INNER JOIN "geoarea_a_set" ON "geoarea_a_set".entity_id = match_rules_full_discounts.geoarea_a_set
  INNER JOIN "geoarea_b_set" ON "geoarea_b_set".entity_id = match_rules_full_discounts.geoarea_b_set
  INNER JOIN "surge_range" ON "surge_range".entity_id = match_rules_full_discounts.surge_range
  INNER JOIN "active_period" ON "active_period".entity_id = match_rules_full_discounts.active_period
  INNER JOIN ride_discounts.match_data
  ON ride_discounts.match_data.data_id = ride_discounts.match_rules_full_discounts.__data_id
  WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
FROM ride_discounts.match_rules_full_discounts
INNER JOIN "data_ids"
ON __data_id = "data_ids".data_id
INNER JOIN ride_discounts.meta_info
ON __meta_info_id = ride_discounts.meta_info.id
WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL)
ORDER BY __revision
LIMIT $3;
)SQL";

constexpr auto kSelectRulesQueryMatchByRulesEmpty =
    R"SQL(WITH "filtered_rules" AS (
  SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN ride_discounts.meta_info
  ON ride_discounts.meta_info.id = ride_discounts.match_rules_full_discounts.__meta_info_id
  WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
SELECT *
FROM "filtered_rules"
ORDER BY __revision
LIMIT $3;)SQL";

constexpr auto kSelectRulesQueryMatchByRulesGroupsEmpty =
    R"SQL(WITH "data_ids" AS (
  SELECT DISTINCT match_rules_full_discounts.__data_id AS data_id
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN ride_discounts.match_data
  ON ride_discounts.match_data.data_id = ride_discounts.match_rules_full_discounts.__data_id
  WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
FROM ride_discounts.match_rules_full_discounts
INNER JOIN "data_ids"
ON __data_id = "data_ids".data_id
INNER JOIN ride_discounts.meta_info
ON __meta_info_id = ride_discounts.meta_info.id
WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL)
ORDER BY __revision
LIMIT $3;
)SQL";

constexpr auto kSelectRulesQueryMatchByRulesIds =
    R"SQL(WITH "filtered_rules" AS (
  SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN ride_discounts.meta_info
  ON ride_discounts.meta_info.id = ride_discounts.match_rules_full_discounts.__meta_info_id
  WHERE     __revision IN (SELECT(UNNEST($4)))
        AND __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
, "intermediate_point_is_set" AS (
  SELECT *
  FROM ride_discounts.intermediate_point_is_set
  WHERE (ride_discounts.intermediate_point_is_set.entity_value = 1))
, "class" AS (
  SELECT *
  FROM ride_discounts.class
  WHERE (ride_discounts.class.entity_value = $1->>0))
, "zone" AS (
  SELECT *
  FROM ride_discounts.zone
  WHERE ((ride_discounts.zone.is_prioritized = false) AND (ride_discounts.zone.name = $1->>1)) AND (ride_discounts.zone.type = 'geonode'))
, "order_type" AS (
  SELECT *
  FROM ride_discounts.order_type
  WHERE (ride_discounts.order_type.entity_type = 'Other'))
, "tag_from_experiment" AS (
  SELECT *
  FROM ride_discounts.tag_from_experiment
  WHERE (ride_discounts.tag_from_experiment.entity_type = 'Other'))
, "tag" AS (
  SELECT *
  FROM ride_discounts.tag
  WHERE (ride_discounts.tag.entity_type = 'Other'))
, "payment_method" AS (
  SELECT *
  FROM ride_discounts.payment_method
  WHERE (ride_discounts.payment_method.entity_type = 'Other'))
, "application_type" AS (
  SELECT *
  FROM ride_discounts.application_type
  WHERE (ride_discounts.application_type.entity_type = 'Other'))
, "has_yaplus" AS (
  SELECT *
  FROM ride_discounts.has_yaplus
  WHERE (ride_discounts.has_yaplus.entity_type = 'Other'))
, "tariff" AS (
  SELECT *
  FROM ride_discounts.tariff
  WHERE (ride_discounts.tariff.entity_type = 'Other'))
, "point_b_is_set" AS (
  SELECT *
  FROM ride_discounts.point_b_is_set
  WHERE (ride_discounts.point_b_is_set.entity_type = 'Other'))
, "geoarea_a_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_a_set
  WHERE (ride_discounts.geoarea_a_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->2)))))
, "geoarea_b_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_b_set
  WHERE (ride_discounts.geoarea_b_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->3)))))
, "surge_range" AS (
  SELECT *
  FROM ride_discounts.surge_range
  WHERE (ride_discounts.surge_range.entity_value && '[0,1.000000)'))
, "active_period" AS (
  SELECT *
  FROM ride_discounts.active_period
  WHERE (
          (ride_discounts.active_period.is_start_utc = ($1->4->>'is_start_utc')::BOOL)
          AND (ride_discounts.active_period.is_end_utc = ($1->4->>'is_end_utc')::BOOL)
          AND (ride_discounts.active_period.entity_value && ($1->4->>'entity_value')::TSTZRANGE)
        ))
SELECT *
FROM "filtered_rules"
  INNER JOIN "intermediate_point_is_set" ON "intermediate_point_is_set".entity_id = "filtered_rules".intermediate_point_is_set
  INNER JOIN "class" ON "class".entity_id = "filtered_rules".class
  INNER JOIN "zone" ON "zone".entity_id = "filtered_rules".zone
  INNER JOIN "order_type" ON "order_type".entity_id = "filtered_rules".order_type
  INNER JOIN "tag_from_experiment" ON "tag_from_experiment".entity_id = "filtered_rules".tag_from_experiment
  INNER JOIN "tag" ON "tag".entity_id = "filtered_rules".tag
  INNER JOIN "payment_method" ON "payment_method".entity_id = "filtered_rules".payment_method
  INNER JOIN "application_type" ON "application_type".entity_id = "filtered_rules".application_type
  INNER JOIN "has_yaplus" ON "has_yaplus".entity_id = "filtered_rules".has_yaplus
  INNER JOIN "tariff" ON "tariff".entity_id = "filtered_rules".tariff
  INNER JOIN "point_b_is_set" ON "point_b_is_set".entity_id = "filtered_rules".point_b_is_set
  INNER JOIN "geoarea_a_set" ON "geoarea_a_set".entity_id = "filtered_rules".geoarea_a_set
  INNER JOIN "geoarea_b_set" ON "geoarea_b_set".entity_id = "filtered_rules".geoarea_b_set
  INNER JOIN "surge_range" ON "surge_range".entity_id = "filtered_rules".surge_range
  INNER JOIN "active_period" ON "active_period".entity_id = "filtered_rules".active_period
ORDER BY __revision
LIMIT $3;)SQL";

constexpr auto kSelectRulesQueryMatchByRulesGroupsIds =
    R"SQL(WITH "intermediate_point_is_set" AS (
  SELECT *
  FROM ride_discounts.intermediate_point_is_set
  WHERE (ride_discounts.intermediate_point_is_set.entity_value = 1))
, "class" AS (
  SELECT *
  FROM ride_discounts.class
  WHERE (ride_discounts.class.entity_value = $1->>0))
, "zone" AS (
  SELECT *
  FROM ride_discounts.zone
  WHERE ((ride_discounts.zone.is_prioritized = false) AND (ride_discounts.zone.name = $1->>1)) AND (ride_discounts.zone.type = 'geonode'))
, "order_type" AS (
  SELECT *
  FROM ride_discounts.order_type
  WHERE (ride_discounts.order_type.entity_type = 'Other'))
, "tag_from_experiment" AS (
  SELECT *
  FROM ride_discounts.tag_from_experiment
  WHERE (ride_discounts.tag_from_experiment.entity_type = 'Other'))
, "tag" AS (
  SELECT *
  FROM ride_discounts.tag
  WHERE (ride_discounts.tag.entity_type = 'Other'))
, "payment_method" AS (
  SELECT *
  FROM ride_discounts.payment_method
  WHERE (ride_discounts.payment_method.entity_type = 'Other'))
, "application_type" AS (
  SELECT *
  FROM ride_discounts.application_type
  WHERE (ride_discounts.application_type.entity_type = 'Other'))
, "has_yaplus" AS (
  SELECT *
  FROM ride_discounts.has_yaplus
  WHERE (ride_discounts.has_yaplus.entity_type = 'Other'))
, "tariff" AS (
  SELECT *
  FROM ride_discounts.tariff
  WHERE (ride_discounts.tariff.entity_type = 'Other'))
, "point_b_is_set" AS (
  SELECT *
  FROM ride_discounts.point_b_is_set
  WHERE (ride_discounts.point_b_is_set.entity_type = 'Other'))
, "geoarea_a_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_a_set
  WHERE (ride_discounts.geoarea_a_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->2)))))
, "geoarea_b_set" AS (
  SELECT *
  FROM ride_discounts.geoarea_b_set
  WHERE (ride_discounts.geoarea_b_set.entity_value = (ARRAY(SELECT jsonb_array_elements_text($1->3)))))
, "surge_range" AS (
  SELECT *
  FROM ride_discounts.surge_range
  WHERE (ride_discounts.surge_range.entity_value && '[0,1.000000)'))
, "active_period" AS (
  SELECT *
  FROM ride_discounts.active_period
  WHERE (
          (ride_discounts.active_period.is_start_utc = ($1->4->>'is_start_utc')::BOOL)
          AND (ride_discounts.active_period.is_end_utc = ($1->4->>'is_end_utc')::BOOL)
          AND (ride_discounts.active_period.entity_value && ($1->4->>'entity_value')::TSTZRANGE)
        ))
, "filtered_data_ids" AS (
  SELECT match_data.data_id
  FROM ride_discounts.match_data
  WHERE data_id IN (SELECT(UNNEST($4))))
, "data_ids" AS (
  SELECT DISTINCT match_rules_full_discounts.__data_id AS data_id
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN "intermediate_point_is_set" ON "intermediate_point_is_set".entity_id = match_rules_full_discounts.intermediate_point_is_set
  INNER JOIN "class" ON "class".entity_id = match_rules_full_discounts.class
  INNER JOIN "zone" ON "zone".entity_id = match_rules_full_discounts.zone
  INNER JOIN "order_type" ON "order_type".entity_id = match_rules_full_discounts.order_type
  INNER JOIN "tag_from_experiment" ON "tag_from_experiment".entity_id = match_rules_full_discounts.tag_from_experiment
  INNER JOIN "tag" ON "tag".entity_id = match_rules_full_discounts.tag
  INNER JOIN "payment_method" ON "payment_method".entity_id = match_rules_full_discounts.payment_method
  INNER JOIN "application_type" ON "application_type".entity_id = match_rules_full_discounts.application_type
  INNER JOIN "has_yaplus" ON "has_yaplus".entity_id = match_rules_full_discounts.has_yaplus
  INNER JOIN "tariff" ON "tariff".entity_id = match_rules_full_discounts.tariff
  INNER JOIN "point_b_is_set" ON "point_b_is_set".entity_id = match_rules_full_discounts.point_b_is_set
  INNER JOIN "geoarea_a_set" ON "geoarea_a_set".entity_id = match_rules_full_discounts.geoarea_a_set
  INNER JOIN "geoarea_b_set" ON "geoarea_b_set".entity_id = match_rules_full_discounts.geoarea_b_set
  INNER JOIN "surge_range" ON "surge_range".entity_id = match_rules_full_discounts.surge_range
  INNER JOIN "active_period" ON "active_period".entity_id = match_rules_full_discounts.active_period
  INNER JOIN "filtered_data_ids"
  ON "filtered_data_ids".data_id = ride_discounts.match_rules_full_discounts.__data_id
  WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
FROM ride_discounts.match_rules_full_discounts
INNER JOIN "data_ids"
ON __data_id = "data_ids".data_id
INNER JOIN ride_discounts.meta_info
ON __meta_info_id = ride_discounts.meta_info.id
WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL)
ORDER BY __revision
LIMIT $3;
)SQL";

constexpr auto kSelectRulesQueryMatchByRulesIdsEmpty =
    R"SQL(WITH "filtered_rules" AS (
  SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN ride_discounts.meta_info
  ON ride_discounts.meta_info.id = ride_discounts.match_rules_full_discounts.__meta_info_id
  WHERE     __revision IN (SELECT(UNNEST($4)))
        AND __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
SELECT *
FROM "filtered_rules"
ORDER BY __revision
LIMIT $3;)SQL";

constexpr auto kSelectRulesQueryMatchByRulesGroupsIdsEmpty =
    R"SQL(WITH "filtered_data_ids" AS (
  SELECT match_data.data_id
  FROM ride_discounts.match_data
  WHERE data_id IN (SELECT(UNNEST($4))))
, "data_ids" AS (
  SELECT DISTINCT match_rules_full_discounts.__data_id AS data_id
  FROM ride_discounts.match_rules_full_discounts
  INNER JOIN "filtered_data_ids"
  ON "filtered_data_ids".data_id = ride_discounts.match_rules_full_discounts.__data_id
  WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL))
SELECT meta_info.value AS meta_info
, match_rules_full_discounts.__data_id
, match_rules_full_discounts.__revision
, match_rules_full_discounts.__updated_at
, match_rules_full_discounts."intermediate_point_is_set"
, match_rules_full_discounts."class"
, match_rules_full_discounts."zone"
, match_rules_full_discounts."order_type"
, match_rules_full_discounts."tag_from_experiment"
, match_rules_full_discounts."tag"
, match_rules_full_discounts."payment_method"
, match_rules_full_discounts."application_type"
, match_rules_full_discounts."has_yaplus"
, match_rules_full_discounts."tariff"
, match_rules_full_discounts."point_b_is_set"
, match_rules_full_discounts."geoarea_a_set"
, match_rules_full_discounts."geoarea_b_set"
, match_rules_full_discounts."surge_range"
, match_rules_full_discounts."active_period"
FROM ride_discounts.match_rules_full_discounts
INNER JOIN "data_ids"
ON __data_id = "data_ids".data_id
INNER JOIN ride_discounts.meta_info
ON __meta_info_id = ride_discounts.meta_info.id
WHERE __revision > $2 AND (NOT empty_discount OR empty_discount IS NULL)
ORDER BY __revision
LIMIT $3;
)SQL";

}  // namespace

INSTANTIATE_TEST_SUITE_P(
    GetSelectRulesQuery, GetSelectRulesQueryP,
    testing::Values(
        GetSelectRulesQueryData{
            true, false, kRulesConditions,
            "[\"default\",\"br_russia\",[\"test\"],[],{\"is_start_utc\":false,"
            "\"is_end_utc\":false,\"entity_value\":\"[2000-01-01 00:00:00 "
            "+00:00,2100-01-01 00:00:00 +00:00)\"}]",
            kSelectRulesQueryMatchByRules},
        GetSelectRulesQueryData{
            true, false, kNotClosedSurgeRangeConditions,
            "[\"default\",\"br_root\",[],[],{\"is_start_utc\":false,\"is_end_"
            "utc\":false,\"entity_value\":\"[2000-01-01 00:00:00 "
            "+00:00,2100-01-01 00:00:00 +00:00)\"}]",
            kSelectRulesQueryWithNotClosedSurgeRange},
        GetSelectRulesQueryData{
            false, false, kRulesConditions,
            "[\"default\",\"br_russia\",[\"test\"],[],{\"is_start_utc\":false,"
            "\"is_end_utc\":false,\"entity_value\":\"[2000-01-01 00:00:00 "
            "+00:00,2100-01-01 00:00:00 +00:00)\"}]",
            kSelectRulesQueryMatchByRulesGroups},
        GetSelectRulesQueryData{true, false, kEmptyRulesConditions, "[]",
                                kSelectRulesQueryMatchByRulesEmpty},
        GetSelectRulesQueryData{false, false, kEmptyRulesConditions, "[]",
                                kSelectRulesQueryMatchByRulesGroupsEmpty},
        GetSelectRulesQueryData{true, false, std::nullopt, "[]",
                                kSelectRulesQueryMatchByRulesEmpty},
        GetSelectRulesQueryData{false, false, std::nullopt, "[]",
                                kSelectRulesQueryMatchByRulesGroupsEmpty},
        GetSelectRulesQueryData{
            true, true, kRulesConditions,
            "[\"default\",\"br_russia\",[\"test\"],[],{\"is_start_utc\":false,"
            "\"is_end_utc\":false,\"entity_value\":\"[2000-01-01 00:00:00 "
            "+00:00,2100-01-01 00:00:00 +00:00)\"}]",
            kSelectRulesQueryMatchByRulesIds},
        GetSelectRulesQueryData{
            false, true, kRulesConditions,
            "[\"default\",\"br_russia\",[\"test\"],[],{\"is_start_utc\":false,"
            "\"is_end_utc\":false,\"entity_value\":\"[2000-01-01 00:00:00 "
            "+00:00,2100-01-01 00:00:00 +00:00)\"}]",
            kSelectRulesQueryMatchByRulesGroupsIds},
        GetSelectRulesQueryData{true, true, kEmptyRulesConditions, "[]",
                                kSelectRulesQueryMatchByRulesIdsEmpty},
        GetSelectRulesQueryData{false, true, kEmptyRulesConditions, "[]",
                                kSelectRulesQueryMatchByRulesGroupsIdsEmpty},
        GetSelectRulesQueryData{true, true, std::nullopt, "[]",
                                kSelectRulesQueryMatchByRulesIdsEmpty},
        GetSelectRulesQueryData{false, true, std::nullopt, "[]",
                                kSelectRulesQueryMatchByRulesGroupsIdsEmpty}));

TEST(GetDataAndExclusions, NoExclusionsOk) {
  static const rules_match::models::Hierarchy kHierarchy =
      formats::json::FromString(R"JSON(
{
    "name": "full_discounts",
    "conditions": [
        {
            "condition_name": "intermediate_point_is_set",
            "default": {
                "value_type": "Other"
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": true,
            "type": "integer"
        },
        {
            "condition_name": "class",
            "default": {
                "value": "default"
            },
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "text"
        }
    ]
}
)JSON")
          .As<handlers::libraries::discounts_match::HierarchyDescription>();

  const auto& query =
      rules_match::queries::GetDataAndExclusions("ride_discounts", kHierarchy);

  ASSERT_EQ(query.GetName(), Query::Name{"select_data_and_exclusions"});
  ASSERT_EQ(query.Statement(),
            R"SQL(
  SELECT data, data_id, series_id
  FROM ride_discounts.match_data
  WHERE match_data.data_id IN (SELECT(UNNEST($1)));
)SQL");
}

TEST(GetDataAndExclusions, ExclusionsOk) {
  const auto& query =
      rules_match::queries::GetDataAndExclusions("ride_discounts", kHierarchy);

  ASSERT_EQ(query.GetName(), Query::Name{"select_data_and_exclusions"});
  ASSERT_EQ(query.Statement(),
            R"SQL(
WITH data_ids AS (
  SELECT data_id
  FROM UNNEST($1) data_id
),
match_data AS (
  SELECT data,
         data_id,
         series_id
  FROM ride_discounts.match_data
  INNER JOIN data_ids USING(data_id)
)
, "order_type" AS (
SELECT data_id, ARRAY_AGG(DISTINCT entity_id) AS excluded_order_type
  FROM ride_discounts.excluded_order_type
  INNER JOIN data_ids USING (data_id)
  GROUP BY data_id)
, "tag_from_experiment" AS (
SELECT data_id, ARRAY_AGG(DISTINCT entity_id) AS excluded_tag_from_experiment
  FROM ride_discounts.excluded_tag_from_experiment
  INNER JOIN data_ids USING (data_id)
  GROUP BY data_id)
, "tag" AS (
SELECT data_id, ARRAY_AGG(DISTINCT entity_id) AS excluded_tag
  FROM ride_discounts.excluded_tag
  INNER JOIN data_ids USING (data_id)
  GROUP BY data_id)
, "payment_method" AS (
SELECT data_id, ARRAY_AGG(DISTINCT entity_id) AS excluded_payment_method
  FROM ride_discounts.excluded_payment_method
  INNER JOIN data_ids USING (data_id)
  GROUP BY data_id)
, "application_type" AS (
SELECT data_id, ARRAY_AGG(DISTINCT entity_id) AS excluded_application_type
  FROM ride_discounts.excluded_application_type
  INNER JOIN data_ids USING (data_id)
  GROUP BY data_id)
, "tariff" AS (
SELECT data_id, ARRAY_AGG(DISTINCT entity_id) AS excluded_tariff
  FROM ride_discounts.excluded_tariff
  INNER JOIN data_ids USING (data_id)
  GROUP BY data_id)
, "surge_range" AS (
SELECT data_id, ARRAY_AGG(DISTINCT entity_id) AS excluded_surge_range
  FROM ride_discounts.excluded_surge_range
  INNER JOIN data_ids USING (data_id)
  GROUP BY data_id)
SELECT match_data.data_id,
       match_data.data,
       match_data.series_id
     , "order_type".excluded_order_type
     , "tag_from_experiment".excluded_tag_from_experiment
     , "tag".excluded_tag
     , "payment_method".excluded_payment_method
     , "application_type".excluded_application_type
     , "tariff".excluded_tariff
     , "surge_range".excluded_surge_range
FROM match_data
LEFT JOIN "order_type" USING (data_id)
LEFT JOIN "tag_from_experiment" USING (data_id)
LEFT JOIN "tag" USING (data_id)
LEFT JOIN "payment_method" USING (data_id)
LEFT JOIN "application_type" USING (data_id)
LEFT JOIN "tariff" USING (data_id)
LEFT JOIN "surge_range" USING (data_id);
)SQL");
}
