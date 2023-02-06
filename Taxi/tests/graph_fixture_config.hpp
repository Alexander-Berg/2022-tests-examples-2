#pragma once

#include <userver/formats/json/value_builder.hpp>

namespace graph::test {

namespace {

std::string ToIsoTime(const ::graph::TimePoint& date) {
  return utils::datetime::Timestring(date, "UTC", "%FT%T");
}

}  // namespace

/// Configuration values for graph-related fixtures
struct GraphTestFixtureConfig {
#if defined(ARCADIA_ROOT)
  /// Path to folder with test graph data
  static const char* kTestGraphDataDir;
  /// Path to precalc file from test graph data
  static const char* kTestPrecalcPath;
  /// Path to folder with real graph data
  static constexpr const char* kGraphDataDir =
      "/usr/share/yandex/taxi/graph/latest/";
  /// Path to precalc file from real graph data
  static constexpr const char* kPrecalcPath =
      "/usr/share/yandex/taxi/graph/latest/graph_precalc.mms.2";
#elif defined(__APPLE__)
  /// Path to folder with test graph data
  static constexpr const char* kTestGraphDataDir =
      "/usr/local/share/yandex/taxi/graph-test/graph3/";
  /// Path to precalc file from test graph data
  static constexpr const char* kTestPrecalcPath =
      "/usr/local/share/yandex/taxi/graph-test/graph3/graph_precalc.mms.2";
  /// Path to folder with real graph data
  static constexpr const char* kGraphDataDir =
      "/usr/local/share/yandex/taxi/graph/current/";
  /// Path to precalc file from real graph data
  static constexpr const char* kPrecalcPath =
      "/usr/local/share/yandex/taxi/graph/current/graph_precalc.mms.2";
#else
  /// Path to folder with test graph data
  static constexpr const char* kTestGraphDataDir =
      "/usr/share/yandex/taxi/graph-test/graph3/";
  /// Path to precalc file from test graph data
  static constexpr const char* kTestPrecalcPath =
      "/usr/share/yandex/taxi/graph-test/graph3/graph_precalc.mms.2";
  /// Path to folder with real graph data
  static constexpr const char* kGraphDataDir =
      "/usr/share/yandex/taxi/graph/latest/";
  /// Path to precalc file from real graph data
  static constexpr const char* kPrecalcPath =
      "/usr/share/yandex/taxi/graph/latest/graph_precalc.mms.2";
#endif

  static constexpr const char* kJamsFilenamePrefix = "";
  static constexpr const char* kJamsPath = "";

  static formats::json::Value GetJamsTestMetaJson() {
    formats::json::ValueBuilder ret;

    const auto& now = utils::datetime::Now();
    const auto& date = now - std::chrono::minutes(4);
    const auto& upload = now - std::chrono::minutes(3);
    const auto& download = now - std::chrono::minutes(2);
    ret["jams_date"] = ToIsoTime(date) + ".123456";
    ret["upload_date"] = ToIsoTime(upload);
    ret["download_date"] = ToIsoTime(download);
    ret["files"] = formats::json::Type::kArray;

    return ret.ExtractValue();
  }
};

}  // namespace graph::test
