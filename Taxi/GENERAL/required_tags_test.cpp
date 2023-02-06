#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>
#include <userver/cache/cache_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/json.hpp>

#include <filters/efficiency/fetch_tags_classes/configs/tags_rules.hpp>
#include "required_tags.hpp"

namespace {

const auto kJsonRequiredTags = R"({
    "__default__": {
      "__default__": {
        "requires_tag": false,
        "tag": ""
      },
      "econom": {
        "requires_tag": false,
        "tag": ""
      },
      "comfort": {
        "requires_tag": true,
        "tag": "good_car"
      },
      "maybach": {
        "requires_tag": true,
        "tag": "new_car"
      }
    }
  })";

}  // namespace

UTEST(TestTagsRules, FallbackRequiredTags) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& tags_exclusion_config = config[configs::kTagsRules];
  const auto& required_tags = tags_exclusion_config.Get("none");
  ASSERT_TRUE(required_tags.IsEmpty());
}

UTEST(TestTagsRules, ParseRequiredTags) {
  tags::models::Cache cache = tags::models::Cache::MakeTestCache();
  // just register names
  cache.UpdateTags({{{"any", tags::models::EntityType::kUdid},
                     {"new_car", "good_car", "random_tag"}}});

  const auto required_tags = formats::json::FromString(kJsonRequiredTags)
                                 .As<configs::TagsRules>()
                                 .Get("none");
  ASSERT_FALSE(required_tags.IsEmpty());

  const models::Classes econom{"econom"};
  const auto& map_econom = required_tags.GetMapForClasses(econom, cache);
  EXPECT_EQ(econom, tags::models::RequiredTags::Filter(
                        map_econom, cache.GetTagIds({"new_car"}), econom));
  EXPECT_EQ(econom, tags::models::RequiredTags::FilterWithDiagnostics(
                        map_econom, cache.GetTagIds({"new_car"}), econom)
                        .filtered_classes);

  const models::Classes vip{"comfort", "business", "maybach"};
  const auto& map_vip = required_tags.GetMapForClasses(vip, cache);
  EXPECT_EQ(vip, tags::models::RequiredTags::Filter(
                     map_vip, cache.GetTagIds({"new_car", "good_car"}), vip));
  EXPECT_EQ(vip, tags::models::RequiredTags::FilterWithDiagnostics(
                     map_vip, cache.GetTagIds({"new_car", "good_car"}), vip)
                     .filtered_classes);
  EXPECT_EQ(
      models::Classes{"business"},
      tags::models::RequiredTags::Filter(map_vip, cache.GetTagIds({}), vip));
  EXPECT_EQ(models::Classes{"business"},
            tags::models::RequiredTags::FilterWithDiagnostics(
                map_vip, cache.GetTagIds({}), vip)
                .filtered_classes);
}
