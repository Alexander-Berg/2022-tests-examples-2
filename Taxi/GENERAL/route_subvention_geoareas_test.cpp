#include <memory>
#include <unordered_map>
#include <utility>

#include <fmt/format.h>
#include <gtest/gtest.h>

#include <userver/dynamic_config/snapshot.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utils/datetime.hpp>

#include <taxi_config/variables/TAGS_SUBVENTION_GEOAREAS_RULES.hpp>

#include <filters/efficiency/fetch_tags/fetch_tags.hpp>
#include <filters/efficiency/route_subvention_geoareas/models/geoarea_index.hpp>
#include <filters/efficiency/route_subvention_geoareas/models/route_geoarea_ids.hpp>
#include <filters/efficiency/route_subvention_geoareas/route_subvention_geoareas.hpp>
#include <geometry/position.hpp>
#include <userver/utest/utest.hpp>

namespace {

namespace filters = candidates::filters;
namespace eff = candidates::filters::efficiency;
namespace filter_models = route_subvention_geoareas::models;

using TagsCache = std::vector<tags::models::EntityWithTags>;

constexpr const char* kConfigFmt = R"([
    {{
      "tags": {{
        "and": [
          {{
            "any_of": ["tag1", "tag2"]
          }},
          {{
            "none_of": ["tag3", "tag4"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        "point_a": ["moscow"]
      }}
    }},
    {{
      "tags": {{
        "and": [
          {{
            "any_of": ["tag1", "tag3"]
          }},
          {{
            "none_of": ["tag2", "tag4"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

tags::models::Cache MakeTagsCache(TagsCache&& tags) {
  tags::models::Cache tags_cache = tags::models::Cache::MakeTestCache();
  tags_cache.UpdateTags(std::move(tags));

  static const auto kRevision = 1u;
  tags_cache.UpdateRevision(kRevision);

  return tags_cache;
}

tags::models::Cache MakeDefaultTagsCache() {
  return MakeTagsCache(TagsCache{
      {{"udid", tags::models::EntityType::kUdid}, {"tag1", "tag2"}},
      {{"car_number", tags::models::EntityType::kCarNumber}, {"tag3"}},
      {{"dbid", tags::models::EntityType::kPark}, {"tag4"}}});
}

void SetDefaultTags(filters::Context& context,
                    const tags::models::Cache& cache) {
  eff::FetchTags::Set(context, cache.GetTagIds({
                                   "tag1",
                                   "tag3",
                               }));
}

void TryAddProperty(const char* name, const std::vector<std::string>& values,
                    std::vector<std::string>& props) {
  if (!values.empty()) {
    props.emplace_back(
        fmt::format("\"{}\": [\"{}\"]", name, fmt::join(values, "\",\"")));
  }
}

dynamic_config::StorageMock MakeConfig(
    const std::vector<std::string>& point_a,
    const std::vector<std::string>& point_b,
    const std::vector<std::string>& midpoints, const char* cfg_fmt) {
  std::vector<std::string> props;
  TryAddProperty("point_a", point_a, props);
  TryAddProperty("point_b", point_b, props);
  TryAddProperty("midpoints", midpoints, props);

  return {
      {taxi_config::TAGS_SUBVENTION_GEOAREAS_RULES,
       formats::json::FromString(fmt::format(cfg_fmt, fmt::join(props, ",")))}};
}

geometry::Position MakePosition(double lon, double lat) {
  return {lon * ::geometry::units::lon, lat * ::geometry::units::lat};
}

std::shared_ptr<const route_subvention_geoareas::models::GeoareaIndex::Geoarea>
MakeGeoarea(std::string name) {
  return std::make_shared<
      route_subvention_geoareas::models::GeoareaIndex::Geoarea>(
      name,
      /*type=*/std::string(), name,
      utils::datetime::Stringtime("2020-08-10T12:55:00+0000"),
      std::vector<std::vector<client_geoareas_base::models::Position>>(
          {{MakePosition(1.0, 2.0), MakePosition(2.0, 2.0),
            MakePosition(2.0, 1.0), MakePosition(1.0, 1.0)}}),
      std::unordered_set<
          route_subvention_geoareas::models::GeoareaIndex::Geoarea::ZoneType>(),
      std::nullopt);
}

std::shared_ptr<const route_subvention_geoareas::models::GeoareaIndex>
MakeDefaultGeoareaIndex() {
  return std::make_shared<
      const route_subvention_geoareas::models::GeoareaIndex>(
      route_subvention_geoareas::models::GeoareaIndex::GeoareasByName{
          {"moscow", MakeGeoarea("moscow")},
          {"mkad", MakeGeoarea("mkad")},
          {"odincovo", MakeGeoarea("odincovo")},
          {"skolkovo", MakeGeoarea("skolkovo")},
          {"krasnogorsk", MakeGeoarea("krasnogorsk")},
          {"moscow_fix", MakeGeoarea("moscow_fix")},
          {"mkad_fix", MakeGeoarea("mkad_fix")},
          {"odincovo_fix", MakeGeoarea("odincovo_fix")},
      });
}

std::shared_ptr<const route_subvention_geoareas::models::GeoareaIndex>
MakeEmptyGeoareaIndex() {
  return std::make_shared<
      const route_subvention_geoareas::models::GeoareaIndex>();
}

filter_models::GeoareaIds MakeGeoareaIds(
    const route_subvention_geoareas::models::GeoareaIndex& geoarea_index,
    const std::vector<std::string>& geoarea_names) {
  filter_models::GeoareaIds res;
  res.reserve(geoarea_names.size());
  for (const auto& name : geoarea_names) {
    res.emplace(geoarea_index.GetRelativeId(name));
  }
  return res;
}

filters::Result Process(
    std::shared_ptr<const route_subvention_geoareas::models::GeoareaIndex>
        geoarea_index,
    const std::vector<std::string>& cfg_point_a,
    const std::vector<std::string>& cfg_point_b,
    const std::vector<std::string>& cfg_midpoints,
    const std::vector<std::string>& order_point_a,
    const std::vector<std::string>& order_point_b,
    const std::vector<std::string>& order_midpoints, const char* cfg_fmt) {
  filter_models::RouteGeoareaIds subvention_geoarea_ids{
      MakeGeoareaIds(*geoarea_index, order_point_a),
      MakeGeoareaIds(*geoarea_index, order_point_b),
      MakeGeoareaIds(*geoarea_index, order_midpoints),
  };

  static const auto tags_cache = MakeDefaultTagsCache();
  static const candidates::GeoMember geomember{{0, 0}, "dbid_uuid"};

  const auto cfg = MakeConfig(cfg_point_a, cfg_point_b, cfg_midpoints, cfg_fmt);
  filters::Context context;
  SetDefaultTags(context, tags_cache);

  eff::RouteSubventionGeoareas filter(filters::FilterInfo{}, cfg.GetSnapshot(),
                                      std::move(geoarea_index), tags_cache,
                                      std::move(subvention_geoarea_ids));
  return filter.Process(geomember, context);
}

filters::Result Process(const std::vector<std::string>& cfg_point_a,
                        const std::vector<std::string>& cfg_point_b,
                        const std::vector<std::string>& cfg_midpoints,
                        const std::vector<std::string>& order_point_a,
                        const std::vector<std::string>& order_point_b,
                        const std::vector<std::string>& order_midpoints,
                        const char* cfg_fmt = kConfigFmt) {
  static const auto geoarea_index = MakeDefaultGeoareaIndex();
  return Process(geoarea_index, cfg_point_a, cfg_point_b, cfg_midpoints,
                 order_point_a, order_point_b, order_midpoints, cfg_fmt);
}

filters::Result ProcessWithMissingGeoareas(
    const std::vector<std::string>& cfg_point_a,
    const std::vector<std::string>& cfg_point_b,
    const std::vector<std::string>& cfg_midpoints,
    const std::vector<std::string>& order_point_a,
    const std::vector<std::string>& order_point_b,
    const std::vector<std::string>& order_midpoints) {
  static const auto geoarea_index = MakeEmptyGeoareaIndex();
  return Process(geoarea_index, cfg_point_a, cfg_point_b, cfg_midpoints,
                 order_point_a, order_point_b, order_midpoints, kConfigFmt);
}

}  // namespace

TEST(RouteSubventionGeoareas, TestAllow) {
  auto actual =
      Process({"moscow"}, {"mkad", "odincovo"}, {"skolkovo"},  // config
              {"moscow"}, {"odincovo"}, {});                   // order
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallow) {
  auto actual =
      Process({"moscow"}, {"mkad", "odincovo"}, {"skolkovo"},  // config
              {"mkad"}, {"krasnogorsk"}, {});                  // order
  EXPECT_EQ(actual, filters::Result::kDisallow);
}

TEST(RouteSubventionGeoareas, TestAllowPointA) {
  auto actual = Process({"moscow"}, {}, {},             // config
                        {"moscow"}, {"odincovo"}, {});  // order
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallowPointA) {
  auto actual = Process({"moscow"}, {}, {},             // config
                        {"odincovo"}, {"moscow"}, {});  // order
  EXPECT_EQ(actual, filters::Result::kDisallow);
}

TEST(RouteSubventionGeoareas, TestAllowPointB) {
  auto actual = Process({}, {"moscow"}, {},             // config
                        {"odincovo"}, {"moscow"}, {});  // order
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallowPointB) {
  auto actual = Process({}, {"moscow"}, {},             // config
                        {"moscow"}, {"odincovo"}, {});  // order
  EXPECT_EQ(actual, filters::Result::kDisallow);
}

TEST(RouteSubventionGeoareas, TestAllowAnyMidpoints) {
  auto actual =
      Process({"moscow"}, {"mkad", "odincovo"}, {},             // config
              {"moscow"}, {"odincovo"}, {"mkad", "skolkovo"});  // order
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowMultipleGeoareas) {
  auto actual = Process({"moscow"}, {"mkad", "odincovo"}, {"mkad"},  // config

                        {"moscow", "moscow_fix"},      //
                        {"odincovo", "odincovo_fix"},  // order
                        {"mkad", "mkad_fix"});         //
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingGeoareas) {
  auto actual = ProcessWithMissingGeoareas(
      {"moscow"}, {"mkad", "odincovo"}, {},             // config
      {"moscow"}, {"odincovo"}, {"mkad", "skolkovo"});  // order
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowWithSomeMissingGeoareas) {
  auto actual =
      Process({"moscow", "missing"}, {"missing"}, {"missing"},      // config
              {"moscow", "moscow_fix"}, {}, {"mkad", "mkad_fix"});  // order
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingTagsNoneOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "none_of": ["missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallowWithSomeMissingTagsNoneOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "none_of": ["tag4", "missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kDisallow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingTagsAnyOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "any_of": ["missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallowWithSomeMissingTagsAnyOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "any_of": ["tag1", "missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kDisallow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingTagsAllOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "all_of": ["missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowWithSomeMissingTagsAllOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "all_of": ["tag1", "missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingTagsSubsetOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "subset_of": ["missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallowWithSomeMissingTagsSubsetOf) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
          "subset_of": ["tag1", "tag3", "missing"]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kDisallow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingTagsNotRule) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
        "not": {{
          "any_of": ["missing"]
        }}
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingTagsOrRule) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
        "or": [
          {{
            "any_of": ["missing"]
          }},
          {{
            "all_of": ["missing"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallowWithSomeMissingTagsOrRule) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
        "or": [
          {{
            "all_of": ["missing"]
          }},
          {{
            "any_of": ["tag1"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kDisallow);
}

TEST(RouteSubventionGeoareas, TestAllowWithMissingTagsAndRule) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
        "and": [
          {{
            "any_of": ["missing"]
          }},
          {{
            "all_of": ["missing"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowWithSomeMissingTagsAndRule) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
        "and": [
          {{
            "all_of": ["missing"]
          }},
          {{
            "any_of": ["tag1"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},    // config
                        {"odincovo"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestAllowIfAnyRuleAllows) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
        "and": [
          {{
            "all_of": ["tag1", "tag3"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        "point_a": ["mkad"]
      }}
    }},
    {{
      "tags": {{
        "and": [
          {{
            "all_of": ["tag1", "tag3"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        "point_a": ["skolkovo"]
      }}
    }},
    {{
      "tags": {{
        "and": [
          {{
            "all_of": ["tag1", "tag3"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"moscow"}, {}, {},  // config
                        {"moscow"}, {}, {},  // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kAllow);
}

TEST(RouteSubventionGeoareas, TestDisallowIfNoRuleAllows) {
  constexpr const char* kCustomCfgFmt = R"([
    {{
      "tags": {{
        "and": [
          {{
            "all_of": ["tag1", "tag3"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        "point_a": ["mkad"]
      }}
    }},
    {{
      "tags": {{
        "and": [
          {{
            "all_of": ["tag1", "tag3"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        "point_a": ["skolkovo"]
      }}
    }},
    {{
      "tags": {{
        "and": [
          {{
            "all_of": ["tag1", "tag3"]
          }}
        ]
      }},
      "subvention_geoareas": {{
        {}
      }}
    }}
  ])";

  auto actual = Process({"odincovo"}, {}, {},  // config
                        {"moscow"}, {}, {},    // order
                        kCustomCfgFmt);
  EXPECT_EQ(actual, filters::Result::kDisallow);
}
