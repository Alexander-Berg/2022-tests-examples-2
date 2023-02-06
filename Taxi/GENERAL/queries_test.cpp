#include <discounts-match/components/replication/queries.hpp>

#include <models/hierarchy.hpp>
#include <models/match_tree.hpp>

#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

using Name = storages::postgres::Query::Name;
const auto kHierarchy =
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
                "value_type": "Other"
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
                "value_type": "Other"
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
                "value_type": "Other"
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

const auto kHierarchyWithoutExclusions =
    formats::json::FromString(R"JSON(
{
    "name": "full_discounts",
    "conditions": [
        {
            "condition_name": "label",
            "default": {"value": "default"},
            "exclusions_for_any": false,
            "exclusions_for_other": false,
            "exclusions_for_type": false,
            "support_any": false,
            "support_other": false,
            "type": "text"
        },
        {
            "condition_name": "active_period",
            "default": {
                "value_type": "Other"
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

const auto kExpectedDiscountWithExclusions = R"SQL(
SELECT
to_jsonb(ARRAY(
  SELECT inner_order_type.entity_value
  FROM ride_discounts.excluded_order_type
           INNER JOIN ride_discounts.order_type AS inner_order_type
                      ON inner_order_type.entity_id = excluded_order_type.entity_id
  WHERE excluded_order_type.data_id = match_rules_full_discounts.__data_id
)) AS order_type_exclusions
,
to_jsonb(ARRAY(
  SELECT inner_tag_from_experiment.entity_value
  FROM ride_discounts.excluded_tag_from_experiment
           INNER JOIN ride_discounts.tag_from_experiment AS inner_tag_from_experiment
                      ON inner_tag_from_experiment.entity_id = excluded_tag_from_experiment.entity_id
  WHERE excluded_tag_from_experiment.data_id = match_rules_full_discounts.__data_id
)) AS tag_from_experiment_exclusions
,
to_jsonb(ARRAY(
  SELECT inner_tag.entity_value
  FROM ride_discounts.excluded_tag
           INNER JOIN ride_discounts.tag AS inner_tag
                      ON inner_tag.entity_id = excluded_tag.entity_id
  WHERE excluded_tag.data_id = match_rules_full_discounts.__data_id
)) AS tag_exclusions
,
to_jsonb(ARRAY(
  SELECT inner_payment_method.entity_value
  FROM ride_discounts.excluded_payment_method
           INNER JOIN ride_discounts.payment_method AS inner_payment_method
                      ON inner_payment_method.entity_id = excluded_payment_method.entity_id
  WHERE excluded_payment_method.data_id = match_rules_full_discounts.__data_id
)) AS payment_method_exclusions
,
to_jsonb(ARRAY(
  SELECT inner_application_type.entity_value
  FROM ride_discounts.excluded_application_type
           INNER JOIN ride_discounts.application_type AS inner_application_type
                      ON inner_application_type.entity_id = excluded_application_type.entity_id
  WHERE excluded_application_type.data_id = match_rules_full_discounts.__data_id
)) AS application_type_exclusions
,
to_jsonb(ARRAY(
  SELECT inner_tariff.entity_value
  FROM ride_discounts.excluded_tariff
           INNER JOIN ride_discounts.tariff AS inner_tariff
                      ON inner_tariff.entity_id = excluded_tariff.entity_id
  WHERE excluded_tariff.data_id = match_rules_full_discounts.__data_id
)) AS tariff_exclusions
,
to_jsonb(ARRAY(
  SELECT
    jsonb_build_object(
        'start', lower(inner_surge_range.entity_value),
        'end', upper(inner_surge_range.entity_value)
    )
  FROM ride_discounts.excluded_surge_range
           INNER JOIN ride_discounts.surge_range AS inner_surge_range
                      ON inner_surge_range.entity_id = excluded_surge_range.entity_id
  WHERE excluded_surge_range.data_id = match_rules_full_discounts.__data_id
)) AS surge_range_exclusions
,(SELECT data FROM ride_discounts.match_data WHERE __data_id = match_data.data_id) AS discount
,meta_info.value->>'create_draft_id' AS create_draft_id
,__data_id AS id
FROM ride_discounts.match_rules_full_discounts
INNER JOIN ride_discounts.meta_info
ON ride_discounts.match_rules_full_discounts.__meta_info_id = ride_discounts.meta_info.id

INNER JOIN ride_discounts.order_type ON "order_type".entity_id = match_rules_full_discounts.order_type
INNER JOIN ride_discounts.tag_from_experiment ON "tag_from_experiment".entity_id = match_rules_full_discounts.tag_from_experiment
INNER JOIN ride_discounts.tag ON "tag".entity_id = match_rules_full_discounts.tag
INNER JOIN ride_discounts.payment_method ON "payment_method".entity_id = match_rules_full_discounts.payment_method
INNER JOIN ride_discounts.application_type ON "application_type".entity_id = match_rules_full_discounts.application_type
INNER JOIN ride_discounts.tariff ON "tariff".entity_id = match_rules_full_discounts.tariff
INNER JOIN ride_discounts.surge_range ON "surge_range".entity_id = match_rules_full_discounts.surge_range
WHERE __data_id = $1;
)SQL";

TEST(GetDiscountWithExclusions, Ok) {
  auto result = rules_match::replication::queries::GetDiscountWithExclusions(
      "ride_discounts", rules_match::models::Hierarchy{kHierarchy});
  ASSERT_EQ(result.Statement(), kExpectedDiscountWithExclusions);
  ASSERT_EQ(result.GetName(), Name("replication__discount_with_exclusions"));
}

TEST(GetDiscountWithExclusions, WithoutAnyExclusions) {
  auto result = rules_match::replication::queries::GetDiscountWithExclusions(
      "ride_discounts",
      rules_match::models::Hierarchy{kHierarchyWithoutExclusions});
  static const auto kExpected = R"SQL(
SELECT(SELECT data FROM ride_discounts.match_data WHERE __data_id = match_data.data_id) AS discount
,meta_info.value->>'create_draft_id' AS create_draft_id
,__data_id AS id
FROM ride_discounts.match_rules_full_discounts
INNER JOIN ride_discounts.meta_info
ON ride_discounts.match_rules_full_discounts.__meta_info_id = ride_discounts.meta_info.id

WHERE __data_id = $1;
)SQL";
  ASSERT_EQ(result.Statement(), kExpected);
  ASSERT_EQ(result.GetName(), Name("replication__discount_with_exclusions"));
}

const auto kExpectedRules = R"SQL(
WITH revision_ids AS (
UPDATE ride_discounts.match_rules_full_discounts
SET replication_id = $1
WHERE __revision = ANY(
  SELECT __revision
  FROM ride_discounts.match_rules_full_discounts
  WHERE replicated_at IS NULL
  LIMIT $2
)
RETURNING __revision
)
SELECT

CASE
    WHEN "intermediate_point_is_set".entity_type = 'Type' THEN
    jsonb_build_object('value', "intermediate_point_is_set".entity_value)
    ELSE
    jsonb_build_object('type', "intermediate_point_is_set".entity_type)
END AS "intermediate_point_is_set"
,
jsonb_build_object('value', "class".entity_value) AS "class"
,
jsonb_build_object(
        'name', "zone".name,
        'is_prioritized', "zone".is_prioritized,
        'type', "zone".type) AS "zone"
,
CASE
    WHEN "order_type".entity_type = 'Type' THEN
    jsonb_build_object('value', "order_type".entity_value)
    ELSE
    jsonb_build_object('type', "order_type".entity_type)
END AS "order_type"
,
CASE
    WHEN "tag_from_experiment".entity_type = 'Type' THEN
    jsonb_build_object('value', "tag_from_experiment".entity_value)
    ELSE
    jsonb_build_object('type', "tag_from_experiment".entity_type)
END AS "tag_from_experiment"
,
CASE
    WHEN "tag".entity_type = 'Type' THEN
    jsonb_build_object('value', "tag".entity_value)
    ELSE
    jsonb_build_object('type', "tag".entity_type)
END AS "tag"
,
CASE
    WHEN "payment_method".entity_type = 'Type' THEN
    jsonb_build_object('value', "payment_method".entity_value)
    ELSE
    jsonb_build_object('type', "payment_method".entity_type)
END AS "payment_method"
,
CASE
    WHEN "application_type".entity_type = 'Type' THEN
    jsonb_build_object('value', "application_type".entity_value)
    ELSE
    jsonb_build_object('type', "application_type".entity_type)
END AS "application_type"
,
CASE
    WHEN "has_yaplus".entity_type = 'Type' THEN
    jsonb_build_object('value', "has_yaplus".entity_value)
    ELSE
    jsonb_build_object('type', "has_yaplus".entity_type)
END AS "has_yaplus"
,
CASE
    WHEN "tariff".entity_type = 'Type' THEN
    jsonb_build_object('value', "tariff".entity_value)
    ELSE
    jsonb_build_object('type', "tariff".entity_type)
END AS "tariff"
,
CASE
    WHEN "point_b_is_set".entity_type = 'Type' THEN
    jsonb_build_object('value', "point_b_is_set".entity_value)
    ELSE
    jsonb_build_object('type', "point_b_is_set".entity_type)
END AS "point_b_is_set"
,
to_jsonb("geoarea_a_set".entity_value) AS "geoarea_a_set"
,
to_jsonb("geoarea_b_set".entity_value) AS "geoarea_b_set"
,
CASE
   WHEN
       "surge_range".entity_type = 'Type' THEN
       jsonb_build_object(
           'value', jsonb_build_object(
               'start', lower("surge_range".entity_value)::DECIMAL,
               'end', upper("surge_range".entity_value)::DECIMAL
             )
       )
   ELSE jsonb_build_object('type', "surge_range".entity_type)
END AS "surge_range"

,
jsonb_build_object(
  'start', lower("active_period".entity_value),
  'end', upper("active_period".entity_value),
  'is_start_utc', "active_period".is_start_utc,
  'is_end_utc', "active_period".is_end_utc) AS "active_period"
,meta_info.value AS meta
,__data_id AS match_data_id
,__revision AS id
FROM ride_discounts.match_rules_full_discounts
INNER JOIN ride_discounts.meta_info
ON ride_discounts.match_rules_full_discounts.__meta_info_id = ride_discounts.meta_info.id

INNER JOIN ride_discounts.intermediate_point_is_set ON "intermediate_point_is_set".entity_id = match_rules_full_discounts.intermediate_point_is_set
INNER JOIN ride_discounts.class ON "class".entity_id = match_rules_full_discounts.class
INNER JOIN ride_discounts.zone ON "zone".entity_id = match_rules_full_discounts.zone
INNER JOIN ride_discounts.order_type ON "order_type".entity_id = match_rules_full_discounts.order_type
INNER JOIN ride_discounts.tag_from_experiment ON "tag_from_experiment".entity_id = match_rules_full_discounts.tag_from_experiment
INNER JOIN ride_discounts.tag ON "tag".entity_id = match_rules_full_discounts.tag
INNER JOIN ride_discounts.payment_method ON "payment_method".entity_id = match_rules_full_discounts.payment_method
INNER JOIN ride_discounts.application_type ON "application_type".entity_id = match_rules_full_discounts.application_type
INNER JOIN ride_discounts.has_yaplus ON "has_yaplus".entity_id = match_rules_full_discounts.has_yaplus
INNER JOIN ride_discounts.tariff ON "tariff".entity_id = match_rules_full_discounts.tariff
INNER JOIN ride_discounts.point_b_is_set ON "point_b_is_set".entity_id = match_rules_full_discounts.point_b_is_set
INNER JOIN ride_discounts.geoarea_a_set ON "geoarea_a_set".entity_id = match_rules_full_discounts.geoarea_a_set
INNER JOIN ride_discounts.geoarea_b_set ON "geoarea_b_set".entity_id = match_rules_full_discounts.geoarea_b_set
INNER JOIN ride_discounts.surge_range ON "surge_range".entity_id = match_rules_full_discounts.surge_range
INNER JOIN ride_discounts.active_period ON "active_period".entity_id = match_rules_full_discounts.active_period
WHERE __revision = ANY(SELECT __revision FROM revision_ids);
)SQL";

TEST(GetRules, Ok) {
  auto result = rules_match::replication::queries::GetRules(
      "ride_discounts", rules_match::models::Hierarchy{kHierarchy});
  ASSERT_EQ(result.Statement(), kExpectedRules);
  ASSERT_EQ(result.GetName(), Name("replication__get_rules"));
}

TEST(GetDataId, Ok) {
  const auto kExpectedDataId = R"SQL(
WITH data AS (
SELECT
match_data.data_id
,
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

ELSE NULL
END AS hierarchy_name

FROM ride_discounts.match_data
WHERE ride_discounts.match_data.replicated_at IS NULL
)
SELECT data_id, hierarchy_name
FROM data
WHERE hierarchy_name IS NOT NULL
LIMIT $1;
)SQL";
  auto result = rules_match::replication::queries::GetDataId(
      "ride_discounts",
      {"full_discounts", "payment_method_discounts", "experimental_discounts"});
  ASSERT_EQ(result.Statement(), kExpectedDataId);
  ASSERT_EQ(result.GetName(), Name("replication__get_data_id"));
}

TEST(SetReplicated, Ok) {
  const auto kExpected = R"SQL(
UPDATE ride_discounts.match_data
SET replicated_at = NOW()
WHERE data_id = ANY($1);
)SQL";
  auto result =
      rules_match::replication::queries::SetReplicated("ride_discounts");
  ASSERT_EQ(result.Statement(), kExpected);
  ASSERT_EQ(result.GetName(), Name("replication__set_replicated"));
}

TEST(SetReplicatedRules, Ok) {
  const auto kExpected = R"SQL(
UPDATE ride_discounts.match_rules_full_discounts
SET replicated_at = NOW()
WHERE __revision = ANY($1) AND replication_id = $2;
)SQL";
  auto result = rules_match::replication::queries::SetReplicatedRules(
      "ride_discounts", rules_match::models::Hierarchy{kHierarchy});
  ASSERT_EQ(result.Statement(), kExpected);
  ASSERT_EQ(result.GetName(), Name("replication__set_replicated_rules"));
}
