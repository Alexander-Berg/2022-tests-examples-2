#include <userver/formats/json.hpp>
#include <userver/utest/utest.hpp>

#include "utils/metrics.hpp"

UTEST(TestMetrics, MethodStatistics) {
  using namespace utils::metrics;
  std::string check = R"({
          "a": {
            "mode_3": {
              "method_3": {
                "iphone": 0,
                "android": 1,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              },
              "$meta": {
                "solomon_children_labels": "method"
              }
            },
            "mode_2": {
              "method_1": {
                "iphone": 0,
                "android": 1,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              },
              "$meta": {
                "solomon_children_labels": "method"
              }
            },
            "mode_1": {
              "method_1": {
                "iphone": 1,
                "android": 0,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              },
              "$meta": {
                "solomon_children_labels": "method"
              },
              "method_2": {
                "iphone": 1,
                "android": 0,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              }
            },
            "$meta": {
              "solomon_children_labels": "mode"
            }
          },
          "b": {
            "mode_2": {
              "method_3b": {
                "iphone": 0,
                "android": 1,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              },
              "$meta": {
                "solomon_children_labels": "method"
              }
            },
            "mode_1": {
              "method_1b": {
                "iphone": 0,
                "android": 1,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              },
              "$meta": {
                "solomon_children_labels": "method"
              },
              "method_2b": {
                "iphone": 1,
                "android": 0,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              }
            },
            "default": {
              "method_1b": {
                "iphone": 1,
                "android": 0,
                "$meta": {
                  "solomon_children_labels": "application_platform"
                }
              },
              "$meta": {
                "solomon_children_labels": "method"
              }
            },
            "$meta": {
              "solomon_children_labels": "mode"
            }
          },
          "$meta": {
            "solomon_children_labels": "point_type"
          }
        })";
  utils::metrics::MethodStatistics method_stats;
  method_stats.Account(PointType::kA, "method_1", "mode_1", Platform::kIphone);
  method_stats.Account(PointType::kA, "method_2", "mode_1", Platform::kIphone);
  method_stats.Account(PointType::kA, "method_1", "mode_2", Platform::kAndroid);
  method_stats.Account(PointType::kA, "method_3", "mode_3", Platform::kAndroid);
  method_stats.Account(PointType::kB, "method_1b", std::nullopt,
                       Platform::kIphone);
  method_stats.Account(PointType::kB, "method_2b", "mode_1", Platform::kIphone);
  method_stats.Account(PointType::kB, "method_1b", "mode_1",
                       Platform::kAndroid);
  method_stats.Account(PointType::kB, "method_3b", "mode_2",
                       Platform::kAndroid);
  auto result_json = method_stats.Format();
  ASSERT_EQ(result_json, formats::json::FromString(check));
}
