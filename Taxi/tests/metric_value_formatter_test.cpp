#include <userver/utest/utest.hpp>

#include "types/metric_value.hpp"

#include <optional>

namespace eats_report_storage::types {

struct GetFormatMetricValue {
  std::string text;
  MetricValue value;
  std::string result;
};

class CheckFmtFormatMetricValue
    : public ::testing::TestWithParam<GetFormatMetricValue> {};

const std::vector<GetFormatMetricValue> kGetFormatMetricValueData{
    {"", MetricValue{}, ""},
    {"", MetricValue{0, 0, 0, "0", "0", "0"}, ""},
    {"{metric:total}", MetricValue{1, 2, 3, "1", "2", "3"}, "1"},
    {"{metric:delta}", MetricValue{1, 2, 3, "1", "2", "3"}, "2"},
    {"{metric:current}", MetricValue{1, 2, 3, "1", "2", "3"}, "3"},
    {"{metric:total} {metric:delta} {metric:current}",
     MetricValue{1, 2, 3, "1", "2", "3"}, "1 2 3"},
    {"a{metric:total} b{metric:delta} c{metric:current}",
     MetricValue{1, 2, 3, "1", "2", "3"}, "a1 b2 c3"},
    {"a{metric:total} b{metric:total} c{metric:total}",
     MetricValue{1, 2, 3, "1", "2", "3"}, "a1 b1 c1"},
};

INSTANTIATE_TEST_SUITE_P(GetFormatMetricValue, CheckFmtFormatMetricValue,
                         ::testing::ValuesIn(kGetFormatMetricValueData));

TEST_P(CheckFmtFormatMetricValue, success_fmt_format_metric_value) {
  const auto& param = GetParam();
  ASSERT_EQ(fmt::format(param.text, fmt::arg("metric", param.value)),
            param.result);
}

class CheckFmtFormatMetricValueFail
    : public ::testing::TestWithParam<GetFormatMetricValue> {};

const std::vector<GetFormatMetricValue> kGetFormatMetricValueDataFail{
    {"{metric}", MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"{metric:tota}", MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"{metric:deltasds}", MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"{metric:currents}", MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"{metric:total} {metric:delta} {metric:current} {metric}",
     MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"{metric:total} {metric:delta} {metric:curre}",
     MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"{metric:total} {metric:delta} {metric:current}",
     MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"{metrics}", MetricValue{1, 2, 3, "1", "2", "3"}, ""},
    {"a {vetric:tot}", MetricValue{1, 2, 3, "1", "2", "3"}, ""},
};

INSTANTIATE_TEST_SUITE_P(GetFormatMetricValue, CheckFmtFormatMetricValueFail,
                         ::testing::ValuesIn(kGetFormatMetricValueDataFail));

TEST_P(CheckFmtFormatMetricValueFail, fail_fmt_format_metric_value) {
  const auto& param = GetParam();
  try {
    auto re = fmt::format(param.text, fmt::arg("metric", param.value));
    ASSERT_NE(param.result, re);
  } catch (fmt::format_error) {
    ASSERT_TRUE(true);
  }
}

}  // namespace eats_report_storage::types
