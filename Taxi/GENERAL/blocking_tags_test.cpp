#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/json.hpp>
#include <userver/fs/blocking/read.hpp>

#include <dispatch-settings/dispatch_settings.hpp>
#include <dispatch-settings/models/settings_values_serialization.hpp>
#include <filters/efficiency/fetch_tags_classes/configs/tags_rules.hpp>
#include <filters/efficiency/fetch_tags_classes/models/blocking_tags.hpp>
#include <filters/efficiency/fetch_tags_classes/models/required_tags.hpp>
#include <utils/mock_dispatch_settings.hpp>

#include "blocking_tags.hpp"

namespace {

const auto kJsonBlockingTags = R"({
  "__default__": {
    "__default__": {
      "DISPATCH_DRIVER_TAGS_BLOCK": ["bad_driver", "bad_car"]
    },
    "econom": {
      "DISPATCH_DRIVER_TAGS_BLOCK": ["econom_excluded"]
    }
  }
})";

using tags::models::BlockingTags;
using tags::models::RequiredTags;

}  // namespace

UTEST(TestTagsRules, ParseBlockingTags) {
  tags::models::Cache cache = tags::models::Cache::MakeTestCache();
  // just register names
  cache.UpdateTags(
      {{{"any", tags::models::EntityType::kUdid},
        {"econom_excluded", "bad_driver", "bad_car", "random_tag"}}});

  auto dispatch_settings = std::make_shared<utils::MockDispatchSettings>(
      formats::json::FromString(kJsonBlockingTags));

  const auto& blocking_tags = tags::models::BlockingTags(*dispatch_settings);

  const models::Classes econom{"econom"};
  const auto& map_econom =
      blocking_tags.GetMapForZoneClasses("none", econom, cache);
  EXPECT_EQ(models::Classes{},
            BlockingTags::Filter(map_econom,
                                 cache.GetTagIds({"econom_excluded"}), econom));
  EXPECT_EQ(models::Classes{},
            BlockingTags::FilterWithDiagnostics(
                map_econom, cache.GetTagIds({"econom_excluded"}), econom)
                .filtered_classes);
  EXPECT_EQ(econom,
            BlockingTags::Filter(map_econom, cache.GetTagIds({"vip"}), econom));
  EXPECT_EQ(econom, BlockingTags::FilterWithDiagnostics(
                        map_econom, cache.GetTagIds({"vip"}), econom)
                        .filtered_classes);

  const models::Classes vip{"comfort", "business", "vip"};
  const auto& map_vip = blocking_tags.GetMapForZoneClasses("none", vip, cache);
  EXPECT_EQ(vip, BlockingTags::Filter(
                     map_vip, cache.GetTagIds({"econom_excluded"}), vip));
  EXPECT_EQ(vip, BlockingTags::FilterWithDiagnostics(
                     map_vip, cache.GetTagIds({"econom_excluded"}), vip)
                     .filtered_classes);
  EXPECT_EQ(models::Classes{},
            BlockingTags::Filter(
                map_vip, cache.GetTagIds({"bad_driver", "random_tag"}), vip));
  EXPECT_EQ(models::Classes{},
            BlockingTags::FilterWithDiagnostics(
                map_vip, cache.GetTagIds({"bad_driver", "random_tag"}), vip)
                .filtered_classes);
  EXPECT_EQ(models::Classes{},
            BlockingTags::Filter(map_vip, cache.GetTagIds({"bad_car"}), vip));
  EXPECT_EQ(models::Classes{}, BlockingTags::FilterWithDiagnostics(
                                   map_vip, cache.GetTagIds({"bad_car"}), vip)
                                   .filtered_classes);
}
