#include <userver/utest/utest.hpp>

#include <boost/algorithm/string/classification.hpp>
#include <boost/algorithm/string/join.hpp>
#include <boost/algorithm/string/split.hpp>

#include <userver/formats/json/serialize.hpp>

#include <prometheus-stats/expose-format.hpp>

namespace prometheus_stats::impl {

namespace {

std::string Sorted(const std::string_view raw) {
  std::vector<std::string> lines;
  boost::split(lines, raw, boost::is_any_of("\n"));
  std::sort(lines.begin(), lines.end());
  return boost::algorithm::join(lines, "\n");
}

void TestToExposeFormat(const std::string_view raw_statistics,
                        const std::string_view expected,
                        const bool sorted = false) {
  const auto statistics = formats::json::FromString(raw_statistics);
  const auto result =
      ToPrometheusExposeFormat({{"application", "processing"}}, statistics);
  if (sorted) {
    EXPECT_EQ(Sorted(expected), Sorted(result));
  } else {
    EXPECT_EQ(expected, result);
  }
}

}  // namespace

TEST(ExposeFormat, ToPrometheusName) {
  EXPECT_EQ(ToPrometheusName("rss_kb"), "rss_kb");
  EXPECT_EQ(ToPrometheusName("httpclient.timings"), "httpclient_timings");
  EXPECT_EQ(ToPrometheusName("httpclient.reply-statuses"),
            "httpclient_reply_statuses");
  EXPECT_EQ(ToPrometheusName("httpclient.event-loop-load.1min"),
            "httpclient_event_loop_load_1min");
  EXPECT_EQ(ToPrometheusName("op./v1/cached-value/source-delete.error-parse"),
            "op__v1_cached_value_source_delete_error_parse");
  EXPECT_EQ(ToPrometheusName("processing-ng.queue.status.kEmpty"),
            "processing_ng_queue_status_kEmpty");
  EXPECT_EQ(ToPrometheusName("1metric"), "_1metric");
  EXPECT_EQ(ToPrometheusName("met:ric"), "met_ric");
}

TEST(ExposeFormat, ToPrometheusLabel) {
  EXPECT_EQ(ToPrometheusLabel("percentile"), "percentile");
  EXPECT_EQ(ToPrometheusLabel("postgresql_error"), "postgresql_error");
  EXPECT_EQ(ToPrometheusLabel("http.worker.id"), "http_worker_id");
  EXPECT_TRUE(ToPrometheusLabel("__./__").empty());
  EXPECT_EQ(ToPrometheusLabel("_42"), "_42");
  EXPECT_EQ(ToPrometheusLabel("_???42"), "_42");
  EXPECT_EQ(ToPrometheusName("la:bel"), "la_bel");
}

TEST(ExposeFormat, Tvm2TicketsCache) {
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
  const auto expected =
      "# TYPE cache_current_documents_count gauge\n"
      "cache_current_documents_count{application=\"processing\",cache_name="
      "\"tvm2-tickets-cache\"} 8\n"
      "# TYPE cache_full_time_time_from_last_update_start_ms gauge\n"
      "cache_full_time_time_from_last_update_start_ms{application="
      "\"processing\",cache_name=\"tvm2-tickets-cache\"} 2521742\n"
      "# TYPE cache_full_time_time_from_last_successful_start_ms gauge\n"
      "cache_full_time_time_from_last_successful_start_ms{application="
      "\"processing\",cache_name=\"tvm2-tickets-cache\"} 2521742\n"
      "# TYPE cache_full_time_last_update_duration_ms gauge\n"
      "cache_full_time_last_update_duration_ms{application=\"processing\","
      "cache_name=\"tvm2-tickets-cache\"} 58\n"
      "# TYPE cache_full_documents_read_count gauge\n"
      "cache_full_documents_read_count{application=\"processing\",cache_name="
      "\"tvm2-tickets-cache\"} 432\n"
      "# TYPE cache_full_documents_parse_failures gauge\n"
      "cache_full_documents_parse_failures{application=\"processing\",cache_"
      "name=\"tvm2-tickets-cache\"} 0\n"
      "# TYPE cache_full_update_attempts_count gauge\n"
      "cache_full_update_attempts_count{application=\"processing\",cache_name="
      "\"tvm2-tickets-cache\"} 56\n"
      "# TYPE cache_full_update_no_changes_count gauge\n"
      "cache_full_update_no_changes_count{application=\"processing\",cache_"
      "name=\"tvm2-tickets-cache\"} 0\n"
      "# TYPE cache_full_update_failures_count gauge\n"
      "cache_full_update_failures_count{application=\"processing\",cache_name="
      "\"tvm2-tickets-cache\"} 0\n";
  TestToExposeFormat(statistics, expected);
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
  const auto expected =
      "# TYPE base_key_some_key_ag_test gauge\n"
      "base_key_some_key_ag_test{application=\"processing\",child_lable_name="
      "\"lable_value_1\"} 76\n"
      "# TYPE base_key_some_key_ag_test1 gauge\n"
      "base_key_some_key_ag_test1{application=\"processing\",child_lable_name="
      "\"lable_value_1\"} 90\n"
      "# TYPE base_key_some_key_field1 gauge\n"
      "base_key_some_key_field1{application=\"processing\",child_lable_name="
      "\"lable_value_2\"} 3\n"
      "# TYPE base_key_some_key_field2 gauge\n"
      "base_key_some_key_field2{application=\"processing\",child_lable_name="
      "\"lable_value_2\"} 6.67\n"
      "# TYPE base_key_some_key_field3 gauge\n"
      "base_key_some_key_field3{application=\"processing\",overriden_lable_"
      "name=\"overriden_lable_value\"} 9999\n";
  TestToExposeFormat(statisics, expected, true);
}

TEST(ExposeFormat, SimpleStatistics) {
  const auto statistics = R"({
    "parent": {
      "child1": 1,
      "child2": 2
    }
  })";
  const auto expected =
      "# TYPE parent_child1 gauge\n"
      "parent_child1{application=\"processing\"} 1\n"
      "# TYPE parent_child2 gauge\n"
      "parent_child2{application=\"processing\"} 2\n";
  TestToExposeFormat(statistics, expected);
}

TEST(ExposeFormat, SimpleParentRenamed) {
  const auto statistics = R"({
    "parent_renamed": {
      "$meta": {
        "solomon_rename": "parent"
      },
      "child": 8
    }
  })";
  const auto expected =
      "# TYPE parent_child gauge\n"
      "parent_child{application=\"processing\"} 8\n";
  TestToExposeFormat(statistics, expected);
}

TEST(ExposeFormat, SimpleParentSkipped) {
  const auto statistics = R"({
    "parent_skipped": {
      "$meta": {
        "solomon_skip": "does_not_matter"
      },
      "child": 8
    }
  })";
  const auto expected =
      "# TYPE child gauge\n"
      "child{application=\"processing\"} 8\n";
  TestToExposeFormat(statistics, expected);
}

}  // namespace prometheus_stats::impl
