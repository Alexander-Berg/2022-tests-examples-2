#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utest/utest.hpp>

#include <solomon-stats/json_converter.hpp>

namespace {

formats::json::Value Sorted(const formats::json::Value& array) {
  EXPECT_TRUE(array.IsArray());

  std::vector<formats::json::Value> data;
  for (const auto& metric : array) {
    data.emplace_back(metric);
  }
  std::sort(
      data.begin(), data.end(),
      [](const formats::json::Value& lhs, const formats::json::Value& rhs) {
        return lhs["labels"]["sensor"].As<std::string>() >
               rhs["labels"]["sensor"].As<std::string>();
      });

  formats::json::ValueBuilder builder;
  for (const auto& metric : data) {
    builder.PushBack(metric);
  }
  return builder.ExtractValue();
}

void Convert(const std::string_view raw_statistics,
             std::string_view raw_expected) {
  const auto statistics = formats::json::FromString(raw_statistics);
  const auto expected = Sorted(formats::json::FromString(raw_expected));

  formats::json::StringBuilder builder;
  solomon_stats::ToSolomonMetricsJson(builder, statistics);
  const auto raw_result = builder.GetString();
  const auto result = Sorted(formats::json::FromString(raw_result));

  EXPECT_EQ(expected, result);
}

}  // namespace

TEST(Converter, Tvm2TicketsCache) {
  const auto statistics = R"({
    "cache": {
      "tvm2-tickets-cache": {
        "$meta": {
          "solomon_label": "cache_name"
        },
        "full": {
          "update": {
            "attempts_count": 56,
            "no_changes_count": 0,
            "failures_count": 0
          },
          "documents": {
            "read_count": 432,
            "parse_failures": 0
          },
          "time": {
            "time-from-last-update-start-ms": 2521742,
            "time-from-last-successful-start-ms": 2521742,
            "last-update-duration-ms": 58
          }
        },
        "current-documents-count": 8
      }
    }
  })";
  const auto expected = R"([
    {"labels": {"sensor": "cache.current-documents-count", "cache_name": "tvm2-tickets-cache"}, "value": 8},
    {"labels": {"sensor": "cache.full.time.time-from-last-update-start-ms", "cache_name": "tvm2-tickets-cache"}, "value": 2521742},
    {"labels": {"sensor": "cache.full.time.time-from-last-successful-start-ms", "cache_name": "tvm2-tickets-cache"}, "value": 2521742},
    {"labels": {"sensor": "cache.full.time.last-update-duration-ms", "cache_name": "tvm2-tickets-cache"}, "value": 58},
    {"labels": {"sensor": "cache.full.documents.read_count", "cache_name": "tvm2-tickets-cache"}, "value": 432},
    {"labels": {"sensor": "cache.full.documents.parse_failures", "cache_name": "tvm2-tickets-cache"}, "value": 0},
    {"labels": {"sensor": "cache.full.update.attempts_count", "cache_name": "tvm2-tickets-cache"}, "value": 56},
    {"labels": {"sensor": "cache.full.update.no_changes_count", "cache_name": "tvm2-tickets-cache"}, "value": 0},
    {"labels": {"sensor": "cache.full.update.failures_count", "cache_name": "tvm2-tickets-cache"}, "value": 0}
  ])";
  Convert(statistics, expected);
}

TEST(Converter, SolomonChildrenLabel) {
  const auto statisics = R"({
    "base_key": {
      "some_key": {
        "$meta": {
          "solomon_children_labels": "child_lable_name"
        },
        "lable_value_1": {
          "ag": {
            "test": 76,
            "test1": 90
          }
        },
        "lable_value_2": {
          "field1": 3,
          "field2": 6.67
        },
        "overriden_lable_value": {
          "$meta": {
            "solomon_label": "overriden_lable_name"
          },
          "field3": 9999
        }
      }
    }
  })";
  const auto expected = R"([
    {"labels": {"child_lable_name": "lable_value_1", "sensor": "base_key.some_key.ag.test"}, "value": 76},
    {"labels": {"child_lable_name": "lable_value_1", "sensor": "base_key.some_key.ag.test1"}, "value": 90},
    {"labels": {"child_lable_name": "lable_value_2", "sensor": "base_key.some_key.field1"}, "value": 3},
    {"labels": {"child_lable_name": "lable_value_2", "sensor": "base_key.some_key.field2"}, "value": 6.67},
    {"labels": {"overriden_lable_name": "overriden_lable_value", "sensor": "base_key.some_key.field3"}, "value": 9999}
  ])";
  Convert(statisics, expected);
}

TEST(Converter, SimpleStatistics) {
  const auto statistics = R"({
    "parent": {
      "child1": 1,
      "child2": 2
    }
  })";
  const auto expected = R"([
    {"labels": {"sensor": "parent.child1"}, "value": 1},
    {"labels": {"sensor": "parent.child2"}, "value": 2}
  ])";
  Convert(statistics, expected);
}

TEST(Converter, SimpleParentRenamed) {
  const auto statistics = R"({
    "parent_renamed": {
      "$meta": {
        "solomon_rename": "parent"
      },
      "child": 8
    }
  })";
  const auto expected = R"([
    {"labels": {"sensor": "parent.child"}, "value": 8}
  ])";
  Convert(statistics, expected);
}

TEST(Converter, SimpleParentSkipped) {
  const auto statistics = R"({
    "parent_skipped": {
      "$meta": {
        "solomon_skip": "does_not_matter"
      },
      "child": 8
    }
  })";
  const auto expected = R"([
    {"labels": {"sensor": "child"}, "value": 8}
  ])";
  Convert(statistics, expected);
}
