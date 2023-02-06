#include "worst_state_test_case.hpp"

#include <utils/json_field_check.hpp>

#include <fmt/format.h>

namespace hejmdal::radio::tester {

namespace params {
const std::string kWorstStateParamName = "worst_state";
const std::string kShouldReachParamName = "should_reach_worst_state";
}  // namespace params

void WorstStateTestCase::Initialize(formats::json::Value params) {
  worst_state_ =
      State::FromString(utils::JsonFieldCheck("WorstStateTestCase", params,
                                              params::kWorstStateParamName)
                            .Required()
                            .String()
                            .Get());
  should_reach_worst_state_ =
      utils::JsonFieldCheck("WorstStateTestCase", params,
                            params::kShouldReachParamName)
          .Bool()
          .GetOr(true);
}

void WorstStateTestCase::StateInCallback(const time::TimePoint& tp,
                                         const State& state) {
  if (first_error_.has_value()) return;
  if (GetTimeRange().Contains(tp) && state >= worst_state_) {
    worst_state_reached_ = true;
    if (state > worst_state_) {
      first_error_ = std::make_pair(tp, state);
    }
  }
}

TestCaseResult WorstStateTestCase::GetResult() const {
  TestCaseResult result(GetId(), GetType(), GetDescription());
  if (first_error_.has_value()) {
    result.passed = false;
    result.error_message =
        fmt::format("At {} state was {} that is worse than {}",
                    time::datetime::Timestring(first_error_->first),
                    first_error_->second.ToString(), worst_state_.ToString());
  } else if (should_reach_worst_state_ && !worst_state_reached_) {
    result.passed = false;
    result.error_message =
        fmt::format("State {} was not reached in the in given time range",
                    worst_state_.ToString());
  }
  return result;
}

}  // namespace hejmdal::radio::tester
