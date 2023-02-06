#include <userver/utest/utest.hpp>

#include <eventus/pipeline/config/error_handler.hpp>
#include <eventus/pipeline/error_handler.hpp>

#include <fmt/format.h>

namespace {

using eventus::pipeline::ErrorHandler;
using eventus::pipeline::ErrorHandlingPolicy;
using ActionEnum = eventus::pipeline::config::ActionAfterErroneousExecution;
using StatsEnum = eventus::pipeline::config::ErroneousStatisticsLevel;

struct CallTimestampSaver {
  void Call() { call_tps.push_back(std::chrono::system_clock::now()); }

  int TimesCalled() const { return call_tps.size(); }

  int64_t GetDiffMs(int index) const {
    if (index == 0 || index > static_cast<int>(call_tps.size()) - 1) return 0;
    auto diff = call_tps[index] - call_tps[index - 1];
    return std::chrono::duration_cast<std::chrono::milliseconds>(diff).count();
  }

  std::vector<std::chrono::system_clock::time_point> call_tps;
};

struct TestArgs {
  int attempts;
  int min_delay_ms;
  int max_delay_ms;
  int delay_factor;
  ActionEnum action_after_error;
  bool fail;
  std::vector<int64_t> expected_delays;
};

std::string PrintTestArgsParam(const ::testing::TestParamInfo<TestArgs>& data) {
  const auto p = data.param;
  std::string max_delay_str = std::to_string(p.max_delay_ms);
  std::string expected_delays_str;
  for (const auto ed : p.expected_delays) {
    expected_delays_str += std::to_string(ed) + "_";
  }
  return fmt::format(
      "attempts_{}__min_delay_ms_{}__max_delay_ms_{}__delay_factor_{}__action_"
      "after_error_{}__fail_{}__expected_delays_{}",
      p.attempts, p.min_delay_ms, max_delay_str, p.delay_factor,
      p.action_after_error, p.fail, expected_delays_str);
}

}  // namespace

class ErrorHandlingPolicyWithWaitingSuite
    : public ::testing::TestWithParam<TestArgs> {};

INSTANTIATE_UTEST_SUITE_P(
    /**/, ErrorHandlingPolicyWithWaitingSuite,
    ::testing::Values(
        TestArgs{3, 10, 50, 5, ActionEnum::kPropagate, true, {10, 50}},
        TestArgs{4, 10, 50, 5, ActionEnum::kReject, true, {10, 50, 50}},
        TestArgs{1, 0, 1000, 1, ActionEnum::kReject, true, {}},
        TestArgs{10,
                 0,
                 {},
                 1,
                 ActionEnum::kReject,
                 true,
                 {0, 0, 0, 0, 0, 0, 0, 0, 0}},
        TestArgs{5, 5, 1000, 2, ActionEnum::kReject, true, {5, 10, 20, 40}},
        TestArgs{5, 10, 100, 1, ActionEnum::kReject, false, {}},
        TestArgs{5, 10, 100, 1, ActionEnum::kReject, true, {10, 10, 10, 10}}),
    PrintTestArgsParam);

UTEST_P(ErrorHandlingPolicyWithWaitingSuite, RunTest) {
  const auto& [attempts, min_delay_ms, max_delay_ms, delay_factor,
               action_after_error, fail, expected_delays] = GetParam();

  eventus::statistics::NodeStatistics stats;
  CallTimestampSaver cts;
  auto fail_func = [&cts]() {
    cts.Call();
    throw std::runtime_error("test");
  };
  auto ok_func = [&cts]() { cts.Call(); };
  auto eh = ErrorHandler(
      ErrorHandlingPolicy{attempts, std::chrono::milliseconds{min_delay_ms},
                          std::chrono::milliseconds{max_delay_ms}, delay_factor,
                          action_after_error, StatsEnum::kError});
  auto action = fail ? eh.TryExecute("", stats, fail_func)
                     : eh.TryExecute("", stats, ok_func);

  if (!fail) {
    ASSERT_TRUE(cts.TimesCalled() == 1);
    ASSERT_TRUE(!action);
    return;
  }

  ASSERT_TRUE(cts.TimesCalled() == attempts);
  for (int i = 1; i < attempts; i++) {
    ASSERT_TRUE(cts.GetDiffMs(i) >= expected_delays[i - 1]);
  }
  ASSERT_TRUE(action && *action == action_after_error);
}
