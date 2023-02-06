#include <js-pipeline/execution/statistics.hpp>
#include <userver/utils/assert.hpp>
#include "common.hpp"

namespace js_pipeline::testing {

namespace {
struct ComponentStatisticsTest : public JSTest {
  using JSTest::JSTest;
};
using js_pipeline::execution::StageMetrics;
using js_pipeline::execution::statistics_utils::GetMaxStages;
void check_equality(std::vector<std::pair<size_t, std::string>>& expected,
                    std::vector<std::pair<size_t, std::string>>& actual) {
  ASSERT_EQ(expected.size(), actual.size());
  std::sort(expected.begin(), expected.end());
  std::sort(actual.begin(), actual.end());
  for (size_t i = 0; i < expected.size(); ++i) {
    ASSERT_EQ(expected[i], actual[i]);
  }
}
}  // namespace

TEST_F(ComponentStatisticsTest, GetLongestStagesTest) {
  std::unordered_map<std::string, StageMetrics> test_data;
  test_data["stage1"].cumulative_execution_time_ms = 750;
  test_data["stage2"].cumulative_execution_time_ms = 300;
  test_data["stage3"].cumulative_execution_time_ms = 50;
  test_data["stage4"].cumulative_execution_time_ms = 75;

  auto accessor = [](const StageMetrics& stage_value) {
    return stage_value.cumulative_execution_time_ms;
  };

  auto actual = GetMaxStages(test_data, 2, accessor);
  auto expected = std::vector<std::pair<size_t, std::string>>{{750, "stage1"},
                                                              {300, "stage2"}};
  check_equality(expected, actual);

  actual = GetMaxStages(test_data, 5, accessor);
  expected = std::vector<std::pair<size_t, std::string>>{
      {750, "stage1"}, {300, "stage2"}, {75, "stage4"}, {50, "stage3"}};
  check_equality(expected, actual);
}
}  // namespace js_pipeline::testing
